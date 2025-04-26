# tests/user/test_auth.py
import pytest

register_url = "/auth/register"
login_url = "/auth/token"
me_url = "/auth/me"


@pytest.mark.asyncio
async def test_register_and_login(client):
    data = {"email": "newuser@example.com", "password": "StrongPass123"}
    
    # Register
    response = client.post(register_url, json=data)
    assert response.status_code == 201
    assert response.json()["email"] == data["email"]
    
    # Login
    login_data = {
        "username": data["email"],
        "password": data["password"]
    }
    response = client.post(login_url, data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert token is not None
    
    # Test protected endpoint
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(me_url, headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == data["email"]