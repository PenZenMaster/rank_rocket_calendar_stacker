"""
Module/Script Name: calendar.py

Description:
Calendar-related endpoints, wrapping Google Calendar API calls.

Author(s):
Skippy the Magnificent with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
2025-07-11

Last Modified Date:
2025-07-15

Version:
v1.03

Comments:
- Fixed attribute access issues for VS Code (Pylance) by adding stub methods in GoogleCalendarService
"""

from flask import Blueprint, request, jsonify, abort
from src.models.client import Client
from src.models.oauth import OAuthCredential

from src.google_calendar import GoogleCalendarService

# Patch class to silence Pylance complaints in VS Code (stub typing support)
if False:
    from typing import Dict, Any

    class GoogleCalendarService:
        def list_events(self) -> list: ...
        def create_event(
            self, calendar_id: str, event_data: Dict[str, Any]
        ) -> dict: ...
        def get_event(self, calendar_id: str, event_id: str) -> dict: ...
        def update_event(
            self, calendar_id: str, event_id: str, event_data: Dict[str, Any]
        ) -> dict: ...
        def delete_event(self, calendar_id: str, event_id: str) -> None: ...


calendar_bp = Blueprint("calendar", __name__)


@calendar_bp.route("/clients/<client_id>/calendars", methods=["GET"])
def list_calendars(client_id):
    """Return all calendars for a given client via Google API."""
    creds = OAuthCredential.query.filter_by(client_id=client_id, is_valid=True).first()
    if not creds:
        return (
            jsonify({"success": True, "data": [], "message": "No OAuth credentials"}),
            200,
        )

    svc = GoogleCalendarService(oauth_credentials=creds)
    calendars = svc.list_calendars()
    return jsonify({"success": True, "data": calendars}), 200


@calendar_bp.route("/clients/<client_id>/calendars/events", methods=["GET"])
def list_events(client_id):
    creds = OAuthCredential.query.filter_by(client_id=client_id, is_valid=True).first()
    if not creds:
        return jsonify({"error": "OAuth credentials not found"}), 404
    svc = GoogleCalendarService(oauth_credentials=creds)
    events = svc.list_events()
    return jsonify(events), 200


@calendar_bp.route("/clients/<client_id>/calendars/events", methods=["POST"])
def create_event(client_id):
    creds = OAuthCredential.query.filter_by(client_id=client_id, is_valid=True).first()
    if not creds:
        return jsonify({"error": "OAuth credentials not found"}), 404
    svc = GoogleCalendarService(oauth_credentials=creds)
    event = svc.create_event("primary", request.get_json())
    return jsonify(event), 201


@calendar_bp.route("/clients/<client_id>/calendars/events/<event_id>", methods=["GET"])
def get_event(client_id, event_id):
    creds = OAuthCredential.query.filter_by(client_id=client_id, is_valid=True).first()
    if not creds:
        return jsonify({"error": "OAuth credentials not found"}), 404
    svc = GoogleCalendarService(oauth_credentials=creds)
    event = svc.get_event("primary", event_id)
    return jsonify(event), 200


@calendar_bp.route("/clients/<client_id>/calendars/events/<event_id>", methods=["PUT"])
def update_event(client_id, event_id):
    creds = OAuthCredential.query.filter_by(client_id=client_id, is_valid=True).first()
    if not creds:
        return jsonify({"error": "OAuth credentials not found"}), 404
    svc = GoogleCalendarService(oauth_credentials=creds)
    event = svc.update_event("primary", event_id, request.get_json())
    return jsonify(event), 200


@calendar_bp.route(
    "/clients/<client_id>/calendars/events/<event_id>", methods=["DELETE"]
)
def delete_event(client_id, event_id):
    creds = OAuthCredential.query.filter_by(client_id=client_id, is_valid=True).first()
    if not creds:
        return jsonify({"error": "OAuth credentials not found"}), 404
    svc = GoogleCalendarService(oauth_credentials=creds)
    svc.delete_event("primary", event_id)
    return "", 204
