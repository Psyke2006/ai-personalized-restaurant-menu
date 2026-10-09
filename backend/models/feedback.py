import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database.connection import Base

def generate_feedback_id() -> str:
    return f"f-{uuid.uuid4()}"

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(String, primary_key=True, default=generate_feedback_id)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    dish_id = Column(String, ForeignKey("dishes.id", ondelete="CASCADE"), nullable=False)
    liked = Column(Boolean, nullable=False, default=True)
    rating = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="feedbacks")
    dish = relationship("Dish", back_populates="feedbacks")
