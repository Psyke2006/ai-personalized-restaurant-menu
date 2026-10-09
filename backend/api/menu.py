import os
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.models.menu import Menu, Dish
from backend.schemas.menu import (
    ManualMenuCreate,
    ManualMenuResponse,
    MenuDetailResponse,
    UploadMenuResponse,
    DishResponse,
)
from backend.menu_processing.extractor import extract_text_from_file
from backend.menu_processing.parser import parse_extracted_menu

router = APIRouter(prefix="/menu", tags=["Menu Management"])

def dish_to_response(dish: Dish) -> DishResponse:
    return DishResponse(
        id=dish.id,
        name=dish.name,
        description=dish.description,
        price=dish.price,
        cuisine=dish.cuisine,
        ingredients=dish.ingredients or [],
        diet_type=dish.diet_type,
        spice_level=dish.spice_level,
        health_tags=dish.health_tags or [],
    )

@router.post("/manual", response_model=ManualMenuResponse, status_code=status.HTTP_201_CREATED)
def create_manual_menu(
    menu_in: ManualMenuCreate,
    db: Session = Depends(get_db)
):
    """Manually adds structured dish items to a menu dataset with transactional persistence."""
    menu = Menu(restaurant_name=menu_in.restaurant_name)
    db.add(menu)
    db.flush()

    dishes_added = []
    for dish_data in menu_in.dishes:
        dish = Dish(
            menu_id=menu.id,
            name=dish_data.name,
            description=dish_data.description,
            price=dish_data.price,
            cuisine=dish_data.cuisine,
            ingredients=dish_data.ingredients,
            diet_type=dish_data.diet_type,
            spice_level=dish_data.spice_level,
            health_tags=dish_data.health_tags,
        )
        db.add(dish)
        dishes_added.append(dish)

    db.commit()
    db.refresh(menu)

    return ManualMenuResponse(
        menu_id=menu.id,
        restaurant_name=menu.restaurant_name,
        total_dishes_added=len(dishes_added),
        created_at=menu.created_at.isoformat() if menu.created_at else datetime.now(timezone.utc).isoformat(),
        dishes=[dish_to_response(d) for d in dishes_added],
    )

@router.get("/{menu_id}", response_model=MenuDetailResponse, status_code=status.HTTP_200_OK)
def get_menu_by_id(menu_id: str, db: Session = Depends(get_db)):
    """Retrieves menu details and its associated dishes by ID."""
    menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Menu with ID '{menu_id}' was not found.",
        )
    return MenuDetailResponse(
        menu_id=menu.id,
        restaurant_name=menu.restaurant_name,
        total_dishes=len(menu.dishes),
        created_at=menu.created_at.isoformat() if menu.created_at else datetime.now(timezone.utc).isoformat(),
        dishes=[dish_to_response(d) for d in menu.dishes],
    )

@router.post("/upload", response_model=UploadMenuResponse, status_code=status.HTTP_200_OK)
async def upload_menu(
    file: UploadFile = File(...),
    restaurant_name: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Uploads a menu file (PDF or Image) for text extraction and dish normalization."""
    # Validate file extension
    filename = file.filename or "unknown"
    ext = os.path.splitext(filename)[1].lower()
    if ext not in [".pdf", ".png", ".jpg", ".jpeg"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Supported formats: PDF, PNG, JPG, JPEG.",
        )

    # Read contents
    contents = await file.read()
    if not contents or len(contents) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds maximum permitted limit (10MB).",
        )

    # Extract text
    try:
        raw_text = extract_text_from_file(contents, filename)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to process menu document: {str(e)}",
        )

    if not raw_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not extract any readable text from the uploaded document.",
        )

    # Parse dishes
    extracted_dishes = parse_extracted_menu(raw_text)
    if not extracted_dishes:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not identify or parse any dish items from extracted text.",
        )

    # Persist Menu and Dishes transactionally
    menu = Menu(restaurant_name=restaurant_name or "Uploaded Restaurant")
    db.add(menu)
    db.flush()

    dishes_added = []
    for dish_data in extracted_dishes:
        dish = Dish(
            menu_id=menu.id,
            name=dish_data.get("name", "Unknown Dish"),
            description=dish_data.get("description"),
            price=float(dish_data.get("price", 0.0)),
            cuisine=dish_data.get("cuisine"),
            ingredients=dish_data.get("ingredients") or [],
            diet_type=dish_data.get("diet_type"),
            spice_level=int(dish_data.get("spice_level", 1)),
            health_tags=dish_data.get("health_tags") or [],
        )
        db.add(dish)
        dishes_added.append(dish)

    db.commit()
    db.refresh(menu)

    return UploadMenuResponse(
        menu_id=menu.id,
        extracted_dishes_count=len(dishes_added),
        status="extracted_and_parsed",
        dishes=[dish_to_response(d) for d in dishes_added],
    )
