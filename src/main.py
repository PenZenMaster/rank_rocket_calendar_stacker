"""
Module/Script Name: src/main.py

Description:
Flask application factory and blueprint registration, with SQLAlchemy initialization centralized here and config-driven behavior.

Author(s):
Skippy the Code Slayer with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
14-07-2025

Last Modified Date:
20-07-2025

Version:
v1.27

Comments:
- Supports dict-based config overrides, including Testing-specific defaults
- Ensures db.init_app(app) is called exactly once in create_app()
- Registered new Events JSON-API blueprint
- Conditionally uses in-memory SQLite DB only when TESTING and no explicit URI provided
"""

import os
import logging
from flask import Flask, send_from_directory
from src.extensions import db
from src.routes.oauth import oauth_bp
from src.routes.oauth_flow import oauth_flow_bp
from src.routes.calendar import calendar_bp
from src.routes.client import client_bp
from src.routes.events_api import events_bp  # <— new import


def create_app(config_obj: str | dict = "src.config.Config"):
    """
    Flask application factory.

    Args:
        config_obj (str | dict): Import path to config class or dict of config overrides.
    """
    # Determine application root and templates path
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    templates_path = os.path.join(root, "templates")
    app = Flask(__name__, template_folder=templates_path)

    # Load configuration
    if isinstance(config_obj, dict):
        # 1) Load default config values to ensure required keys
        from src.config import Config

        app.config.from_object(Config)
        # 2) Override with provided dict (e.g., TESTING, SQLALCHEMY_DATABASE_URI)
        app.config.update(config_obj)
        # 3) If running tests without an explicit DB URI, use in-memory SQLite
        if app.config.get("TESTING") and not config_obj.get("SQLALCHEMY_DATABASE_URI"):
            app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        # 4) Ensure track modifications is set to False if unspecified
        if "SQLALCHEMY_TRACK_MODIFICATIONS" not in app.config:
            app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    else:
        app.config.from_object(config_obj)

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
    app.register_blueprint(events_bp)

    return app


if __name__ == "__main__":
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
