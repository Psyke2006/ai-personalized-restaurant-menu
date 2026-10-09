import pytest
from fastapi.testclient import TestClient
from backend.main import app

def test_complete_e2e_journey():
    client = TestClient(app)

    # 1. System Health
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    health = res.json()
    assert health["status"] == "healthy"
    assert health["version"] == "1.0.0"
    assert health["recommender_engine"] == "active"

    # 2. Create User Profile
    user_payload = {
        "name": "Integration Test Diner",
        "budget": 500.0,
        "spice_tolerance": 3,
        "health_goal": "high_protein",
        "dietary_preferences": ["vegetarian"],
        "allergies": ["peanuts"],
        "favorite_cuisines": ["Indian", "Italian"],
        "favorite_ingredients": ["paneer", "mushroom"],
    }
    res = client.post("/api/v1/users/profile", json=user_payload)
    assert res.status_code == 201
    user = res.json()
    user_id = user["id"]
    assert user_id.startswith("u-")
    assert user["name"] == "Integration Test Diner"

    # 3. Retrieve User Profile
    res = client.get(f"/api/v1/users/{user_id}")
    assert res.status_code == 200
    retrieved_user = res.json()
    assert retrieved_user["id"] == user_id
    assert retrieved_user["budget"] == 500.0

    # 4. Ingest Menu Manually
    menu_payload = {
        "restaurant_name": "Grand Bistro",
        "dishes": [
            {
                "name": "Paneer Tikka",
                "description": "Grilled cottage cheese with aromatic spices",
                "price": 280.0,
                "cuisine": "Indian",
                "ingredients": ["paneer", "yogurt", "bell pepper", "spices"],
                "diet_type": "vegetarian",
                "spice_level": 3,
                "health_tags": ["high_protein"],
            },
            {
                "name": "Peanut Satay Skewers",
                "description": "Grilled tofu with peanut sauce",
                "price": 320.0,
                "cuisine": "Thai",
                "ingredients": ["tofu", "peanuts", "chili"],
                "diet_type": "vegan",
                "spice_level": 4,
                "health_tags": ["high_protein"],
            },
            {
                "name": "Chicken Biryani",
                "description": "Spiced chicken and rice",
                "price": 400.0,
                "cuisine": "Indian",
                "ingredients": ["chicken", "rice", "spices"],
                "diet_type": "non-vegetarian",
                "spice_level": 3,
                "health_tags": ["high_protein"],
            },
            {
                "name": "Mushroom Risotto",
                "description": "Arborio rice with wild mushrooms",
                "price": 450.0,
                "cuisine": "Italian",
                "ingredients": ["rice", "mushroom", "parmesan"],
                "diet_type": "vegetarian",
                "spice_level": 1,
                "health_tags": ["low_calorie"],
            },
        ],
    }
    res = client.post("/api/v1/menu/manual", json=menu_payload)
    assert res.status_code == 201
    menu = res.json()
    menu_id = menu["menu_id"]
    assert menu_id.startswith("m-")
    assert menu["total_dishes_added"] == 4
    assert len(menu["dishes"]) == 4

    dish_map = {d["name"]: d["id"] for d in menu["dishes"]}
    assert all(did.startswith("d-") for did in dish_map.values())

    # 5. Retrieve Full Original Menu
    res = client.get(f"/api/v1/menu/{menu_id}")
    assert res.status_code == 200
    menu_details = res.json()
    assert menu_details["total_dishes"] == 4
    assert len(menu_details["dishes"]) == 4

    # 6. Request Recommendations and Verify Ranking & Hard Constraints
    res = client.post("/api/v1/recommendations/rank", json={"user_id": user_id, "menu_id": menu_id})
    assert res.status_code == 200
    rank = res.json()

    # Hard constraints verification:
    # 1) Peanut allergy -> Peanut Satay Skewers strictly filtered
    filtered_names = [f["name"] for f in rank["filtered_dishes"]]
    assert "Peanut Satay Skewers" in filtered_names
    peanut_dish = [f for f in rank["filtered_dishes"] if f["name"] == "Peanut Satay Skewers"][0]
    assert peanut_dish["compatibility_status"] == "FILTERED"
    assert any("peanut" in r.lower() for r in peanut_dish["exclusion_reasons"])

    # 2) Vegetarian diet -> Chicken Biryani strictly filtered
    assert "Chicken Biryani" in filtered_names
    chicken_dish = [f for f in rank["filtered_dishes"] if f["name"] == "Chicken Biryani"][0]
    assert chicken_dish["compatibility_status"] == "FILTERED"
    assert any("vegetarian" in r.lower() for r in chicken_dish["exclusion_reasons"])

    # 3) Compatible dishes -> Paneer Tikka and Mushroom Risotto
    rec_names = [r["name"] for r in rank["recommended_dishes"]]
    assert "Paneer Tikka" in rec_names
    assert "Mushroom Risotto" in rec_names

    # 4) Scoring and tie-breaker ordering:
    # Paneer Tikka matches cuisine (Indian), ingredient (paneer), spice (3), budget (280 <= 500), health (high_protein)
    # Must rank #1
    assert rank["recommended_dishes"][0]["name"] == "Paneer Tikka"
    score_before = rank["recommended_dishes"][0]["match_score"]
    assert 0 <= score_before <= 100

    # 5) Full menu integrity:
    assert len(rank["all_dishes"]) == 4

    # 7. Submit Feedback for Paneer Tikka
    paneer_dish_id = dish_map["Paneer Tikka"]
    fb_payload = {
        "user_id": user_id,
        "dish_id": paneer_dish_id,
        "liked": True,
        "rating": 5,
    }
    res = client.post("/api/v1/feedback", json=fb_payload)
    assert res.status_code == 201
    fb = res.json()
    assert fb["feedback_id"].startswith("f-")
    assert fb["status"] == "persisted"

    # 8. Re-rank and verify feedback persistence & score influence
    res = client.post("/api/v1/recommendations/rank", json={"user_id": user_id, "menu_id": menu_id})
    assert res.status_code == 200
    rank_after = res.json()
    paneer_rec = [r for r in rank_after["recommended_dishes"] if r["name"] == "Paneer Tikka"][0]
    assert any("5 stars" in r for r in paneer_rec["match_reasons"])
    assert paneer_rec["match_score"] >= score_before

    # 9. Verify Error Handling
    # Unknown user
    res = client.get("/api/v1/users/u-non-existent")
    assert res.status_code == 404
    assert res.json()["error"]["code"] == "RESOURCE_NOT_FOUND"

    # Unknown menu
    res = client.get("/api/v1/menu/m-non-existent")
    assert res.status_code == 404
    assert res.json()["error"]["code"] == "RESOURCE_NOT_FOUND"

    # Invalid feedback rating
    res = client.post("/api/v1/feedback", json={"user_id": user_id, "dish_id": paneer_dish_id, "liked": True, "rating": 10})
    assert res.status_code == 422
    assert res.json()["error"]["code"] == "VALIDATION_ERROR"
