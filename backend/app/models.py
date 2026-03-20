from pydantic import BaseModel
from typing import Optional


# --- Transcription ---

class TranscriptionResponse(BaseModel):
    text: str


# --- Ingredient Extraction ---

class Ingredient(BaseModel):
    ingredient: str
    quantity: float
    unit: str


class ExtractIngredientsRequest(BaseModel):
    text: str


class ExtractIngredientsResponse(BaseModel):
    ingredients: list[Ingredient]


# --- Nutrition Lookup ---

class NutritionLookupRequest(BaseModel):
    ingredients: list[Ingredient]


class NutritionItem(BaseModel):
    ingredient_name: str
    quantity: float
    unit: str
    calories: float
    protein: float
    carbs: float
    fat: float
    source: str  # "ifct" | "usda" | "not_found"


class NutritionLookupResponse(BaseModel):
    items: list[NutritionItem]
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float


# --- Meal Logging ---

class MealLogRequest(BaseModel):
    date: str                   # YYYY-MM-DD
    meal_slot: str              # breakfast | lunch | dinner | snacks
    transcription: Optional[str] = None
    items: list[NutritionItem]


class MealLogItemResponse(BaseModel):
    id: int
    ingredient_name: str
    quantity: float
    unit: str
    calories: float
    protein: float
    carbs: float
    fat: float
    source: str


class MealLogResponse(BaseModel):
    id: int
    date: str
    meal_slot: str
    transcription: Optional[str]
    created_at: str
    items: list[MealLogItemResponse]


class DayMealsResponse(BaseModel):
    date: str
    meals: list[MealLogResponse]
    total_calories: float


# --- Meal History ---

class DaySummary(BaseModel):
    date: str
    total_calories: float
    meals: list[MealLogResponse]


class HistoryResponse(BaseModel):
    days: list[DaySummary]
    has_more: bool
