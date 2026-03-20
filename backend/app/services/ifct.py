"""
IFCT 2017 in-memory nutrition lookup service.

Loads backend/data/ifct2017.json once on import and exposes lookup_ifct().
Matching tiers (in order):
  1. Exact alias match (lowercased, stripped)
  1b. Strip common suffixes ("curry", "cooked", "raw", "boiled", "fried"), retry
  2. Token Jaccard similarity over all food names (threshold 0.5)
"""

import json
import os
from functools import lru_cache

_DATA_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "ifct2017.json"
)

# Populated by initialize() at app startup
_foods: dict = {}          # code -> record dict
_alias_index: dict = {}    # lowercase alias -> food code
_token_sets: dict = {}     # code -> list of pre-tokenized sets (name + aliases)

_STRIP_SUFFIXES = {"curry", "cooked", "raw", "boiled", "fried", "roasted", "grilled", "steamed"}


def _ensure_loaded() -> None:
    """Load the JSON file and build indexes. Safe to call multiple times."""
    global _foods, _alias_index, _token_sets
    if _foods:
        return

    path = os.path.normpath(_DATA_PATH)
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"IFCT data not found at {path}. "
            "Run backend/scripts/compile_ifct.py to generate it."
        )

    with open(path, encoding="utf-8") as f:
        _foods = json.load(f)

    for code, record in _foods.items():
        for alias in record.get("aliases", []):
            _alias_index[alias.lower().strip()] = code
        # Also index the canonical name
        _alias_index[record["name"].lower().strip()] = code
        # Pre-tokenize name + all aliases for fuzzy matching
        _token_sets[code] = [
            set(record["name"].lower().split()),
            *[set(a.lower().split()) for a in record.get("aliases", [])],
        ]


def initialize() -> None:
    """Load IFCT data at app startup. Call once from the lifespan hook."""
    _ensure_loaded()


def _jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _best_fuzzy(query: str) -> str | None:
    """Return the food code with highest token Jaccard score, or None if < 0.5."""
    q_tokens = set(query.lower().split())
    best_code, best_score = None, 0.0
    for code, token_sets in _token_sets.items():
        score = max(_jaccard(q_tokens, ts) for ts in token_sets)
        if score > best_score:
            best_code, best_score = code, score
    return best_code if best_score >= 0.5 else None


@lru_cache(maxsize=512)
def lookup_ifct(ingredient_name: str) -> dict | None:
    """
    Look up nutrition for ingredient_name in the IFCT 2017 dataset.

    Returns a dict with keys:
        calories (kcal/100g), protein (g/100g), carbs (g/100g),
        fat (g/100g), source="ifct"
    or None if no confident match found.
    """
    _ensure_loaded()
    name = ingredient_name.lower().strip()

    # Tier 1: exact alias match
    code = _alias_index.get(name)

    # Tier 1b: strip trailing suffix words and retry
    if code is None:
        words = name.split()
        stripped = " ".join(w for w in words if w not in _STRIP_SUFFIXES).strip()
        if stripped and stripped != name:
            code = _alias_index.get(stripped)

    # Tier 2: token Jaccard fuzzy match
    if code is None:
        code = _best_fuzzy(name)

    if code is None:
        return None

    record = _foods[code]
    return {
        "calories": record["energy_kcal"],
        "protein": record["protein_g"],
        "carbs": record["carb_g"],
        "fat": record["fat_g"],
        "source": "ifct",
    }
