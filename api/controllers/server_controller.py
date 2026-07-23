import threading
from flask import Blueprint, json, request, Response
from api.tools.vpn_tool import VPNTool
from nxcore.controllers.base_controller import response_data, response_ok
from config import main_path

routes = Blueprint("server", __name__)


@routes.route("/activate", methods=["POST"])
def activate() -> Response:
    """Initialize server configuration and start VPN background thread.

    :return: Response indicating server activation has started.
    :rtype: flask.Response
    """
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
    """Update server configuration and restart VPN service.

    :return: Response confirming service restart.
    :rtype: flask.Response
    """
    data = request.json
    with open("data/config.json", "r") as a:
        config_dict = json.loads(a.read())
    config_dict.update(data)
    with open("data/config.json", "w") as f:
        f.write(json.dumps(config_dict))

    VPNTool.restart_service()
    return response_ok("Active")


@routes.route("/activate", methods=["GET"])
def get_config() -> Response:
    """Get current server configuration.

    :return: Response containing config dictionary.
    :rtype: flask.Response
    """
    try:
        with open("data/config.json", "r") as f:
            config_dict = json.loads(f.read())
        return response_data(config_dict)
    except Exception:
        return response_data({})

