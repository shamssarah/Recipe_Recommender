import pandas as pd
import json

from sklearn.feature_extraction.text import CountVectorizer
from nltk.stem import WordNetLemmatizer
from parsing_utils import parse_ingredient, singularize

lemmatizer = WordNetLemmatizer()

TAG_PATH = "./data/canonical_map.json"
DATASET = "./data/recipes_reduced.json"

tagging_map = json.load(open(TAG_PATH, "r"))
tagging_map = {k: v for k, v in tagging_map.items() if v is not None}

def ingredient_match(tag: str, query: str) -> bool:
    tag_tokens = set(tag.lower().split())
    query_tokens = set(query.lower().split())
    if not tag_tokens or not query_tokens:
        return False
    overlap = tag_tokens & query_tokens
    return len(overlap) / max(len(tag_tokens), len(query_tokens)) >= 0.70

def attach_tags(recipe):
    base_tags = set()
    specific_tags = set()
    
    for item in recipe:
        ingredient = item['ingredient'].lower().strip()
        matched = False

        for key, value in tagging_map.items():
            if ingredient_match(key, ingredient):
                if value is not None:
                    base_tags.update(value['base'])
                    specific_tags.update(value['specific'])
                matched = True

        if not matched and ingredient:
            base_tags.add(ingredient)
            specific_tags.add(ingredient)

    return {
        "base": [singularize(t) for t in base_tags if t.strip()],
        "specific": [singularize(t) for t in specific_tags if t.strip()]
    }

def generate_phrase_frequencies(corpus_series, output_path='./data/reduced_phrases.csv'):
    corpus = [item['ingredient'] for sublist in corpus_series for item in sublist if item.get('ingredient')]
    vectorizer = CountVectorizer(ngram_range=(2, 3), stop_words='english')
    X = vectorizer.fit_transform(corpus)
    
    df = pd.DataFrame({
        'Phrase': vectorizer.get_feature_names_out(), 
        'Frequency': X.sum(axis=0).A1
    }).sort_values(by='Frequency', ascending=False)
    
    df.to_csv(output_path, index=False)
    print(f"------- Phrase frequencies saved to {output_path} -------")


def testing():
    
    print("--- RUNNING PARSER & TAGGER TEST ---\n")
    
    test_ingredients = [
        "4 chicken breast tenderloins, cut into bite-size pieces",
        "salt and ground black pepper to taste",
        "2 tablespoons extra-virgin olive oil, divided",
        "2 stalks celery, finely chopped",
        "2 small carrots, finely chopped",
        "3 cloves garlic, finely chopped",
        "2 (14 ounce) cans chicken broth",
        "2 cups medium egg noodles"
    ]
    
    # 1. Run your real parser
    parsed_results = parse_ingredient(test_ingredients)
    print("--- 1. PARSED INGREDIENTS ---")
    print(json.dumps(parsed_results, indent=4))
    
    # 2. Run your real tagger using your actual JSON map
    final_tags = attach_tags(parsed_results)
    print("\n--- 2. FINAL TAGS ---")
    print(json.dumps(final_tags, indent=4))

# if __name__ == "__main__":
#     # Temporarily comment out normal execution logic while testing
#     testing()

if __name__ == "__main__":
    with open(DATASET, 'r', encoding='utf-8') as f:
        recipe = pd.read_json(f)

    if DATASET == "./data/recipes_reduced.json":
        rename_columns = {
            "recipe_title": "title", "ingredients_raw": "ingredients", 
            "directions_raw": "instructions", "ingredients_canonical": "cleaned_ingredients",
            "est_prep_time_min": "prep_time", "est_cook_time_min": "cook_time"
        }
        drop_columns = [
            "ingredients",
            "directions", "num_ingredients", "num_steps", "ingredient_text",
            "directions_text", "combined_text",
            "primary_taste", "secondary_taste", "fast_hits", "slow_hits", "medium_hits", "cook_speed",
            "difficulty", "is_halal", "is_kosher", "is_gluten_free", "dietary_profile",
            "healthiness_score", "health_flags", "main_ingredient", "health_level"
        ]
        
        recipe = recipe.drop(columns=drop_columns, errors='ignore').rename(columns=rename_columns)

    VALID_COLUMNS = [
        "title", "category","tag", "prep_time", "cook_time", "cook_speed","description","ingredients", 
        "cleaned_ingredients", "instructions","cuisine_list","course_list", "tastes", "is_vegan", "is_vegetarian", 
        "is_nut_free", "is_dairy_free", "picture_link"
    ]

    recipe.reset_index(drop=True, inplace=True)
    recipe.dropna(inplace=True)

    recipe["cleaned_ingredients"] = recipe.ingredients.apply(parse_ingredient) 
    recipe["tag"] = recipe["cleaned_ingredients"].apply(attach_tags)

    # Ensure only valid columns that actually exist in the dataframe are kept
    available_columns = [col for col in VALID_COLUMNS if col in recipe.columns]
    recipe = recipe[available_columns]
    
    recipe.to_json("./data/processed_recipes.json", orient="records", indent=4, force_ascii=False)
    print("------- Tags attached & JSON saved -------")

    # Optional: Generate the reduced phrases CSV for diagnostics
    # generate_phrase_frequencies(recipe["cleaned_ingredients"])