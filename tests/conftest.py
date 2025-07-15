"""
Module/Script Name: conftest.py

Description:
Pytest fixtures for Flask app and test database, plus test client definition.
Hard-coded sys.path insert for Windows compatibility with src module resolution.

Author(s):
Skippy the Code Slayer with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
13-07-2025

Last Modified Date:
15-07-2025

Version:
v1.08

Comments:
- Hard-coded sys.path.insert for Windows to resolve `src` during pytest execution
"""

import sys
# Add full absolute path to src for Windows pytest compatibility
sys.path.insert(0, r"E:\\projects\\rank_rocket_calendar_stacker\\src")


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
