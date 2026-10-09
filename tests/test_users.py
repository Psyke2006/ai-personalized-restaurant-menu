def test_create_user_profile_success(client):
    payload = {
        "name": "Tanishkk Pachpute",
        "budget": 500.0,
        "spice_tolerance": 3,
        "health_goal": "high_protein",
        "dietary_preferences": ["vegetarian"],
        "allergies": ["peanuts", "tree nuts"],
        "favorite_cuisines": ["Indian", "Italian"],
        "favorite_ingredients": ["paneer", "mushroom"],
    }
    response = client.post("/api/v1/users/profile", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Tanishkk Pachpute"
    assert data["budget"] == 500.0
    assert data["spice_tolerance"] == 3
    assert data["health_goal"] == "high_protein"
    assert data["dietary_preferences"] == ["vegetarian"]
    assert data["allergies"] == ["peanuts", "tree nuts"]
    assert data["favorite_cuisines"] == ["Indian", "Italian"]
    assert data["favorite_ingredients"] == ["paneer", "mushroom"]
    assert data["id"].startswith("u-")

    # Verify retrieval
    get_res = client.get(f"/api/v1/users/{data['id']}")
    assert get_res.status_code == 200
    retrieved = get_res.json()
    assert retrieved["id"] == data["id"]
    assert retrieved["name"] == "Tanishkk Pachpute"

def test_get_nonexistent_user(client):
    response = client.get("/api/v1/users/u-non-existent-user-id")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "RESOURCE_NOT_FOUND"
    assert "not found" in data["error"]["message"].lower()
    assert "timestamp" in data["error"]

def test_create_user_invalid_budget(client):
    payload = {
        "name": "Invalid Budget User",
        "budget": -50.0,
        "spice_tolerance": 3,
    }
    response = client.post("/api/v1/users/profile", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert "timestamp" in data["error"]

def test_create_user_invalid_spice_tolerance(client):
    payload = {
        "name": "Invalid Spice User",
        "budget": 200.0,
        "spice_tolerance": 6,
    }
    response = client.post("/api/v1/users/profile", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"
