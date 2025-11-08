from pydantic import BaseModel, Field
from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from typing import Dict, List, Optional
from model import Recipe

router = APIRouter(
    prefix="/recipes",  # All routes in this router will start with /recipes
    tags=["recipes"]
)

# --- 1. Pydantic Models for Ingredients and Recipes ---

# A. Model for a single item in the list (The Ingredient input)
class IngredientCreate(BaseModel):
    item: str = Field(..., description="Name of the ingredient (e.g., 'Flour', 'Milk').")
    quantity: str = Field(..., description="Quantity needed (e.g., '2 cups', '1/2 teaspoon').")
    # In a real app, you might add 'unit' and 'amount' fields


class RecipeUpdate(BaseModel):
    title: Optional[str] = None
    ingredients: Optional[List[str]] = None
    instructions: Optional[str] = None


# B. Model for the Recipe creation payload (The multiple input container)
class RecipeCreate(BaseModel):
    title: str = Field(..., min_length=5)
    description: str
    prepTime: str
    cookTime: str
    servings: int
    
    # CRITICAL: This field accepts a list of the IngredientCreate model.
    ingredients: List[IngredientCreate] = Field(
        ...,
        description="A list of ingredients required for the recipe."
    )
    
    instructions: List[str] = Field(..., description="List of step-by-step instructions.")

# C. Internal/Response Model (What the database stores and API returns)
# Includes an 'id' and a mock 'author_id' that the backend generates/manages
class Recipe(RecipeCreate):
    id: int
    author_id: int

# --- 2. In-Memory "Database" for Recipes ---

_recipes: Dict[int, Recipe] = {}
_id_counter = 1

# --- 3. Router Endpoints ---

@router.post("/", response_model=Recipe, status_code=status.HTTP_201_CREATED)
async def create_recipe(payload: RecipeCreate):
    """
    Creates a new recipe and stores it. 
    The payload validates the nested list of ingredients automatically.
    """
    global _id_counter
    rid = _id_counter
    
    # In a real app, author_id would come from an authentication token
    author_id = 101 
    
    # Create the full Recipe object for storage
    recipe = Recipe(id=rid, author_id=author_id, **payload.dict())
    _recipes[rid] = recipe
    _id_counter += 1
    
    return recipe

@router.get("/{recipe_id}", response_model=Recipe)
async def get_recipe(recipe_id: int):
    """Retrieves a single recipe by ID."""
    if recipe_id not in _recipes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe ID {recipe_id} not found."
        )
    return _recipes[recipe_id]






@router.get("/", response_model=List[Recipe])
async def list_recipes(ingredient: Optional[str] = Query(None, description="Filter recipes that contain this ingredient")):
    results = list(_recipes.values())
    if ingredient:
        ingredient_lower = ingredient.lower()
        results = [r for r in results if any(ingredient_lower in ing.lower() for ing in r.ingredients)]
    return results


@router.get("/{recipe_id}", response_model=Recipe)
async def get_recipe(recipe_id: int):
    recipe = _recipes.get(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


@router.put("/{recipe_id}", response_model=Recipe)
async def update_recipe(recipe_id: int, payload: RecipeUpdate):
    existing = _recipes.get(recipe_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Recipe not found")
    updated_data = existing.dict()
    update_fields = payload.dict(exclude_unset=True)
    updated_data.update(update_fields)
    updated = Recipe(**updated_data)
    _recipes[recipe_id] = updated
    return updated


@router.delete("/{recipe_id}", response_model=dict)
async def delete_recipe(recipe_id: int):
    if recipe_id not in _recipes:
        raise HTTPException(status_code=404, detail="Recipe not found")
    del _recipes[recipe_id]
    return {"deleted": recipe_id}

