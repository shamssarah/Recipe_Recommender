import pandas as pd
import numpy as np
import re
corpus = []

def parse_ingredient(ingredient_list):

    output = []
    pattern = re.compile(r"""
        ^
        (?P<quantity>[\d\s\/]+)?
        \s*
        (?P<unit> 
             (?:\(.*?\)\s*)?          # optional (10.75 ounce) prefix
        (?:cups?|tablespoons?|tbsp|teaspoons?|tsp|
           ounces?|oz|pounds?|lbs?|
           cloves?|slices?|stalks?|sprigs?|
           cans?|pinch|dash|bunch|heads?|packages?|bags?)
            
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
    methods = [
        'shredded', 'sliced', 'minced', 'chopped', 'diced', 'cubed',
        'finely', 'pinched', 'skinless', 'softened', 'melted', 'thinly',
        'beaten', 'peeled', 'seeded', 'cored', 'trimmed', 'halved',
        'drained', 'rinsed', 'thawed', 'cooked', 'boneless', 'divided',
        'optional', 'to taste', 'as needed', 'room temperature', 'grated',
        'zested', 'skinless','inches','pieces','quartered','rinsed and drained',
        'freshly ground','lightly beaten','finely chopped','thinly sliced',
        'cut','inch','torn into'
    ]
    

    strip_phrases = [
        'room temperature', 'to taste', 'as needed', 'or more',
        'package frozen', 'freshly ground', 'lightly beaten','refrigerated'
        'finely chopped', 'thinly sliced', 'or to taste', 'taste','fluid ounce','fluid ounces'
    ]

    for raw in ingredient_list:
        raw = raw.replace("ADVERTISEMENT", "").strip()
        for phrase in strip_phrases:
            raw = re.sub(rf'\b{phrase}\b', '', raw, flags=re.IGNORECASE)



        m = pattern.match(raw)
        ingredient_str = m.group("ingredient").strip() if m else raw


        # extract type before stripping — these DO matter
        detected_type = None
        for t in type_keywords:
            if re.search(rf'\b{t}\b', ingredient_str, re.IGNORECASE):
                detected_type = t
                ingredient_str = re.sub(rf'\b{t}\b', '', ingredient_str, flags=re.IGNORECASE)
                break  # take the first match only

        # now strip methods
        tokens = ingredient_str.split()
        tokens = [t for t in tokens if t.lower() not in methods]
        ingredient_clean = ' '.join(tokens).strip()
        ingredient_clean = re.sub(r'\s+', ' ', ingredient_clean)

        output.append( {
            "quantity":   (m.group("quantity") or "").strip() or None if m else None,
            "unit":       (m.group("unit") or "").strip() or None if m else None,
            "type":       detected_type,
            "ingredient": ingredient_clean
        })
        corpus.append(ingredient_clean)

    return output




recipe = pd.read_json ("data/recipes_raw_nosource_ar.json").T

# cleaning data
recipe.reset_index(drop=True, inplace=True)
recipe.dropna(inplace=True)
recipe['tag'] = recipe.ingredients.apply(parse_ingredient) 
# this will not be needed if the data is scraped directly from the website with the ingredients already separated into quantity, unit and ingredient name


import matplotlib.pyplot as plt
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer

# Extract 2-word and 3-word phrases, ignoring common stop words
vectorizer = CountVectorizer(ngram_range=(2, 3), stop_words='english')
X = vectorizer.fit_transform(corpus)

# Sum frequencies and pair with the phrase names
frequencies = X.sum(axis=0).A1
phrases = vectorizer.get_feature_names_out()

# Create a DataFrame, sort by frequency, and grab the top 10
df = pd.DataFrame({'Phrase': phrases, 'Frequency': frequencies})
df = df.sort_values(by='Frequency', ascending=False).head(1000)
df.to_csv('top_1000_phrases.csv', index=False)

# Plotting
# plt.figure(figsize=(10, 20))
# plt.barh(df['Phrase'], df['Frequency'], color='skyblue')
# plt.gca().invert_yaxis() # Put the highest frequency at the top
# plt.title('Most Common Ingredient Phrases (Bi-grams & Tri-grams)')
# plt.xlabel('Frequency')
# plt.tight_layout()
# plt.show()
