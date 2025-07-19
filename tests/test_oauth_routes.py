"""
Module/Script Name: tests/test_oauth_routes.py

Description:
Pytest suite for CRUD endpoints in src/routes/oauth.py for OAuthCredential management.
Covers listing, creation, retrieval, updating, deletion, and validation error cases.

Author(s):
Skippy the Code Slayer

Created Date:
18-07-2025

Last Modified Date:
18-07-2025

Version:
v1.01

Comments:
- Uses unique in-memory SQLite DB per test via UUID-based URI for isolation
- Seeds a Client record in setup
- Guarded access to client_obj.id to avoid NoneType issues
- Tests include GET list (empty/non-empty), POST, GET by id, PUT, DELETE, and invalid payload scenarios
"""

import pytest
import uuid
from src.main import create_app
from src.extensions import db
from src.models.client import Client
from src.models.oauth_credential import OAuthCredential


# Override any global DB setup fixture to prevent unintended seeding
@pytest.fixture(autouse=True)
def setup_db():
    yield


@pytest.fixture
def app():
    # Create a fresh in-memory SQLite DB per test suite
    uid = uuid.uuid4().hex
    db_uri = f"sqlite:///file:{uid}?mode=memory&cache=shared&uri=true"
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": db_uri})
    with app.app_context():
        # Reset schema
        db.drop_all()
        db.create_all()
        # Seed a Client for FK constraints
        client = Client(
            name="TestClient",
            email="test@client.com",
            google_account_email="google@client.com",
        )
        db.session.add(client)
        db.session.commit()
        yield app
        # Teardown: close session, drop, and dispose engine
        db.session.remove()
        db.drop_all()
        engine = db.get_engine(app=app)
        engine.dispose()


@pytest.fixture
def client(app):
    return app.test_client()


def test_list_oauth_empty(client):
    resp = client.get("/api/oauth")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_create_oauth(client):
    client_obj = Client.query.first()
    assert client_obj is not None
    cid = client_obj.id
    payload = {
        "client_id": cid,
        "google_client_id": "gid123",
        "google_client_secret": "secretxyz",
        "scopes": ["scope1", "scope2"],
    }
    resp = client.post("/api/oauth", json=payload)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["client_id"] == cid
    assert data["google_client_id"] == "gid123"
    assert data.get("scopes") == ["scope1", "scope2"]
    # GET list now returns one record
    list_resp = client.get("/api/oauth")
    assert list_resp.status_code == 200
    records = list_resp.get_json()
    assert isinstance(records, list)
    assert any(c.get("id") == data.get("id") for c in records)


def test_get_oauth_by_id(client):
    client_obj = Client.query.first()
    assert client_obj is not None
    cid = client_obj.id
    payload = {
        "client_id": cid,
        "google_client_id": "gidA",
        "google_client_secret": "secA",
        "scopes": ["s1"],
    }
    post = client.post("/api/oauth", json=payload)
    oid = post.get_json().get("id")
    get_resp = client.get(f"/api/oauth/{oid}")
    assert get_resp.status_code == 200
    assert get_resp.get_json().get("id") == oid


def test_update_oauth(client):
    client_obj = Client.query.first()
    assert client_obj is not None
    cid = client_obj.id
    post = client.post(
        "/api/oauth",
        json={
            "client_id": cid,
            "google_client_id": "gidB",
            "google_client_secret": "secB",
            "scopes": ["sB"],
        },
    )
    oid = post.get_json().get("id")
    update = {"google_client_secret": "newSecret", "scopes": ["newScope"]}
    put = client.put(f"/api/oauth/{oid}", json=update)
    assert put.status_code == 200
    updated = put.get_json()
    assert updated.get("google_client_secret") == "newSecret"
    assert updated.get("scopes") == ["newScope"]


def test_delete_oauth(client):
    client_obj = Client.query.first()
    assert client_obj is not None
    cid = client_obj.id
    post = client.post(
        "/api/oauth",
        json={
            "client_id": cid,
            "google_client_id": "gidC",
            "google_client_secret": "secC",
            "scopes": ["sC"],
        },
    )
    oid = post.get_json().get("id")
    del_resp = client.delete(f"/api/oauth/{oid}")
    assert del_resp.status_code == 200
    get_resp = client.get(f"/api/oauth/{oid}")
    assert get_resp.status_code == 404
    assert "message" in get_resp.get_json()


@pytest.mark.parametrize(
    "payload, error_msg",
    [
        ({}, "'client_id' is required."),
        ({"client_id": 9999}, "Client 9999 not found."),
        (
            {"client_id": 1, "google_client_id": "gid"},
            "'google_client_secret' is required.",
        ),
    ],
)
def test_create_oauth_invalid(client, payload, error_msg):
    resp = client.post("/api/oauth", json=payload)
    assert resp.status_code == 400
    msg = resp.get_json().get("message")
    assert error_msg in msg
