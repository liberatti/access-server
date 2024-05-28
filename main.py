import os
import signal
import threading
import time
from flask import (
    Flask,
    render_template,
    send_from_directory,
    Blueprint,
)
from flask_restful import Api
from flask_jwt_extended import (
    JWTManager,
)
import schedule
from flask_cors import CORS
from api.utils import handle_sigterm, ma, gen_random_string,chmod_r
from api.controller.user_controller import routes as user_routes
from api.controller.server_controller import routes as server_routes
from api.controller.policy_controller import routes as policy_routes
from config import JWT_EXPIRATION_DELTA
from api.tools.vpn_tool import FirewallTool, VPNTool
from api.model.policy_model import PolicyClientModel, PolicyModel
from api.model.user_model import (
    UserPolicyModel,
    UserModel,
    PortMappingModel,
)
from api.model.vpn_model import VPNSessionModel

app = Flask(__name__)

app.config["JWT_EXPIRATION_DELTA"] = JWT_EXPIRATION_DELTA
app.config["JWT_SECRET_KEY"] = gen_random_string(64)

bp = Blueprint("gw", __name__, template_folder="templates")
jwt = JWTManager(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

ma.init_app(app)
api = Api(app)
static_files_dir = "./static"


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/<path:path>")
def catch_all(path):
    _path = path.lower().strip()
    if path in ["", "/", None]:
        return send_from_directory(static_files_dir, "index.html", mimetype="text/html")
    elif _path.endswith(".css"):
        return send_from_directory(static_files_dir, path, mimetype="text/css")
    elif _path.endswith(".js"):
        return send_from_directory(
            static_files_dir, path, mimetype="application/javascript"
        )
    return send_from_directory(static_files_dir, path)


app.register_blueprint(bp, url_prefix="/")
app.register_blueprint(user_routes, url_prefix="/api/user")
app.register_blueprint(policy_routes, url_prefix="/api/policy")
app.register_blueprint(server_routes, url_prefix="/api/server")

signal.signal(signal.SIGTERM, handle_sigterm)


def _scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)


def create_db():
    if not os.path.exists(f"data"):
        os.mkdir(f"data")
    UserModel().create_schema()
    PolicyModel().create_schema()
    PolicyClientModel().create_schema()
    UserPolicyModel().create_schema()
    PortMappingModel().create_schema()
    VPNSessionModel().create_schema()


if __name__ == "__main__":
    schedule.every().day.at("01:00").do(VPNTool.update_crl)
    schedule.every(5).seconds.do(VPNTool.session_monitor)

    scheduler_thread = threading.Thread(
        target=_scheduler,
        daemon=False,
    )
    scheduler_thread.start()

    if not os.path.exists(f"data/admin.db"):
        create_db()

    if VPNTool.is_initialized():
        chmod_r("data",0o777,recursive=True)
        FirewallTool.create_firewall()
        VPNTool.start_service(wait=False)

    app.run(host="0.0.0.0")
