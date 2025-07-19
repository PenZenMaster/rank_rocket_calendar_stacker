"""
Module/Script Name: src/routes/client.py

Description:
CRUD endpoints for managing Client records via REST API, plus Google Calendar listing.

Author(s):
Skippy the Magnificent with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
11-07-2025

Last Modified Date:
30-07-2025

Version:
v1.12

Comments:
- Added IntegrityError handling on create/update to return friendly 400 on unique constraint failures
- Rolls back session on error to maintain clean state
- Imports IntegrityError from sqlalchemy.exc
"""

from flask import Blueprint, request, jsonify, abort
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError
from src.extensions import db
from src.models.client import Client
from src.models.oauth_credential import OAuthCredential
from src.services.google_calendar_service import GoogleCalendarService

client_bp = Blueprint("client_bp", __name__, url_prefix="/api")


# JSON Error Handlers
@client_bp.errorhandler(400)
def handle_bad_request(e):
    """Return JSON for 400 Bad Request errors."""
    description = e.description if isinstance(e, HTTPException) else str(e)
    return jsonify(message=description), 400


@client_bp.errorhandler(404)
def handle_not_found(e):
    """Return JSON for 404 Not Found errors."""
    description = e.description if isinstance(e, HTTPException) else str(e)
    return jsonify(message=description), 404


def validate_client_data(data):
    """Ensure required fields are present and valid."""
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    if not name:
        abort(400, description="Client 'name' is required and cannot be empty.")
    if not email or "@" not in email:
        abort(400, description="Valid 'email' is required.")
    return name, email


def validate_google_email(data):
    """Ensure google_account_email field is present and valid."""
    google_email = data.get("google_account_email", "").strip()
    if not google_email or "@" not in google_email:
        abort(400, description="Valid 'google_account_email' is required.")
    return google_email


@client_bp.route("/clients", methods=["GET"])
def get_clients():
    """List all clients."""
    clients = Client.query.all()
    return jsonify([c.to_dict() for c in clients]), 200


@client_bp.route("/clients/<int:client_id>", methods=["GET"])
def get_client(client_id: int):
    """Fetch a single client by ID."""
    client = Client.query.get_or_404(
        client_id, description=f"Client {client_id} not found."
    )
    return jsonify(client.to_dict()), 200


@client_bp.route("/clients", methods=["POST"])
def create_client():
    """Create a new client."""
    data = request.get_json() or {}
    name, email = validate_client_data(data)
    google_email = validate_google_email(data)
    new_client = Client(name=name, email=email, google_account_email=google_email)

    db.session.add(new_client)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(
            400, description="A client with this Google account email already exists."
        )
    return jsonify(new_client.to_dict()), 201


@client_bp.route("/clients/<int:client_id>", methods=["PUT"])
def update_client(client_id: int):
    """Update an existing client."""
    client = Client.query.get_or_404(
        client_id, description=f"Client {client_id} not found."
    )
    data = request.get_json() or {}
    name, email = validate_client_data(data)
    google_email = validate_google_email(data)
    client.name = name
    client.email = email
    client.google_account_email = google_email
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(
            400, description="A client with this Google account email already exists."
        )
    return jsonify(client.to_dict()), 200


@client_bp.route("/clients/<int:client_id>", methods=["DELETE"])
def delete_client(client_id: int):
    """Delete a client."""
    client = Client.query.get_or_404(
        client_id, description=f"Client {client_id} not found."
    )
    db.session.delete(client)
    db.session.commit()
    return jsonify({"message": f"Client {client_id} deleted."}), 200


@client_bp.route("/clients/<int:client_id>/calendars", methods=["GET"])
def get_client_calendars(client_id: int):
    """Return all Google Calendars for a given client."""
    Client.query.get_or_404(client_id, description=f"Client {client_id} not found.")
    creds = OAuthCredential.query.filter_by(client_id=client_id, is_valid=True).first()
    if not creds:
        abort(400, description="No valid OAuth credentials for this client.")
    svc = GoogleCalendarService(creds)
    calendars = svc.list_calendars()
    return jsonify(calendars), 200
