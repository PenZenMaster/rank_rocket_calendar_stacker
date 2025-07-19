"""
Module/Script Name: src/routes/oauth.py

Description:
CRUD endpoints for managing OAuthCredential records linked to clients.

Author(s):
Skippy the Code Slayer with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
13-07-2025

Last Modified Date:
29-07-2025

Version:
v1.02

Comments:
- Added GET /api/oauth for listing credentials
- Retains POST, GET by id, PUT, DELETE endpoints for full CRUD
- JSON error handlers for consistent error responses
"""

from flask import Blueprint, request, jsonify, abort
from werkzeug.exceptions import HTTPException
from src.extensions import db
from src.models.client import Client
from src.models.oauth_credential import OAuthCredential

oauth_bp = Blueprint("oauth_bp", __name__)


# JSON Error Handlers
@oauth_bp.errorhandler(400)
def handle_bad_request(e):
    """Return JSON for 400 Bad Request errors."""
    description = e.description if isinstance(e, HTTPException) else str(e)
    return jsonify(message=description), 400


@oauth_bp.errorhandler(404)
def handle_not_found(e):
    """Return JSON for 404 Not Found errors."""
    description = e.description if isinstance(e, HTTPException) else str(e)
    return jsonify(message=description), 404


def validate_oauth_data(data):
    """Ensure required fields are present and valid."""
    client_id = data.get("client_id")
    if not client_id:
        abort(400, description="'client_id' is required.")
    Client.query.get_or_404(client_id, description=f"Client {client_id} not found.")
    required_fields = ["google_client_id", "google_client_secret", "scopes"]
    for field in required_fields:
        if not data.get(field):
            abort(400, description=f"'{field}' is required.")
    return data


@oauth_bp.route("/api/oauth", methods=["GET"])
def list_oauth():
    """List all OAuthCredential records."""
    creds = OAuthCredential.query.all()
    return jsonify([c.to_dict() for c in creds]), 200


@oauth_bp.route("/api/oauth", methods=["POST"])
def create_oauth():
    """Create a new OAuthCredential."""
    data = validate_oauth_data(request.get_json() or {})
    oauth = OAuthCredential(**data, is_valid=False)
    db.session.add(oauth)
    db.session.commit()
    return jsonify(oauth.to_dict()), 201


@oauth_bp.route("/api/oauth/<int:oauth_id>", methods=["GET"])
def get_oauth(oauth_id: int):
    """Fetch a single OAuthCredential by ID."""
    oauth = OAuthCredential.query.get_or_404(oauth_id)
    return jsonify(oauth.to_dict()), 200


@oauth_bp.route("/api/oauth/<int:oauth_id>", methods=["PUT"])
def update_oauth(oauth_id: int):
    """Update an existing OAuthCredential."""
    oauth = OAuthCredential.query.get_or_404(oauth_id)
    data = request.get_json() or {}
    for attr in [
        "google_client_id",
        "google_client_secret",
        "scopes",
        "client_id",
        "is_valid",
        "token_status",
        "expires_at",
    ]:
        if attr in data:
            setattr(oauth, attr, data[attr])
    db.session.commit()
    return jsonify(oauth.to_dict()), 200


@oauth_bp.route("/api/oauth/<int:oauth_id>", methods=["DELETE"])
def delete_oauth(oauth_id: int):
    """Delete an OAuthCredential."""
    oauth = OAuthCredential.query.get_or_404(oauth_id)
    db.session.delete(oauth)
    db.session.commit()
    return jsonify({"message": f"OAuthCredential {oauth_id} deleted."}), 200
