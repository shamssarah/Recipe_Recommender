import re
import pandas as pd
import unicodedata
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag, word_tokenize

lemmatizer = WordNetLemmatizer()

def normalize_fractions(text):
    # 1. Safely check for None or NaN without triggering Pandas array errors
    if text is None or (isinstance(text, float) and text != text): 
        return text
    
    # 2. If the data is dirty and handed us a list instead of a string, join it
    if isinstance(text, list):
        text = " ".join(str(x) for x in text)
        
    # 3. Proceed with normalization safely
    return unicodedata.normalize('NFKC', str(text)).replace('\u2044', '/').replace('\\/', '/')

def singularize(text: str) -> str:
    tokens = text.split()
    if not tokens:
        return text
    tokens[-1] = lemmatizer.lemmatize(tokens[-1], pos='n')
    return ' '.join(tokens)

# def extract_ingredient_nouns(text: str) -> str:
#     FOOD_NOUNS_COMPOUND = {'baking mix'}
#     text = text.lower().replace('-', ' ')
    
#     strip_phrases = [
#         'to taste', 'as needed', 'or more', 'room temperature',
#         'freshly ground', 'finely chopped', 'thinly sliced'
#     ]
#     for phrase in strip_phrases:
#         text = re.sub(rf'\b{phrase}\b', '', text, flags=re.IGNORECASE)
    
#     if text in FOOD_NOUNS_COMPOUND:
#         return text

#     tokens = word_tokenize(text.strip())
#     tagged = pos_tag(tokens)

#     keep_pos = {'NN', 'NNS', 'NNP', 'NNPS', 'JJ'}
#     pos_exceptions = {
#         'skinless', 'boneless', 'seedless', 'halves',
#         'pounded', 'thick', 'lean', 'frozen', 'refrigerated', 'unflavored'
#     }
#     FOOD_NOUNS = {
#         'cauliflower', 'broccoli', 'zucchini', 'arugula', 'quinoa',
#         'edamame', 'tahini', 'cilantro', 'jalapeño', 'serrano',
#         'rotini', 'fusilli', 'focaccia', 'baguette', 'brioche',
  
#         'chicken', 'beef', 'pork', 'turkey', 'lamb', 'fish', 'shrimp', 'salmon',
#         'apple', 'orange', 'lemon', 'lime', 'potato', 'tomato', 'onion', 'garlic', 'cheese'
#     }

#     nouns = [word for word, pos in tagged 
#             if (pos in keep_pos or word.lower() in FOOD_NOUNS)
#             and word.isalpha()
#             and word.lower() not in pos_exceptions]

#     return ' '.join(nouns)

def extract_ingredient_nouns(text: str) -> str:
    FOOD_NOUNS_COMPOUND = {'baking mix'}
    text = text.lower().replace('-', ' ')
    
    strip_phrases = [
        'to taste', 'as needed', 'or more', 'room temperature',
        'freshly ground', 'finely chopped', 'thinly sliced', 'bite size'
    ]
    for phrase in strip_phrases:
        text = re.sub(rf'\b{phrase}\b', '', text, flags=re.IGNORECASE)
    
    if text in FOOD_NOUNS_COMPOUND:
        return text

    tokens = word_tokenize(text.strip())
    tagged = pos_tag(tokens)

    # Blacklist: Only drop Adverbs (RB, RBR, RBS) and Past-Tense Verbs (VBD, VBN)
    drop_pos = {'RB', 'RBR', 'RBS', 'VBD', 'VBN'}
    
    # Exceptions that NLTK often mislabels as verbs/adverbs but we want to keep
    keep_exceptions = {'chicken', 'roasted', 'smoked', 'dried', 'fried', 'baked'}

    nouns = [
        word for word, pos in tagged 
        if (pos not in drop_pos or word.lower() in keep_exceptions)
        and word.isalpha()
    ]

    return ' '.join(nouns)

def parse_ingredient(ingredient_list):
    output = []
    pattern = re.compile(r"""
        ^
        (?P<quantity>[\d\s\/\u2044]+)?
        \s*
        (?P<unit>
        (?:\(.*?\)\s*)?
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
    
    type_keywords = [
        'powder', 'dried', 'fresh', 'whole', 'ground',
        'large', 'medium', 'small', 'extra', 'lean', 'low', 'fat',
        'unsalted', 'salted', 'unsweetened', 'sweetened', 'condensed',
        'reduced', 'light', 'dark', 'heavy', 'plain', 'pure',
        'instant', 'active', 'quick', 'sharp', 'creamy'
    ]

    strip_phrases = [
        'room temperature',"lukewarm","hot","warm","cold","cool",
        'to taste', 'as needed', 'or more',
        'package frozen', 'freshly ground', 'lightly beaten',
        'finely chopped', 'thinly sliced', 'or to taste', 'taste', 'fluid ounce', 'fluid ounces',
        'shredded', 'sliced', 'minced', 'chopped', 'diced', 'cubed',
        'finely', 'pinched', 'skinless', 'softened', 'melted', 'thinly',
        'beaten', 'peeled', 'seeded', 'cored', 'trimmed', 'halved',
        'drained', 'rinsed', 'thawed', 'cooked', 'boneless', 'divided',
        'optional', 'grated', 'zested', 'torn', 'into', 'refrigerated',
        'inches', 'pieces', 'quartered', 'cut', 'inch', 'halves', 'lean',
        'crushed', 'crumbled', 'ground', 'broken', 'mashed', 'uncooked',
        'chunks', 'overripe', 'pinches', 'garnish', 'dry', 
        'italian style', 'italian-style', 'italian seasoned', 'italian-seasoned',
        'cola', 'philidelphia', 'fritos', 'reynolds','bite-size','size'
    ]

    for raw in ingredient_list:
        raw = normalize_fractions(raw)
        
        raw = re.sub(r'\bfor\s+a\s+.*', '', raw, flags=re.IGNORECASE).strip()
        raw = re.sub(r'\brecipe\b', '', raw, flags=re.IGNORECASE).strip()
        raw = raw.replace("ADVERTISEMENT", "").strip()
        
        for phrase in strip_phrases:
            raw = re.sub(rf'\b{phrase}\b', '', raw, flags=re.IGNORECASE)
        
        if not raw.strip():
            continue 

        m = pattern.match(raw)
        ingredient_str = m.group("ingredient").strip() if m else raw
        
        ingredient_str = re.sub(r'\(.*?\)', '', ingredient_str)
        ingredient_str = re.sub(r'\b\d+\b', '', ingredient_str)
        ingredient_str = ingredient_str.replace('-', ' ').strip()

        detected_type = None
        for t in type_keywords:
            if re.search(rf'\b{t}\b', ingredient_str, re.IGNORECASE):
                detected_type = t
                ingredient_str = re.sub(rf'\b{t}\b', '', ingredient_str, flags=re.IGNORECASE)
                break

        ingredient_str = re.sub(r'[^a-zA-Z \']', '', ingredient_str)
        ingredient_clean = extract_ingredient_nouns(ingredient_str)
        ingredient_clean = lemmatizer.lemmatize(ingredient_clean)

        output.append({
            "quantity":   (m.group("quantity") or "").strip() or None if m else None,
            "unit":       (m.group("unit") or "").strip() or None if m else None,
            "type":       detected_type,
            "ingredient": ingredient_clean
        })
        
    return output
