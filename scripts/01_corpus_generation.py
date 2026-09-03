import unicodedata

import pandas as pd
import re
from sklearn.feature_extraction.text import CountVectorizer
from parsing_utils import parse_ingredient,normlize_fractions


def testing ():
    recipe = {
        "ingredients": ["cup butter, divided","½ cup vegetable shortening","3 tablespoons sugar"]
    }
    recipe = pd.DataFrame(recipe)
    print (parse_ingredient(recipe.ingredients))

if __name__ == "__main__":


    recipe = pd.read_json ("data/recipes_reduced.json", orient='records')

    recipe.reset_index(drop=True, inplace=True)
    recipe.dropna(inplace=True)
    recipe['parsed_ingredients'] = recipe.ingredients.apply(parse_ingredient) 
    
    corpus = [
        item['ingredient'] 
        for row_list in recipe['parsed_ingredients'] 
        for item in row_list 
        if item.get('ingredient')
    ]
    # this will not be needed if the data is scraped directly from the website with the ingredients already separated into quantity, unit and ingredient name

    # Extract 2-word and 3-word phrases, ignoring common stop words
    vectorizer = CountVectorizer(ngram_range=(2, 3), stop_words='english')
    X = vectorizer.fit_transform(corpus)

    # Sum frequencies and pair with the phrase names
    frequencies = X.sum(axis=0).A1
    phrases = vectorizer.get_feature_names_out()

    # Create a DataFrame, sort by frequency, and grab the top 10
    df = pd.DataFrame({'Phrase': phrases, 'Frequency': frequencies})
    df = df.sort_values(by='Frequency', ascending=False)

    df.to_csv('./data/reduced_phrases.csv', index=False)

