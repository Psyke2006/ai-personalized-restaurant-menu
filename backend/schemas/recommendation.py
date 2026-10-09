from typing import List, Optional
from pydantic import BaseModel, Field

class RecommendationRequest(BaseModel):
    user_id: str = Field(..., description="Target user UUID or ID")
    menu_id: str = Field(..., description="Target restaurant menu UUID or ID")

class RecommendedDishItem(BaseModel):
    dish_id: str
    name: str
    price: float
    cuisine: Optional[str] = None
    match_score: int
    compatibility_status: str
    match_reasons: List[str] = Field(default_factory=list)

class FilteredDishItem(BaseModel):
    dish_id: str
    name: str
    price: float
    compatibility_status: str
    exclusion_reasons: List[str] = Field(default_factory=list)

class AllDishItem(BaseModel):
    dish_id: str
    name: str
    price: float
    cuisine: Optional[str] = None
    compatibility_status: str
    match_score: Optional[int] = None
    match_reasons: List[str] = Field(default_factory=list)
    exclusion_reasons: List[str] = Field(default_factory=list)

class RecommendationResponse(BaseModel):
    user_id: str
    recommended_dishes: List[RecommendedDishItem] = Field(default_factory=list)
    filtered_dishes: List[FilteredDishItem] = Field(default_factory=list)
    all_dishes: List[AllDishItem] = Field(default_factory=list)
