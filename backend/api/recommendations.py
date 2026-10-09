from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.models.user import User
from backend.models.menu import Menu
from backend.models.feedback import Feedback
from backend.schemas.recommendation import RecommendationRequest, RecommendationResponse
from backend.recommender.recommender import rank_menu

router = APIRouter(prefix="/recommendations", tags=["Recommendation & Ranking"])

@router.post("/rank", response_model=RecommendationResponse, status_code=status.HTTP_200_OK)
def rank_recommendations(
    req: RecommendationRequest,
    db: Session = Depends(get_db)
):
    """Ranks menu dishes for a user profile, applying hard safety filters and calculating weighted match scores."""
    user = db.query(User).filter(User.id == req.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User profile with ID '{req.user_id}' was not found.",
        )

    menu = db.query(Menu).filter(Menu.id == req.menu_id).first()
    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Menu with ID '{req.menu_id}' was not found.",
        )

    # Fetch any historical feedback from this user
    feedbacks = db.query(Feedback).filter(Feedback.user_id == req.user_id).all()
    user_feedbacks = {
        fb.dish_id: {"rating": fb.rating, "liked": fb.liked}
        for fb in feedbacks
    }

    # Prepare user profile dict
    user_dict = {
        "id": user.id,
        "name": user.name,
        "budget": user.budget,
        "spice_tolerance": user.spice_tolerance,
        "health_goal": user.health_goal,
        "dietary_preferences": [p.diet for p in user.dietary_preferences],
        "allergies": [a.allergen for a in user.allergies],
        "favorite_cuisines": [c.cuisine for c in user.favorite_cuisines],
        "favorite_ingredients": [i.ingredient for i in user.favorite_ingredients],
    }

    # Prepare dishes list
    dishes_list = []
    for dish in menu.dishes:
        dishes_list.append({
            "id": dish.id,
            "name": dish.name,
            "description": dish.description,
            "price": dish.price,
            "cuisine": dish.cuisine,
            "ingredients": dish.ingredients or [],
            "diet_type": dish.diet_type,
            "spice_level": dish.spice_level,
            "health_tags": dish.health_tags or [],
        })

    ranking_result = rank_menu(
        user_profile=user_dict,
        dishes=dishes_list,
        user_feedbacks=user_feedbacks
    )

    return RecommendationResponse(
        user_id=ranking_result["user_id"],
        recommended_dishes=ranking_result["recommended_dishes"],
        filtered_dishes=ranking_result["filtered_dishes"],
        all_dishes=ranking_result["all_dishes"],
    )
