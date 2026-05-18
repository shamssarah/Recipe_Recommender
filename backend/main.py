from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from backend.data_loader import load_recipes
from backend.logic.matching_logic import match_recipes

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")

RECIPES = load_recipes()

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
        return {"error": "Recipe not found"}, 404
    return recipe

@app.get("/ingredients")
def get_ingredients():
    all_ingredients = set()
    for recipe in RECIPES:
        all_ingredients.update(recipe['tag']['base'])
        # all_ingredients.update(recipe['tag']['specific'])
    return sorted(list(all_ingredients))