"""
Module/Script Name: src/main.py

Description:
Flask application factory and blueprint registration

Author(s):
Skippy the Code Slayer with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
14-07-2025

Last Modified Date:
15-07-2025

Version:
v1.06

Comments:
- Registered oauth_flow_bp to enable /authorize and /callback routes
- Added executable app.run block for local development testing
- Added root (/) route for dev sanity check
- Registered calendar_bp to enable /clients/<client_id>/calendars endpoint
- Added teardown_appcontext handler to ensure db.session is removed
"""

from flask import Flask
from src.extensions import db
from src.routes.oauth import oauth_bp
from src.routes.oauth_flow import oauth_flow_bp  # Added for auth flow
from src.routes.calendar import calendar_bp  # Register calendar endpoints


def create_app(config_obj="src.config.Config"):
    app = Flask(__name__)
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
