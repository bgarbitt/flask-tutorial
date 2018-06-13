import os
import tempfile

import pytest
from flaskr import create_app
from flaskr.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')

@pytest.fixture
def app():
    # mkstemp() creates a temp file and path. This overrides DATABASE path, so
    # the tests don't overwrite the real database. After the tests, the path is
    # reset to what it was before testing, and the new files are removed.
    db_fd, db_path = tempfile.mkstemp()

    # TESTING tells flask tests are about to go down. Flask reacts by doing some
    # internal stuff. There are other extensions to assist in testing.
    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
    })

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)
    
    yield app

    os.close(db_fd)
    os.unlink(db_path)

# The client fixture calls app.test_client() with the created app in the app
# fixture (above). The client will be used to make requests to the app without
# using the server.
@pytest.fixture
def client(app):
    return app.test_client()

# The runner fixture is like the client fixture, except a runner that is able to
# call Click commands registered by the app.
@pytest.fixture
def runner(app):
    return app.test_cli_runner()

# Pytest uses fixtures by matching their function names with the names of
# arguements in the test functions.

class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')

# By using the auth fixture we can call auth.login() in a test to login as a
# test user, which was done in the app fixture.
@pytest.fixture
def auth(client):
    return AuthActions(client)