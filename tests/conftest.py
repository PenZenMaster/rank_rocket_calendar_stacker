"""
Module/Script Name: conftest.py

Description:
Pytest fixtures for Flask app and test database, plus test client definition.

Author(s):
Skippy the Code Slayer with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
13-07-2025

Last Modified Date:
14-07-2025

Version:
v1.06
"""

import pytest
from src.main import create_app
from src.extensions import db


@pytest.fixture(scope="module")
def app():
    app = create_app("src.config.TestingConfig")
    yield app


@pytest.fixture(scope="function", autouse=True)
def setup_db(app):
    with app.app_context():
        db.drop_all()
        db.create_all()

        # Models are loaded via src.models import in main.py

        from src.models.client import Client

        test_client = Client(name="Test Client", email="test@example.com")
        db.session.add(test_client)
        db.session.commit()

        yield

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()
