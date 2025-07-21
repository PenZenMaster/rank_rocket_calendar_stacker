"""
Module/Script Name: src/routes/oauth_flow.py

Description:
Handles OAuth 2.0 redirect and callback logic for authorization flow

Author(s):
Skippy the Magnificent with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
14-07-2025

Last Modified Date:
20-07-2025

Version:
v1.13

Comments:
- Enhanced callback to persist refresh_token and expires_at
- Added validation toggle and optional debug logging
- ✅ Now correctly saves tokens to the DB
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
    """Redirect user to Google's OAuth 2.0 authorization page."""
    oauth_entry = OAuthCredential.query.get_or_404(oauth_id)

    client_config = {
        "web": {
            "client_id": oauth_entry.google_client_id,
            "client_secret": oauth_entry.google_client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [oauth_entry.google_redirect_uri],
        }
    }

    scopes = oauth_entry.scopes.splitlines()

    flow = Flow.from_client_config(
        client_config=client_config,
        scopes=scopes,
        redirect_uri=oauth_entry.google_redirect_uri,
    )

    authorization_url, state = flow.authorization_url(
        access_type="offline", include_granted_scopes="true", prompt="consent"
    )

    session["state"] = state
    session["oauth_id"] = oauth_id

    print("Redirecting to Google:", authorization_url)
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
        scopes=oauth_entry.scopes.splitlines(),
        state=state,
    )
    flow.redirect_uri = oauth_entry.google_redirect_uri

    try:
        flow.fetch_token(authorization_response=request.url)
        credentials = flow.credentials

        oauth_entry.access_token = credentials.token
        oauth_entry.refresh_token = credentials.refresh_token
        oauth_entry.expires_at = credentials.expiry
        oauth_entry.is_valid = True

        db.session.commit()

        print(f"[OAuth] ✅ Token stored for OAuth ID {oauth_id}")

    except Exception as e:
        print(f"[OAuth] ❌ Error fetching token: {e}")
        return f"OAuth callback failed: {e}", 500

    return redirect("/")
