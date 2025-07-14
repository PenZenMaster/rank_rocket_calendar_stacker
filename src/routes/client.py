"""
Module/Script Name: client.py

Description:
CRUD endpoints for managing Client records via REST API, plus Google Calendar listing.

Author(s):
Skippy the Magnificent with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
2025-07-11

Last Modified Date:
2025-07-15

Comments:
- Version 1.07  # matched GoogleCalendarService constructor to actual parameters
"""

from flask import Blueprint, request, jsonify, abort
from src.extensions import db
from src.models.client import Client
from src.models.oauth import OAuthCredential
from src.google_calendar import GoogleCalendarService

client_bp = Blueprint("client_bp", __name__)


def validate_client_data(data):
    """Ensure required fields are present and valid."""
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    if not name:
        abort(400, description="Client 'name' is required and cannot be empty.")
    if not email or "@" not in email:
        abort(400, description="Valid 'email' is required.")
    return name, email


@client_bp.route("/api/clients", methods=["GET"])
def get_clients():
    """List all clients."""
    clients = Client.query.all()
    return jsonify([c.to_dict() for c in clients]), 200


@client_bp.route("/api/clients", methods=["POST"])
def create_client():
    """Create a new client."""
    data = request.get_json() or {}
    name, email = validate_client_data(data)
    google_account_email = data.get("google_account_email", "").strip()
    if not google_account_email or "@" not in google_account_email:
        abort(400, description="Valid 'google_account_email' is required.")
    new_client = Client(name=name, email=email)

    db.session.add(new_client)
    db.session.commit()
    return jsonify(new_client.to_dict()), 201


@client_bp.route("/api/clients/<int:client_id>", methods=["PUT"])
def update_client(client_id):
    """Update an existing client."""
    client = Client.query.get_or_404(
        client_id, description=f"Client {client_id} not found."
    )
    data = request.get_json() or {}
    name, email = validate_client_data(data)
    client.name = name
    client.email = email
    db.session.commit()
    return jsonify(client.to_dict()), 200


@client_bp.route("/api/clients/<int:client_id>", methods=["DELETE"])
def delete_client(client_id):
    """Delete a client."""
    client = Client.query.get_or_404(
        client_id, description=f"Client {client_id} not found."
    )
    db.session.delete(client)
    db.session.commit()
    return jsonify({"message": f"Client {client_id} deleted."}), 200


@client_bp.route("/api/clients/<int:client_id>/calendars", methods=["GET"])
def get_client_calendars(client_id):
    """Return all Google Calendars for a given client."""
    # 1) Ensure client exists
    Client.query.get_or_404(client_id, description=f"Client {client_id} not found.")
    # 2) Fetch valid OAuth credentials
    creds = OAuthCredential.query.filter_by(client_id=client_id, is_valid=True).first()
    if not creds:
        abort(400, description="No valid OAuth credentials for this client.")
    # 3) Instantiate GoogleCalendarService with correct constructor usage
    svc = GoogleCalendarService(creds)
    # 4) Retrieve and return calendars
    calendars = svc.list_calendars()
    return jsonify(calendars), 200
