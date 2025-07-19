"""
Module/Script Name: src/main.py

Description:
Application factory and entry point for the Flask app, including static file serving and API blueprint registration.

Author(s):
Skippy the Code Slayer with assistance from George Penzenik

Created Date:
10-07-2025

Last Modified Date:
19-07-2025

Version:
v1.12

Comments:
- Prepended project root to sys.path for direct package imports
- Configured static_folder and root route to serve index.html
- Auto-creates tables in development after importing all models
- Registers Client, OAuth Flow, OAuth CRUD, Events API, and Calendar blueprints
"""
import os
import sys
from flask import Flask, send_from_directory

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from extensions import db, migrate  # noqa: E402
# Import models to register them with SQLAlchemy metadata
import routes.client  # noqa: F401
import models.client  # noqa: F401
import models.oauth_credential  # noqa: F401

from routes.client import client_bp  # noqa: E402
from routes.oauth_flow import oauth_flow_bp  # noqa: E402
from routes.oauth import oauth_bp  # noqa: E402
from routes.events_api import events_bp  # noqa: E402
from routes.calendar import calendar_bp  # noqa: E402


def create_app(test_config=None):
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))
    app = Flask(
        __name__,
        instance_relative_config=True,
        static_folder=static_dir,
        static_url_path=''
    )
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///app.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config:
        app.config.update(test_config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Create tables for all imported models
    with app.app_context():
        db.create_all()

    # Register API blueprints
    app.register_blueprint(client_bp)
    app.register_blueprint(oauth_flow_bp)
    app.register_blueprint(oauth_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(calendar_bp)

    # Serve the front-end index.html
    @app.route('/')
    def index():
        return send_from_directory(static_dir, 'index.html')

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
