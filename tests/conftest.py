# sets up pytest fixtures that:Create a temporary Flask app for testing, Give you a fake browser (test client) to make requests, Automatically clean up the database after each test
#2022

import pytest
from website import create_test_app, drop_database

@pytest.fixture()
def app():
    app = create_test_app()
    app.config.update({
        "TESTING": True,
    })

    yield app

    drop_database(app)

@pytest.fixture()
def client(app):
    return app.test_client()