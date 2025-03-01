import pytest
from app import create_app
from app.extensions import mongo
from flask import json
from bson import ObjectId

@pytest.fixture
def client():
    """Setup test client and configure in-memory database."""
    app = create_app()
    app.config["TESTING"] = True
    app.config["MONGO_URI"] = "mongodb+srv://naveen:dbpasscode@cluster0.faokq.mongodb.net/testdata?retryWrites=true&w=majority&appName=Cluster0"  # Use a test DB
    
    with app.test_client() as client:
        with app.app_context():
            # Clear test database before each test
            mongo.db.users.delete_many({})
        yield client  # Return test client

def test_get_users_empty(client):
    """Test GET /api/users when no users exist."""
    response = client.get("/api/users")
    assert response.status_code == 200
    assert response.json == []  # Expecting empty list

def test_create_user(client):
    """Test POST /api/users to create a new user."""
    new_user = {"username": "testuser", "email": "test@example.com"}
    response = client.post("/api/users", json=new_user)
    
    assert response.status_code == 201
    assert "id" in response.json  # MongoDB ObjectId should be returned
    assert response.json["username"] == new_user["username"]
    assert response.json["email"] == new_user["email"]

def test_get_users_non_empty(client):
    """Test GET /api/users after creating a user."""
    mongo.db.users.insert_one({"username": "john_doe", "email": "john@example.com"})
    
    response = client.get("/api/users")
    assert response.status_code == 200
    assert len(response.json) == 1  # Expecting one user
    assert response.json[0]["username"] == "john_doe"

def test_get_user_by_id(client):
    """Test GET /api/users/<id> to fetch a single user."""
    user_id = mongo.db.users.insert_one({"username": "alice", "email": "alice@example.com"}).inserted_id

    response = client.get(f"/api/users/{user_id}")
    assert response.status_code == 200
    assert response.json["username"] == "alice"

def test_get_user_not_found(client):
    """Test GET /api/users/<id> for a non-existing user."""
    fake_id = ObjectId()
    response = client.get(f"/api/users/{fake_id}")
    assert response.status_code == 404
    assert response.json == {"error": "User not found"}
