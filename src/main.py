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
v1.07

Comments:
- Extended create_app to accept dict config for pytest integration
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
        app.config.update(config_obj)
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

    app.register_blueprint(oauth_bp)
    app.register_blueprint(oauth_flow_bp)  # Register new blueprint
    app.register_blueprint(calendar_bp)  # Register calendar endpoints

    return app


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.DEBUG)
    logging.debug("Starting Flask app...")

    app = create_app()
    app.run(debug=True)
