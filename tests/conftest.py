"""
Module/Script Name: conftest.py

Description:
Pytest fixtures for Flask app and test database, properly resetting SQLAlchemy mappings.

Author(s):
Skippy the Code Slayer with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
13-07-2025

Last Modified Date:
14-07-2025

Version:
v1.05

Comments:
- Moved clear_mappers() to post-yield teardown
- Added db.session.remove() and db.drop_all() after yield
"""

import pytest
from sqlalchemy.orm import clear_mappers, configure_mappers

from src.extensions import db
from src.main import create_app
from src.config import TestingConfig
from src.models.client import Client, OAuthCredential  # ✅ Import class directly


@pytest.fixture(scope="session")
def app():
    return create_app(TestingConfig)


@pytest.fixture(scope="function", autouse=True)
def setup_db(app):
    """Ensure test database is reset and mappers configured for each test"""
    with app.app_context():
        db.drop_all()
        db.create_all()
        configure_mappers()

        # ✅ Insert test client
        test_client = Client(name="Test Client", email="test@example.com")
        db.session.add(test_client)
        db.session.commit()

        yield

        # ✅ Teardown
        db.session.remove()
        db.drop_all()
        clear_mappers()
