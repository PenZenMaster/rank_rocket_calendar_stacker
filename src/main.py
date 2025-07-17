"""
Module/Script Name: src/main.py

Description:
Flask application factory and blueprint registration, now supporting dict-based config overrides in testing and loading templates from the project-level templates/ directory.

Author(s):
Skippy the Code Slayer with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
14-07-2025

Last Modified Date:
19-07-2025

Version:
v1.19

Comments:
DB Troubleshooting
"""

import os
import sys

# DON'T CHANGE THIS !!!
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
    # Determine project-level templates directory
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    templates_path = os.path.join(root, "templates")
    app = Flask(__name__, template_folder=templates_path)

    # Load config: dict overrides for testing or object for production
    if isinstance(config_obj, dict):
        app.config.update(config_obj)
    else:
        app.config.from_object(config_obj)

    if app.config.get("TESTING"):
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        app.config["SERVER_NAME"] = "localhost"
        app.config["SECRET_KEY"] = "test-secret"

    print(f"SQLALCHEMY_DATABASE_URI: {app.config.get("SQLALCHEMY_DATABASE_URI")}")

    # Initialize database
    db.init_app(app)
    with app.app_context():
        # Ensure all models are imported so SQLAlchemy can find them
        from src.models import client, oauth, oauth_credential, user, base

        # Explicitly reload the client module to ensure latest definition is used
        import importlib

        importlib.reload(client)

        print(f"Path of loaded client.py: {client.__file__}")

        db.create_all()

        # Debugging: Print columns of the Client table
        from sqlalchemy import inspect

        inspector = inspect(db.engine)
        print("Columns in clients table:", inspector.get_columns("clients"))

    # In testing mode, push a test request context to enable url_for
    if app.config.get("TESTING"):
        ctx = app.test_request_context()
        ctx.push()

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
        static_folder_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "static")
        )
        if static_folder_path is None:
            return "Static folder not configured", 404

        if os.path.exists(os.path.join(static_folder_path, path)):
            return send_from_directory(static_folder_path, path)
        else:
            return "File not found", 404

    app.run(debug=True)
