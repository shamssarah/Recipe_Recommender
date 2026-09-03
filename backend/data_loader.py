import json

def load_recipes(path="data/processed_recipes.json"):
    with open(path,'r', encoding='utf-8') as f:
        recipes = json.load(f)
    for i, recipe in enumerate(recipes):
        recipe['id'] = i
    print (f"Loaded {len(recipes)} recipes.")
    print (f"Example recipe: {recipes[0]['title']} with id {recipes[0]['id']}")
    return recipes