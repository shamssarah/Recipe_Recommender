import json

def load_recipes(path="data/recipes_with_tags.json"):
    with open(path) as f:
        return json.load(f)