from backend.recommender.filtering import filter_dishes, matches_term
from backend.recommender.scoring import score_dish, WEIGHT_CUISINE, WEIGHT_INGREDIENT, WEIGHT_DIET, WEIGHT_BUDGET, WEIGHT_SPICE, WEIGHT_HEALTH, WEIGHT_FEEDBACK
from backend.recommender.recommender import rank_menu

def test_weights_sum_to_one():
    total = (
        WEIGHT_CUISINE + WEIGHT_INGREDIENT + WEIGHT_DIET +
        WEIGHT_BUDGET + WEIGHT_SPICE + WEIGHT_HEALTH + WEIGHT_FEEDBACK
    )
    assert round(total, 5) == 1.0

def test_token_aware_allergen_matching():
    # "nut" should not match "minute" or "donut" if not a word boundary
    assert not matches_term("nut", "10 minute steak")
    assert matches_term("nut", "crushed mixed nut topping")
    assert matches_term("peanuts", "crunchy peanut butter")

def test_allergen_filtering_with_aliases():
    dishes = [
        {"id": "d-1", "name": "Peanut Satay", "ingredients": ["tofu", "groundnuts", "chili"], "diet_type": "vegan", "price": 300},
        {"id": "d-2", "name": "Paneer Tikka", "ingredients": ["paneer", "yogurt", "capsicum"], "diet_type": "vegetarian", "price": 250},
    ]
    compatible, filtered = filter_dishes(
        user_allergies=["peanuts"],
        user_diets=[],
        dishes=dishes
    )
    assert len(compatible) == 1
    assert compatible[0]["id"] == "d-2"
    assert len(filtered) == 1
    assert filtered[0]["id"] == "d-1"
    assert any("groundnuts" in r.lower() or "peanut" in r.lower() for r in filtered[0]["exclusion_reasons"])

def test_strict_dietary_filtering():
    dishes = [
        {"id": "d-1", "name": "Chicken Curry", "ingredients": ["chicken", "curry sauce"], "diet_type": "non-vegetarian", "price": 350},
        {"id": "d-2", "name": "Dal Tadka", "ingredients": ["lentils", "spices", "ghee"], "diet_type": "vegetarian", "price": 180},
    ]
    compatible, filtered = filter_dishes(
        user_allergies=[],
        user_diets=["vegetarian"],
        dishes=dishes
    )
    assert len(compatible) == 1
    assert compatible[0]["id"] == "d-2"
    assert len(filtered) == 1
    assert filtered[0]["id"] == "d-1"
    assert "vegetarian" in filtered[0]["exclusion_reasons"][0].lower()

def test_uncertainty_handling_for_missing_ingredients():
    dishes = [
        {"id": "d-unknown", "name": "Mystery Soup", "ingredients": [], "diet_type": "vegetarian", "price": 150}
    ]
    # User has allergy, but dish has NO ingredient metadata
    compatible, filtered = filter_dishes(
        user_allergies=["shellfish"],
        user_diets=[],
        dishes=dishes
    )
    assert len(compatible) == 0
    assert len(filtered) == 1
    assert filtered[0]["compatibility_status"] == "NEEDS_VERIFICATION"
    assert "uncertainty warning" in filtered[0]["exclusion_reasons"][0].lower()

def test_scoring_determinism_and_bounds():
    user = {
        "budget": 300.0,
        "spice_tolerance": 3,
        "health_goal": "high_protein",
        "dietary_preferences": ["vegetarian"],
        "allergies": [],
        "favorite_cuisines": ["Indian"],
        "favorite_ingredients": ["paneer"],
    }
    dish = {
        "id": "d-10",
        "name": "Paneer Bhurji",
        "price": 280.0,
        "cuisine": "Indian",
        "ingredients": ["paneer", "onion", "tomato"],
        "diet_type": "vegetarian",
        "spice_level": 3,
        "health_tags": ["high_protein"],
    }
    score1, reasons1 = score_dish(user, dish)
    score2, reasons2 = score_dish(user, dish)

    assert score1 == score2
    assert 0 <= score1 <= 100
    assert score1 >= 85
    assert len(reasons1) > 0

def test_budget_decay():
    user = {"budget": 100.0, "spice_tolerance": 3, "dietary_preferences": []}
    within_budget_dish = {"id": "d-1", "price": 100.0, "spice_level": 3}
    over_budget_dish = {"id": "d-2", "price": 200.0, "spice_level": 3}

    score_within, _ = score_dish(user, within_budget_dish)
    score_over, _ = score_dish(user, over_budget_dish)

    assert score_within > score_over

