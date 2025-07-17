"""
Module/Script Name: oauth.py

Description:
CRUD endpoints for managing OAuthCredential records linked to clients.

Author(s):
Skippy the Code Slayer with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
13-07-2025

Last Modified Date:
13-07-2025

Version:
v1.01

Comments:
- Updated to use OAuthCredential dynamic constructor and to_dict
"""

from flask import Blueprint, request, jsonify, abort
from src.extensions import db
from src.models.client import Client
from src.models.oauth_credential import OAuthCredential

oauth_bp = Blueprint("oauth_bp", __name__)


def validate_oauth_data(data):
    client_id = data.get("client_id")
    if not client_id:
        abort(400, description="'client_id' is required.")

    # Check if client exists
    Client.query.get_or_404(client_id, description=f"Client {client_id} not found.")

    required_fields = ["google_client_id", "google_client_secret", "scopes"]
    for field in required_fields:
        if not data.get(field):
            abort(400, description=f"'{field}' is required.")

    return data


@oauth_bp.route("/api/oauth", methods=["POST"])
def create_oauth():
    data = validate_oauth_data(request.get_json() or {})
    oauth = OAuthCredential(**data, is_valid=False)
    db.session.add(oauth)
    db.session.commit()
    return jsonify(oauth.to_dict()), 201


@oauth_bp.route("/api/oauth/<int:oauth_id>", methods=["GET"])
def get_oauth(oauth_id):
    oauth = OAuthCredential.query.get_or_404(oauth_id)
    return jsonify(oauth.to_dict()), 200


@oauth_bp.route("/api/oauth/<int:oauth_id>", methods=["PUT"])
def update_oauth(oauth_id):
    oauth = OAuthCredential.query.get_or_404(oauth_id)
    data = request.get_json() or {}

    for attr in ["google_client_id", "google_client_secret", "scopes"]:
        if attr in data:
            setattr(oauth, attr, data[attr])

    db.session.commit()
    return jsonify(oauth.to_dict()), 200


@oauth_bp.route("/api/oauth/<int:oauth_id>", methods=["DELETE"])
def delete_oauth(oauth_id):
    oauth = OAuthCredential.query.get_or_404(oauth_id)
    db.session.delete(oauth)
    db.session.commit()
    return jsonify({"message": f"OAuthCredential {oauth_id} deleted."}), 200
