import os
from flask import Flask, send_from_directory
from dotenv import load_dotenv

from src.config import Config
from src.extensions import db, cors, migrate
from src.routes.user import user_bp
from src.routes.client import client_bp


def create_app():
    # Load environment variables from .env
    load_dotenv()

    # Initialize Flask app
    app = Flask(
        __name__, static_folder=os.path.join(os.path.dirname(__file__), "static")
    )

    # Load configuration from src/config.py
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    migrate.init_app(app, db)

    # Register blueprints with new URL prefixes
    app.register_blueprint(user_bp, url_prefix="/api/users")
    app.register_blueprint(client_bp, url_prefix="/api")

    # Create database tables if they don't exist
    # with app.app_context():
    #    db.create_all()

    # Serve static files and index.html for SPA
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve(path):
        static_folder = app.static_folder
        if static_folder is None:
            return "Static folder not configured", 404

        target = os.path.join(static_folder, path) if path else None
        if target and os.path.exists(target):
            return send_from_directory(static_folder, path)

        index_file = os.path.join(static_folder, "index.html")
        if os.path.exists(index_file):
            return send_from_directory(static_folder, "index.html")

        return "index.html not found", 404

    return app


if __name__ == "__main__":
    # Create and run the app
    app = create_app()
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=app.config["DEBUG"],
    )
