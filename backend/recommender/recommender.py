from typing import Dict, Any, List, Optional
from backend.recommender.filtering import filter_dishes
from backend.recommender.scoring import score_dish

def rank_menu(
    user_profile: Dict[str, Any],
    dishes: List[Dict[str, Any]],
    user_feedbacks: Optional[Dict[str, Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Executes the recommendation pipeline:
    1. Deterministic hard allergy and dietary filtering
    2. Weighted preference scoring of eligible dishes
    3. Stable tie-breaker sorting
    4. Deterministic explanation generation
    5. Preserves all dishes for complete menu presentation
    """
    user_allergies = user_profile.get("allergies") or []
    user_diets = user_profile.get("dietary_preferences") or []

    compatible_dishes, filtered_dishes = filter_dishes(
        user_allergies=user_allergies,
        user_diets=user_diets,
        dishes=dishes
    )

    recommended = []
    for dish in compatible_dishes:
        score, reasons = score_dish(
            user_profile=user_profile,
            dish=dish,
            user_feedbacks=user_feedbacks
        )
        rec_item = {
            "dish_id": dish.get("id"),
            "name": dish.get("name"),
            "price": dish.get("price"),
            "cuisine": dish.get("cuisine"),
            "match_score": score,
            "compatibility_status": dish.get("compatibility_status", "COMPATIBLE"),
            "match_reasons": reasons,
        }
        recommended.append(rec_item)

    # Deterministic tie-breaking sort:
    # 1. match_score (descending)
    # 2. price (ascending)
    # 3. name (ascending)
    # 4. dish_id (ascending)
    recommended.sort(
        key=lambda d: (-d["match_score"], d["price"], d["name"] or "", d["dish_id"] or "")
    )

    filtered_output = []
    for dish in filtered_dishes:
        filt_item = {
            "dish_id": dish.get("id"),
            "name": dish.get("name"),
            "price": dish.get("price"),
            "compatibility_status": dish.get("compatibility_status", "FILTERED"),
            "exclusion_reasons": dish.get("exclusion_reasons", []),
        }
        filtered_output.append(filt_item)

    filtered_output.sort(
        key=lambda d: (d["name"] or "", d["dish_id"] or "")
    )

    # Complete menu list preserving all items
    all_dishes_output = []
    for r in recommended:
        all_dishes_output.append({
            "dish_id": r["dish_id"],
            "name": r["name"],
            "price": r["price"],
            "cuisine": r.get("cuisine"),
            "compatibility_status": r["compatibility_status"],
            "match_score": r["match_score"],
            "match_reasons": r["match_reasons"],
            "exclusion_reasons": [],
        })
    for f in filtered_output:
        all_dishes_output.append({
            "dish_id": f["dish_id"],
            "name": f["name"],
            "price": f["price"],
            "cuisine": None,
            "compatibility_status": f["compatibility_status"],
            "match_score": None,
            "match_reasons": [],
            "exclusion_reasons": f["exclusion_reasons"],
        })

    return {
        "user_id": user_profile.get("id"),
        "recommended_dishes": recommended,
        "filtered_dishes": filtered_output,
        "all_dishes": all_dishes_output,
    }
