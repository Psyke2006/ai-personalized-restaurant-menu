import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database.connection import Base

def generate_user_id() -> str:
    return f"u-{uuid.uuid4()}"

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_user_id)
    name = Column(String, nullable=False)
    budget = Column(Float, nullable=False, default=0.0)
    spice_tolerance = Column(Integer, nullable=False, default=3)
    health_goal = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    dietary_preferences = relationship(
        "DietaryPreference", back_populates="user", cascade="all, delete-orphan", lazy="joined", order_by="DietaryPreference.id"
    )
    allergies = relationship(
        "Allergy", back_populates="user", cascade="all, delete-orphan", lazy="joined", order_by="Allergy.id"
    )
    favorite_cuisines = relationship(
        "FavoriteCuisine", back_populates="user", cascade="all, delete-orphan", lazy="joined", order_by="FavoriteCuisine.id"
    )
    favorite_ingredients = relationship(
        "FavoriteIngredient", back_populates="user", cascade="all, delete-orphan", lazy="joined", order_by="FavoriteIngredient.id"
    )
    feedbacks = relationship(
        "Feedback", back_populates="user", cascade="all, delete-orphan"
    )

class DietaryPreference(Base):
    __tablename__ = "dietary_preferences"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    diet = Column(String, nullable=False)

    user = relationship("User", back_populates="dietary_preferences")

class Allergy(Base):
    __tablename__ = "allergies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    allergen = Column(String, nullable=False)

    user = relationship("User", back_populates="allergies")

class FavoriteCuisine(Base):
    __tablename__ = "favorite_cuisines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    cuisine = Column(String, nullable=False)

    user = relationship("User", back_populates="favorite_cuisines")

class FavoriteIngredient(Base):
    __tablename__ = "favorite_ingredients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    ingredient = Column(String, nullable=False)

    user = relationship("User", back_populates="favorite_ingredients")
