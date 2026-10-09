from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.models.user import User
from backend.models.menu import Dish
from backend.models.feedback import Feedback
from backend.schemas.feedback import FeedbackCreate, FeedbackResponse

router = APIRouter(prefix="/feedback", tags=["Feedback Loop"])

@router.post("", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def submit_feedback(
    fb_in: FeedbackCreate,
    db: Session = Depends(get_db)
):
    """Submits user feedback (Likes, Dislikes, 1-5 Star Ratings) for a specific dish."""
    # Validate user exists
    user = db.query(User).filter(User.id == fb_in.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User profile with ID '{fb_in.user_id}' was not found.",
        )

    # Validate dish exists
    dish = db.query(Dish).filter(Dish.id == fb_in.dish_id).first()
    if not dish:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dish with ID '{fb_in.dish_id}' was not found.",
        )

    feedback = Feedback(
        user_id=fb_in.user_id,
        dish_id=fb_in.dish_id,
        liked=fb_in.liked,
        rating=fb_in.rating,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)

    return FeedbackResponse(
        feedback_id=feedback.id,
        status="persisted",
        message="Feedback successfully recorded for personalization.",
    )
