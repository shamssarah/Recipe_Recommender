# STAPLES = {
#     'salt', 'water', 'black pepper', 'oil',  # universal
#     # everything below is "likely" but not guaranteed
#     'sugar', 'flour', 'butter', 'eggs', 'milk', 
#     'vegetable oil', 'garlic',
# }

# Users may or may not include everything that exist in their pantry
# so we want to consider common ingredients found in the cuisine they usually make
# however, that should not be rigid and should all user to exclude ingredient they may have run out of

# The cuisine they usually make can be explicitly asked at the time of user creation and from cooking history

# def matching for protein/fiber tracker
def match_recipes( user_ingredients: list[str], recipes: list[dict], top_n: int = 100, mode: str = 'base'):
    available = set(user_ingredients) #| STAPLES
    print(f"Available: {available}")
    
    # print first recipe tags to compare
    first = recipes[0]
    print(f"First recipe tags: {set(first['tag'][mode])} --> {first['title']}, {first['id']}")
    
    results = []
    for recipe in recipes:
        # use mode to decide which tags to match against
        tags = set(recipe['tag'][mode])  # 'base' or 'specific'
        
        matched = available & tags
        missing = tags - available
        coverage = len(matched) / len(tags) if tags else 0
        
        results.append({
            "id": recipe['id'],
            "title": recipe['title'],
            "coverage": round(coverage, 2),
            "ingredients": list(tags),
            "missing": list(missing),
            "matched": list(matched),
            "picture": recipe.get('picture_link', None)
        })
    
    return sorted(results, key=lambda x: x['coverage'], reverse=True)[:top_n]