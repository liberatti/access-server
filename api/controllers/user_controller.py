import bcrypt
from flask import Blueprint, request, Response
from marshmallow import ValidationError
from nxcore.controllers.base_controller import (
    has_any_authority,
    response_data,
    response_error_parse,
    response_error_404,
    response_error_401,
    response_error_500,
    response_error_403,
)
from nxcore.middleware.jwt_manager import JWTManager
from api.repository.user_model import UserDao
from api.repository.vpn_model import VPNSessionDao
from api.tools.vpn_tool import VPNTool
from api.tools.firewall_tool import FirewallTool
from config import SECURITY_ENABLED

routes = Blueprint("user", __name__)


@routes.route("", methods=["POST"])
@has_any_authority(["superuser"])
def save() -> Response:
    model = UserDao()
    try:
        data = request.json
        if "password" in data:
            hashed = bcrypt.hashpw(data["password"].encode("utf8"), bcrypt.gensalt())
            data.update({"password": hashed.decode("utf-8")})
        pk = model.persist(data)
        VPNTool.create_client(pk)
        FirewallTool.create_user(pk)
        FirewallTool.refresh_user_chain(pk)
        user = model.get_by_id(pk)
        model.commit()
        model.close()
        user.pop("password", None)
        return response_data(user)
    except ValidationError as err:
        model.close()
        return response_error_parse(err)


@routes.route("", methods=["GET"])
@has_any_authority(["viewer", "superuser"])
def get() -> Response:
    model = UserDao()
    if "size" in request.args and "page" in request.args:
        per_page = int(request.args.get("size"))
        page = int(request.args.get("page"))
        result = model.query_all(page, per_page)
    else:
        result = model.query_all()
    if result["metadata"]["total_pages"] > 0:
        sessionDao = VPNSessionDao()
        for r in result["data"]:
            sessions = sessionDao.get_all_by_user_id(r["id"])
            r.update({"sessions": sessions})
            r.pop("password", None)
        sessionDao.close()
        model.close()
        return response_data(result)
    else:
        model.close()
        return response_error_404()


@routes.route("/<user_id>", methods=["GET"])
@has_any_authority(["viewer", "superuser"])
def get_by_id(user_id) -> Response:
    model = UserDao()
    user = model.get_by_id(user_id)
    model.close()
    if user:
        user.pop("password", None)
        return response_data(user)
    else:
        return response_error_404()


@routes.route("/<user_id>", methods=["PUT"])
@has_any_authority(["superuser"])
def update(user_id) -> Response:
    model = UserDao()
    user = model.get_by_id(user_id)
    try:
        data = request.json
        if "password" in data and len(data["password"]) > 1:
            hashed = bcrypt.hashpw(data["password"].encode("utf8"), bcrypt.gensalt())
            data.update({"password": hashed.decode("utf-8")})
        else:
            data.update({"password": user["password"]})

        model.update_by_id(user_id, data)
        model.commit()
        model.close()
        FirewallTool.refresh_user_chain(user_id)
        data.pop("password", None)
        return response_data(data)
    except ValidationError as err:
        model.close()
        return response_error_parse(err)


@routes.route("/<user_id>", methods=["DELETE"])
@has_any_authority(["superuser"])
def delete(user_id) -> Response:
    model = UserDao()
    user = model.get_by_id(user_id)
    try:
        result = model.delete_by_id(user_id)
        model.commit()
        FirewallTool.remove_user(user_id)
        VPNTool.remove_client(user_id)
        model.close()
        if result:
            return response_data({"message": f"Record {user_id} removed", "code": 200})
        else:
            return response_error_404()
    except Exception as e:
        model.close()
        return response_error_500(str(e))


@routes.route("/<user_id>/config/<target>", methods=["GET"])
@has_any_authority(["viewer", "superuser"])
def get_config_by_id(user_id, target) -> Response:
    model = UserDao()
    user = model.get_by_id(user_id)
    model.close()
    if user:
        config = VPNTool.get_openvpn_client(user_id, target)
        return Response(
            config, headers={"Content-Type": "text/plain; charset=utf-8"}
        )
    else:
        return response_error_404()


@routes.route("/login", methods=["POST"])
def login() -> Response:
    model = UserDao()
    try:
        user = model.find_by_username(request.json["username"])
        model.close()
        if user:
            if bcrypt.checkpw(
                request.json["password"].encode("utf8"), user["password"].encode("utf8")
              ):
                jwt_mgr = JWTManager.get_current_instance()
                access_token = jwt_mgr.create_access_token(
                    sub=user["username"],
                    authorities=[user["role"]],
                    profile=user,
                    extra_claims={"aud": "as"}
                )
                return response_data(
                    {"access_token": access_token, "token_type": "Bearer"}
                )
        return response_error_403()
    except ValidationError as err:
        model.close()
        return response_error_parse(err)


@routes.route("/info/", methods=["GET"])
@has_any_authority(["viewer", "superuser"])
def info() -> Response:
    if SECURITY_ENABLED:
        jwt_mgr = JWTManager.get_current_instance()
        token = jwt_mgr.get_token_from_request()
        payload = jwt_mgr.decode(token)
        return response_data({"username": payload["sub"]})
    else:
        return response_data({"username": "dummy"})
