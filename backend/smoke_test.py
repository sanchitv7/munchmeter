"""
Smoke test: extraction + nutrition lookup without the frontend.
Run from backend/ with the venv active:
    uv run python smoke_test.py
"""

import asyncio
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


asyncio.run(main())
