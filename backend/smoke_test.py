"""
Smoke test: extraction + nutrition lookup without the frontend.
Run from backend/ with the venv active:
    uv run python smoke_test.py          # full pipeline
    uv run python smoke_test.py --usda   # USDA key check only
"""

import asyncio
import sys
from app.services.ingredient_parser import extract_ingredients
from app.services.nutrition import lookup_nutrition

SAMPLE_TRANSCRIPTION = (
    "aaj subah maine do ande khaye, ek paratha ghee ke saath, "
    "aur ek cup dahi. phir ek cup chai bhi."
)


async def main():
    print("=== Sample transcription ===")
    print(SAMPLE_TRANSCRIPTION)
    print()

    print("=== Extracting ingredients ===")
    ingredients = await extract_ingredients(SAMPLE_TRANSCRIPTION)
    for ing in ingredients:
        print(f"  {ing.quantity} {ing.unit} {ing.ingredient}")
    print()

    print("=== Nutrition lookup ===")
    items = await lookup_nutrition(ingredients)
    for item in items:
        print(
            f"  {item.ingredient_name:<25} "
            f"cal={item.calories:>6.1f}  "
            f"protein={item.protein:>5.1f}g  "
            f"carbs={item.carbs:>5.1f}g  "
            f"fat={item.fat:>5.1f}g  "
            f"[{item.source}]"
        )
    print()
    print(f"  {'TOTAL':<25} cal={sum(i.calories for i in items):>6.1f}  "
          f"protein={sum(i.protein for i in items):>5.1f}g  "
          f"carbs={sum(i.carbs for i in items):>5.1f}g  "
          f"fat={sum(i.fat for i in items):>5.1f}g")


async def usda_check():
    """Quick USDA key smoke test — one lookup, no Gemini."""
    import httpx
    from app.config import settings

    key = settings.usda_api_key
    masked = key[:6] + "..." + key[-4:] if len(key) > 10 else key
    print(f"=== USDA key check (key: {masked}) ===")

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(
            "https://api.nal.usda.gov/fdc/v1/foods/search",
            params={"query": "egg", "api_key": key, "pageSize": 1},
        )

    if resp.status_code == 200:
        food = resp.json().get("foods", [{}])[0]
        print(f"  OK — got: {food.get('description', '(no description)')}")
    else:
        print(f"  FAIL {resp.status_code}: {resp.text}")


if "--usda" in sys.argv:
    asyncio.run(usda_check())
else:
    asyncio.run(main())
