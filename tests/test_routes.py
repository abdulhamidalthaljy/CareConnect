import pytest
from src.app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome to CareConnect' in response.data

def test_login(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data

def test_register(client):
    response = client.get('/register')
    assert response.status_code == 200
    assert b'Register' in response.data

def test_dashboard(client):
    # Assuming user is logged in, this would require a login fixture or mock
    response = client.get('/dashboard')
    assert response.status_code == 302  # Redirect if not logged in
    # Further tests would require user authentication setup

def test_logout(client):
    response = client.get('/logout')
    assert response.status_code == 302  # Redirect after logout
    # Further tests would require user authentication setup