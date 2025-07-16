"""
Module/Script Name: src/main.py

Description:
Flask application factory and blueprint registration, now supporting dict-based config overrides in testing.

Author(s):
Skippy the Code Slayer with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
14-07-2025

Last Modified Date:
17-07-2025

Version:
v1.09

Comments:
- Extended create_app to accept dict config for pytest integration
- Added default in-memory SQLite for testing dict configs without DB URI
- Set SERVER_NAME for URL generation in tests
- Preserves original string-based config loading
"""

from flask import Flask
from src.extensions import db
from src.routes.oauth import oauth_bp
from src.routes.oauth_flow import oauth_flow_bp  # Added for auth flow
from src.routes.calendar import calendar_bp  # Register calendar endpoints


def create_app(config_obj: str | dict = "src.config.Config"):
    """
    Flask application factory.

    Args:
        config_obj (str | dict): Import path to config class or dict of config overrides.
    """
    app = Flask(__name__)
    # Support dict for test overrides, otherwise load from object path
    if isinstance(config_obj, dict):
        # Update app config with overrides
        app.config.update(config_obj)
        # Ensure a default database URI for testing
        if app.config.get("TESTING") and not app.config.get("SQLALCHEMY_DATABASE_URI"):
            app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        # Ensure SERVER_NAME for URL building in tests
        if app.config.get("TESTING") and not app.config.get("SERVER_NAME"):
            app.config["SERVER_NAME"] = "localhost"
    else:
        app.config.from_object(config_obj)

    db.init_app(app)
    with app.app_context():
        db.create_all()

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    @app.route("/")
    def index():
        return "Rank Rocket Calendar Stacker is Alive!"

    # Register blueprints
    app.register_blueprint(oauth_bp)
    app.register_blueprint(oauth_flow_bp)
    app.register_blueprint(calendar_bp)

    return app


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.DEBUG)
    logging.debug("Starting Flask app...")

    app = create_app()
    app.run(debug=True)
