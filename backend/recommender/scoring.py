from typing import Dict, Any, List, Tuple, Optional

# Baseline weights documented in ARCHITECTURE.md
WEIGHT_CUISINE = 0.20
WEIGHT_INGREDIENT = 0.20
WEIGHT_DIET = 0.20
WEIGHT_BUDGET = 0.15
WEIGHT_SPICE = 0.10
WEIGHT_HEALTH = 0.10
WEIGHT_FEEDBACK = 0.05

assert round(
    WEIGHT_CUISINE + WEIGHT_INGREDIENT + WEIGHT_DIET +
    WEIGHT_BUDGET + WEIGHT_SPICE + WEIGHT_HEALTH + WEIGHT_FEEDBACK,
    5
) == 1.0, "Weights must sum to 1.0"

def score_dish(
    user_profile: Dict[str, Any],
    dish: Dict[str, Any],
    user_feedbacks: Optional[Dict[str, Dict[str, Any]]] = None
) -> Tuple[int, List[str]]:
    """
    Computes a deterministic match score (0-100) and rule-derived bullet reasons.
    user_feedbacks is a mapping of dish_id -> {"rating": int, "liked": bool}.
    """
    match_reasons = []

    # 1. Cuisine Match (0.20)
    user_cuisines = [c.strip().lower() for c in user_profile.get("favorite_cuisines") or []]
    dish_cuisine = (dish.get("cuisine") or "").strip().lower()
    if user_cuisines:
        if dish_cuisine and dish_cuisine in user_cuisines:
            s_cuisine = 1.0
            raw_cuisine = dish.get("cuisine")
            match_reasons.append(f"Matches {raw_cuisine} favorite cuisine")
        else:
            s_cuisine = 0.0
    else:
        s_cuisine = 0.5

    # 2. Ingredient Preference (0.20)
    user_ingredients = [i.strip().lower() for i in user_profile.get("favorite_ingredients") or []]
    dish_ingredients = [i.strip().lower() for i in dish.get("ingredients") or []]
    matched_ingredients = []
    if user_ingredients:
        for u_ing in user_ingredients:
            if any(u_ing in d_ing for d_ing in dish_ingredients):
                matched_ingredients.append(u_ing)
        if matched_ingredients:
            s_ingredient = min(1.0, len(matched_ingredients) / len(user_ingredients))
            capitalized_ing = ", ".join(ing.capitalize() for ing in matched_ingredients)
            match_reasons.append(f"Contains {capitalized_ing}, a favorite ingredient")
        else:
            s_ingredient = 0.0
    else:
        s_ingredient = 0.5

    # 3. Diet Compatibility (0.20)
    user_diets = [d.strip().lower() for d in user_profile.get("dietary_preferences") or []]
    dish_diet = (dish.get("diet_type") or "").strip().lower()
    if user_diets:
        if any(d in dish_diet for d in user_diets) or ("vegetarian" in user_diets and dish_diet in ["vegan", "vegetarian"]):
            s_diet = 1.0
            diet_name = user_diets[0].capitalize()
            match_reasons.append(f"Matches {diet_name} dietary preference")
        else:
            s_diet = 0.5
    else:
        s_diet = 0.5

    # 4. Budget Match (0.15)
    budget = float(user_profile.get("budget", 0.0))
    price = float(dish.get("price", 0.0))
    if budget > 0:
        if price <= budget:
            s_budget = 1.0
            match_reasons.append(f"Within budget (₹{int(price) if price.is_integer() else price} / ₹{int(budget) if budget.is_integer() else budget})")
        else:
            # Over budget decay
            decay = (price - budget) / budget
            s_budget = max(0.0, 1.0 - decay)
    else:
        s_budget = 1.0 if price == 0 else 0.5

    # 5. Spice Tolerance (0.10)
    user_spice = int(user_profile.get("spice_tolerance", 3))
    dish_spice = int(dish.get("spice_level", 1))
    diff = abs(dish_spice - user_spice)
    s_spice = max(0.0, min(1.0, 1.0 - (diff / 5.0)))
    if diff == 0:
        match_reasons.append(f"Matches preferred spice level (Level {dish_spice})")
    elif diff <= 1:
        match_reasons.append(f"Close to preferred spice level (Level {dish_spice})")

    # 6. Health Goal Match (0.10)
    user_goal = (user_profile.get("health_goal") or "").strip().lower()
    dish_tags = [t.strip().lower() for t in dish.get("health_tags") or []]
    if user_goal:
        if user_goal in dish_tags:
            s_health = 1.0
            match_reasons.append(f"Includes {user_goal} health tag")
        else:
            s_health = 0.0
    else:
        s_health = 0.5

    # 7. Historical Feedback (0.05)
    dish_id = dish.get("id") or dish.get("dish_id")
    feedback_record = (user_feedbacks or {}).get(dish_id)
    if feedback_record:
        rating = feedback_record.get("rating", 3)
        # 1 -> 0.0, 2 -> 0.25, 3 -> 0.5, 4 -> 0.75, 5 -> 1.0
        s_feedback = max(0.0, min(1.0, (rating - 1) / 4.0))
        if rating >= 4:
            match_reasons.append(f"Previously rated {rating} stars by you")
    else:
        s_feedback = 0.5  # Neutral when no prior interaction

    # Total weighted sum
    raw_score = (
        (WEIGHT_CUISINE * s_cuisine) +
        (WEIGHT_INGREDIENT * s_ingredient) +
        (WEIGHT_DIET * s_diet) +
        (WEIGHT_BUDGET * s_budget) +
        (WEIGHT_SPICE * s_spice) +
        (WEIGHT_HEALTH * s_health) +
        (WEIGHT_FEEDBACK * s_feedback)
    )

    score_percentage = int(round(raw_score * 100))
    # Constrain to 0-100
    score_percentage = max(0, min(100, score_percentage))

    return score_percentage, match_reasons
