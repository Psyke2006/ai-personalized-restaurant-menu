import re
from typing import List, Tuple, Dict, Any, Optional

ALLERGEN_SYNONYMS: Dict[str, List[str]] = {
    "peanut": ["peanut", "peanuts", "groundnut", "groundnuts", "peanut butter", "peanut oil"],
    "peanuts": ["peanut", "peanuts", "groundnut", "groundnuts", "peanut butter", "peanut oil"],
    "tree nut": ["tree nut", "tree nuts", "nut", "nuts", "almond", "almonds", "walnut", "walnuts", "cashew", "cashews", "pistachio", "pistachios", "hazelnut", "hazelnuts", "pecan", "pecans"],
    "tree nuts": ["tree nut", "tree nuts", "nut", "nuts", "almond", "almonds", "walnut", "walnuts", "cashew", "cashews", "pistachio", "pistachios", "hazelnut", "hazelnuts", "pecan", "pecans"],
    "dairy": ["dairy", "milk", "cheese", "butter", "yogurt", "paneer", "cream", "ghee", "curd"],
    "milk": ["dairy", "milk", "cheese", "butter", "yogurt", "paneer", "cream", "ghee", "curd"],
    "gluten": ["gluten", "wheat", "flour", "maida", "barley", "rye"],
    "wheat": ["gluten", "wheat", "flour", "maida", "barley", "rye"],
    "soy": ["soy", "soya", "soybean", "soybeans", "tofu", "soy sauce", "edamame"],
    "soya": ["soy", "soya", "soybean", "soybeans", "tofu", "soy sauce", "edamame"],
    "egg": ["egg", "eggs", "egg white", "egg yolk", "mayonnaise"],
    "eggs": ["egg", "eggs", "egg white", "egg yolk", "mayonnaise"],
    "fish": ["fish", "salmon", "tuna", "cod", "tilapia", "anchovy"],
    "shellfish": ["shellfish", "shrimp", "prawn", "prawns", "crab", "lobster", "mussel", "oyster", "clam"],
    "seafood": ["fish", "shellfish", "seafood", "shrimp", "prawn", "prawns", "crab", "lobster"],
}

NON_VEG_KEYWORDS = [
    "chicken", "mutton", "lamb", "beef", "pork", "bacon", "ham",
    "fish", "prawn", "prawns", "shrimp", "crab", "lobster", "meat",
    "turkey", "duck", "seafood", "gelatin"
]

ANIMAL_DERIVED_KEYWORDS = NON_VEG_KEYWORDS + [
    "dairy", "milk", "cheese", "butter", "yogurt", "paneer", "cream",
    "ghee", "curd", "honey", "egg", "eggs", "mayo", "mayonnaise"
]

JAIN_RESTRICTED_KEYWORDS = [
    "onion", "garlic", "potato", "potatoes", "carrot", "carrots",
    "radish", "beetroot", "ginger", "turnip"
] + NON_VEG_KEYWORDS

HALAL_RESTRICTED_KEYWORDS = [
    "pork", "bacon", "ham", "lard", "alcohol", "wine", "beer", "rum", "whiskey"
]

def normalize_text(text: str) -> str:
    """Lowercases, strips leading/trailing spaces, and collapses extra whitespace."""
    if not text:
        return ""
    return re.sub(r"\s+", " ", text.strip().lower())

def tokenize(text: str) -> List[str]:
    """Tokenizes text into words for boundary-aware matching."""
    norm = normalize_text(text)
    return re.findall(r"\b[a-z0-9]+\b", norm)

def get_variants(term: str) -> List[str]:
    """Generates simple singular and plural variants for english food words."""
    norm = normalize_text(term)
    if not norm:
        return []
    variants = [norm]
    if norm.endswith("ies") and len(norm) > 4:
        variants.append(norm[:-3] + "y")
    elif norm.endswith("es") and len(norm) > 3:
        variants.append(norm[:-2])
        variants.append(norm[:-1])
    elif norm.endswith("s") and len(norm) > 2:
        variants.append(norm[:-1])
    else:
        variants.append(norm + "s")
        variants.append(norm + "es")
    return list(dict.fromkeys(variants))

def matches_term(term: str, target_text: str) -> bool:
    """Checks if a term or its singular/plural variant appears in target text using word boundaries."""
    norm_target = normalize_text(target_text)
    if not term or not norm_target:
        return False
    variants = get_variants(term)
    for v in variants:
        pattern = r"\b" + re.escape(v) + r"\b"
        if re.search(pattern, norm_target):
            return True
    return False

