from flask import Blueprint, request
from marshmallow import ValidationError
from api.utils import has_any_authority, logger
from api.tools.response_builder import ResponseBuilder
from api.model.dmz_model import DMZServiceDao
routes = Blueprint("dmz", __name__)


@routes.route("", methods=["POST"])
@has_any_authority(["superuser"])
def save():
    model = DMZServiceDao()
    try:
        data = request.json
        pk = model.persist(data)
        model.commit()
        model.close()
        return ResponseBuilder.data(data)
    except ValidationError as err:
        return ResponseBuilder.error_parse(err)


@routes.route("", methods=["GET"])
@has_any_authority(["viewer", "superuser"])
def get():
    model = DMZServiceDao()
    if "size" in request.args and "page" in request.args:
        per_page = int(request.args.get("size"))
        page = int(request.args.get("page"))
        result = model.query_all(page, per_page)
    else:
        result = model.query_all()
    if result["metadata"]["total_pages"] > 0:
        return ResponseBuilder.data(result)
    else:
        return ResponseBuilder.error_404(request.url)


@routes.route("/<user_id>", methods=["GET"])
@has_any_authority(["viewer", "superuser"])
def get_by_id(user_id):
    user = DMZServiceDao().get_by_id(user_id)
    if user:
        return ResponseBuilder.data(user)
    else:
        return ResponseBuilder.error_404(request.url)


@routes.route("/<user_id>", methods=["PUT"])
@has_any_authority(["superuser"])
def update(user_id):
    model = DMZServiceDao()
    user = model.get_by_id(user_id)
    try:
        data = request.json
        model.update_by_id(user_id, data)
        model.commit()
        model.close()
        return ResponseBuilder.data(data)
    except ValidationError as err:
        return ResponseBuilder.error_parse(err)


@routes.route("/<user_id>", methods=["DELETE"])
@has_any_authority(["superuser"])
def delete(user_id):
    model = DMZServiceDao()
    response = None
    try:
        result = model.delete_by_id(user_id)
        model.commit()
        if result:
            response = ResponseBuilder.data_removed(user_id)
        else:
            response = ResponseBuilder.error_404(request.url)
    except Exception as e:
        response = ResponseBuilder.error_500(e)
    model.close()
    return response