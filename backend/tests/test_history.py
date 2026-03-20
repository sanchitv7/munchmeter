"""Tests for GET /api/meals/history endpoint."""

import pytest
import pytest_asyncio
import httpx
from httpx import AsyncClient, ASGITransport

from app.main import app


# ── Helpers ───────────────────────────────────────────────────────────────────

def _meal_payload(date: str, meal_slot: str = "lunch", calories: float = 200.0) -> dict:
    return {
        "date": date,
        "meal_slot": meal_slot,
        "transcription": None,
        "items": [
            {
                "ingredient_name": "rice",
                "quantity": 100.0,
                "unit": "g",
                "calories": calories,
                "protein": 3.0,
                "carbs": 28.0,
                "fat": 0.5,
                "source": "ifct",
            }
        ],
    }


@pytest_asyncio.fixture
async def client():
    from app.database import get_db

    # Clean all meal data before each test
    async for db in get_db():
        await db.execute("DELETE FROM meal_log_items")
        await db.execute("DELETE FROM meal_logs")
        await db.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ── Tests ─────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_history_empty(client):
    """History with no meals returns empty days list."""
    resp = await client.get("/api/meals/history")
    assert resp.status_code == 200
    body = resp.json()
    assert "days" in body
    assert "has_more" in body
    assert isinstance(body["days"], list)
    assert body["has_more"] is False


@pytest.mark.asyncio
async def test_history_returns_grouped_by_date(client):
    """Meals on different dates appear as separate day entries."""
    # Create meals on two distinct dates
    r1 = await client.post("/api/meals", json=_meal_payload("2026-01-01", calories=300.0))
    assert r1.status_code == 201
    r2 = await client.post("/api/meals", json=_meal_payload("2026-01-02", calories=500.0))
    assert r2.status_code == 201

    resp = await client.get("/api/meals/history")
    assert resp.status_code == 200
    body = resp.json()

    dates = [d["date"] for d in body["days"]]
    assert "2026-01-01" in dates
    assert "2026-01-02" in dates
    # Newest first
    assert dates.index("2026-01-02") < dates.index("2026-01-01")


@pytest.mark.asyncio
async def test_history_total_calories_aggregated(client):
    """total_calories for a day sums all items across all meals."""
    date = "2026-01-03"
    await client.post("/api/meals", json=_meal_payload(date, meal_slot="breakfast", calories=150.0))
    await client.post("/api/meals", json=_meal_payload(date, meal_slot="dinner", calories=350.0))

    resp = await client.get("/api/meals/history")
    assert resp.status_code == 200
    body = resp.json()

    day = next((d for d in body["days"] if d["date"] == date), None)
    assert day is not None
    assert day["total_calories"] == pytest.approx(500.0)
    assert len(day["meals"]) == 2


@pytest.mark.asyncio
async def test_history_pagination_has_more(client):
    """has_more is True when there are more dates beyond the requested limit."""
    # Create 3 meals on distinct dates
    for i in range(4, 7):
        await client.post("/api/meals", json=_meal_payload(f"2026-01-{i:02d}"))

    # Request only 1 date at a time
    resp = await client.get("/api/meals/history?limit=1&offset=0")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["days"]) == 1
    assert body["has_more"] is True


@pytest.mark.asyncio
async def test_history_pagination_offset(client):
    """Offset skips the first N dates."""
    for i in range(10, 13):
        await client.post("/api/meals", json=_meal_payload(f"2026-02-{i:02d}"))

    resp_page1 = await client.get("/api/meals/history?limit=2&offset=0")
    resp_page2 = await client.get("/api/meals/history?limit=2&offset=2")

    page1_dates = {d["date"] for d in resp_page1.json()["days"]}
    page2_dates = {d["date"] for d in resp_page2.json()["days"]}
    # Pages should not overlap
    assert page1_dates.isdisjoint(page2_dates)


@pytest.mark.asyncio
async def test_history_response_structure(client):
    """Each day in the response has the expected fields."""
    date = "2026-03-01"
    await client.post("/api/meals", json=_meal_payload(date))

    resp = await client.get("/api/meals/history")
    assert resp.status_code == 200
    body = resp.json()

    day = next((d for d in body["days"] if d["date"] == date), None)
    assert day is not None
    assert "date" in day
    assert "total_calories" in day
    assert "meals" in day
    meal = day["meals"][0]
    assert "id" in meal
    assert "meal_slot" in meal
    assert "items" in meal
