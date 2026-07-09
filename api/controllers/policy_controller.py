from flask import Blueprint, request, Response
from marshmallow import ValidationError
from nxcore.controllers.base_controller import (
    has_any_authority,
    response_data,
    response_error_parse,
    response_error_404,
    response_data_removed,
)
from api.repository.policy_model import PolicyDao
from api.tools.firewall_tool import FirewallTool
from api.repository.user_model import UserDao

routes = Blueprint("policy", __name__)


@routes.route("", methods=["POST"])
@has_any_authority(["superuser"])
def save() -> Response:
    model = PolicyDao()
    try:
        request.json.update({"type": "user"})
        pk = model.persist(request.json)
        policy = model.get_by_id(pk)
        FirewallTool.create_policy_chain(pk)
        FirewallTool.refresh_policy_chain(pk)
        model.commit()
        model.close()
        return response_data(policy)
    except ValidationError as err:
        model.close()
        return response_error_parse(err)


@routes.route("", methods=["GET"])
@has_any_authority(["viewer", "superuser"])
def get() -> Response:
    model = PolicyDao()
    if "size" in request.args and "page" in request.args:
        per_page = int(request.args.get("size"))
        page = int(request.args.get("page"))
        result = model.query_all(page, per_page)
    else:
        result = model.query_all()

    if result["metadata"]["total_pages"] > 0:
        for p in result["data"]:
            if "clients" in p:
                u_model = UserDao()
                for c in p["clients"]:
                    client = u_model.get_descr(c["id"])
                    if client:
                        c.update(client)
                u_model.close()

        model.close()
        return response_data(result)
    else:
        model.close()
        return response_error_404()


@routes.route("/<policy_id>", methods=["GET"])
@has_any_authority(["viewer", "superuser"])
def get_by_id(policy_id) -> Response:
    model = PolicyDao()
    policy = model.get_by_id(policy_id)

    if policy:
        if "clients" in policy:
            u_model = UserDao()
            for c in policy["clients"]:
                descr = u_model.get_descr(c["id"])
                if descr:
                    c.update(descr)
            u_model.close()
        model.close()
        return response_data(policy)
    else:
        model.close()
        return response_error_404()


@routes.route("/<policy_id>", methods=["PUT"])
@has_any_authority(["superuser"])
def update(policy_id) -> Response:
    model = PolicyDao()
    try:
        model.update_by_id(policy_id, request.json)
        policy = model.get_by_id(policy_id)
        model.commit()
        model.close()
        FirewallTool.refresh_policy_chain(policy_id)
        return response_data(policy)
    except ValidationError as err:
        model.close()
        return response_error_parse(err)


@routes.route("/<policy_id>", methods=["DELETE"])
@has_any_authority(["superuser"])
def delete(policy_id) -> Response:
    model = PolicyDao()
    model.delete_by_id(policy_id)
    model.commit()
    model.close()
    return response_data_removed(policy_id)
