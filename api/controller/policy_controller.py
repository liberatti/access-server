from flask import Blueprint, request
from marshmallow import ValidationError
from api.utils import has_any_authority
from api.model.policy_model import PolicyDao
from api.tools.response_builder import ResponseBuilder
from api.tools.firewall_tool import FirewallTool
from api.model.user_model import UserDao

routes = Blueprint("policy", __name__)


@routes.route("", methods=["POST"])
@has_any_authority(["admin"])
def save():
    model = PolicyDao()
    response = None
    try:
        request.json.update({"type": "user"})
        pk = model.persist(request.json)
        policy = model.get_by_id(pk)
        FirewallTool.create_policy_chain(pk)
        model.commit()
        model.close()
        response = ResponseBuilder.data(policy)
    except ValidationError as err:
        response = ResponseBuilder.error_parse(err)
    return response


@routes.route("", methods=["GET"])
@has_any_authority(["admin"])
def get():
    model = PolicyDao()
    if "size" in request.args and "page" in request.args:
        per_page = int(request.args.get("size"))
        page = int(request.args.get("page"))
        result = model.query_all(page, per_page)
    else:
        result = model.query_all()

    if result['metadata']["total_pages"] > 0:
        for p in result["data"]:
            if "clients" in p:
                u_model = UserDao()
                for c in p["clients"]:
                    client = u_model.get_descr(c["id"])
                    if client:
                        c.update(client)

        return ResponseBuilder.data(result)
    else:
        return ResponseBuilder.error_404(request.url)


@routes.route("/<policy_id>", methods=["GET"])
@has_any_authority(["admin"])
def get_by_id(policy_id):
    policy = PolicyDao().get_by_id(policy_id)

    if policy:
        if "clients" in policy:
            u_model = UserDao()
            for c in policy["clients"]:
                c.update(u_model.get_descr(c["id"]))
        return ResponseBuilder.data(policy)
    else:
        return ResponseBuilder.error_404(request.url)


@routes.route("/<policy_id>", methods=["PUT"])
@has_any_authority(["admin"])
def update(policy_id):
    model = PolicyDao()
    response = None
    try:
        model.update_by_id(policy_id, request.json)
        policy = model.get_by_id(policy_id)
        model.commit()
        model.close()
        FirewallTool.refresh_policy_chain(policy_id)
        response = ResponseBuilder.data(policy)
    except ValidationError as err:
        response = ResponseBuilder.error_parse(err)
    return response


@routes.route("/<policy_id>", methods=["DELETE"])
@has_any_authority(["admin"])
def delete(policy_id):
    model = PolicyDao()
    model.delete_by_id(policy_id)
    model.commit()
    model.close()
    return ResponseBuilder.data_removed(policy_id)