def check_allergen_conflict(user_allergies: List[str], dish_ingredients: List[str], dish_name: str) -> List[str]:
    """Checks for allergen matches between user allergies and dish ingredients/name."""
    conflicts = []
    combined_targets = list(dish_ingredients) + [dish_name]

    for allergen in user_allergies:
        norm_allergen = normalize_text(allergen)
        if not norm_allergen:
            continue

        # Build alias search set
        search_terms = set([norm_allergen])
        for key, aliases in ALLERGEN_SYNONYMS.items():
            if matches_term(key, norm_allergen):
                search_terms.update([normalize_text(a) for a in aliases])

        # Check against dish ingredients and name
        matched = False
        for target in combined_targets:
            for term in search_terms:
                if matches_term(term, target):
                    conflicts.append(f"Incompatible: Contains {term} (User Allergen: {allergen})")
                    matched = True
                    break
            if matched:
                break
    return conflicts

def check_dietary_conflict(dietary_preferences: List[str], dish_diet_type: Optional[str], dish_ingredients: List[str], dish_name: str) -> List[str]:
    """Checks for dietary conflicts (vegetarian, vegan, jain, halal)."""
    conflicts = []
    norm_diet_type = normalize_text(dish_diet_type or "")
    combined_targets = list(dish_ingredients) + [dish_name]

    for diet in dietary_preferences:
        norm_diet = normalize_text(diet)

        if "vegetarian" in norm_diet and "vegan" not in norm_diet:
            if "non" in norm_diet_type and "veg" in norm_diet_type:
                conflicts.append(f"Incompatible with {diet} dietary preference (Tagged non-vegetarian)")
            else:
                for target in combined_targets:
                    for nv in NON_VEG_KEYWORDS:
                        if matches_term(nv, target):
                            conflicts.append(f"Incompatible with {diet} dietary preference (Contains {nv})")
                            break
                    if conflicts:
                        break

        elif "vegan" in norm_diet:
            if norm_diet_type in ["non-vegetarian", "non-veg", "vegetarian"]:
                # May contain dairy or meat
                pass
            for target in combined_targets:
                for ad in ANIMAL_DERIVED_KEYWORDS:
                    if matches_term(ad, target):
                        conflicts.append(f"Incompatible with {diet} dietary preference (Contains {ad})")
                        break
                if conflicts:
                    break

        elif "jain" in norm_diet:
            for target in combined_targets:
                for jain_word in JAIN_RESTRICTED_KEYWORDS:
                    if matches_term(jain_word, target):
                        conflicts.append(f"Incompatible with {diet} dietary preference (Contains {jain_word})")
                        break
                if conflicts:
                    break

        elif "halal" in norm_diet:
            for target in combined_targets:
                for h_word in HALAL_RESTRICTED_KEYWORDS:
                    if matches_term(h_word, target):
                        conflicts.append(f"Incompatible with {diet} dietary preference (Contains {h_word})")
                        break
                if conflicts:
                    break

    return conflicts

def filter_dishes(user_allergies: List[str], user_diets: List[str], dishes: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Applies hard allergy and strict dietary filters.
    Returns (compatible_dishes, filtered_dishes).
    Dishes with missing ingredients get flagged with NEEDS_VERIFICATION if the user has allergies.
    """
    compatible = []
    filtered = []

    for dish in dishes:
        ingredients = dish.get("ingredients") or []
        name = dish.get("name", "")
        diet_type = dish.get("diet_type")

        # Check for uncertainty: user has allergies, but dish has no ingredient metadata
        if user_allergies and not ingredients:
            dish_copy = dict(dish)
            dish_copy["compatibility_status"] = "NEEDS_VERIFICATION"
            dish_copy["exclusion_reasons"] = [
                "Uncertainty warning: Dish metadata lacks ingredient list. Please verify with restaurant staff for allergy safety."
            ]
            filtered.append(dish_copy)
            continue

        allergen_conflicts = check_allergen_conflict(user_allergies, ingredients, name)
        diet_conflicts = check_dietary_conflict(user_diets, diet_type, ingredients, name)

        all_conflicts = allergen_conflicts + diet_conflicts

        if all_conflicts:
            dish_copy = dict(dish)
            dish_copy["compatibility_status"] = "FILTERED"
            dish_copy["exclusion_reasons"] = all_conflicts
            filtered.append(dish_copy)
        else:
            dish_copy = dict(dish)
            dish_copy["compatibility_status"] = "COMPATIBLE"
            dish_copy["exclusion_reasons"] = []
            compatible.append(dish_copy)

    return compatible, filtered
