import bcrypt
from flask import Blueprint, request, Response
from marshmallow import ValidationError
from nxcore.controllers.base_controller import (
    has_any_authority,
    response_data,
    response_error_parse,
    response_error_404,
    response_error_500,
    response_error_403,
    get_pagination,
)
from nxcore.middleware.jwt_manager import JWTManager
from api.model.user_model import UserDao
from api.model.vpn_model import VPNSessionDao
from api.tools.vpn_tool import VPNTool
from api.tools.firewall_tool import FirewallTool
from config import SECURITY_ENABLED

routes = Blueprint("user", __name__)


@routes.route("", methods=["POST"])
@has_any_authority(["superuser"])
def save() -> Response:
    """Create and persist a new user, hashing password and generating VPN/firewall rules.

    :return: Response containing saved user details or validation error.
    :rtype: flask.Response
    """
    with UserDao() as model:
        try:
            data = request.json
            if "password" in data:
                hashed = bcrypt.hashpw(
                    data["password"].encode("utf8"), bcrypt.gensalt()
                )
                data.update({"password": hashed.decode("utf-8")})
            pk = model.persist(data)
            VPNTool.create_client(pk)
            FirewallTool.create_user(pk)
            FirewallTool.refresh_user_chain(pk)
            user = model.get_by_id(pk)
            user.pop("password", None)
            return response_data(user)
        except ValidationError as err:
            return response_error_parse(err)


@routes.route("", methods=["GET"])
@has_any_authority(["viewer", "superuser"])
def get() -> Response:
    """Retrieve all users with active sessions and pagination.

    :return: Response containing list of users or 404 error if empty.
    :rtype: flask.Response
    """
    with UserDao() as model:
        result = model.get_all(pagination=get_pagination())
        with VPNSessionDao() as sessionDao:
            for r in result["data"]:
                sessions = sessionDao.get_all_by_user_id(r["id"])
                r.update({"sessions": sessions})
                r.pop("password", None)
        return response_data(result)


@routes.route("/<user_id>", methods=["GET"])
@has_any_authority(["viewer", "superuser"])
def get_by_id(user_id) -> Response:
    """Retrieve user details by ID.

    :param user_id: User identifier.
    :type user_id: str
    :return: Response containing user record or 404 error.
    :rtype: flask.Response
    """
    with UserDao() as model:
        user = model.get_by_id(user_id)
        if user:
            user.pop("password", None)
            return response_data(user)
    return response_error_404()


@routes.route("/<user_id>", methods=["PUT"])
@has_any_authority(["superuser"])
def update(user_id) -> Response:
    """Update an existing user record and refresh firewall chains.

    :param user_id: User identifier.
    :type user_id: str
    :return: Response containing updated user data or validation error.
    :rtype: flask.Response
    """
    with UserDao() as model:
        user = model.get_by_id(user_id)
        try:
            data = request.json
            if "password" in data and len(data["password"]) > 1:
                hashed = bcrypt.hashpw(
                    data["password"].encode("utf8"), bcrypt.gensalt()
                )
                data.update({"password": hashed.decode("utf-8")})
            else:
                data.update({"password": user["password"]})
            model.update_by_id(user_id, data)
            FirewallTool.refresh_user_chain(user_id)
            data.pop("password", None)
            return response_data(data)
        except ValidationError as err:
            return response_error_parse(err)


@routes.route("/<user_id>", methods=["DELETE"])
@has_any_authority(["superuser"])
def delete(user_id) -> Response:
    """Delete user, remove firewall rules, and revoke VPN certificates.

    :param user_id: User identifier.
    :type user_id: str
    :return: Response confirming user deletion or 404/500 error.
    :rtype: flask.Response
    """
    with UserDao() as model:
        try:
            result = model.delete_by_id(user_id)
            FirewallTool.remove_user(user_id)
            VPNTool.remove_client(user_id)
            if result:
                return response_data(
                    {"message": f"Record {user_id} removed", "code": 200}
                )
            else:
                return response_error_404()
        except Exception as e:
            return response_error_500(str(e))


@routes.route("/<user_id>/config/<target>", methods=["GET"])
@has_any_authority(["viewer", "superuser"])
def get_config_by_id(user_id, target) -> Response:
    """Generate and return OpenVPN configuration profile (.ovpn) for a user.

    :param user_id: User identifier.
    :type user_id: str
    :param target: Target profile format name.
    :type target: str
    :return: Plain text OpenVPN configuration response.
    :rtype: flask.Response
    """
    with UserDao() as model:
        user = model.get_by_id(user_id)
    if user:
        config = VPNTool.get_openvpn_client(user_id, target)
        return Response(config, headers={"Content-Type": "text/plain; charset=utf-8"})
    else:
        return response_error_404()


@routes.route("/login", methods=["POST"])
def login() -> Response:
    """Authenticate user credentials and issue a JWT access token.

    :return: Response containing Bearer access token or 403 error.
    :rtype: flask.Response
    """
    with UserDao() as model:
        try:
            user = model.find_by_username(request.json["username"])
            if user:
                if bcrypt.checkpw(
                    request.json["password"].encode("utf8"),
                    user["password"].encode("utf8"),
                ):
                    jwt_mgr = JWTManager.get_current_instance()
                    access_token = jwt_mgr.create_access_token(
                        sub=user["username"],
                        authorities=[user["role"]],
                        profile=user,
                        extra_claims={"aud": "as"},
                    )
                    return response_data(
                        {"access_token": access_token, "token_type": "Bearer"}
                    )
                return response_error_403()
            return response_error_403()
        except ValidationError as err:
            return response_error_parse(err)


@routes.route("/info/", methods=["GET"])
@has_any_authority(["viewer", "superuser"])
def info() -> Response:
    """Retrieve logged-in user information from request JWT token.

    :return: Response containing username payload.
    :rtype: flask.Response
    """
    if SECURITY_ENABLED:
        jwt_mgr = JWTManager.get_current_instance()
        token = jwt_mgr.get_token_from_request()
        payload = jwt_mgr.decode(token)
        return response_data({"username": payload["sub"]})
    else:
        return response_data({"username": "dummy"})
