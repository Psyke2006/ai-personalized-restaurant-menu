from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class UserProfileCreate(BaseModel):
    name: str = Field(..., min_length=1, description="User's full name")
    budget: float = Field(..., ge=0, description="Dining budget constraint")
    spice_tolerance: int = Field(..., ge=1, le=5, description="Spice tolerance level (1 to 5)")
    health_goal: Optional[str] = Field(None, description="Health goal e.g. high_protein, low_calorie")
    dietary_preferences: List[str] = Field(default_factory=list, description="Strict dietary preferences")
    allergies: List[str] = Field(default_factory=list, description="Allergies to strictly exclude")
    favorite_cuisines: List[str] = Field(default_factory=list, description="Cuisines preferred by the user")
    favorite_ingredients: List[str] = Field(default_factory=list, description="Ingredients preferred by the user")

class UserProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    budget: float
    spice_tolerance: int
    health_goal: Optional[str] = None
    dietary_preferences: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    favorite_cuisines: List[str] = Field(default_factory=list)
    favorite_ingredients: List[str] = Field(default_factory=list)
    created_at: Optional[str] = None
