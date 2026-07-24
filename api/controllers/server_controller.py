import threading
from flask import Blueprint, json, request, Response
from api.tools.vpn_tool import VPNTool
from api.tools.pki_tool import PKITool
from api.model.server_config_model import ServerConfigDao
from nxcore.controllers.base_controller import response_data, response_ok

routes = Blueprint("server", __name__)


@routes.route("/activate", methods=["PUT"])
def update() -> Response:
    """Update server configuration and restart VPN service.

    :return: Response confirming service restart.
    :rtype: flask.Response
    """
    data = request.json
    with ServerConfigDao() as dao:
        config_dict = dao.get_config()
        if config_dict:
            pk = config_dict["id"]
            config_dict.update(data)
            dao.update_by_id(pk, config_dict)
        else:
            dao.persist(data)
    PKITool.update_server_pki(data["name"])
    VPNTool.restart_service()
    return response_ok("Active")


@routes.route("/activate", methods=["GET"])
def get_config() -> Response:
    """Get current server configuration.

    :return: Response containing config dictionary.
    :rtype: flask.Response
    """
    try:
        with ServerConfigDao() as dao:
            config_dict = dao.get_config() or {}
        return response_data(config_dict)
    except Exception:
        return response_data({})
