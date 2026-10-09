def test_feedback_submission_and_effect_on_ranking(client):
    # 1. Create User
    u_res = client.post("/api/v1/users/profile", json={
        "name": "Foodie User",
        "budget": 500.0,
        "spice_tolerance": 3,
    })
    assert u_res.status_code == 201
    user_id = u_res.json()["id"]

    # 2. Create Menu
    m_res = client.post("/api/v1/menu/manual", json={
        "restaurant_name": "Feedback Cafe",
        "dishes": [
            {
                "name": "Special Pasta",
                "price": 250.0,
                "spice_level": 3,
                "ingredients": ["pasta", "tomato", "cheese"],
                "diet_type": "vegetarian"
            }
        ]
    })
    assert m_res.status_code == 201
    menu_id = m_res.json()["menu_id"]
    dish_id = m_res.json()["dishes"][0]["id"]

    # 3. Check initial ranking score without feedback
    rank1 = client.post("/api/v1/recommendations/rank", json={"user_id": user_id, "menu_id": menu_id}).json()
    score_before = rank1["recommended_dishes"][0]["match_score"]

    # 4. Submit 5-star positive feedback
    fb_res = client.post("/api/v1/feedback", json={
        "user_id": user_id,
        "dish_id": dish_id,
        "liked": True,
        "rating": 5
    })
    assert fb_res.status_code == 201
    fb_data = fb_res.json()
    assert fb_data["feedback_id"].startswith("f-")
    assert fb_data["status"] == "persisted"

    # 5. Check subsequent ranking score with feedback
    rank2 = client.post("/api/v1/recommendations/rank", json={"user_id": user_id, "menu_id": menu_id}).json()
    score_after = rank2["recommended_dishes"][0]["match_score"]

    assert score_after >= score_before
    assert any("rated 5 stars" in r.lower() for r in rank2["recommended_dishes"][0]["match_reasons"])

def test_feedback_nonexistent_user(client):
    # Create menu
    m_res = client.post("/api/v1/menu/manual", json={
        "restaurant_name": "Test Cafe",
        "dishes": [{"name": "Tea", "price": 50.0, "spice_level": 1}]
    })
    dish_id = m_res.json()["dishes"][0]["id"]

    fb_res = client.post("/api/v1/feedback", json={
        "user_id": "u-nonexistent",
        "dish_id": dish_id,
        "liked": True,
        "rating": 5
    })
    assert fb_res.status_code == 404
    assert fb_res.json()["error"]["code"] == "RESOURCE_NOT_FOUND"

def test_feedback_nonexistent_dish(client):
    u_res = client.post("/api/v1/users/profile", json={"name": "Alice", "budget": 100.0, "spice_tolerance": 2})
    user_id = u_res.json()["id"]

    fb_res = client.post("/api/v1/feedback", json={
        "user_id": user_id,
        "dish_id": "d-nonexistent",
        "liked": True,
        "rating": 4
    })
    assert fb_res.status_code == 404
    assert fb_res.json()["error"]["code"] == "RESOURCE_NOT_FOUND"

def test_feedback_invalid_rating(client):
    fb_res = client.post("/api/v1/feedback", json={
        "user_id": "u-test",
        "dish_id": "d-test",
        "liked": True,
        "rating": 6  # Exceeds max rating of 5
    })
    assert fb_res.status_code == 422
    assert fb_res.json()["error"]["code"] == "VALIDATION_ERROR"
