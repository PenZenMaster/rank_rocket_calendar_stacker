"""
Module/Script Name: conftest.py

Description:
Pytest fixtures for Flask app and test database, properly resetting SQLAlchemy mappings.

Author(s):
Skippy the Code Slayer with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
13-07-2025

Last Modified Date:
13-07-2025

Version:
v1.04

Comments:
- Switched app fixture to use TestingConfig directly (Option B)
"""

import pytest
from sqlalchemy.orm import clear_mappers, configure_mappers

from src.extensions import db
from src.main import create_app
from src.config.testing import TestingConfig


@pytest.fixture(scope="session")
def app():
    app = create_app(TestingConfig)
    return app


@pytest.fixture(scope="function", autouse=True)
def setup_db(app):
    """Ensure test database is reset and mappers configured for each test"""
    clear_mappers()

    with app.app_context():
        db.drop_all()
        db.create_all()

        # Import models after db is reinitialized
        from src.models.client import Client
        from src.models.oauth import OAuthCredential

        configure_mappers()

        # Insert test client
        test_client = Client(name="Test Client")
        db.session.add(test_client)
        db.session.commit()

        yield
