from collections import Counter

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from backend.data_loader import load_recipes
from backend.logic.matching_logic import match_recipes



# -------------------- STARTUP --------------------

RECIPES = load_recipes()

all_ingredients = []
for recipe in RECIPES:
    all_ingredients.extend(recipe['tag']['base'])

counts = Counter(all_ingredients)
SORTED_INGREDIENTS = [item for item, _ in counts.most_common()]  # all, sorted by freq

#-------------------- APP SETUP --------------------


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")


# --- Page routes ---
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("main_page.html", {"request": request})

@app.get("/recipe")
def recipe_page(request: Request):
    return templates.TemplateResponse("view_recipe.html", {"request": request})

# --- API routes ---
@app.post("/match")
def match(payload: dict):
    ingredients = payload.get("ingredients", [])
    mode = payload.get("mode", "base")
    return match_recipes(ingredients, RECIPES, mode=mode)

@app.get("/recipe/{recipe_id}")
def get_recipe(recipe_id: int):
    recipe = next((r for r in RECIPES if r['id'] == recipe_id), None)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe

@app.get("/ingredients/common")
def get_common_ingredients():
    return SORTED_INGREDIENTS[:2000]  # top 2000, called once on frontend init

@app.get("/ingredients/search")
def search_ingredients(q: str):
    if len(q) < 3:
        return []
    q_lower = q.lower()
    matches = [i for i in SORTED_INGREDIENTS if q_lower in i.lower()]
    return matches[:10]
