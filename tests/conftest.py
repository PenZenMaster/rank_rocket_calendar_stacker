"""
Module/Script Name: tests/conftest.py
Path: E:/projects/rank_rocket_calendar_stacker/tests/conftest.py

Description:
Pytest fixtures for Flask app and in-memory test database, plus test client definition.
Hard-coded sys.path insert for Windows pytest compatibility with src module resolution.

Author(s):
Skippy the Code Slayer with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
13-07-2025

Last Modified Date:
17-07-2025

Version:
v1.28

Comments:
- Relies solely on create_app for SQLAlchemy init and config-driven behavior
- No global request-context push: tests should manage contexts explicitly if needed
- setup_db fixture handles fresh schema setup/teardown per function
"""

import sys

# Add full absolute path to src for Windows pytest compatibility
sys.path.insert(0, r"E:\projects\rank_rocket_calendar_stacker\src")

# Preload models and configure mappers globally to avoid import-time errors
import src.models.client
import src.models.oauth_credential
from sqlalchemy.orm import configure_mappers

try:
    configure_mappers()
except Exception:
    # Mappers may already be configured; safe to ignore
    pass

import pytest
from src.main import create_app
from src.extensions import db


@pytest.fixture(scope="module")
def app():
    """
    Create Flask app for testing using TestingConfig.
    SQLAlchemy is initialized inside create_app.
    """
    return create_app("src.config.TestingConfig")


@pytest.fixture(scope="function", autouse=True)
def setup_db(app):
    """
    Fresh in-memory database per test function.
    Drops and recreates all tables, seeds a default client, then tears down.
    """
    with app.app_context():
        db.drop_all()
        db.create_all()

        # Seed a default client for dependent tests
        from src.models.client import Client

        test_client = Client(
            name="Test Client",
            email="test@example.com",
            google_email="test@example.com",
        )
        db.session.add(test_client)
        db.session.commit()

        yield  # run the test

        # Teardown: remove session and drop tables
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """
    Flask test client for endpoint testing.
    """
    return app.test_client()
