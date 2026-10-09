from pydantic import BaseModel, Field

class FeedbackCreate(BaseModel):
    user_id: str = Field(..., description="ID of the user providing feedback")
    dish_id: str = Field(..., description="ID of the dish being rated")
    liked: bool = Field(..., description="Whether the user liked the dish")
    rating: int = Field(..., ge=1, le=5, description="1 to 5 star rating")

class FeedbackResponse(BaseModel):
    feedback_id: str
    status: str = "persisted"
    message: str = "Feedback successfully recorded for personalization."
