# REST API SPECIFICATION

## Overview & Base Configuration

- **Base URL**: `http://localhost:8000/api/v1`
- **Protocol**: HTTP / REST
- **Content-Type**: `application/json`

---

## 1. System Health

### `GET /health`
Returns system status and backend operational health.

#### Response `200 OK`
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "recommender_engine": "active"
}
```

---

## 2. User Profile Management

### `POST /users/profile`
Creates or updates a user's dietary profile, preferences, and safety constraints.

#### Request Body
```json
{
  "name": "Tanishkk Pachpute",
  "budget": 500.0,
  "spice_tolerance": 3,
  "health_goal": "high_protein",
  "dietary_preferences": ["vegetarian"],
  "allergies": ["peanuts", "tree nuts"],
  "favorite_cuisines": ["Indian", "Italian"],
  "favorite_ingredients": ["paneer", "mushroom"]
}
```

#### Response `201 Created`
```json
{
  "id": "u-12345678-abcd-ef01-2345-6789abcdef01",
  "name": "Tanishkk Pachpute",
  "budget": 500.0,
  "spice_tolerance": 3,
  "health_goal": "high_protein",
  "dietary_preferences": ["vegetarian"],
  "allergies": ["peanuts", "tree nuts"],
  "favorite_cuisines": ["Indian", "Italian"],
  "favorite_ingredients": ["paneer", "mushroom"],
  "created_at": "2026-10-09T20:00:00Z"
}
```

---

### `GET /users/{user_id}`
Retrieves user profile details by UUID.

#### Response `200 OK`
```json
{
  "id": "u-12345678-abcd-ef01-2345-6789abcdef01",
  "name": "Tanishkk Pachpute",
  "budget": 500.0,
  "spice_tolerance": 3,
  "health_goal": "high_protein",
  "dietary_preferences": ["vegetarian"],
  "allergies": ["peanuts", "tree nuts"],
  "favorite_cuisines": ["Indian", "Italian"],
  "favorite_ingredients": ["paneer", "mushroom"]
}
```

---

## 3. Menu Ingestion & Dish Management

### `POST /menu/manual`
Manually adds structured dish items to a menu dataset.

#### Request Body
```json
{
  "restaurant_name": "Spice Bistro",
  "dishes": [
    {
      "name": "Paneer Tikka",
      "description": "Char-grilled cottage cheese marinated in aromatic Indian spices",
      "price": 280.0,
      "cuisine": "Indian",
      "ingredients": ["paneer", "yogurt", "bell pepper", "spices"],
      "diet_type": "vegetarian",
      "spice_level": 3,
      "health_tags": ["high_protein"]
    },
    {
      "name": "Peanut Satay Skewers",
      "description": "Grilled skewers with rich spicy peanut dip sauce",
      "price": 320.0,
      "cuisine": "Thai",
      "ingredients": ["tofu", "peanuts", "soy sauce", "chili"],
      "diet_type": "vegan",
      "spice_level": 4,
      "health_tags": ["high_protein"]
    }
  ]
}
```

#### Response `201 Created`
```json
{
  "menu_id": "m-87654321-fedc-ba09-8765-4321fedcba09",
  "restaurant_name": "Spice Bistro",
  "total_dishes_added": 2,
  "created_at": "2026-10-09T20:05:00Z"
}
```

---

### `POST /menu/upload`
Uploads a menu file (PDF or Image) for OCR/Gemini extraction.

#### Request (`multipart/form-data`)
- `file`: PDF or Image binary (`menu.pdf` / `menu.png`)
- `restaurant_name`: String (optional)

#### Response `200 OK`
```json
{
  "menu_id": "m-99998888-7777-6666-5555-444433332222",
  "extracted_dishes_count": 12,
  "status": "extracted_and_parsed",
  "dishes": [
    {
      "id": "d-001",
      "name": "Paneer Tikka",
      "price": 280.0,
      "cuisine": "Indian",
      "ingredients": ["paneer", "yogurt", "bell pepper"],
      "diet_type": "vegetarian",
      "spice_level": 3,
      "health_tags": ["high_protein"]
    }
  ]
}
```

---

## 4. Recommendation & Ranking Engine

### `POST /recommendations/rank`
Ranks menu dishes for a given user profile, applying hard safety filters and calculating weighted match scores.

#### Request Body
```json
{
  "user_id": "u-12345678-abcd-ef01-2345-6789abcdef01",
  "menu_id": "m-87654321-fedc-ba09-8765-4321fedcba09"
}
```

#### Response `200 OK`
```json
{
  "user_id": "u-12345678-abcd-ef01-2345-6789abcdef01",
  "recommended_dishes": [
    {
      "dish_id": "d-001",
      "name": "Paneer Tikka",
      "price": 280.0,
      "cuisine": "Indian",
      "match_score": 91,
      "compatibility_status": "COMPATIBLE",
      "match_reasons": [
        "Matches Vegetarian dietary preference",
        "Matches Indian favorite cuisine",
        "Contains Paneer, a favorite ingredient",
        "Within budget (₹280 / ₹500)",
        "Matches preferred spice level (Level 3)",
        "Includes high_protein health tag"
      ]
    }
  ],
  "filtered_dishes": [
    {
      "dish_id": "d-002",
      "name": "Peanut Satay Skewers",
      "price": 320.0,
      "compatibility_status": "FILTERED",
      "exclusion_reasons": [
        "Incompatible: Contains peanuts (User Allergen)"
      ]
    }
  ]
}
```

---

## 5. Feedback Loop

### `POST /feedback`
Submits user feedback (Likes, Dislikes, 1-5 Star Ratings) for a specific dish.

#### Request Body
```json
{
  "user_id": "u-12345678-abcd-ef01-2345-6789abcdef01",
  "dish_id": "d-001",
  "liked": true,
  "rating": 5
}
```

#### Response `201 Created`
```json
{
  "feedback_id": "f-11112222-3333-4444-5555-666677778888",
  "status": "persisted",
  "message": "Feedback successfully recorded for personalization."
}
```

---

## Error Handling Standards

All error responses adhere to standard HTTP status codes and return structured error objects:

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "User profile with ID 'u-99999' was not found.",
    "timestamp": "2026-10-09T20:10:00Z"
  }
}
```

| Code | Status | Description |
|---|---|---|
| `400 Bad Request` | Validation Error | Invalid payload format or missing mandatory fields |
| `404 Not Found` | Resource Missing | Specified user_id, menu_id, or dish_id does not exist |
| `422 Unprocessable` | Schema Mismatch | Malformed JSON data or invalid data types |
| `500 Internal Error` | Server Exception | Unhandled internal exception |
