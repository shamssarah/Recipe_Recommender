import pandas as pd
import json
import re
import nltk

nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger_eng')
nltk.download('wordnet')

from nltk.stem import WordNetLemmatizer
from nltk import pos_tag, word_tokenize
lemmatizer = WordNetLemmatizer()


TAG_PATH = "../../data/double_tagging_map.json"
DATASET_1 = "../../data/recipes_raw_nosource_ar.json"
# DATASET_2 = "../../data/allrecipes.csv"

tagging_map = json.load(open(TAG_PATH, "r"))
tagging_map = {k: v for k, v in tagging_map.items() if v is not None}
# values are matched to keys, values provide the correct tag to be attached to the recipe for searching purposes


# def singularize(text: str) -> str:
#     tokens = text.split()
#     return ' '.join(lemmatizer.lemmatize(t, pos='n') for t in tokens)

def singularize(text: str) -> str:
    tokens = text.split()
    if not tokens:
        return text
    tokens[-1] = lemmatizer.lemmatize(tokens[-1], pos='n')
    return ' '.join(tokens)

def ingredient_match(tag: str, query: str) -> bool:
    tag_tokens = set(tag.lower().split())
    query_tokens = set(query.lower().split())
    
    if not tag_tokens or not query_tokens:
        return False
    
    overlap = tag_tokens & query_tokens
    longer = max(len(tag_tokens), len(query_tokens))
    return len(overlap) / longer >= 0.70

def extract_ingredient_nouns(text: str) -> str:

    FOOD_NOUNS_COMPOUND = {
        'baking mix'
        }

    text = text.lower().replace('-', ' ')
    
    # still strip these first — POS tagger won't catch them reliably
    strip_phrases = [
        'to taste', 'as needed', 'or more', 'room temperature',
        'freshly ground', 'finely chopped', 'thinly sliced'
    ]
    for phrase in strip_phrases:
        text = re.sub(rf'\b{phrase}\b', '', text, flags=re.IGNORECASE)
    
    if text in FOOD_NOUNS_COMPOUND:
        return text

    tokens = word_tokenize(text.strip())
    tagged = pos_tag(tokens)

    # print (f"POS tags for '{text}': {tagged}")

    # keep nouns and adjectives that are likely part of ingredient names
    keep_pos = {'NN', 'NNS', 'NNP', 'NNPS', 'JJ'}
    pos_exceptions = {
    'skinless', 'boneless', 'seedless', 'boneless', 'halves',
        'pounded', 'thick', 'lean', 'frozen', 'refrigerated','unflavored'
    }

    FOOD_NOUNS = {
        'cauliflower', 'broccoli', 'zucchini', 'arugula', 'quinoa',
        'edamame', 'tahini', 'cilantro', 'jalapeño', 'serrano',
        'rotini', 'fusilli', 'focaccia', 'baguette', 'brioche',
    }



    nouns = [word for word, pos in tagged 
            if (pos in keep_pos or word.lower() in FOOD_NOUNS)
            and word.isalpha()
            and word.lower() not in pos_exceptions]

    return ' '.join(nouns)


