#include <iostream>
#include <vector>
#include <unordered_set>
#include <sstream>
#include <algorithm>

using namespace std;

// --- Recipe structure ---
struct Recipe {
    int id;
    string name;
    vector<string> ingredients;
};

// --- Helper: split comma-separated strings into tokens ---
vector<string> split(const string &s, char delimiter) {
    vector<string> tokens;
    string token;
    istringstream tokenStream(s);
    while (getline(tokenStream, token, delimiter)) {
        // trim spaces
        token.erase(remove_if(token.begin(), token.end(), ::isspace), token.end());
        // lowercase for uniformity
        transform(token.begin(), token.end(), token.begin(), ::tolower);
        tokens.push_back(token);
    }
    return tokens;
}

// --- Efficient ingredient matching ---
vector<Recipe> searchRecipes(const vector<Recipe> &recipes, const string &query) {
    vector<string> queryIngredients = split(query, ',');
    vector<Recipe> matches;

    for (const auto &recipe : recipes) {
        unordered_set<string> ingSet;
        for (auto ing : recipe.ingredients) {
            transform(ing.begin(), ing.end(), ing.begin(), ::tolower);
            ingSet.insert(ing);
        }

        bool allFound = true;
        for (auto q : queryIngredients) {
            if (ingSet.find(q) == ingSet.end()) {
                allFound = false;
                break;
            }
        }

        if (allFound) {
            matches.push_back(recipe);
        }
    }

    return matches;
}

// --- Demo ---
int main() {
    // Dummy dataset
    vector<Recipe> recipes = {
        {1, "Spaghetti Bolognese", {"tomato", "pasta", "beef", "garlic", "onion"}},
        {2, "Garlic Bread", {"bread", "butter", "garlic"}},
        {3, "Pasta Salad", {"pasta", "tomato", "cucumber", "olive oil"}},
        {4, "Tomato Soup", {"tomato", "garlic", "onion"}}
    };

    string query = "tomato, pasta, garlic";
    vector<Recipe> results = searchRecipes(recipes, query);

    cout << "Query: " << query << "\n";
    cout << "Matching Recipes:\n";
    for (auto r : results) {
        cout << " - " << r.name << " (ID: " << r.id << ")\n";
    }

    return 0;
}
