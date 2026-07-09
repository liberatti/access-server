import threading
from flask import Blueprint, json, request, Response
from api.tools.vpn_tool import VPNTool
from nxcore.controllers.base_controller import response_data, response_ok
from config import main_path

routes = Blueprint("server", __name__)


@routes.route("/status", methods=["GET"])
def status() -> Response:
    config_dict = dict({"status": "pending"})
    if VPNTool.is_initialized():
        with open(f"{main_path}/data/config.json", "r") as a:
            config_dict = json.loads(a.read())
            if VPNTool.is_active():
                config_dict.update({"status": "online"})
            else:
                config_dict.update({"status": "loading"})

    return response_data(config_dict)


@routes.route("/activate", methods=["POST"])
def activate() -> Response:
    config_dict = request.json
    init_thread = threading.Thread(
        target=VPNTool.initialize,
        args=(config_dict,),
        daemon=True,
    )
    init_thread.start()
    return response_data({"status": "loading"})


@routes.route("/activate", methods=["PUT"])
def update() -> Response:
    data = request.json
    with open(f"data/config.json", "r") as a:
        config_dict = json.loads(a.read())
    config_dict.update(data)
    with open(f"data/config.json", "w") as f:
        f.write(json.dumps(config_dict))

    VPNTool.restart_service()
    return response_ok("Active")
