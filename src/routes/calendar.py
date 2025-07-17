"""
Module/Script Name: src/routes/calendar.py

Description:
Calendar UI endpoints for Google Calendar management with Event CRUD views.

Author(s):
Skippy the Code Slayer with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
18-07-2025

Last Modified Date:
18-07-2025

Version:
v1.07

Comments:
- Wired UI Event CRUD endpoints to GoogleCalendarService
- Added helper for credential validation and redirection
- Render calendar list, event form, handle create, update, delete with flash messages
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.models.oauth_credential import OAuthCredential
from src.google_calendar import GoogleCalendarService

calendar_bp = Blueprint("calendar", __name__)


def _get_service_or_redirect(client_id):
    """Helper to retrieve GoogleCalendarService or redirect to OAuth if no valid credentials."""
    creds = OAuthCredential.query.filter_by(client_id=client_id, is_valid=True).first()
    if not creds:
        flash(
            "No Google OAuth credentials found. Connect your account first.", "warning"
        )
        return redirect(url_for("oauth_flow_bp.authorize", oauth_id=client_id))
    return GoogleCalendarService(creds)


@calendar_bp.route("/clients/<int:client_id>/calendars", methods=["GET"])
def list_calendars(client_id):
    """Display list of calendars or redirect if unauthorized."""
    svc = _get_service_or_redirect(client_id)
    if not isinstance(svc, GoogleCalendarService):
        return svc
    calendars = svc.list_calendars()
    return render_template(
        "calendar/list.html", client_id=client_id, calendars=calendars
    )


@calendar_bp.route(
    "/clients/<int:client_id>/calendars/events/new", methods=["GET", "POST"]
)
def create_event(client_id):
    """Render form or create new event and redirect to list view."""
    svc = _get_service_or_redirect(client_id)
    if not isinstance(svc, GoogleCalendarService):
        return svc
    if request.method == "POST":
        data = request.form
        svc.create_event(
            "primary",
            {
                "summary": data.get("summary"),
                "description": data.get("description"),
                "start": {"dateTime": data.get("start")},
                "end": {"dateTime": data.get("end")},
            },
        )
        flash("Event created successfully.", "success")
        return redirect(url_for("calendar.list_calendars", client_id=client_id))
    return render_template(
        "calendar/event_form.html", action="New", event=None, client_id=client_id
    )


@calendar_bp.route(
    "/clients/<int:client_id>/calendars/events/<string:event_id>/edit",
    methods=["GET", "POST"],
)
def edit_event(client_id, event_id):
    """Render edit form or update event and redirect to list view."""
    svc = _get_service_or_redirect(client_id)
    if not isinstance(svc, GoogleCalendarService):
        return svc
    if request.method == "POST":
        data = request.form
        svc.update_event(
            "primary",
            event_id,
            {
                "summary": data.get("summary"),
                "description": data.get("description"),
                "start": {"dateTime": data.get("start")},
                "end": {"dateTime": data.get("end")},
            },
        )
        flash("Event updated successfully.", "success")
        return redirect(url_for("calendar.list_calendars", client_id=client_id))
    event = svc.get_event("primary", event_id)
    return render_template(
        "calendar/event_form.html", action="Edit", event=event, client_id=client_id
    )


@calendar_bp.route(
    "/clients/<int:client_id>/calendars/events/<string:event_id>/delete",
    methods=["POST"],
)
def delete_event(client_id, event_id):
    """Delete event and redirect to list view."""
    svc = _get_service_or_redirect(client_id)
    if not isinstance(svc, GoogleCalendarService):
        return svc
    svc.delete_event("primary", event_id)
    flash("Event deleted successfully.", "success")
    return redirect(url_for("calendar.list_calendars", client_id=client_id))
