import traceback

from flask import Flask, Blueprint
from flask_cors import CORS
from flask_restful import Api

import config
import nxcore.config as nxcore_config
from nxcore.controllers.base_controller import response_error_404, response_error_500
from nxcore.middleware.logging_manager import logger, LoggingManager
from nxcore.middleware.jwt_manager import JWTManager

from api.routes import register as register_api_routes

nxcore_config.init(
    {
        "LOGLEVEL": config.LOGLEVEL,
        "JWT_SECRET_KEY": config.JWT_SECRET_KEY,
        "JWT_AUD": config.JWT_AUD,
        "SECURITY_ENABLED": config.SECURITY_ENABLED,
        "API_KEY": config.API_KEY,
    }
)


app = Flask(__name__)
app.config["LOGLEVEL"] = config.LOGLEVEL
app.url_map.strict_slashes = False
CORS(app, resources={r"/*": {"origins": "*"}})

LoggingManager(app)
JWTManager(app)


api = Api(app)

bp = Blueprint("gw", __name__, template_folder="templates")
register_api_routes(app, bp)
app.register_blueprint(bp)


@app.errorhandler(404)
def not_found_error(error):
    """
    Handles 404 Not Found errors.
    """
    return response_error_404()


@app.errorhandler(500)
def internal_error(error):
    """
    Handles 500 Internal Server errors and logs the stack trace.
    """
    stack_trace = traceback.format_exc()
    logger.error(f"500 Error: {error}, Stack Trace: {stack_trace}")
    return response_error_500("Unexpected Server Error", details=stack_trace)


@app.errorhandler(Exception)
def handle_exception(error):
    """
    Generic exception handler that logs the stack trace and returns a 500 error.
    """
    stack_trace = traceback.format_exc()
    logger.error(f"Internal Server Error: {stack_trace}")
    return response_error_500("Unexpected Server Error", details=stack_trace)
