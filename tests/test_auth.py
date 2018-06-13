import pytest
from flask import g, session
from flaskr.db import get_db

def test_register(client, app):
    # client.get() makes a request to the uri+extension and returns the response
    # object. So if the status_code returns 200, the test continues.
    assert client.get('/auth/register').status_code == 200
    # request is made to register. Assuming it succeeds we then confirm we've
    # been redirected by checking our current location.
    response = client.post(
        '/auth/register', data={'username': 'a', 'password': 'a'}
    )
    assert 'http://localhost/auth/login' == response.headers['Location']

    with app.app_context():
        assert get_db().execute(
            "select * from user where username = 'a'",
        ).fetchone() is not None

# Tells Pytest to run the test with these values. We convert message to bytes
# because response.data.message is in bytes.
@pytest.mark.parametrize(('username', 'password', 'message'), (
    (''    , ''    , b'Username is required.'),
    ('a'   , ''    , b'Password is required.'),
    ('test', 'test', b'already registered'   ),
))
def test_register_validate_input(client, username, password, message):
    response = client.post(
        '/auth/register',
        data={'username': username, 'password': password}
    )
    # response.data contains the response body in bytes. Bytes must be compared
    # to bytes, so to make it into unicode, use get_data(as_text=True).
    assert message in response.data

def test_login(client, auth):
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    assert response.headers['Location'] == 'http://localhost/'
    
    # Using client in a 'with' block gives access to context variables like
    # 'session' once the response is returned. This would give errors usually.
    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user['username'] == 'test'

@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a'   , 'test', b'Incorrect username.'),
    ('test', 'a'   , b'Incorrect password.'),
))
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data

def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session