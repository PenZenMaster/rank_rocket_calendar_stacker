"""
Module/Script Name: tests/test_oauth.py

Description:
Pytest test suite for src/routes/user.py, testing CRUD user endpoints.

Author(s):
Skippy the Code Slayer with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
17-07-2025

Last Modified Date:
22-07-2025

Version:
v1.04

Comments:
- Added DummySession.remove() to support teardown without session errors
- Annotated DummyUser.id as Optional[int] to satisfy type checker
- Added explicit assert to confirm session.added is not None before attribute access
- Continues using create_app with TestingConfig and registers user_bp blueprint
"""

import pytest
from typing import Optional, List
from unittest.mock import patch, MagicMock
from src.main import create_app
from src.routes.user import user_bp
from src.models.user import User
from src.models.user import db as real_db


@pytest.fixture
def app(monkeypatch):
    # Create Flask app via factory to initialize extensions and DB
    app = create_app("src.config.TestingConfig")
    app.register_blueprint(user_bp)
    return app


@pytest.fixture
def client(app):
    return app.test_client()


class DummyUser:
    id: Optional[int]
    username: Optional[str]
    email: Optional[str]

    def __init__(self, username: Optional[str] = None, email: Optional[str] = None):
        self.id = None
        self.username = username
        self.email = email

    def to_dict(self) -> dict:
        return {"id": self.id, "username": self.username, "email": self.email}


class DummySession:
    def __init__(self):
        self.added: Optional[DummyUser] = None
        self.deleted: Optional[DummyUser] = None
        self.committed: bool = False

    def add(self, instance: DummyUser) -> None:
        self.added = instance
        instance.id = 1

    def delete(self, instance: DummyUser) -> None:
        self.deleted = instance

    def commit(self) -> None:
        self.committed = True

    def remove(self) -> None:
        # No-op stub to satisfy teardown remove() calls
        pass


class DummyQuery:
    def __init__(self, users: Optional[List[DummyUser]] = None):
        self._users: List[DummyUser] = users or []

    def all(self) -> List[DummyUser]:
        return self._users

    def get_or_404(self, user_id: int) -> DummyUser:
        for user in self._users:
            if user.id == user_id:
                return user
        from flask import abort

        abort(404)


def setup_monkeypatch(monkeypatch, users_list: List[DummyUser]) -> DummySession:
    """
    Helper to patch User.query and db.session for tests.
    """
    dummy_query = DummyQuery(users=users_list)
    monkeypatch.setattr(User, "query", dummy_query)
    session = DummySession()
    monkeypatch.setattr(real_db, "session", session)
    return session


def test_get_users_empty(monkeypatch, client):
    session = setup_monkeypatch(monkeypatch, [])
    response = client.get("/users")
    assert response.status_code == 200
    assert response.get_json() == []


def test_get_users_with_users(monkeypatch, client):
    u1 = DummyUser("alice", "alice@example.com")
    u1.id = 1
    u2 = DummyUser("bob", "bob@example.com")
    u2.id = 2
    setup_monkeypatch(monkeypatch, [u1, u2])
    response = client.get("/users")
    assert response.status_code == 200
    assert response.get_json() == [
        {"id": 1, "username": "alice", "email": "alice@example.com"},
        {"id": 2, "username": "bob", "email": "bob@example.com"},
    ]


def test_create_user(monkeypatch, client):
    import src.routes.user as user_module

    monkeypatch.setattr(user_module, "User", DummyUser)
    session = setup_monkeypatch(monkeypatch, [])
    response = client.post(
        "/users", json={"username": "charlie", "email": "charlie@example.com"}
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["id"] == 1
    assert data["username"] == "charlie"
    assert data["email"] == "charlie@example.com"
    # Ensure added is not None before accessing attributes
    assert session.added is not None
    assert session.added.username == "charlie"
    assert session.committed


def test_get_user_exists(monkeypatch, client):
    u1 = DummyUser("alice", "alice@example.com")
    u1.id = 1
    setup_monkeypatch(monkeypatch, [u1])
    response = client.get("/users/1")
    assert response.status_code == 200
    assert response.get_json() == {
        "id": 1,
        "username": "alice",
        "email": "alice@example.com",
    }


def test_get_user_not_found(monkeypatch, client):
    setup_monkeypatch(monkeypatch, [])
    response = client.get("/users/99")
    assert response.status_code == 404


def test_update_user(monkeypatch, client):
    u1 = DummyUser("alice", "alice@old.com")
    u1.id = 1
    session = setup_monkeypatch(monkeypatch, [u1])
    response = client.put("/users/1", json={"email": "alice@new.com"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["email"] == "alice@new.com"
    assert session.committed


def test_delete_user(monkeypatch, client):
    u1 = DummyUser("alice", "alice@example.com")
    u1.id = 1
    session = setup_monkeypatch(monkeypatch, [u1])
    response = client.delete("/users/1")
    assert response.status_code == 204
    assert session.deleted == u1
    assert session.committed
