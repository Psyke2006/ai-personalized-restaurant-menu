import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.database.connection import Base

def generate_menu_id() -> str:
    return f"m-{uuid.uuid4()}"

def generate_dish_id() -> str:
    return f"d-{uuid.uuid4()}"

class Menu(Base):
    __tablename__ = "menus"

    id = Column(String, primary_key=True, default=generate_menu_id)
    restaurant_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    dishes = relationship("Dish", back_populates="menu", cascade="all, delete-orphan", lazy="joined")

class Dish(Base):
    __tablename__ = "dishes"

    id = Column(String, primary_key=True, default=generate_dish_id)
    menu_id = Column(String, ForeignKey("menus.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    cuisine = Column(String, nullable=True)
    ingredients = Column(JSON, nullable=False, default=list)
    diet_type = Column(String, nullable=True)
    spice_level = Column(Integer, nullable=False, default=1)
    health_tags = Column(JSON, nullable=False, default=list)

    menu = relationship("Menu", back_populates="dishes")
    feedbacks = relationship("Feedback", back_populates="dish", cascade="all, delete-orphan")
