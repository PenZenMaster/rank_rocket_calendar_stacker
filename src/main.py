""" "
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
v1.01

Comments:
- Registered oauth_bp blueprint without url_prefix to expose routes at root level
- Ensures tests can access routes like /authorize and /oauth_credentials directly
"""

from flask import Flask
from src.extensions import db
from src.routes.oauth import oauth_bp


def create_app(config_obj="src.config.Config"):
    app = Flask(__name__)
    app.config.from_object(config_obj)

    db.init_app(app)
    with app.app_context():
        db.create_all()

    # Register OAuth blueprint directly without a prefix for route accessibility
    app.register_blueprint(oauth_bp)

    return app
