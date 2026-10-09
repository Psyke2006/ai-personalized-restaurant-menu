from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.models.user import (
    User,
    DietaryPreference,
    Allergy,
    FavoriteCuisine,
    FavoriteIngredient,
)
from backend.schemas.user import UserProfileCreate, UserProfileResponse

router = APIRouter(prefix="/users", tags=["User Profile Management"])

def user_to_response(user: User) -> UserProfileResponse:
    return UserProfileResponse(
        id=user.id,
        name=user.name,
        budget=user.budget,
        spice_tolerance=user.spice_tolerance,
        health_goal=user.health_goal,
        dietary_preferences=[p.diet for p in user.dietary_preferences],
        allergies=[a.allergen for a in user.allergies],
        favorite_cuisines=[c.cuisine for c in user.favorite_cuisines],
        favorite_ingredients=[i.ingredient for i in user.favorite_ingredients],
        created_at=user.created_at.isoformat() if user.created_at else None,
    )

@router.post("/profile", response_model=UserProfileResponse, status_code=status.HTTP_201_CREATED)
def create_or_update_user_profile(
    profile_in: UserProfileCreate,
    db: Session = Depends(get_db)
):
    """Creates or updates a user's dietary profile, preferences, and safety constraints."""
    user = User(
        name=profile_in.name,
        budget=profile_in.budget,
        spice_tolerance=profile_in.spice_tolerance,
        health_goal=profile_in.health_goal,
    )
    db.add(user)
    db.flush()

    for diet in profile_in.dietary_preferences:
        db.add(DietaryPreference(user_id=user.id, diet=diet))

    for allergen in profile_in.allergies:
        db.add(Allergy(user_id=user.id, allergen=allergen))

    for cuisine in profile_in.favorite_cuisines:
        db.add(FavoriteCuisine(user_id=user.id, cuisine=cuisine))

    for ingredient in profile_in.favorite_ingredients:
        db.add(FavoriteIngredient(user_id=user.id, ingredient=ingredient))

    db.commit()
    db.refresh(user)

    return user_to_response(user)

@router.get("/{user_id}", response_model=UserProfileResponse, status_code=status.HTTP_200_OK)
def get_user_profile(user_id: str, db: Session = Depends(get_db)):
    """Retrieves user profile details by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User profile with ID '{user_id}' was not found.",
        )
    return user_to_response(user)
