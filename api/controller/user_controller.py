import bcrypt
from flask import Blueprint, request
from flask_jwt_extended import create_access_token, get_jwt
from marshmallow import ValidationError
from api.model.user_model import PortMappingDao, UserDao
from api.utils import has_any_authority, logger
from api.tools.vpn_tool import VPNTool
from api.tools.response_builder import ResponseBuilder
from api.tools.firewall_tool import FirewallTool
from config import SECURITY_ENABLED

routes = Blueprint("user", __name__)


@routes.route("", methods=["POST"])
@has_any_authority(["admin"])
def save():
    model = UserDao()
    try:
        data = request.json
        if "password" in data:
            hashed = bcrypt.hashpw(data["password"].encode("utf8"), bcrypt.gensalt())
            data.update({"password": hashed.decode("utf-8")})
        pk = model.persist(data)
        VPNTool.create_client(pk)
        FirewallTool.refresh_user_chain(pk)
        user = model.get_by_id(pk)
        model.commit()
        user.pop("password")
        return ResponseBuilder.data(user)
    except ValidationError as err:
        return ResponseBuilder.error_parse(err)


@routes.route("", methods=["GET"])
@has_any_authority(["admin"])
def get():
    model = UserDao()
    if "size" in request.args and "page" in request.args:
        per_page = int(request.args.get("size"))
        page = int(request.args.get("page"))
        result = model.query_all(page, per_page)
    else:
        result = model.query_all()
    if result['metadata']["total_pages"] > 0:
        for r in result["data"]:
            r.pop("password")
        return ResponseBuilder.data(result)
    else:
        return ResponseBuilder.error_404(request.url)


@routes.route("/<user_id>", methods=["GET"])
@has_any_authority(["admin"])
def get_by_id(user_id):
    user = UserDao().get_by_id(user_id)
    if user:
        user.pop("password")
        return ResponseBuilder.data(user)
    else:
        return ResponseBuilder.error_404(request.url)


@routes.route("/<user_id>", methods=["PUT"])
@has_any_authority(["admin"])
def update(user_id):
    model = UserDao()
    try:
        data = request.json
        if "password" in data:
            hashed = bcrypt.hashpw(data["password"].encode("utf8"), bcrypt.gensalt())
            data.update({"password": hashed.decode("utf-8")})
        model.update_by_id(user_id, data)
        model.commit()
        FirewallTool.refresh_user_chain(user_id)
        data.pop("password")
        return ResponseBuilder.data(data)
    except ValidationError as err:
        return ResponseBuilder.error_parse(err)


@routes.route("/<user_id>", methods=["DELETE"])
@has_any_authority(["admin"])
def delete(user_id):
    model = UserDao()
    user=model.get_by_id(user_id)
    response = None
    try:
        result = model.delete_by_id(user_id)
        if result:
            daoMapping = PortMappingDao(connection=model.connection)
            daoMapping.delete_by_user(user_id)
        model.commit()

        VPNTool.remove_client(user_id)
        if result:
            response = ResponseBuilder.data_removed(user_id)
        else:
            response = ResponseBuilder.error_404(request.url)
    except Exception as e:
        response = ResponseBuilder.error_500(e)
    model.close()
    return response


@routes.route("/<user_id>/config", methods=["GET"])
@has_any_authority(["user", "admin"])
def get_config_by_id(user_id):
    user = UserDao().get_by_id(user_id)
    if user:
        config = VPNTool.get_openvpn_client(user_id)
        return ResponseBuilder.raw(
            config, headers={"Content-Type": "text/plain; charset=utf-8"}
        )
    else:
        return ResponseBuilder.error_404(request.url)


@routes.route("/login", methods=["POST"])
def login():
    model = UserDao()
    try:
        user = model.find_by_username(request.json["username"])
        if user:
            if bcrypt.checkpw(
                request.json["password"].encode("utf8"), user["password"].encode("utf8")
            ):
                additional_claims = {"aud": "tooka-admin", "role": user["role"]}
                access_token = create_access_token(
                    identity=user["username"], additional_claims=additional_claims
                )
                return ResponseBuilder.data(
                    {"access_token": access_token, "token_type": "Bearer"}
                )
        else:
            return ResponseBuilder.error_403()

    except ValidationError as err:
        return ResponseBuilder.error_parse(err)


@routes.route("/info/", methods=["GET"])
@has_any_authority(["user", "admin"])
def info():
    if SECURITY_ENABLED:
        claims = get_jwt()
        return {"username": claims["sub"]}
    else:
        return {"username": "dummy"}
