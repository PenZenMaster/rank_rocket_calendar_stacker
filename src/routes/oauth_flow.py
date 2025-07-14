"""
Module/Script Name: oauth_flow.py

Description:
Google OAuth2 Authorization & Callback handlers for Calendar integration.

Author(s):
Skippy the Code Slayer with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
13-07-2025

Last Modified Date:
13-07-2025

Version:
v1.00

Comments:
- Implements /authorize and /callback OAuth2 endpoints
"""

import os
import uuid
import json
from flask import Blueprint, request, redirect, session, abort, url_for
from google_auth_oauthlib.flow import Flow
from src.models.oauth import OAuthCredential
from src.extensions import db

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

oauth_flow_bp = Blueprint("oauth_flow_bp", __name__)


@oauth_flow_bp.route("/authorize/<int:oauth_id>")
def authorize(oauth_id):
    oauth = OAuthCredential.query.get_or_404(oauth_id)

    # Create OAuth flow
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": oauth.google_client_id,
                "client_secret": oauth.google_client_secret,
                "redirect_uris": [url_for("oauth_flow_bp.callback", _external=True)],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=(
            json.loads(oauth.scopes) if isinstance(oauth.scopes, str) else oauth.scopes
        ),
    )

    state = str(uuid.uuid4())
    session["oauth_state"] = state
    session["oauth_id"] = oauth.id
    flow.redirect_uri = url_for("oauth_flow_bp.callback", _external=True)

    auth_url, _ = flow.authorization_url(
        access_type="offline", include_granted_scopes="true", state=state
    )
    return redirect(auth_url)


@oauth_flow_bp.route("/callback")
def callback():
    state = request.args.get("state")
    if state != session.get("oauth_state"):
        abort(400, description="Invalid state token")

    oauth_id = session.get("oauth_id")
    oauth = OAuthCredential.query.get_or_404(oauth_id)

    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": oauth.google_client_id,
                "client_secret": oauth.google_client_secret,
                "redirect_uris": [url_for("oauth_flow_bp.callback", _external=True)],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=(
            json.loads(oauth.scopes) if isinstance(oauth.scopes, str) else oauth.scopes
        ),
        state=state,
    )
    flow.redirect_uri = url_for("oauth_flow_bp.callback", _external=True)

    flow.fetch_token(authorization_response=request.url)
    creds = flow.credentials

    oauth.access_token = creds.token
    oauth.refresh_token = creds.refresh_token
    oauth.expires_at = creds.expiry
    oauth.is_valid = True
    db.session.commit()

    return redirect("/")  # or send a success message/redirect to dashboard