def test_rank_menu_preserves_full_menu():
    user = {
        "id": "u-test",
        "allergies": ["peanuts"],
        "dietary_preferences": ["vegetarian"],
        "budget": 500.0,
        "spice_tolerance": 3,
    }
    dishes = [
        {"id": "d-1", "name": "Paneer Tikka", "price": 280.0, "ingredients": ["paneer", "capsicum"], "diet_type": "vegetarian", "spice_level": 3},
        {"id": "d-2", "name": "Peanut Chaat", "price": 120.0, "ingredients": ["peanuts", "onion"], "diet_type": "vegetarian", "spice_level": 2},
        {"id": "d-3", "name": "Chicken Tikka", "price": 320.0, "ingredients": ["chicken"], "diet_type": "non-vegetarian", "spice_level": 4},
        {"id": "d-4", "name": "Aloo Gobi", "price": 180.0, "ingredients": ["potato", "cauliflower"], "diet_type": "vegetarian", "spice_level": 3},
    ]

    result = rank_menu(user, dishes)
    assert len(result["recommended_dishes"]) == 2  # Paneer Tikka, Aloo Gobi
    assert len(result["filtered_dishes"]) == 2     # Peanut Chaat (peanut), Chicken Tikka (non-veg)
    assert len(result["all_dishes"]) == 4          # Full menu preserved

    # Recommended dishes sorted by score descending
    assert result["recommended_dishes"][0]["match_score"] >= result["recommended_dishes"][1]["match_score"]

def test_recommendation_rank_api(client):
    # 1. Create a user
    user_payload = {
        "name": "Tanishkk Pachpute",
        "budget": 500.0,
        "spice_tolerance": 3,
        "health_goal": "high_protein",
        "dietary_preferences": ["vegetarian"],
        "allergies": ["peanuts", "tree nuts"],
        "favorite_cuisines": ["Indian"],
        "favorite_ingredients": ["paneer"],
    }
    u_res = client.post("/api/v1/users/profile", json=user_payload)
    assert u_res.status_code == 201
    user_id = u_res.json()["id"]

    # 2. Create a manual menu
    menu_payload = {
        "restaurant_name": "Spice Bistro",
        "dishes": [
            {
                "name": "Paneer Tikka",
                "description": "Char-grilled cottage cheese",
                "price": 280.0,
                "cuisine": "Indian",
                "ingredients": ["paneer", "yogurt", "bell pepper"],
                "diet_type": "vegetarian",
                "spice_level": 3,
                "health_tags": ["high_protein"],
            },
            {
                "name": "Peanut Satay Skewers",
                "description": "Grilled skewers with peanut sauce",
                "price": 320.0,
                "cuisine": "Thai",
                "ingredients": ["tofu", "peanuts", "soy sauce"],
                "diet_type": "vegan",
                "spice_level": 4,
                "health_tags": ["high_protein"],
            },
        ],
    }
    m_res = client.post("/api/v1/menu/manual", json=menu_payload)
    assert m_res.status_code == 201
    menu_id = m_res.json()["menu_id"]

    # 3. Call rank endpoint
    rank_res = client.post("/api/v1/recommendations/rank", json={"user_id": user_id, "menu_id": menu_id})
    assert rank_res.status_code == 200
    rank_data = rank_res.json()

    assert rank_data["user_id"] == user_id
    assert len(rank_data["recommended_dishes"]) == 1
    assert rank_data["recommended_dishes"][0]["name"] == "Paneer Tikka"
    assert rank_data["recommended_dishes"][0]["compatibility_status"] == "COMPATIBLE"
    assert rank_data["recommended_dishes"][0]["match_score"] > 80
    assert len(rank_data["recommended_dishes"][0]["match_reasons"]) > 0

    assert len(rank_data["filtered_dishes"]) == 1
    assert rank_data["filtered_dishes"][0]["name"] == "Peanut Satay Skewers"
    assert rank_data["filtered_dishes"][0]["compatibility_status"] == "FILTERED"
    assert len(rank_data["filtered_dishes"][0]["exclusion_reasons"]) > 0

    assert len(rank_data["all_dishes"]) == 2

def test_recommendation_rank_unknown_entities(client):
    res = client.post("/api/v1/recommendations/rank", json={"user_id": "u-unknown", "menu_id": "m-unknown"})
    assert res.status_code == 404
    data = res.json()
    assert data["error"]["code"] == "RESOURCE_NOT_FOUND"
