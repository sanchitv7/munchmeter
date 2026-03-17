import json
from google import genai
from google.genai import types
from app.config import settings
from app.models import Ingredient

HINGLISH_MAP = """
Common Hindi/Hinglish → English ingredient mappings (normalise before extraction):
- anda / ande / egg → egg
- roti / chapati / chapatti → chapati
- dahi / curd → yogurt
- ghee → clarified butter
- paratha / parantha → paratha
- dal / daal → lentil curry
- sabzi → vegetable curry
- paneer → cottage cheese (Indian)
- chawal / rice → rice
- aloo / potato → potato
- pyaaz / onion → onion
- tamatar / tomato → tomato
- doodh / milk → milk
- makhan / butter → butter
- namkeen → salted snack
"""

SYSTEM_PROMPT = f"""You are a nutrition assistant that extracts ingredients from meal descriptions.

{HINGLISH_MAP}

Extract ALL ingredients from the user's meal description. For each ingredient return:
- ingredient: English name (normalised from Hindi/Hinglish if needed)
- quantity: numeric amount (e.g. 2, 0.5, 100)
- unit: measurement unit (e.g. piece, gram, cup, tablespoon, slice)

If quantity is unclear, estimate a reasonable serving size.
Return ONLY valid JSON — an array of objects with keys: ingredient, quantity, unit.
"""


async def extract_ingredients(text: str) -> list[Ingredient]:
    """Use Gemini Flash to extract structured ingredients from a meal description."""
    client = genai.Client(api_key=settings.google_api_key)

    response = await client.aio.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=text,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            temperature=0.1,
        ),
    )

    raw = response.text.strip()
    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    data = json.loads(raw)
    return [Ingredient(**item) for item in data]
