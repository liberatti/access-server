from flask import Blueprint, request, Response
from marshmallow import ValidationError
from nxcore.controllers.base_controller import (
    has_any_authority,
    response_data,
    response_error_parse,
    response_error_404,
    response_error_500,
    response_data_removed,
)
from api.repository.dmz_model import DMZServiceDao

routes = Blueprint("dmz", __name__)


@routes.route("", methods=["POST"])
@has_any_authority(["superuser"])
def save() -> Response:
    model = DMZServiceDao()
    try:
        data = request.json
        pk = model.persist(data)
        model.commit()
        model.close()
        return response_data(data)
    except ValidationError as err:
        model.close()
        return response_error_parse(err)


@routes.route("", methods=["GET"])
@has_any_authority(["viewer", "superuser"])
def get() -> Response:
    model = DMZServiceDao()
    if "size" in request.args and "page" in request.args:
        per_page = int(request.args.get("size"))
        page = int(request.args.get("page"))
        result = model.query_all(page, per_page)
    else:
        result = model.query_all()
    model.close()
    if result["metadata"]["total_pages"] > 0:
        return response_data(result)
    else:
        return response_error_404()


@routes.route("/<user_id>", methods=["GET"])
@has_any_authority(["viewer", "superuser"])
def get_by_id(user_id) -> Response:
    model = DMZServiceDao()
    user = model.get_by_id(user_id)
    model.close()
    if user:
        return response_data(user)
    else:
        return response_error_404()


@routes.route("/<user_id>", methods=["PUT"])
@has_any_authority(["superuser"])
def update(user_id) -> Response:
    model = DMZServiceDao()
    try:
        data = request.json
        model.update_by_id(user_id, data)
        model.commit()
        model.close()
        return response_data(data)
    except ValidationError as err:
        model.close()
        return response_error_parse(err)


@routes.route("/<user_id>", methods=["DELETE"])
@has_any_authority(["superuser"])
def delete(user_id) -> Response:
    model = DMZServiceDao()
    try:
        result = model.delete_by_id(user_id)
        model.commit()
        model.close()
        if result:
            return response_data_removed(user_id)
        else:
            return response_error_404()
    except Exception as e:
        model.close()
        return response_error_500(str(e))
