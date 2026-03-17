from fastapi import APIRouter, HTTPException
from app.models import ExtractIngredientsRequest, ExtractIngredientsResponse
from app.services.ingredient_parser import extract_ingredients

router = APIRouter()


@router.post("/extract-ingredients", response_model=ExtractIngredientsResponse)
async def extract(request: ExtractIngredientsRequest):
    """Extract structured ingredients from a meal transcription using Gemini."""
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    ingredients = await extract_ingredients(request.text)
    return ExtractIngredientsResponse(ingredients=ingredients)
