def test_create_manual_menu_success(client):
    payload = {
        "restaurant_name": "Spice Bistro",
        "dishes": [
            {
                "name": "Paneer Tikka",
                "description": "Char-grilled cottage cheese marinated in aromatic Indian spices",
                "price": 280.0,
                "cuisine": "Indian",
                "ingredients": ["paneer", "yogurt", "bell pepper", "spices"],
                "diet_type": "vegetarian",
                "spice_level": 3,
                "health_tags": ["high_protein"],
            },
            {
                "name": "Peanut Satay Skewers",
                "description": "Grilled skewers with rich spicy peanut dip sauce",
                "price": 320.0,
                "cuisine": "Thai",
                "ingredients": ["tofu", "peanuts", "soy sauce", "chili"],
                "diet_type": "vegan",
                "spice_level": 4,
                "health_tags": ["high_protein"],
            },
        ],
    }
    response = client.post("/api/v1/menu/manual", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["restaurant_name"] == "Spice Bistro"
    assert data["total_dishes_added"] == 2
    assert data["menu_id"].startswith("m-")
    assert len(data["dishes"]) == 2
    assert data["dishes"][0]["name"] == "Paneer Tikka"
    assert data["dishes"][0]["id"].startswith("d-")
    assert data["dishes"][1]["name"] == "Peanut Satay Skewers"
    assert data["dishes"][1]["id"].startswith("d-")

    # Verify retrieval
    menu_id = data["menu_id"]
    get_res = client.get(f"/api/v1/menu/{menu_id}")
    assert get_res.status_code == 200
    menu_data = get_res.json()
    assert menu_data["menu_id"] == menu_id
    assert menu_data["total_dishes"] == 2
    assert len(menu_data["dishes"]) == 2

def test_get_nonexistent_menu(client):
    response = client.get("/api/v1/menu/m-nonexistent")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "RESOURCE_NOT_FOUND"

def test_create_menu_invalid_dish_price(client):
    payload = {
        "restaurant_name": "Invalid Price Bistro",
        "dishes": [
            {
                "name": "Free Dish Error",
                "price": -10.0,
                "spice_level": 1,
            }
        ],
    }
    response = client.post("/api/v1/menu/manual", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"
