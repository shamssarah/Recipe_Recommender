# WiseCook 🍳

A recipe recommendation system that matches recipes to the ingredients you actually have. Built to minimize grocery trips and reduce food waste.

## What it does

- Add ingredients you have to your pantry
- WiseCook finds recipes ranked by how many ingredients you already have
- Shows exactly what's missing and how close you are to making each dish
- Normalizes ingredient variants at index time — recipe ingredients like `garlic powder`, 
  `minced garlic`, `cloves garlic` all become the tag `garlic` via the canonical map
- Supports excluding ingredients you have but don't want to use e.g. to prioritize the use of ingredients that are nearing expiration
- Assumes common staples (salt, pepper, oil, water) are always available

## How it works

### Data Pipeline
The [Eight Portions recipe dataset](https://eightportions.com/datasets/Recipes/#fn:1) 
is processed through a multi-stage pipeline:

1. **Ingredient parser** — extracts quantity, unit, type, and ingredient name from raw strings using regex and NLTK POS tagging
   - Strips preparation methods (chopped, minced, diced) using POS tagging rather than hardcoded rules
   - Preserves meaningful type descriptors (dried, ground, fresh) as a separate field
   - Handles messy real-world data: `"2 (10.75 ounce) cans condensed cream of mushroom soup ADVERTISEMENT"` → `{ quantity: 2, unit: "(10.75 ounce) cans", type: "condensed", ingredient: "cream of mushroom soup" }`

2. **Canonical map** — normalizes ingredient variants using an LLM (Gemini Flash) - done on the top 1000 ingredients currently:
   - Maps messy phrases to clean canonical forms: `"cloves garlic"`, `"garlic minced"`, `"minced garlic"` → `"garlic"`
   - Two-tier structure:
     - `base` — broadest interchangeable form for loose matching (`"ground beef"` → `"beef"`)
     - `specific` — exact store form for precise matching (`"ground beef"` → `"ground beef"`)
   - Handles brand names, regional variants, compound phrases, and partial phrases

3. **Tag generation** — assigns base and specific tags to each recipe using fuzzy token overlap matching

### Matching Engine
- Merges user pantry with a configurable staples list
- Scores each recipe by coverage: `matched ingredients / total recipe ingredients`
- Supports `base` mode (loose) and `specific` mode (precise)
- Returns top N recipes sorted by coverage with missing ingredient list

### Backend
- FastAPI serving both the frontend pages and API endpoints
- Recipes loaded into memory on startup for fast matching

### Frontend
- Vanilla HTML/CSS/JS
- Ingredient chips with include/exclude toggle
- Live recipe cards updating on every pantry change

## Project Structure

```
project/
  backend/
    main.py           # FastAPI app and routes
    matcher.py        # matching engine
    data_loader.py    # loads processed recipes on startup
  frontend/
    static/
      css/main.css
      js/main.js
    templates/
      main_page.html
      view_recipe.html
  data/               # not included in repo — generate locally
    processed_recipes.json
    canonical_map.json
```

## Setup

### Prerequisites
```bash
pip install fastapi uvicorn nltk pandas google-generativeai python-dotenv
```

```python
import nltk
nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger_eng')
nltk.download('wordnet')
```

### Generate the data
```bash
# 1. Download the AllRecipes dataset from Kaggle:
# https://www.kaggle.com/datasets/nguyentuongquang/all-recipes

# 2. Run the canonicalization script (requires Gemini API key)
export GEMINI_API_KEY=your_key_here
python data/build_canonical_map.py

# 3. Process the recipes
python data/process_recipes.py
```

### Run
```bash
uvicorn backend.main:app --reload
```

Visit `http://127.0.0.1:8000`

## Roadmap

- [ ] Receipt OCR scanning to auto-populate pantry
- [ ] Cuisine preference learning
- [ ] Collaborative filtering — "users with similar taste liked..."
- [ ] Nutrition tracking (protein, fiber, calories per recipe)
- [ ] User accounts and persistent pantry
- [ ] Expanded recipe dataset via scraping
- [ ] "Almost ready" shelf — recipes needing only 1-2 more items with cheapest buy suggestions

## Data
- Dataset: Eight Portions recipe dataset (https://eightportions.com/datasets/Recipes/#fn:1) not included in repo — run pipeline locally to generate

The canonical ingredient map is generated using the Gemini Flash API and cached locally as `canonical_map.json`.
