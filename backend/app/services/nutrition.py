import httpx
from app.config import settings
from app.models import Ingredient, NutritionItem

USDA_SEARCH_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"

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

# Piece/count grams per item for common ingredients
_PIECE_WEIGHTS: dict[str, float] = {
    "egg": 50.0,
    "chapati": 80.0,
    "roti": 80.0,
    "paratha": 100.0,
    "naan": 90.0,
    "idli": 60.0,
    "dosa": 80.0,
    "bread": 30.0,
    "slice": 30.0,
    "banana": 120.0,
    "apple": 180.0,
    "orange": 130.0,
    "potato": 150.0,
    "onion": 110.0,
    "tomato": 100.0,
}


def _unit_to_grams(ingredient: str, quantity: float, unit: str) -> float:
    unit_lower = unit.lower().strip()

    if unit_lower in _WEIGHT_UNITS:
        return quantity * _WEIGHT_UNITS[unit_lower]

    if unit_lower in _VOLUME_UNITS:
        return quantity * _VOLUME_UNITS[unit_lower]

    if unit_lower in ("piece", "pieces", "count", "serving", "servings", "number", "nos", "no"):
        ingredient_key = ingredient.lower().strip()
        grams_per_piece = next(
            (v for k, v in _PIECE_WEIGHTS.items() if k in ingredient_key),
            100.0,
        )
        return quantity * grams_per_piece

    # Unknown unit — treat quantity as grams
    return quantity


async def lookup_nutrition(ingredients: list[Ingredient]) -> list[NutritionItem]:
    results: list[NutritionItem] = []

    async with httpx.AsyncClient(timeout=10.0) as client:
        for ing in ingredients:
            gram_weight = _unit_to_grams(ing.ingredient, ing.quantity, ing.unit)
            item = await _fetch_one(client, ing, gram_weight)
            results.append(item)

    return results


async def _fetch_one(
    client: httpx.AsyncClient,
    ing: Ingredient,
    gram_weight: float,
) -> NutritionItem:
    try:
        response = await client.get(
            USDA_SEARCH_URL,
            params={
                "query": ing.ingredient,
                "api_key": settings.usda_api_key,
                "dataType": ["SR Legacy", "Foundation"],
                "pageSize": 1,
            },
        )
    except httpx.RequestError as exc:
        raise RuntimeError(f"USDA request failed: {exc}") from exc

    if response.status_code != 200:
        raise RuntimeError(f"USDA API error {response.status_code}: {response.text}")

    data = response.json()
    foods = data.get("foods", [])

    if not foods:
        return NutritionItem(
            ingredient_name=ing.ingredient,
            quantity=ing.quantity,
            unit=ing.unit,
            calories=0.0,
            protein=0.0,
            carbs=0.0,
            fat=0.0,
            source="usda_not_found",
        )

    food = foods[0]
    nutrients = {n["nutrientName"]: n.get("value", 0.0) for n in food.get("foodNutrients", [])}

    scale = gram_weight / 100.0

    def get_nutrient(*names: str) -> float:
        for name in names:
            if name in nutrients:
                return round(nutrients[name] * scale, 2)
        return 0.0

    calories = get_nutrient("Energy", "Energy (Atwater General Factors)")
    protein = get_nutrient("Protein")
    carbs = get_nutrient("Carbohydrate, by difference")
    fat = get_nutrient("Total lipid (fat)")

    return NutritionItem(
        ingredient_name=ing.ingredient,
        quantity=ing.quantity,
        unit=ing.unit,
        calories=calories,
        protein=protein,
        carbs=carbs,
        fat=fat,
        source="usda",
    )
