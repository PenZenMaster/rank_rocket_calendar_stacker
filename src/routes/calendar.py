"""
Module/Script Name: calendar.py

Description:
Calendar-related endpoints, wrapping Google Calendar API calls.

Author(s):
Skippy the Magnificent with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
2025-07-11

Last Modified Date:
2025-07-11

Comments:
- Version 1.01  # bumped for parameter fix
"""

from flask import Blueprint, request, jsonify, abort
from src.models.client import OAuthCredential
from src.google_calendar import GoogleCalendarService

calendar_bp = Blueprint("calendar", __name__)


@calendar_bp.route("/clients/<client_id>/calendars", methods=["GET"])
def list_calendars(client_id):
    """Return all calendars for a given client via Google API."""
    # 1. Fetch valid OAuth credentials
    creds = OAuthCredential.query.filter_by(client_id=client_id, is_valid=True).first()
    if not creds:
        return (
            jsonify({"success": True, "data": [], "message": "No OAuth credentials"}),
            200,
        )

    # 2. Instantiate service with the correct parameter
    svc = GoogleCalendarService(oauth_credentials=creds)  # ← was missing/incorrect
    calendars = svc.list_calendars()
    return jsonify({"success": True, "data": calendars}), 200
