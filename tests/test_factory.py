from flaskr import create_app

def test_config():
    # Checks to see if we're not doing any tests before running a test.
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing

def test_hello(client):
    response = client.get('/hello')
    assert response.data == b'Hello, World!'