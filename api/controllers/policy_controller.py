from flask import Blueprint, request, Response
from marshmallow import ValidationError
from nxcore.controllers.base_controller import (
    has_any_authority,
    response_data,
    response_error_parse,
    response_error_404,
    response_data_removed,
    get_pagination,
)
from api.model.policy_model import PolicyDao
from api.tools.firewall_tool import FirewallTool
from api.model.user_model import UserDao

routes = Blueprint("policy", __name__)


@routes.route("", methods=["GET"])
@has_any_authority(["viewer", "superuser"])
def get() -> Response:
    """Retrieve all policies with pagination and attached client details.

    :return: Response containing list of policies or 404 error if empty.
    :rtype: flask.Response
    """
    with PolicyDao() as model:
        result = model.get_all(pagination=get_pagination())
        for p in result["data"]:
            if "clients" in p:
                with UserDao() as u_model:
                    for c in p["clients"]:
                        client = u_model.get_descr(c["id"])
                        if client:
                            c.update(client)
        return response_data(result)


@routes.route("/<policy_id>", methods=["GET"])
@has_any_authority(["viewer", "superuser"])
def get_by_id(policy_id) -> Response:
    """Retrieve a policy by ID with client description details.

    :param policy_id: Policy identifier.
    :type policy_id: str
    :return: Response containing policy record or 404 error.
    :rtype: flask.Response
    """
    with PolicyDao() as model:
        policy = model.get_by_id(policy_id)
        if policy:
            if "clients" in policy:
                with UserDao() as u_model:
                    for c in policy["clients"]:
                        descr = u_model.get_descr(c["id"])
                        if descr:
                            c.update(descr)
            return response_data(policy)
        else:
            return response_error_404()


@routes.route("", methods=["POST"])
@has_any_authority(["superuser"])
def save() -> Response:
    """Create and persist a new policy and set up firewall chains.

    :return: Response containing saved policy details or validation error.
    :rtype: flask.Response
    """
    try:
        request.json.update({"type": "user"})
        with PolicyDao() as model:
            pk = model.persist(request.json)
            policy = model.get_by_id(pk)
            FirewallTool.create_policy_chain(pk)
            FirewallTool.refresh_policy_chain(pk)
        return response_data(policy)
    except ValidationError as err:
        return response_error_parse(err)


@routes.route("/<policy_id>", methods=["PUT"])
@has_any_authority(["superuser"])
def update(policy_id) -> Response:
    """Update an existing policy by ID and refresh firewall chains.

    :param policy_id: Policy identifier.
    :type policy_id: str
    :return: Response containing updated policy or validation error.
    :rtype: flask.Response
    """
    try:
        with PolicyDao() as model:
            model.update_by_id(policy_id, request.json)
            policy = model.get_by_id(policy_id)
        FirewallTool.refresh_policy_chain(policy_id)
        return response_data(policy)
    except ValidationError as err:
        return response_error_parse(err)


@routes.route("/<policy_id>", methods=["DELETE"])
@has_any_authority(["superuser"])
def delete(policy_id) -> Response:
    """Delete a policy by ID.

    :param policy_id: Policy identifier.
    :type policy_id: str
    :return: Response confirming policy deletion.
    :rtype: flask.Response
    """
    with PolicyDao() as model:
        model.delete_by_id(policy_id)
    return response_data_removed(policy_id)
