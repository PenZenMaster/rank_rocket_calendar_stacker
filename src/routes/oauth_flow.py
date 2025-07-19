"""
Module/Script Name: src/routes/oauth_flow.py

Description:
Handles OAuth 2.0 redirect and callback logic for authorization flow.

Author(s):
Skippy the Code Slayer with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
14-07-2025

Last Modified Date:
18-07-2025

Version:
v1.13

Comments:
- Deferred import of `Flow` from `google_auth_oauthlib.flow` into view functions to avoid circular import with stdlib `calendar` module
- Redirect to `/` after successful OAuth callback so client list is displayed in the UI
"""

from flask import Blueprint, redirect, request, session, abort
from src.models.oauth_credential import OAuthCredential
from src.extensions import db

oauth_flow_bp = Blueprint("oauth_flow_bp", __name__)


@oauth_flow_bp.route("/authorize/<int:oauth_id>")
def authorize(oauth_id):
    """Initiate OAuth 2.0 flow for a given OAuthCredential."""
    # Defer import to avoid global google_auth_oauthlib.flow import
    from google_auth_oauthlib.flow import Flow

    oauth_entry = db.session.get(OAuthCredential, oauth_id)
    if not oauth_entry:
        abort(404, description="OAuth credentials not found.")

    client_config = {
        "web": {
            "client_id": oauth_entry.google_client_id,
            "client_secret": oauth_entry.google_client_secret,
            "redirect_uris": [oauth_entry.google_redirect_uri],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }

    flow = Flow.from_client_config(
        client_config=client_config,
        scopes=["https://www.googleapis.com/auth/calendar"],
        redirect_uri=oauth_entry.google_redirect_uri,
    )

    authorization_url, state = flow.authorization_url(
        access_type="offline", include_granted_scopes="true"
    )

    session["state"] = state
    session["oauth_id"] = oauth_id

    return redirect(authorization_url)


@oauth_flow_bp.route("/callback")
def callback():
    """Handle OAuth callback, exchange code for tokens, and persist."""
    # Defer import to avoid top-level import issues
    from google_auth_oauthlib.flow import Flow

    state = session.get("state")
    oauth_id = session.get("oauth_id")
    if not oauth_id:
        abort(400, description="Missing OAuth session state.")

    oauth_entry = db.session.get(OAuthCredential, oauth_id)
    if not oauth_entry:
        abort(404, description="OAuth credentials not found.")

    client_config = {
        "web": {
            "client_id": oauth_entry.google_client_id,
            "client_secret": oauth_entry.google_client_secret,
            "redirect_uris": [oauth_entry.google_redirect_uri],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }

    flow = Flow.from_client_config(
        client_config=client_config,
        scopes=["https://www.googleapis.com/auth/calendar"],
        state=state,
    )
    flow.redirect_uri = oauth_entry.google_redirect_uri

    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials
    oauth_entry.access_token = credentials.token
    db.session.commit()

    # Redirect back to the client list in the UI
    return redirect("/")
