"""
Module/Script Name: src/routes/oauth_flow.py

Description:
Handles OAuth 2.0 redirect and callback logic for authorization flow

Author(s):
Skippy the Magnificent with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
14-07-2025

Last Modified Date:
22-07-2025

Version:
v1.11

Comments:
- Redirect to '/lients' after successful OAuth callback so client list is displayed in the UI
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from flask import Blueprint, redirect, request, url_for, session
from google_auth_oauthlib.flow import Flow
from src.models.oauth_credential import OAuthCredential
from src.extensions import db

import pathlib
import json

# Create blueprint
oauth_flow_bp = Blueprint("oauth_flow_bp", __name__)


@oauth_flow_bp.route("/authorize/<int:oauth_id>")
def authorize(oauth_id):
    oauth_entry = db.session.get(OAuthCredential, oauth_id)
    if not oauth_entry:
        return "OAuth credentials not found", 404

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
    state = session.get("state")
    oauth_id = session.get("oauth_id")
    if not oauth_id:
        return "Missing session oauth_id", 400

    oauth_entry = db.session.get(OAuthCredential, oauth_id)
    if not oauth_entry:
        return "OAuth credentials not found", 404

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

    # Redirect back to the client list UI
    return redirect("/")
