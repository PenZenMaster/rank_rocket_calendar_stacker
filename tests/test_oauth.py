"""
Module/Script Name: test_oauth.py

Description:
Unit tests for OAuthCredential API endpoints.

Author(s):
Skippy the Code Slayer with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
13-07-2025

Last Modified Date:
13-07-2025

Version:
v1.00

Comments:
- Requires test client, test DB setup
"""

import pytest
from flask import Flask
from src.extensions import db
from src.models.client import Client, OAuthCredential


def create_client(app):
    client = Client(
        name="Test Client",
        email="client@test.com",
        google_account_email="gacc@test.com",
    )
    db.session.add(client)
    db.session.commit()
    return client


@pytest.fixture
def oauth_test_client(app):
    client = create_client(app)
    return app.test_client(), client


def test_create_oauth(oauth_test_client):
    test_client, client = oauth_test_client
    data = {
        "client_id": client.id,
        "google_client_id": "test-gid",
        "google_client_secret": "test-gsecret",
        "scopes": "https://www.googleapis.com/auth/calendar.readonly",
    }
    response = test_client.post("/api/oauth", json=data)
    assert response.status_code == 201
    payload = response.get_json()
    assert payload["client_id"] == client.id
    assert payload["is_valid"] is False


def test_get_oauth(oauth_test_client):
    test_client, client = oauth_test_client
    oauth = OAuthCredential(
        client_id=client.id,
        google_client_id="gid",
        google_client_secret="gsecret",
        scopes="scope1",
    )
    db.session.add(oauth)
    db.session.commit()

    response = test_client.get(f"/api/oauth/{oauth.id}")
    assert response.status_code == 200
    assert response.get_json()["id"] == oauth.id


def test_update_oauth(oauth_test_client):
    test_client, client = oauth_test_client
    oauth = OAuthCredential(
        client_id=client.id,
        google_client_id="gid",
        google_client_secret="gsecret",
        scopes="scope1",
    )
    db.session.add(oauth)
    db.session.commit()

    update_data = {"scopes": "updated.scope"}
    response = test_client.put(f"/api/oauth/{oauth.id}", json=update_data)
    assert response.status_code == 200
    assert response.get_json()["scopes"] == "updated.scope"


def test_delete_oauth(oauth_test_client):
    test_client, client = oauth_test_client
    oauth = OAuthCredential(
        client_id=client.id,
        google_client_id="gid",
        google_client_secret="gsecret",
        scopes="scope1",
    )
    db.session.add(oauth)
    db.session.commit()

    response = test_client.delete(f"/api/oauth/{oauth.id}")
    assert response.status_code == 200
    assert f"OAuthCredential {oauth.id} deleted." in response.get_json()["message"]
