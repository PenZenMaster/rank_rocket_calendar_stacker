"""
Module/Script Name: tests/test_client_routes.py

Description:
Pytest suite for the Client CRUD JSON API endpoints in src/routes/client.py.
Covers listing, creation, retrieval, update, deletion, and validation error cases.

Author(s):
Skippy the Code Slayer with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
18-07-2025

Last Modified Date:
18-07-2025

Version:
v1.03

Comments:
- Uses in-memory SQLite when TESTING=True via create_app override
- Fixtures for app/client setup and teardown (drop schema before create)
- Tests for:
  • GET /api/clients (empty and non-empty)
  • POST /api/clients (valid and invalid payloads)
  • GET, PUT, DELETE /api/clients/<id>
"""

import pytest
from src.main import create_app
from src.extensions import db


@pytest.fixture
def app():
    # Create a Flask app configured for testing
    app = create_app({"TESTING": True})
    with app.app_context():
        # Ensure a clean slate for each test run
        db.drop_all()
        db.create_all()
        yield app
        # Teardown: remove session and drop all tables
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_get_clients_empty(client):
    resp = client.get("/api/clients")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_create_client(client):
    payload = {
        "name": "Test Client",
        "email": "test@example.com",
        "google_account_email": "google@example.com",
    }
    resp = client.post("/api/clients", json=payload)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["name"] == "Test Client"
    assert data["email"] == "test@example.com"
    assert data["google_account_email"] == "google@example.com"
    assert isinstance(data["id"], int)

    # Now GET should return one client
    list_resp = client.get("/api/clients")
    assert list_resp.status_code == 200
    assert isinstance(list_resp.get_json(), list)
    assert any(c["id"] == data["id"] for c in list_resp.get_json())


def test_get_client_by_id(client):
    # Create
    payload = {
        "name": "Foo",
        "email": "foo@bar.com",
        "google_account_email": "goo@bar.com",
    }
    post = client.post("/api/clients", json=payload)
    id_ = post.get_json()["id"]
    # Retrieve
    get_resp = client.get(f"/api/clients/{id_}")
    assert get_resp.status_code == 200
    client_data = get_resp.get_json()
    assert client_data["id"] == id_
    assert client_data["name"] == "Foo"


def test_update_client(client):
    payload = {
        "name": "Foo",
        "email": "foo@bar.com",
        "google_account_email": "goo@bar.com",
    }
    post = client.post("/api/clients", json=payload)
    id_ = post.get_json()["id"]
    update = {
        "name": "Foo2",
        "email": "foo2@bar.com",
        "google_account_email": "goo2@bar.com",
    }
    put_resp = client.put(f"/api/clients/{id_}", json=update)
    assert put_resp.status_code == 200
    updated = put_resp.get_json()
    assert updated["id"] == id_
    assert updated["name"] == "Foo2"
    assert updated["email"] == "foo2@bar.com"
    assert updated["google_account_email"] == "goo2@bar.com"


def test_delete_client(client):
    payload = {
        "name": "DelMe",
        "email": "del@me.com",
        "google_account_email": "del@google.com",
    }
    post = client.post("/api/clients", json=payload)
    id_ = post.get_json()["id"]
    del_resp = client.delete(f"/api/clients/{id_}")
    assert del_resp.status_code == 200
    # Attempt to retrieve deleted client
    get_resp = client.get(f"/api/clients/{id_}")
    assert get_resp.status_code == 404


# Edge case: invalid payload
@pytest.mark.parametrize(
    "payload, error_msg",
    [
        ({}, "Client 'name' is required"),
        ({"name": "A"}, "Valid 'email' is required"),
        ({"name": "A", "email": "a@b.com"}, "Valid 'google_account_email' is required"),
    ],
)
def test_create_client_invalid(client, payload, error_msg):
    resp = client.post("/api/clients", json=payload)
    assert resp.status_code == 400
    json_data = resp.get_json()
    assert error_msg in json_data.get("message", json_data.get("error", ""))
