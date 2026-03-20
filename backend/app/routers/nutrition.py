from fastapi import APIRouter, HTTPException
from app.models import NutritionLookupRequest, NutritionLookupResponse
from app.services.nutrition import lookup_nutrition

router = APIRouter()


@router.post("/nutrition-lookup", response_model=NutritionLookupResponse)
async def nutrition_lookup(request: NutritionLookupRequest):
    """Look up nutrition data for a list of ingredients using USDA FoodData Central."""
    if not request.ingredients:
        raise HTTPException(status_code=400, detail="Ingredients list cannot be empty")

    try:
        items = await lookup_nutrition(request.ingredients)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    return NutritionLookupResponse(
        items=items,
        total_calories=round(sum(i.calories for i in items), 2),
        total_protein=round(sum(i.protein for i in items), 2),
        total_carbs=round(sum(i.carbs for i in items), 2),
        total_fat=round(sum(i.fat for i in items), 2),
    )
