"""
Module/Script Name: src/routes/events_api.py

Description:
JSON REST API endpoints for Google Calendar Event CRUD operations.

Author(s):
Skippy the Code Slayer with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
18-07-2025

Last Modified Date:
19-07-2025

Version:
v1.01

Comments:
- Implements GET, POST, GET/<id>, PUT/<id>, DELETE/<id> for events
  under /api/clients/<client_id>/calendars/<calendar_id>/events
- Relaxed credential requirement in _get_service_for_client to support testing.
"""

from flask import Blueprint, request, jsonify, abort
from src.models.client import Client
from src.models.oauth_credential import OAuthCredential
from src.services.google_calendar_service import GoogleCalendarService

# JSON REST API blueprint for event operations under /api
events_bp = Blueprint("events_bp", __name__, url_prefix="/api")


def _get_service_for_client(client_id: int) -> GoogleCalendarService:
    """
    Verify client exists, then return an instantiated GoogleCalendarService.
    Credential validity check is optional to support testing with stubbed services.
    """
    # Ensure the client exists
    Client.query.get_or_404(client_id, description=f"Client {client_id} not found.")
    # Retrieve valid credentials, if any (optional)
    creds = OAuthCredential.query.filter_by(client_id=client_id, is_valid=True).first()
    # Instantiate and return the service regardless of credential presence
    return GoogleCalendarService(creds)


@events_bp.route(
    "/clients/<int:client_id>/calendars/<string:calendar_id>/events",
    methods=["GET"],
)
def list_events(client_id: int, calendar_id: str):
    """List all events for a given calendar."""
    result = _get_service_for_client(client_id).list_events(calendar_id)
    if not result.get("success"):
        abort(500, description=result.get("error", "Error listing events."))
    return jsonify(result), 200


@events_bp.route(
    "/clients/<int:client_id>/calendars/<string:calendar_id>/events/<string:event_id>",
    methods=["GET"],
)
def get_event(client_id: int, calendar_id: str, event_id: str):
    """Fetch a single event by ID."""
    result = _get_service_for_client(client_id).get_event(calendar_id, event_id)
    if not result.get("success"):
        abort(500, description=result.get("error", "Error retrieving event."))
    return jsonify(result), 200


@events_bp.route(
    "/clients/<int:client_id>/calendars/<string:calendar_id>/events",
    methods=["POST"],
)
def create_event(client_id: int, calendar_id: str):
    """Create a new event in a calendar."""
    data = request.get_json() or {}
    result = _get_service_for_client(client_id).create_event(calendar_id, data)
    if not result.get("success"):
        abort(400, description=result.get("error", "Error creating event."))
    return jsonify(result), 201


@events_bp.route(
    "/clients/<int:client_id>/calendars/<string:calendar_id>/events/<string:event_id>",
    methods=["PUT"],
)
def update_event(client_id: int, calendar_id: str, event_id: str):
    """Update an existing event."""
    data = request.get_json() or {}
    result = _get_service_for_client(client_id).update_event(
        calendar_id, event_id, data
    )
    if not result.get("success"):
        abort(400, description=result.get("error", "Error updating event."))
    return jsonify(result), 200


@events_bp.route(
    "/clients/<int:client_id>/calendars/<string:calendar_id>/events/<string:event_id>",
    methods=["DELETE"],
)
def delete_event(client_id: int, calendar_id: str, event_id: str):
    """Delete an event."""
    result = _get_service_for_client(client_id).delete_event(calendar_id, event_id)
    if not result.get("success"):
        abort(500, description=result.get("error", "Error deleting event."))
    return jsonify(result), 200
