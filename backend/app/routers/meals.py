from fastapi import APIRouter, Depends, HTTPException
import aiosqlite
from app.database import get_db
from app.models import MealLogRequest, MealLogResponse, MealLogItemResponse, DayMealsResponse, DaySummary, HistoryResponse

router = APIRouter()

VALID_MEAL_SLOTS = {"breakfast", "lunch", "dinner", "snacks"}


async def _fetch_meal_log(db: aiosqlite.Connection, meal_log_id: int) -> MealLogResponse:
    async with db.execute(
        "SELECT id, date, meal_slot, transcription, created_at FROM meal_logs WHERE id = ?",
        (meal_log_id,),
    ) as cursor:
        row = await cursor.fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail=f"Meal log {meal_log_id} not found")

    log = dict(row)

    async with db.execute(
        "SELECT id, ingredient_name, quantity, unit, calories, protein, carbs, fat, source "
        "FROM meal_log_items WHERE meal_log_id = ?",
        (meal_log_id,),
    ) as cursor:
        item_rows = await cursor.fetchall()

    items = [MealLogItemResponse(**dict(r)) for r in item_rows]
    return MealLogResponse(**log, items=items)


@router.post("/meals", response_model=MealLogResponse, status_code=201)
async def create_meal(request: MealLogRequest, db: aiosqlite.Connection = Depends(get_db)):
    """Log a meal with its nutritional breakdown."""
    if request.meal_slot not in VALID_MEAL_SLOTS:
        raise HTTPException(
            status_code=400,
            detail=f"meal_slot must be one of {sorted(VALID_MEAL_SLOTS)}",
        )

    async with db.execute(
        "INSERT INTO meal_logs (date, meal_slot, transcription) VALUES (?, ?, ?)",
        (request.date, request.meal_slot, request.transcription),
    ) as cursor:
        meal_log_id = cursor.lastrowid

    for item in request.items:
        await db.execute(
            "INSERT INTO meal_log_items "
            "(meal_log_id, ingredient_name, quantity, unit, calories, protein, carbs, fat, source) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                meal_log_id,
                item.ingredient_name,
                item.quantity,
                item.unit,
                item.calories,
                item.protein,
                item.carbs,
                item.fat,
                item.source,
            ),
        )

    await db.commit()
    return await _fetch_meal_log(db, meal_log_id)


@router.get("/meals/history", response_model=HistoryResponse)
async def get_meal_history(offset: int = 0, limit: int = 20, db: aiosqlite.Connection = Depends(get_db)):
    """Get paginated meal history grouped by date, newest first."""
    # Fetch limit+1 dates to determine has_more
    async with db.execute(
        "SELECT DISTINCT date FROM meal_logs ORDER BY date DESC LIMIT ? OFFSET ?",
        (limit + 1, offset),
    ) as cursor:
        date_rows = await cursor.fetchall()

    has_more = len(date_rows) > limit
    dates = [row["date"] for row in date_rows[:limit]]

    days = []
    for date in dates:
        async with db.execute(
            "SELECT id FROM meal_logs WHERE date = ? ORDER BY created_at DESC",
            (date,),
        ) as cursor:
            meal_rows = await cursor.fetchall()

        meals = [await _fetch_meal_log(db, row["id"]) for row in meal_rows]
        total_calories = round(sum(item.calories for meal in meals for item in meal.items), 2)
        days.append(DaySummary(date=date, total_calories=total_calories, meals=meals))

    return HistoryResponse(days=days, has_more=has_more)


@router.get("/meals", response_model=DayMealsResponse)
async def get_meals(date: str, db: aiosqlite.Connection = Depends(get_db)):
    """Get all meals logged for a given date (YYYY-MM-DD)."""
    async with db.execute(
        "SELECT id FROM meal_logs WHERE date = ?", (date,)
    ) as cursor:
        rows = await cursor.fetchall()

    meals = [await _fetch_meal_log(db, row["id"]) for row in rows]

    total_calories = round(
        sum(item.calories for meal in meals for item in meal.items), 2
    )

    return DayMealsResponse(date=date, meals=meals, total_calories=total_calories)
