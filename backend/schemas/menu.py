from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class DishCreate(BaseModel):
    name: str = Field(..., min_length=1, description="Dish name")
    description: Optional[str] = Field(None, description="Dish description")
    price: float = Field(..., ge=0.0, description="Price in currency units")
    cuisine: Optional[str] = Field(None, description="Cuisine type")
    ingredients: List[str] = Field(default_factory=list, description="List of ingredients")
    diet_type: Optional[str] = Field(None, description="Diet type e.g. vegetarian, vegan")
    spice_level: int = Field(default=1, ge=1, le=5, description="Spice level between 1 and 5")
    health_tags: List[str] = Field(default_factory=list, description="Health tags e.g. high_protein")

class DishResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: Optional[str] = None
    price: float
    cuisine: Optional[str] = None
    ingredients: List[str] = Field(default_factory=list)
    diet_type: Optional[str] = None
    spice_level: int = 1
    health_tags: List[str] = Field(default_factory=list)

class ManualMenuCreate(BaseModel):
    restaurant_name: str = Field(..., min_length=1, description="Name of the restaurant")
    dishes: List[DishCreate] = Field(..., min_length=1, description="List of dishes to add")

class ManualMenuResponse(BaseModel):
    menu_id: str
    restaurant_name: str
    total_dishes_added: int
    created_at: str
    dishes: List[DishResponse] = Field(default_factory=list)

class MenuDetailResponse(BaseModel):
    menu_id: str
    restaurant_name: str
    total_dishes: int
    created_at: str
    dishes: List[DishResponse] = Field(default_factory=list)

class UploadMenuResponse(BaseModel):
    menu_id: str
    extracted_dishes_count: int
    status: str
    dishes: List[DishResponse] = Field(default_factory=list)
