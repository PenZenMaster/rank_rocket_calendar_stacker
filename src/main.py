"""
Module/Script Name: src/main.py

Description:
Flask application factory and blueprint registration, with SQLAlchemy initialization centralized here and config-driven behavior.

Author(s):
Skippy the Code Slayer with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
14-07-2025

Last Modified Date:
17-07-2025

Version:
v1.23

Comments:
- Supports dict-based config overrides, including Testing-specific defaults
- Ensures db.init_app(app) is called exactly once in create_app
- Schema management delegated fully to migrations or test fixtures
"""

import os
import sys

# Ensure project root is on sys.path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask
from src.extensions import db
from src.routes.oauth import oauth_bp
from src.routes.oauth_flow import oauth_flow_bp
from src.routes.calendar import calendar_bp
from src.routes.client import client_bp


def create_app(config_obj: str | dict = "src.config.Config"):
    """
    Flask application factory.

    Args:
        config_obj (str | dict): Import path to config class or dict of config overrides.
    """
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    templates_path = os.path.join(root, "templates")
    app = Flask(__name__, template_folder=templates_path)

    # Load configuration (object or dict)
    if isinstance(config_obj, dict):
        app.config.update(config_obj)
    else:
        app.config.from_object(config_obj)

    # Testing-specific overrides: ensure in-memory DB and essentials
    if app.config.get("TESTING"):
        app.config.setdefault("SQLALCHEMY_DATABASE_URI", "sqlite:///:memory:")
        app.config.setdefault("SERVER_NAME", "localhost")
        app.config.setdefault("SECRET_KEY", "test-secret")

    # Initialize extensions
    db.init_app(app)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    # Register blueprints
    app.register_blueprint(oauth_bp)
    app.register_blueprint(oauth_flow_bp)
    app.register_blueprint(calendar_bp)
    app.register_blueprint(client_bp)

    return app


if __name__ == "__main__":
    import logging
    from flask import send_from_directory

    logging.basicConfig(level=logging.DEBUG)
    logging.debug("Starting Flask app...")

    app = create_app()

    @app.route("/", defaults={"path": "index.html"})
    @app.route("/<path:path>")
    def serve(path):
        static_folder = os.path.join(os.path.dirname(__file__), "static")
        file_path = os.path.join(static_folder, path)
        if os.path.exists(file_path):
            return send_from_directory(static_folder, path)
        return "File not found", 404

    app.run(debug=True)
