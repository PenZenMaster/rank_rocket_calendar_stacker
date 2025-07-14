"""
Module/Script Name: main.py

Description:
Application entry point, app factory, and route registration

Author(s):
Skippy the Code Slayer with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
13-07-2025

Last Modified Date:
13-07-2025

Version:
v1.01

Comments:
- Registered oauth_flow_bp blueprint
"""

from flask import Flask
from src.extensions import db, migrate
from src.routes.client import client_bp
from src.routes.calendar import calendar_bp
from src.routes.user import user_bp
from src.routes.oauth import oauth_bp
from src.routes.oauth_flow import oauth_flow_bp
from src.config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(client_bp)
    app.register_blueprint(calendar_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(oauth_bp)
    app.register_blueprint(oauth_flow_bp)

    return app
