"""Tests for the IFCT 2017 in-memory lookup service."""

import pytest
from app.services.ifct import lookup_ifct, _ensure_loaded


@pytest.fixture(autouse=True)
def load_data():
    _ensure_loaded()


def test_exact_alias_match():
    result = lookup_ifct("rice")
    assert result is not None
    assert result["calories"] > 0


def test_alias_case_insensitive():
    lower = lookup_ifct("rice")
    upper = lookup_ifct("RICE")
    mixed = lookup_ifct("Rice")
    assert lower is not None
    assert lower == upper == mixed


def test_hinglish_alias():
    result = lookup_ifct("chawal")
    assert result is not None
    # chawal is rice — should have substantial calories
    assert result["calories"] > 200


def test_suffix_stripping():
    result = lookup_ifct("lentil curry")
    assert result is not None
    # "curry" stripped -> "lentil" -> matches masoor dal / dal entries
    assert result["calories"] > 0


def test_fuzzy_match_partial():
    result = lookup_ifct("masoor")
    assert result is not None
    assert result["protein"] > 0


def test_no_match_returns_none():
    result = lookup_ifct("cheeseburger")
    assert result is None


def test_nutrient_values_are_floats():
    result = lookup_ifct("egg")
    assert result is not None
    for key in ("calories", "protein", "carbs", "fat"):
        assert isinstance(result[key], float), f"{key} should be float"


def test_source_is_ifct():
    result = lookup_ifct("paneer")
    assert result is not None
    assert result["source"] == "ifct"


def test_paratha_lookup():
    result = lookup_ifct("paratha")
    assert result is not None
    assert result["calories"] > 0


def test_chai_lookup():
    result = lookup_ifct("chai")
    assert result is not None
    assert result["calories"] > 0


def test_dahi_alias():
    result = lookup_ifct("dahi")
    assert result is not None
    assert result["protein"] > 0
