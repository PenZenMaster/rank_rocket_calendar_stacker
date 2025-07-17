"""
Module/Script Name: tests/conftest.py
Path: E:/projects/rank_rocket_calendar_stacker/tests/conftest.py

Description:
Pytest fixtures for Flask app and test database, plus test client definition.
Hard-coded sys.path insert for Windows compatibility with src module resolution.

Author(s):
Skippy the Code Slayer with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
13-07-2025

Last Modified Date:
17-07-2025

Version:
v1.15

Comments:
- Module-level import and mapper configuration to ensure SQLAlchemy relationships resolve at import time
- Auto-strip duplicate configure_mappers calls to avoid mapping errors
- Deferred model loading inside setup_db for schema operations
"""

import sys

# Add full absolute path to src for Windows pytest compatibility
sys.path.insert(0, r"E:\projects\rank_rocket_calendar_stacker\src")

# Preload model modules and configure mappers globally
import src.models.client
import src.models.oauth_credential
from sqlalchemy.orm import configure_mappers

try:
    configure_mappers()
except Exception:
    # mappers may already be configured; ignore
    pass

import pytest
from src.main import create_app
from src.extensions import db


@pytest.fixture(scope="module")
def app():
    # Instantiate Flask app with testing config
    app = create_app("src.config.TestingConfig")
    yield app


@pytest.fixture(scope="function", autouse=True)
def setup_db(app):
    with app.app_context():
        # Ensure fresh schema for each test
        db.drop_all()
        db.create_all()

        # Seed a test client
        from src.models.client import Client

        test_client = Client(
            name="Test Client",
            email="test@example.com",
            google_email="test@example.com",
        )
        db.session.add(test_client)
        db.session.commit()

        yield

        # Teardown
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()
