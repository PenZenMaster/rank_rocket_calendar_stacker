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
v1.13

Comments:
- Hard-coded sys.path.insert for Windows to resolve `src` during pytest execution
- Preload and configure all SQLAlchemy model mappers to avoid relationship resolution errors
"""

import sys

# Add full absolute path to src for Windows pytest compatibility
sys.path.insert(0, r"E:\projects\rank_rocket_calendar_stacker\src")

# Pre-load model modules and configure mappers before any test execution
import src.models.client
import src.models.oauth_credential
from sqlalchemy.orm import configure_mappers

configure_mappers()

import pytest
from src.main import create_app
from src.extensions import db


@pytest.fixture(autouse=True)
def preload_models():
    """Ensure SQLAlchemy mappers are configured before each test"""
    # Re-run to pick up any late-bound relationships
    configure_mappers()


@pytest.fixture(scope="module")
def app():
    # Create Flask app with testing config
    app = create_app("src.config.TestingConfig")
    yield app


@pytest.fixture(scope="function", autouse=True)
def setup_db(app):
    with app.app_context():
        db.drop_all()
        db.create_all()

        # Populate test client with required google_email
        from src.models.client import Client

        test_client = Client(
            name="Test Client",
            email="test@example.com",
            google_email="test@example.com",
        )
        db.session.add(test_client)
        db.session.commit()

        yield

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()
