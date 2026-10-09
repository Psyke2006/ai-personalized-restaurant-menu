import re
import json
from typing import List, Dict, Any, Optional
from backend.config import settings

def heuristic_parse_dishes(raw_text: str) -> List[Dict[str, Any]]:
    """
    Parses unstructured menu text into structured dish records using regex heuristics.
    Matches lines containing dish name, price, and optional description/ingredients.
    """
    dishes = []
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

    # Patterns matching: "Name - ₹250", "Name ... 250", "Name: 250", "Name 250.00"
    dish_pattern = re.compile(
        r"^([A-Za-z\s'&/]+?)(?:\s*[-–—:]\s*|\s+\.{2,}\s*|\s+)[₹$]?\s*(\d+(?:\.\d{1,2})?)(?:\s*[-–—:]\s*(.+))?$"
    )

    for line in lines:
        match = dish_pattern.match(line)
        if match:
            name = match.group(1).strip()
            price_str = match.group(2).strip()
            extra_info = match.group(3).strip() if match.group(3) else ""

            if len(name) < 2 or name.lower() in ["menu", "drinks", "starters", "main course", "desserts", "page"]:
                continue

            try:
                price = float(price_str)
            except ValueError:
                continue

            # Infer ingredients and description
            ingredients = []
            if extra_info:
                # Look for comma-separated ingredients
                parts = [p.strip() for p in re.split(r"[,;]", extra_info) if p.strip()]
                ingredients = parts

            # Heuristic diet type detection
            name_lower = name.lower()
            extra_lower = extra_info.lower()
            combined = f"{name_lower} {extra_lower}"

            if any(w in combined for w in ["chicken", "mutton", "fish", "prawn", "meat", "pork", "beef"]):
                diet_type = "non-vegetarian"
            elif any(w in combined for w in ["vegan", "tofu"]):
                diet_type = "vegan"
            else:
                diet_type = "vegetarian"

            # Heuristic spice level detection
            spice_level = 1
            if "spicy" in combined or "hot" in combined or "schezwan" in combined:
                spice_level = 4
            elif "tikka" in combined or "masala" in combined or "curry" in combined:
                spice_level = 3

            # Heuristic health tags
            health_tags = []
            if any(w in combined for w in ["paneer", "chicken", "tofu", "protein", "dal", "lentil"]):
                health_tags.append("high_protein")
            if any(w in combined for w in ["salad", "soup", "grilled", "steamed", "low carb"]):
                health_tags.append("low_calorie")

            dishes.append({
                "name": name,
                "description": extra_info or f"Authentic {name}",
                "price": price,
                "cuisine": "Indian" if any(w in combined for w in ["paneer", "tikka", "masala", "dal", "biryani", "roti", "curry"]) else "Continental",
                "ingredients": ingredients,
                "diet_type": diet_type,
                "spice_level": spice_level,
                "health_tags": health_tags,
            })

    return dishes

def parse_with_gemini(raw_text: str, api_key: str) -> Optional[List[Dict[str, Any]]]:
    """
    Calls Gemini API to normalize extracted menu text into JSON dish items.
    Enforces strict JSON schema validation.
    """
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = f"""
You are an expert menu parser. Extract all dish items from the following raw restaurant menu text.
Return ONLY a valid JSON list of objects conforming exactly to this structure:
[
  {{
    "name": "string",
    "description": "string",
    "price": float,
    "cuisine": "string",
    "ingredients": ["string"],
    "diet_type": "vegetarian" | "vegan" | "non-vegetarian",
    "spice_level": integer between 1 and 5,
    "health_tags": ["string"]
  }}
]

Raw menu text:
\"\"\"
{raw_text}
\"\"\"
"""
        response = model.generate_content(prompt)
        text_resp = response.text.strip()
        # Clean json markdown tags if present
        if text_resp.startswith("```"):
            text_resp = re.sub(r"^```(?:json)?\n", "", text_resp)
            text_resp = re.sub(r"\n```$", "", text_resp)

        parsed = json.loads(text_resp)
        if isinstance(parsed, list):
            return parsed
    except Exception:
        pass
    return None

def parse_extracted_menu(raw_text: str) -> List[Dict[str, Any]]:
    """
    Main parser entrypoint. Uses Gemini if key is present and call succeeds,
    otherwise reliably falls back to deterministic heuristic parsing.
    """
    if settings.GEMINI_API_KEY:
        gemini_result = parse_with_gemini(raw_text, settings.GEMINI_API_KEY)
        if gemini_result:
            return gemini_result

    return heuristic_parse_dishes(raw_text)
