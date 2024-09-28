import threading
from flask import Blueprint, json, request
from api.tools.vpn_tool import VPNTool
from api.tools.response_builder import ResponseBuilder
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
