from flask import Blueprint, request, Response
from marshmallow import ValidationError
from nxcore.controllers.base_controller import (
    has_any_authority,
    response_data,
    response_error_parse,
    response_error_404,
    response_error_500,
    response_data_removed,
    get_pagination,
)
from api.model.dmz_model import DMZServiceDao

routes = Blueprint("dmz", __name__)


@routes.route("", methods=["GET"])
@has_any_authority(["viewer", "superuser"])
def get() -> Response:
    """Retrieve all DMZ services with pagination.

    :return: Response containing DMZ service records or 404 error if empty.
    :rtype: flask.Response
    """
    with DMZServiceDao() as model:
        result = model.get_all(pagination=get_pagination())
        return response_data(result)


@routes.route("/<user_id>", methods=["GET"])
@has_any_authority(["viewer", "superuser"])
def get_by_id(user_id) -> Response:
    """Retrieve a DMZ service by ID.

    :param user_id: DMZ service identifier.
    :type user_id: str
    :return: Response containing DMZ service record or 404 error.
    :rtype: flask.Response
    """
    with DMZServiceDao() as model:
        user = model.get_by_id(user_id)
    if user:
        return response_data(user)
    else:
        return response_error_404()


@routes.route("", methods=["POST"])
@has_any_authority(["superuser"])
def save() -> Response:
    """Create and persist a new DMZ service.

    :return: Response containing saved DMZ service data or validation error.
    :rtype: flask.Response
    """
    try:
        with DMZServiceDao() as model:
            data = request.json
            model.persist(data)
            return response_data(data)
    except ValidationError as err:
        return response_error_parse(err)


@routes.route("/<user_id>", methods=["PUT"])
@has_any_authority(["superuser"])
def update(user_id) -> Response:
    """Update an existing DMZ service by ID.

    :param user_id: DMZ service identifier.
    :type user_id: str
    :return: Response containing updated DMZ service data or validation error.
    :rtype: flask.Response
    """
    try:
        with DMZServiceDao() as model:
            data = request.json
            model.update_by_id(user_id, data)
        return response_data(data)
    except ValidationError as err:
        return response_error_parse(err)


@routes.route("/<user_id>", methods=["DELETE"])
@has_any_authority(["superuser"])
def delete(user_id) -> Response:
    """Delete a DMZ service by ID.

    :param user_id: DMZ service identifier.
    :type user_id: str
    :return: Response confirming removal or error response.
    :rtype: flask.Response
    """
    try:
        with DMZServiceDao() as model:
            result = model.delete_by_id(user_id)
        if result:
            return response_data_removed(user_id)
        else:
            return response_error_404()
    except Exception as e:
        return response_error_500(str(e))
