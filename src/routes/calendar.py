"""
Module/Script Name: src/routes/calendar.py

Description:
Calendar UI endpoints for Google Calendar management with Event CRUD views.

Author(s):
Skippy the Code Slayer with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
18-07-2025

Last Modified Date:
19-07-2025

Version:
v1.09

Comments:
- _get_service returns None when no valid credentials
- Routes flash and redirect on missing credentials
- Render templates under templates/calendar
- Full Python header and type annotations
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask.typing import ResponseReturnValue
from src.models.oauth_credential import OAuthCredential
from src.google_calendar import GoogleCalendarService, CalendarApiError

calendar_bp = Blueprint("calendar", __name__)


def _get_service(client_id: int) -> GoogleCalendarService | None:
    """
    Helper to retrieve GoogleCalendarService or None if missing/invalid creds.
    """
    creds = OAuthCredential.query.filter_by(client_id=client_id, is_valid=True).first()
    if creds is None:
        return None
    return GoogleCalendarService(creds)


@calendar_bp.route("/clients/<int:client_id>/calendars", methods=["GET"])
def list_calendars(client_id: int) -> ResponseReturnValue:
    svc = _get_service(client_id)
    if svc is None:
        flash(
            "No Google OAuth credentials found. Connect your account first.", "warning"
        )
        return redirect(url_for("client_bp.get_clients"))
    try:
        calendars = svc.list_calendars()
    except CalendarApiError as e:
        flash(str(e), "danger")
        calendars = []
    return render_template(
        "calendar/list.html", client_id=client_id, calendars=calendars
    )


@calendar_bp.route("/clients/<int:client_id>/calendars/events", methods=["GET"])
def list_events(client_id: int) -> ResponseReturnValue:
    svc = _get_service(client_id)
    if svc is None:
        flash(
            "No Google OAuth credentials found. Connect your account first.", "warning"
        )
        return redirect(url_for("calendar.list_calendars", client_id=client_id))
    try:
        events = svc.list_events()
    except CalendarApiError as e:
        flash(str(e), "danger")
        events = []
    return render_template("calendar/events.html", client_id=client_id, events=events)


@calendar_bp.route(
    "/clients/<int:client_id>/calendars/events/new", methods=["GET", "POST"]
)
def create_event(client_id: int) -> ResponseReturnValue:
    svc = _get_service(client_id)
    if svc is None:
        flash(
            "No Google OAuth credentials found. Connect your account first.", "warning"
        )
        return redirect(url_for("calendar.list_calendars", client_id=client_id))
    if request.method == "POST":
        event_data = request.form.to_dict()
        try:
            svc.create_event("primary", event_data)
            flash("Event created successfully.", "success")
            return redirect(url_for("calendar.list_events", client_id=client_id))
        except CalendarApiError as e:
            flash(str(e), "danger")
            return render_template(
                "calendar/event_form.html",
                client_id=client_id,
                event=event_data,
                action="Create",
            )
    return render_template(
        "calendar/event_form.html", client_id=client_id, event=None, action="Create"
    )


@calendar_bp.route(
    "/clients/<int:client_id>/calendars/events/<string:event_id>/edit",
    methods=["GET", "POST"],
)
def edit_event(client_id: int, event_id: str) -> ResponseReturnValue:
    svc = _get_service(client_id)
    if svc is None:
        flash(
            "No Google OAuth credentials found. Connect your account first.", "warning"
        )
        return redirect(url_for("calendar.list_calendars", client_id=client_id))
    if request.method == "POST":
        event_data = request.form.to_dict()
        try:
            svc.update_event("primary", event_id, event_data)
            flash("Event updated successfully.", "success")
            return redirect(url_for("calendar.list_events", client_id=client_id))
        except CalendarApiError as e:
            flash(str(e), "danger")
            return render_template(
                "calendar/event_form.html",
                client_id=client_id,
                event=event_data,
                action="Edit",
            )
    try:
        event = svc.get_event("primary", event_id)
    except CalendarApiError as e:
        flash(str(e), "danger")
        return redirect(url_for("calendar.list_events", client_id=client_id))
    return render_template(
        "calendar/event_form.html", client_id=client_id, event=event, action="Edit"
    )


@calendar_bp.route(
    "/clients/<int:client_id>/calendars/events/<string:event_id>/delete",
    methods=["POST"],
)
def delete_event(client_id: int, event_id: str) -> ResponseReturnValue:
    svc = _get_service(client_id)
    if svc is None:
        flash(
            "No Google OAuth credentials found. Connect your account first.", "warning"
        )
        return redirect(url_for("calendar.list_calendars", client_id=client_id))
    try:
        svc.delete_event("primary", event_id)
        flash("Event deleted successfully.", "success")
    except CalendarApiError as e:
        flash(str(e), "danger")
    return redirect(url_for("calendar.list_events", client_id=client_id))
