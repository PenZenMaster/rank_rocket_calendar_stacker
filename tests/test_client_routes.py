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
20-07-2025

Version:
v1.04

Comments:
- Uses a unique in-memory SQLite DB per test via UUID in URI to ensure isolation
- Fixtures for app/client setup and teardown (drop schema before create)
- Tests for:
  • GET /api/clients (empty and non-empty)
  • POST /api/clients (valid and invalid payloads)
  • GET, PUT, DELETE /api/clients/<id>
"""

import pytest
import uuid
from src.main import create_app
from src.extensions import db


@pytest.fixture
def app():
    # Generate a unique in-memory database URI for isolation
    unique_id = uuid.uuid4().hex
    # SQLite URI for a shared in-memory DB with a unique name
    db_uri = f"sqlite:///file:{unique_id}?mode=memory&cache=shared&uri=true"
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": db_uri})
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
    clients = list_resp.get_json()
    assert isinstance(clients, list)
    assert len(clients) == 1
    assert any(c["id"] == data["id"] for c in clients)


def test_get_client_by_id(client):
    # Create a client
    payload = {
        "name": "Foo",
        "email": "foo@bar.com",
        "google_account_email": "goo@bar.com",
    }
    post_resp = client.post("/api/clients", json=payload)
    id_ = post_resp.get_json()["id"]
    # Retrieve the client
    get_resp = client.get(f"/api/clients/{id_}")
    assert get_resp.status_code == 200
    client_data = get_resp.get_json()
    assert client_data["id"] == id_
    assert client_data["name"] == "Foo"


def test_update_client(client):
    # Setup: create a client
    payload = {
        "name": "Foo",
        "email": "foo@bar.com",
        "google_account_email": "goo@bar.com",
    }
    post_resp = client.post("/api/clients", json=payload)
    id_ = post_resp.get_json()["id"]
    # Perform update
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
    # Setup: create a client
    payload = {
        "name": "DelMe",
        "email": "del@me.com",
        "google_account_email": "del@google.com",
    }
    post_resp = client.post("/api/clients", json=payload)
    id_ = post_resp.get_json()["id"]
    # Delete the client
    del_resp = client.delete(f"/api/clients/{id_}")
    assert del_resp.status_code == 200
    # Verify deletion
    get_resp = client.get(f"/api/clients/{id_}")
    assert get_resp.status_code == 404


# Edge case: invalid payloads for client creation
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
