import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")  # free tier model


def process_data(recipes: list[dict], batch_size: int = 25) -> dict:
    """
    recipes: list of {"id": ..., "name": ..., "description": ...}
    returns: dict mapping id -> {"cuisine": [...], "meal_type": [...]} or None
    """
    results = {}

    for i in range(0, len(recipes), batch_size):
        batch = recipes[i:i + batch_size]

        phrase_list = "\n".join(
            f'- id: {r["id"]}, name: "{r["name"]}", description: "{r.get("description", "")}"'
            for r in batch
        )

        prompt = f"""You are a culinary data normalizer.
For each recipe below, determine its cuisine and meal type, then return a JSON object.

Rules:
1. Use the name first to determine cuisine and meal_type.
2. Use the description (if provided) to refine or confirm.
3. If name and description agree, use that answer. If they disagree, prefer the more specific one. If both are equally specific and genuinely different, include both (max 2 values per field).
4. meal_type must be one of: ["breakfast", "lunch", "dinner", "dessert", "appetizer", "side", "beverage", "snack", "main"]. Use "main" only when a dish is generic enough to fit both lunch and dinner.
5. cuisine should be a specific region/style (e.g. "Italian", "Mexican", "Japanese"), not vague ("international", "fusion" allowed only if genuinely mixed).
6. If a recipe has no discernible cuisine or meal type at all, use null for that field.

Recipes:
{phrase_list}

Return ONLY a valid JSON object (no markdown, no explanation) in this exact shape:
{{
    "<id>": {{"cuisine": ["..."], "meal_type": ["..."]}},
    "<id>": null,
    ...
}}
"""

        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"},
        )

        try:
            parsed = json.loads(response.text)
            results.update(parsed)
        except (json.JSONDecodeError, AttributeError) as e:
            print(f"Failed to parse batch starting at index {i}: {e}")
            # fall back: mark this whole batch as failed so you can retry/inspect later
            for r in batch:
                results[str(r["id"])] = {"error": "parse_failed"}

    return results