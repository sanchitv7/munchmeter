import asyncio
import httpx
from app.config import settings
from app.models import Ingredient, NutritionItem
from app.services.ifct import lookup_ifct

USDA_SEARCH_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"

# Simple in-memory cache: ingredient name (lowercased) -> per-100g nutrients + portions, or None on miss
_usda_cache: dict[str, dict | None] = {}

# Unit-to-gram conversion
_WEIGHT_UNITS: dict[str, float] = {
    "g": 1.0,
    "gram": 1.0,
    "grams": 1.0,
    "kg": 1000.0,
    "kilogram": 1000.0,
    "oz": 28.35,
    "ounce": 28.35,
    "lb": 453.6,
    "pound": 453.6,
}

_VOLUME_UNITS: dict[str, float] = {
    "ml": 1.0,
    "milliliter": 1.0,
    "l": 1000.0,
    "liter": 1000.0,
    "cup": 240.0,
    "cups": 240.0,
    "tbsp": 15.0,
    "tablespoon": 15.0,
    "tsp": 5.0,
    "teaspoon": 5.0,
}

# Piece/count grams per item — corrected weights, ~55 entries
_PIECE_WEIGHTS: dict[str, float] = {
    # Indian breads
    "roti": 40.0,
    "chapati": 40.0,
    "phulka": 35.0,
    "paratha": 80.0,
    "naan": 90.0,
    "puri": 30.0,
    "bhatura": 80.0,
    # South Indian
    "idli": 40.0,
    "dosa": 80.0,
    "uttapam": 120.0,
    "vada": 50.0,
    # Eggs
    "egg": 50.0,
    # Bread / western
    "bread": 30.0,
    "slice": 30.0,
    "bun": 45.0,
    "roll": 50.0,
    # Fruits
    "banana": 120.0,
    "apple": 180.0,
    "orange": 130.0,
    "mango": 200.0,
    "guava": 100.0,
    "papaya": 150.0,
    "pear": 150.0,
    "peach": 130.0,
    "plum": 70.0,
    "kiwi": 70.0,
    "lemon": 60.0,
    # Vegetables
    "potato": 150.0,
    "onion": 110.0,
    "tomato": 100.0,
    "carrot": 80.0,
    "cucumber": 200.0,
    "capsicum": 120.0,
    "brinjal": 200.0,
    "eggplant": 200.0,
    "cauliflower": 500.0,
    "cabbage": 900.0,
    # Snacks / sweets
    "samosa": 60.0,
    "pakora": 20.0,
    "gulab jamun": 50.0,
    "laddoo": 40.0,
    "dhokla": 40.0,
    # Other
    "biscuit": 10.0,
    "cookie": 15.0,
}

_PIECE_UNITS = {"piece", "pieces", "count", "serving", "servings", "number", "nos", "no"}


def _resolve_gram_weight(ing: Ingredient, usda_portions: list[dict]) -> float:
    """Return gram weight for the ingredient's quantity + unit.

    Priority:
    1. Weight / volume units — direct conversion.
    2. Piece units + USDA foodPortions match.
    3. Piece units + _PIECE_WEIGHTS table.
    4. Unknown unit — treat quantity as grams.
    """
    unit_lower = ing.unit.lower().strip()

    if unit_lower in _WEIGHT_UNITS:
        return ing.quantity * _WEIGHT_UNITS[unit_lower]

    if unit_lower in _VOLUME_UNITS:
        return ing.quantity * _VOLUME_UNITS[unit_lower]

    if unit_lower in _PIECE_UNITS:
        # Try USDA foodPortions first
        if usda_portions:
            best = usda_portions[0]
            gram_weight = best.get("gramWeight", 0.0)
            if gram_weight > 0:
                return ing.quantity * gram_weight

        # Fall back to _PIECE_WEIGHTS table
        ingredient_key = ing.ingredient.lower().strip()
        grams_per_piece = next(
            (v for k, v in _PIECE_WEIGHTS.items() if k in ingredient_key),
            100.0,
        )
        return ing.quantity * grams_per_piece

    # Unknown unit — treat quantity as grams
    return ing.quantity


async def _fetch_usda(client: httpx.AsyncClient, name: str) -> dict | None:
    """Fetch USDA FoodData Central for name. Returns per-100g nutrient dict with
    a 'portions' key, or None on miss. Results are cached."""
    cache_key = name.lower().strip()
    if cache_key in _usda_cache:
        return _usda_cache[cache_key]

    try:
        response = await client.get(
            USDA_SEARCH_URL,
            params={
                "query": name,
                "api_key": settings.usda_api_key,
                "dataType": ["SR Legacy", "Foundation"],
                "pageSize": 1,
            },
        )
    except httpx.RequestError as exc:
        raise RuntimeError(f"USDA request failed: {exc}") from exc

    if response.status_code != 200:
        raise RuntimeError(f"USDA API error {response.status_code}: {response.text}")

    foods = response.json().get("foods", [])
    if not foods:
        _usda_cache[cache_key] = None
        return None

    food = foods[0]
    nutrients = {n["nutrientName"]: n.get("value", 0.0) for n in food.get("foodNutrients", [])}
    portions = food.get("foodPortions", [])
    result = {"nutrients": nutrients, "portions": portions}
    _usda_cache[cache_key] = result
    return result


def _make_item(ing: Ingredient, source: str, calories: float, protein: float, carbs: float, fat: float) -> NutritionItem:
    return NutritionItem(
        ingredient_name=ing.ingredient,
        quantity=ing.quantity,
        unit=ing.unit,
        calories=calories,
        protein=protein,
        carbs=carbs,
        fat=fat,
        source=source,
    )


async def _lookup_one(client: httpx.AsyncClient, ing: Ingredient) -> NutritionItem:
    """Resolve nutrition for a single ingredient: IFCT → USDA → not_found."""
    # --- Tier 1: IFCT (synchronous, instant) ---
    ifct = lookup_ifct(ing.ingredient)
    if ifct is not None:
        scale = _resolve_gram_weight(ing, []) / 100.0
        return _make_item(
            ing, "ifct",
            round(ifct["calories"] * scale, 2),
            round(ifct["protein"] * scale, 2),
            round(ifct["carbs"] * scale, 2),
            round(ifct["fat"] * scale, 2),
        )

    # --- Tier 2: USDA ---
    usda = await _fetch_usda(client, ing.ingredient)

    if usda is None:
        return _make_item(ing, "not_found", 0.0, 0.0, 0.0, 0.0)

    scale = _resolve_gram_weight(ing, usda["portions"]) / 100.0
    nutrients = usda["nutrients"]

    def get_nutrient(*names: str) -> float:
        for n in names:
            if n in nutrients:
                return round(nutrients[n] * scale, 2)
        return 0.0

    return _make_item(
        ing, "usda",
        get_nutrient("Energy", "Energy (Atwater General Factors)"),
        get_nutrient("Protein"),
        get_nutrient("Carbohydrate, by difference"),
        get_nutrient("Total lipid (fat)"),
    )


async def lookup_nutrition(ingredients: list[Ingredient]) -> list[NutritionItem]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        results = await asyncio.gather(
            *[_lookup_one(client, ing) for ing in ingredients]
        )
    return list(results)
