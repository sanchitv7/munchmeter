"""Tests for the nutrition lookup service (IFCT + USDA parallel lookup)."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models import Ingredient, NutritionItem
from app.services import nutrition as nutrition_mod
from app.services.nutrition import (
    _resolve_gram_weight,
    _lookup_one,
    lookup_nutrition,
)


# ── Helpers ──────────────────────────────────────────────────────────────────

def make_ing(name: str, qty: float = 1.0, unit: str = "piece") -> Ingredient:
    return Ingredient(ingredient=name, quantity=qty, unit=unit)


def make_client() -> MagicMock:
    """Return a mock httpx.AsyncClient."""
    return MagicMock()


# ── _resolve_gram_weight ──────────────────────────────────────────────────────

def test_gram_weight_weight_unit():
    ing = make_ing("rice", qty=100.0, unit="g")
    assert _resolve_gram_weight(ing, []) == 100.0


def test_gram_weight_kg_unit():
    ing = make_ing("rice", qty=0.1, unit="kg")
    assert _resolve_gram_weight(ing, []) == pytest.approx(100.0)


def test_gram_weight_volume_cup():
    ing = make_ing("milk", qty=1.0, unit="cup")
    assert _resolve_gram_weight(ing, []) == 240.0


def test_piece_weight_roti_corrected():
    """Roti should now be 40 g/piece, not the old 80 g."""
    ing = make_ing("roti", qty=1.0, unit="piece")
    assert _resolve_gram_weight(ing, []) == 40.0


def test_piece_weight_fallback_when_no_portions():
    ing = make_ing("roti", qty=2.0, unit="piece")
    result = _resolve_gram_weight(ing, [])
    assert result == 80.0  # 2 × 40


def test_usda_portions_used_for_piece_unit():
    ing = make_ing("bread", qty=1.0, unit="piece")
    portions = [{"gramWeight": 45.0}]
    assert _resolve_gram_weight(ing, portions) == 45.0


def test_unknown_unit_treats_as_grams():
    ing = make_ing("salt", qty=5.0, unit="pinch")
    assert _resolve_gram_weight(ing, []) == 5.0


# ── _lookup_one ───────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_lookup_ifct_wins_over_usda():
    """IFCT hit -> source='ifct', USDA _fetch_usda must never be called."""
    client = make_client()
    with patch.object(nutrition_mod, "_fetch_usda", new_callable=AsyncMock) as mock_usda:
        item = await _lookup_one(client, make_ing("rice", qty=100.0, unit="g"))
    assert item.source == "ifct"
    mock_usda.assert_not_called()


@pytest.mark.asyncio
async def test_lookup_usda_fallback():
    """IFCT miss -> USDA hit -> source='usda'."""
    client = make_client()
    usda_payload = {
        "nutrients": {
            "Energy": 52.0,
            "Protein": 0.3,
            "Carbohydrate, by difference": 14.0,
            "Total lipid (fat)": 0.2,
        },
        "portions": [],
    }
    with patch.object(nutrition_mod, "lookup_ifct", return_value=None), \
         patch.object(nutrition_mod, "_fetch_usda", new_callable=AsyncMock, return_value=usda_payload):
        item = await _lookup_one(client, make_ing("apple", qty=100.0, unit="g"))
    assert item.source == "usda"
    assert item.calories == pytest.approx(52.0)


@pytest.mark.asyncio
async def test_lookup_not_found():
    """Both IFCT and USDA miss -> source='not_found', all nutrients=0."""
    client = make_client()
    with patch.object(nutrition_mod, "lookup_ifct", return_value=None), \
         patch.object(nutrition_mod, "_fetch_usda", new_callable=AsyncMock, return_value=None):
        item = await _lookup_one(client, make_ing("xyzunknownfood123"))
    assert item.source == "not_found"
    assert item.calories == 0.0
    assert item.protein == 0.0
    assert item.carbs == 0.0
    assert item.fat == 0.0


# ── lookup_nutrition (parallel gather) ──────────────────────────────────────

@pytest.mark.asyncio
async def test_parallel_gather_returns_all_in_order():
    """lookup_nutrition returns one NutritionItem per ingredient, in order."""
    ingredients = [
        make_ing("rice", 100.0, "g"),
        make_ing("egg", 1.0, "piece"),
        make_ing("paneer", 50.0, "g"),
    ]
    results = await lookup_nutrition(ingredients)
    assert len(results) == 3
    assert results[0].ingredient_name == "rice"
    assert results[1].ingredient_name == "egg"
    assert results[2].ingredient_name == "paneer"
    for r in results:
        assert isinstance(r, NutritionItem)
        assert r.source in ("ifct", "usda", "not_found")
