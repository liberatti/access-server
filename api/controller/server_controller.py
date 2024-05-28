import socket
import threading
from flask import Blueprint, json, request
from api.utils import has_any_authority, logger
from api.tools.vpn_tool import VPNTool
from api.tools.response_builder import ResponseBuilder
from api.model.user_model import PortMappingModel
from config import main_path

routes = Blueprint("server", __name__)


@routes.route("/status", methods=["GET"])
def status():
    config = dict({"status": "pending"})
    if VPNTool.is_initialized():
        with open(f"{main_path}/data/config.json", "r") as a:
            config = json.loads(a.read())
            if VPNTool.is_active():
                config.update({"status": "online"})
            else:
                config.update({"status": "loading"})

    return ResponseBuilder.data(config)


@routes.route("/activate", methods=["POST"])
def activate():
    config = request.json
    init_thread = threading.Thread(
        target=VPNTool.initialize,
        args=(config,),
        daemon=True,
    )
    init_thread.start()
    return ResponseBuilder.data({"status": "loading"})


@routes.route("/port_map", methods=["POST"])
def port_map():
    model = PortMappingModel()
    if "static" in request.json["type"]:
        if model.is_free(request.json["bind_port"]):
            pk = model.persist(request.json)
            model.commit()
            model.close()
            return ResponseBuilder.data({"id": pk})
        return ResponseBuilder.error_500("Port in use")


@routes.route("/port_map/<port_map>", methods=["DELETE"])
@has_any_authority(["admin"])
def del_port_map(port_map):
    model = PortMappingModel()
    response = None
    try:
        result = model.delete_by_id(port_map)
        model.commit()
        if result:
            response = ResponseBuilder.data_removed(port_map)
        else:
            response = ResponseBuilder.error_404(request.url)
    except Exception as e:
        response = ResponseBuilder.error_500(e)
    model.close()
    return response


@routes.route("/activate", methods=["PUT"])
def update():
    data = request.json
    with open(f"data/config.json", "r") as a:
        config = json.loads(a.read())
    config.update(data)
    with open(f"data/config.json", "w") as f:
        f.write(json.dumps(config))

    VPNTool.restart_service()
    return ResponseBuilder.ok("Active")
