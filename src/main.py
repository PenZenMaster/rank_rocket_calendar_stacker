"""
Module/Script Name: src/main.py

Description:
Flask application factory and blueprint registration

Author(s):
Skippy the Code Slayer with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
14-07-2025

Last Modified Date:
14-07-2025

Version:
v1.02

Comments:
- Registered oauth_flow_bp to enable /authorize and /callback routes
"""

from flask import Flask
from src.extensions import db
from src.routes.oauth import oauth_bp
from src.routes.oauth_flow import oauth_flow_bp  # Added for auth flow


def create_app(config_obj="src.config.Config"):
    app = Flask(__name__)
    app.config.from_object(config_obj)

    db.init_app(app)
    with app.app_context():
        db.create_all()

    app.register_blueprint(oauth_bp)
    app.register_blueprint(oauth_flow_bp)  # Register new blueprint

    return app
