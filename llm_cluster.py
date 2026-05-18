import google.generativeai as genai
import pandas as pd
import json
import time
import os
from dotenv import load_dotenv
import os

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-flash-latest")  # free tier model
#gemini-flash-latest
def canonicalize_batch(phrases: list[str]) -> dict:
    phrase_list = "\n".join(f"- {p}" for p in phrases)

    prompt = f"""You are a culinary data normalizer.

For each phrase below, return a JSON object mapping the phrase to either:
- An object with "base" and "specific" keys, each containing a list of canonical ingredient names
- null if the phrase contains NO ingredient at all

"base" = broadest interchangeable form (used for loose matching)
"specific" = exact store-bought form (used for precise matching)
For most ingredients base and specific are identical — only differ when form meaningfully changes the dish.

Rules:

1. STRIP all preparation methods — these are noise:
   - Physical: minced, chopped, diced, sliced, cubed, shredded, crushed, crumbled, halved, quartered, torn, overripe, chunks
   - State: softened, melted, beaten, thawed, cooked, heated, cooled, warmed, chilled, refrigerated
   - Trim: peeled, seeded, cored, trimmed, drained, rinsed, zested, grated
   - Size: thick, thin, fine, coarse, inch, pieces, florets
   - Noise suffixes: "to taste", "or more", "as needed", "room temperature", "garnish"
   - Section headers: "for the sauce", "for the crust", "for the rest" → null
   - EXCEPTION — these look like methods but ARE ingredients, keep them:
     "bread crumbs", "breadcrumbs", "croutons", "drippings", "zest"

2. BASE vs SPECIFIC — guiding principle:
   If substituting form A for form B would ruin the dish → keep specific, do NOT generalize base.
   If substituting form A for form B is a reasonable everyday swap → generalize base.

   Meat cuts — always differentiate:
   - "ground beef" → {{"base": ["beef"], "specific": ["ground beef"]}}
   - "chicken breast" → {{"base": ["chicken"], "specific": ["chicken breast"]}}
   - "minced chicken" → {{"base": ["chicken"], "specific": ["ground chicken"]}}
   - "pork loin" → {{"base": ["pork"], "specific": ["pork loin"]}}
   - "cod fillet", "boneless cod" → {{"base": ["cod"], "specific": ["cod fillet"]}}

   Dairy — only generalize if interchangeable in everyday cooking:
   - "skim milk", "whole milk", "2% milk" → {{"base": ["milk"], "specific": ["skim milk"]}} etc.
   - "condensed milk", "sweetened condensed milk" → {{"base": ["condensed milk"], "specific": ["condensed milk"]}}
   - "evaporated milk" → {{"base": ["evaporated milk"], "specific": ["evaporated milk"]}}
   - "heavy cream", "whipping cream" → {{"base": ["cream"], "specific": ["heavy cream"]}}

   Flour — always differentiate:
   - "all-purpose flour" → {{"base": ["flour"], "specific": ["all-purpose flour"]}}
   - "bread flour" → {{"base": ["flour"], "specific": ["bread flour"]}}
   - "whole wheat flour" → {{"base": ["flour"], "specific": ["whole wheat flour"]}}

   Stock/broth — always differentiate:
   - "chicken broth", "chicken stock" → {{"base": ["broth"], "specific": ["chicken broth"]}}
   - "beef broth" → {{"base": ["broth"], "specific": ["beef broth"]}}

   Everything else — base and specific are identical:
   - "garlic" → {{"base": ["garlic"], "specific": ["garlic"]}}
   - "dried oregano" → {{"base": ["oregano"], "specific": ["oregano"]}}
   - "ground cumin" → {{"base": ["cumin"], "specific": ["cumin"]}}
   - "unsalted butter" → {{"base": ["butter"], "specific": ["butter"]}}
   - "fresh ginger" → {{"base": ["ginger"], "specific": ["ginger"]}}

3. GENERALIZE — strip brand names and regional variants:
   - "kosher salt", "sea salt", "himalayan salt" → {{"base": ["salt"], "specific": ["salt"]}}
   - "extra virgin olive oil" → {{"base": ["olive oil"], "specific": ["olive oil"]}}
   - "confectioners sugar", "powdered sugar", "caster sugar" → {{"base": ["powdered sugar"], "specific": ["powdered sugar"]}}
   - "campbell's cream of mushroom" → {{"base": ["cream of mushroom soup"], "specific": ["cream of mushroom soup"]}}
   - "betty crocker cake mix" → {{"base": ["cake mix"], "specific": ["cake mix"]}}
   - "reynolds wrap aluminum foil" → null (not an ingredient)

4. SPLIT compound phrases — apply base/specific to each part:
   - "salt and pepper" → {{"base": ["salt", "black pepper"], "specific": ["salt", "black pepper"]}}
   - "oil and vinegar" → {{"base": ["oil", "vinegar"], "specific": ["oil", "vinegar"]}}

5. COLLAPSE duplicates:
   - "cloves garlic", "garlic minced", "minced garlic" → {{"base": ["garlic"], "specific": ["garlic"]}}
   - "cream of mushroom", "cream of mushroom soup" → {{"base": ["cream of mushroom soup"], "specific": ["cream of mushroom soup"]}}
   - "pepper taste", "black pepper taste" → {{"base": ["black pepper"], "specific": ["black pepper"]}}

6. Return null ONLY when the entire phrase has no ingredient:
   - "cut inch" → null
   - "room temperature" → null
   - "finely chopped" → null
   - "fluid ounces" → null
   - "for the sauce" → null
   - "for the rest" → null

Return ONLY valid JSON. No explanation, no markdown, no backticks.

Phrases:
{phrase_list}

Format:
{{
  "phrase": {{"base": ["ingredient"], "specific": ["ingredient"]}} or null
}}"""


    response = model.generate_content(prompt)
    raw = response.text.strip()
    
    # strip markdown code fences if Gemini adds them
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    
    return json.loads(raw.strip())


def build_canonical_map(csv_path: str, output_path: str = "canonical_map.json"):
    df = pd.read_csv(csv_path)
    phrases = df["Phrase"].tolist()

    canonical_map = {}
    batch_size = 50

    for i in range(0, len(phrases), batch_size):
        batch = phrases[i:i + batch_size]
        print(f"Batch {i // batch_size + 1} / {-(-len(phrases) // batch_size)}...")

        try:
            result = canonicalize_batch(batch)
            canonical_map.update(result)
        except json.JSONDecodeError as e:
            print(f"  JSON parse failed on batch {i}, skipping. Error: {e}")
        except Exception as e:
            print(f"  Error: {e}")

        time.sleep(3)  # free tier: 15 RPM, so 1s between calls is safe

    ingredients_only = {k: v for k, v in canonical_map.items() if v is not None}
    noise = [k for k, v in canonical_map.items() if v is None]

    with open(output_path, "w") as f:
        json.dump(canonical_map, f, indent=2)

    print(f"\nDone — {len(ingredients_only)} ingredients, {len(noise)} noise phrases removed.")
    print(f"Saved to {output_path}")
    return canonical_map


if __name__ == "__main__":
    build_canonical_map("data/1000_2000_phrases.csv")