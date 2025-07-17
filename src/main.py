"""
Module/Script Name: src/main.py

Description:
Flask application factory and blueprint registration, now supporting dict-based config overrides in testing and loading templates from the project-level templates/ directory.

Author(s):
Skippy the Code Slayer with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
14-07-2025

Last Modified Date:
18-07-2025

Version:
v1.11

Comments:
- Added project-level templates directory via `template_folder`
- Ensured dict configs set SECRET_KEY, SERVER_NAME, and in-memory SQLite URI
- Preserves original string-based config loading
"""

import os
from flask import Flask
from src.extensions import db
from src.routes.oauth import oauth_bp
from src.routes.oauth_flow import oauth_flow_bp
from src.routes.calendar import calendar_bp


def create_app(config_obj: str | dict = "src.config.Config"):
    """
    Flask application factory.

    Args:
        config_obj (str | dict): Import path to config class or dict of config overrides.
    """
    # Create app with templates folder at project root
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    templates_path = os.path.join(root, "templates")
    app = Flask(__name__, template_folder=templates_path)
    # Monkey-patch flask.url_for to support URL building outside request context in tests
    import flask

    orig_url_for = flask.url_for

    def safe_url_for(endpoint, *args, **kwargs):
        try:
            return orig_url_for(endpoint, *args, **kwargs)
        except RuntimeError:
            adapter = app.create_url_adapter(None)
            if adapter is None:
                # Fallback to original url_for to raise a meaningful error
                return orig_url_for(endpoint, *args, **kwargs)
            # Build URL outside request context using adapter
            return adapter.build(endpoint, kwargs)

    flask.url_for = safe_url_for

    # Support dict for test overrides
    if isinstance(config_obj, dict):
        app.config.update(config_obj)
        # Testing defaults
        if app.config.get("TESTING"):
            app.config.setdefault("SQLALCHEMY_DATABASE_URI", "sqlite:///:memory:")
            app.config.setdefault("SERVER_NAME", "localhost")
            app.config.setdefault("SECRET_KEY", "test-secret")
    else:
        app.config.from_object(config_obj)

    # Initialize database
    db.init_app(app)
    with app.app_context():
        db.create_all()

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

    return app


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.DEBUG)
    logging.debug("Starting Flask app...")

    app = create_app()
    app.run(debug=True)
