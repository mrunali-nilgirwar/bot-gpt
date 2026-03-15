from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# -----------------------------------------------
# TEST 1 - Check app is running
# -----------------------------------------------
def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "BOT GPT is running!"}


# -----------------------------------------------
# TEST 2 - Create a user
# -----------------------------------------------
def test_create_user():
    response = client.post("/users", json={
        "name": "Test User",
        "email": "testuser123@test.com"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test User"
    assert data["email"] == "testuser123@test.com"
    assert "id" in data


# -----------------------------------------------
# TEST 3 - Duplicate email should fail
# -----------------------------------------------
def test_duplicate_email():
    # First create a user
    client.post("/users", json={
        "name": "Duplicate User",
        "email": "duplicate@test.com"
    })
    # Try to create same email again
    response = client.post("/users", json={
        "name": "Duplicate User",
        "email": "duplicate@test.com"
    })
    assert response.status_code == 400


# -----------------------------------------------
# TEST 4 - List conversations for non existent user
# -----------------------------------------------
def test_list_conversations_empty():
    response = client.get("/conversations?user_id=9999")
    assert response.status_code == 200
    assert response.json() == []


# -----------------------------------------------
# TEST 5 - Get non existent conversation
# -----------------------------------------------
def test_get_conversation_not_found():
    response = client.get("/conversations/9999")
    assert response.status_code == 404
