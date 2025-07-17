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
v1.14

Comments:
- Added project-level templates directory via `template_folder`
- Ensured dict configs set SECRET_KEY, SERVER_NAME, and in-memory SQLite URI
- Automatically push test request context to support url_for in tests
- Preserves original string-based config loading
"""

import os
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

    # Initialize database
    db.init_app(app)
    with app.app_context():
        db.create_all()

    # In testing mode, push a test request context to enable url_for
    if app.config.get("TESTING"):
        ctx = app.test_request_context()
        ctx.push()

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    # Healthcheck endpoint
    @app.route("/")
    def index():
        return "Rank Rocket Calendar Stacker is Alive!"

    # Register blueprints
    app.register_blueprint(oauth_bp)
    app.register_blueprint(oauth_flow_bp)
    app.register_blueprint(calendar_bp)
    app.register_blueprint(client_bp)
    return app


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.DEBUG)
    logging.debug("Starting Flask app...")

    app = create_app()
    app.run(debug=True)
