from flask import render_template, current_app

from api.controllers.user_controller import routes as user_routes
from api.controllers.policy_controller import routes as policy_routes
from api.controllers.server_controller import routes as server_routes
from api.controllers.dmz_controller import routes as dmz_routes

routes = [
    (user_routes, "/api/user"),
    (policy_routes, "/api/policy"),
    (server_routes, "/api/server"),
    (dmz_routes, "/api/dmz"),
]


def register(app, bp):
    """
    Register all API routes with the Flask application.

    Args:
        app (Flask): The main Flask application instance.
        bp (Blueprint): The main Blueprint for API routes.
    """

    @bp.route("/")
    def index():
        """
        Serve the main index page.
        """
        return render_template("index.html")

    @bp.route("/<path:path>")
    def catch_all(path: str):
        """
        Handle requests to any path by serving the index page,
        unless it's a request for a static file with an extension.
        """
        if "." in path and not path.endswith("/"):
            try:
                return current_app.send_static_file(path)
            except Exception:
                pass
        return render_template("index.html")

    for route, url_prefix in routes:
        app.register_blueprint(route, url_prefix=url_prefix)
