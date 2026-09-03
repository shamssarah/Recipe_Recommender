import json
from parsing_utils import parse_ingredient
from 03_attaching_tags import attach_tags

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
#     # Temporarily comment out your normal execution logic while you test
#     testing()