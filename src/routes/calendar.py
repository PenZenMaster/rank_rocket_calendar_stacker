"""
Module/Script Name: src/routes/calendar.py

Description:
Calendar-related endpoints, restoring HTML UI for event CRUD with Google Calendar integration.

Author(s):
Skippy the Magnificent with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
2025-07-11

Last Modified Date:
2025-07-16

Version:
v1.08

Comments:
- Switched from JSON API to HTML rendering
- Added event list, create, edit, delete flows with flash messages
- Integrated CalendarApiError handling in UI
- Added explicit return type annotations for Pylance compliance
- Ensured all code paths return a Response
"""

from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask.typing import ResponseReturnValue
from src.models.oauth import OAuthCredential
from src.google_calendar import GoogleCalendarService, CalendarApiError

calendar_bp = Blueprint("calendar", __name__, template_folder="templates/calendar")


def _get_service_or_redirect(client_id: int) -> GoogleCalendarService | None:
    creds = OAuthCredential.query.filter_by(client_id=client_id, is_valid=True).first()
    if not creds:
        flash(
            "No Google OAuth credentials found. Connect your account first.", "warning"
        )
        return None
    return GoogleCalendarService(creds)


@calendar_bp.route("/clients/<int:client_id>/calendars")
def list_calendars(client_id: int) -> ResponseReturnValue:
    svc = _get_service_or_redirect(client_id)
    if not svc:
        return redirect(url_for("client_bp.get_clients"))
    try:
        calendars = svc.list_calendars()
    except CalendarApiError as e:
        flash(str(e), "danger")
        calendars = []
    return render_template("list.html", client_id=client_id, calendars=calendars)


@calendar_bp.route("/clients/<int:client_id>/calendars/events")
def list_events(client_id: int) -> ResponseReturnValue:
    svc = _get_service_or_redirect(client_id)
    if not svc:
        return redirect(url_for("calendar.list_calendars", client_id=client_id))
    try:
        events = svc.list_events()
    except CalendarApiError as e:
        flash(str(e), "danger")
        events = []
    return render_template("events.html", client_id=client_id, events=events)


@calendar_bp.route(
    "/clients/<int:client_id>/calendars/events/new", methods=["GET", "POST"]
)
def create_event(client_id: int) -> ResponseReturnValue:
    svc = _get_service_or_redirect(client_id)
    if not svc:
        return redirect(url_for("calendar.list_calendars", client_id=client_id))
    if request.method == "POST":
        event_data = request.form.to_dict()
        try:
            svc.create_event("primary", event_data)
            flash("Event created successfully.", "success")
            return redirect(url_for("calendar.list_events", client_id=client_id))
        except CalendarApiError as e:
            flash(str(e), "danger")
            # Re-render form with submitted data
            return render_template(
                "event_form.html",
                client_id=client_id,
                event=event_data,
                action="Create",
            )
    return render_template(
        "event_form.html", client_id=client_id, event=None, action="Create"
    )


@calendar_bp.route(
    "/clients/<int:client_id>/calendars/events/<string:event_id>/edit",
    methods=["GET", "POST"],
)
def edit_event(client_id: int, event_id: str) -> ResponseReturnValue:
    svc = _get_service_or_redirect(client_id)
    if not svc:
        return redirect(url_for("calendar.list_calendars", client_id=client_id))
    if request.method == "POST":
        event_data = request.form.to_dict()
        try:
            svc.update_event("primary", event_id, event_data)
            flash("Event updated successfully.", "success")
            return redirect(url_for("calendar.list_events", client_id=client_id))
        except CalendarApiError as e:
            flash(str(e), "danger")
            # Re-render form with submitted data
            return render_template(
                "event_form.html", client_id=client_id, event=event_data, action="Edit"
            )
    # GET path
    try:
        event = svc.get_event("primary", event_id)
    except CalendarApiError as e:
        flash(str(e), "danger")
        return redirect(url_for("calendar.list_events", client_id=client_id))
    return render_template(
        "event_form.html", client_id=client_id, event=event, action="Edit"
    )


@calendar_bp.route(
    "/clients/<int:client_id>/calendars/events/<string:event_id>/delete",
    methods=["POST"],
)
def delete_event(client_id: int, event_id: str) -> ResponseReturnValue:
    svc = _get_service_or_redirect(client_id)
    if not svc:
        return redirect(url_for("calendar.list_calendars", client_id=client_id))
    try:
        svc.delete_event("primary", event_id)
        flash("Event deleted successfully.", "success")
    except CalendarApiError as e:
        flash(str(e), "danger")
    return redirect(url_for("calendar.list_events", client_id=client_id))