def parse_ingredient(ingredient_list): # duplicate of the function in ingredient_cluster.py, should be moved to a common utils file

    output = []
    pattern = re.compile(r"""
        ^
        (?P<quantity>[\d\s\\\/]+)?
        \s*
        (?P<unit>
        (?:\(.*?\)\s*)?          # optional (10.75 ounce) prefix
        (?:cups?|tablespoons?|tbsp|teaspoons?|tsp|
           ounces?|oz|pounds?|lbs?|gallons?|liters?|milliliters?|ml|grams?|kg|pinches?|dashes?|
           cloves?|slices?|stalks?|sprigs?|
           cans?|pinch|dash|bunch|heads?|packages?|bags?|
            inches?|inch?|box?|boxes?|package?|cubes?|drops?|
            fillets?|envelopes?|quarts?)
        )?
        \s*
        (?P<ingredient>.+)
        $
    """, re.VERBOSE | re.IGNORECASE)
    
    type_keywords = ['powder', 'dried', 'fresh', 'whole', 'ground',
                 'large', 'medium', 'small', 'extra', 'lean', 'low', 'fat',
                'unsalted', 'salted', 'unsweetened', 'sweetened', 'condensed',
                'reduced', 'light', 'dark', 'heavy', 'plain', 'pure',
                'instant', 'active', 'quick', 'sharp', 'creamy']
       # strip method words — these don't matter



    strip_phrases = [
        'room temperature',"lukewarm","hot","warm","cold","cool",
        'to taste', 'as needed', 'or more',
        'package frozen', 'freshly ground', 'lightly beaten',
        'finely chopped', 'thinly sliced', 'or to taste', 'taste','fluid ounce','fluid ounces',
        'shredded', 'sliced', 'minced', 'chopped', 'diced', 'cubed',
        'finely', 'pinched', 'skinless', 'softened', 'melted', 'thinly',
        'beaten', 'peeled', 'seeded', 'cored', 'trimmed', 'halved',
        'drained', 'rinsed', 'thawed', 'cooked', 'boneless', 'divided',
        'optional', 'grated', 'zested', 'torn', 'into', 'refrigerated',
        'inches', 'pieces', 'quartered', 'cut', 'inch', 'halves', 'lean',
        'crushed', 'crumbled', 'ground', 'broken',"shredded", "sliced",
        "minced", "chopped", "diced", "cubed", "mashed","uncooked"
        "finely", "pinched", "skinless", "softened", "melted", "thinly", 
        "beaten", "peeled", "seeded", "cored", "trimmed", "halved","chunks","chopped","overripe","pinches",
        "garnish","dry","italian style","italian-style","italian seasoned","italian-seasoned"
        "cola","philidelphia","fritos",'reynolds'


        
    ]

    for raw in ingredient_list:
        # print ("------- Processing ingredient -------\n ----------------------------")
        # print (f"Original: {raw}")
        # remove "recipe for..." pattern but keep what comes before "for"
        raw = re.sub(r'\bfor\s+a\s+.*', '', raw, flags=re.IGNORECASE).strip()
        raw = re.sub(r'\brecipe\b', '', raw, flags=re.IGNORECASE).strip()
        raw = raw.replace("ADVERTISEMENT", "").strip()
        for phrase in strip_phrases:
            raw = re.sub(rf'\b{phrase}\b', '', raw, flags=re.IGNORECASE)
        
        if not raw.strip():
            continue  # skip empty ingredients entirely

        # print (f"After method stripping: {raw}")
        

        m = pattern.match(raw)
        ingredient_str = m.group("ingredient").strip() if m else raw
        
        ingredient_str = re.sub(r'\(.*?\)', '', ingredient_str)
        ingredient_str = re.sub(r'\b\d+\b', '', ingredient_str)
        ingredient_str = ingredient_str.replace('-', ' ')
        ingredient_str = ingredient_str.strip()

        # print (f"Ingredient: {ingredient_str}")
        

        # extract type before POS stripping — still matters
        detected_type = None
        for t in type_keywords:
            if re.search(rf'\b{t}\b', ingredient_str, re.IGNORECASE):
                detected_type = t
                ingredient_str = re.sub(rf'\b{t}\b', '', ingredient_str, flags=re.IGNORECASE)
                break

        # print (f"After type stripping: {ingredient_str}, detected type: {detected_type}")


        # replace manual method stripping with POS tagging
        ingredient_str = re.sub(r'[^a-zA-Z \']', '', ingredient_str) # remove non-alphabetic characters before POS tagging
        ingredient_clean = extract_ingredient_nouns(ingredient_str)
        ingredient_clean = lemmatizer.lemmatize(ingredient_clean)

        # print (f"After POS stripping: {ingredient_clean}")

        output.append( {
            "quantity":   (m.group("quantity") or "").strip() or None if m else None,
            "unit":       (m.group("unit") or "").strip() or None if m else None,
            "type":       detected_type,
            "ingredient": ingredient_clean
        })
        

    return output

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

        # not in map — use as-is for both
        if not matched and ingredient:
            base_tags.add(ingredient)
            specific_tags.add(ingredient)

    return {
        "base": [singularize(t) for t in base_tags if t.strip()],
        "specific": [singularize(t) for t in specific_tags if t.strip()]
    }

if __name__ == "__main__":
    # # Example usage
    # ingredients =[
    #     # "6 roma (plum) tomatoes, chopped ADVERTISEMENT",
    #     #  "2 cubes chicken bouillon ADVERTISEMENT",
    #     #  "10 ounces broccoli florets ADVERTISEMENT",
    #     #  "10 ounces cauliflower florets ADVERTISEMENT",
    #     #  "1 1\/2 pounds salmon fillets ADVERTISEMENT",
    #     #  "4 (4 ounce) fillets salmon ADVERTISEMENT",
    #     # "1 recipe pastry for a 9 inch double crust pie ADVERTISEMENT",
    #     "1 recipe pastry for a 9 inch single crust pie ADVERTISEMENT",
    #     # "1 (.25 ounce) envelope unflavored gelatin ADVERTISEMENT",
    #     # "1 (.25 ounce) package unflavored gelatin ADVERTISEMENT",
    #     "1 cup baking mix ADVERTISEMENT",
    #       "Reynolds\u00ae Parchment Paper ADVERTISEMENT",


    #     ]
    # parsed = parse_ingredient(ingredients)

    # print (attach_tags(parsed))

    recipe = pd.read_json (DATASET_1).T
    recipe.reset_index(drop=True, inplace=True)
    recipe.dropna(inplace=True)
    recipe['cleaned_ingredients'] = recipe.ingredients.apply(parse_ingredient) 
    # for recipe_ in recipe.head():/
    recipe['tag'] = recipe['cleaned_ingredients'].apply(attach_tags)
    recipe = recipe[[
    'title', 
    'tag', 
    'ingredients', 
    'cleaned_ingredients', 
    'instructions', 
    'picture_link'
]]
    recipe.to_json("../../data/recipes_with_tags.json", orient="records", indent=4)

    print ("------- Tags attached -------")



