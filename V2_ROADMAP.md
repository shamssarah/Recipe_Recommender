# WiseCook — V2 Roadmap & Dev Log
<!-- https://github.com/onzie9/all_recipes_data -->
A running log of ideas, bugs, and planned improvements. Update this as you go.

---

## Current State (V1)

- Ingredient parser — regex + NLTK POS tagging, extracts quantity / unit / type / ingredient name
- Canonical map — LLM-generated (Gemini Flash), base/specific two-tier structure, top 1000 phrases
- Tag generation — fuzzy token overlap matching, base and specific tags per recipe
- Matching engine — coverage scoring, staples list, base/specific mode, top N results
- FastAPI backend — serves frontend + API endpoints, recipes loaded into memory on startup
- Frontend — vanilla HTML/CSS/JS, ingredient chips with include/exclude toggle, live results, staples pre-populated, dropdown autocomplete from /ingredients endpoint

---

## UX Architecture (Planned)

Current single page becomes a multi-page app:

```
Home / Discovery page
  → popular recipes, cuisine browsing, trending

User Pantry page  (current main_page)
  → Pantry Staples section (pre-populated, toggleable)
  → My Pantry section (user built, persistent via DB)
  → Using Today section (drives /match, expiring soon items)

Recipe page  (view_recipe.html)
  → image, description, ingredients, instructions
  → nutrition info, user rating, cuisine/meal type tags

User page
  → saved recipes, cuisine preferences, pantry history
```

"Using Today" section only makes sense once pantry is persistent (needs DB).

---

## Improvements / TODO

### Frontend
- [ ] **Beautify the dropdown** — style the datalist suggestions, add keyboard navigation,
      consider replacing native datalist with a custom dropdown for more control over appearance
- [ ] **(V2)Flexible top_n** — replace fixed top 10 with a "show more" button or a
      user-controlled slider. Users should be able to see all results if they want
<!-- - [ ] **7. Pixel art icons** — ingredient and cuisine icons made in Krita/Inkscape,
      good practice for game design. Could make the UI feel distinct and fun -->
- [ ] **UX design + color system** — define a proper color palette, typography scale,
      spacing system. Currently unstyled. (custom icons and warm food-inspired palette)
- [ ] **Popular recipes on home page** — surface trending/highly rated recipes on the
      landing page rather than showing nothing until ingredients are added.
      Based on aggregate user cook/save data
- [ ] **Restructure pages** — current main_page becomes the pantry/search page.
      Add a proper home/discovery page as the entry point

### Backend & Data
- [ ] **(V2)Add database** — SQLite to start, PostgreSQL later. Store:
      user pantry (ingredients + quantities + expiry dates), saved recipes,
      cuisine preferences, cook/skip history. Pantry should persist between sessions
- [ ] **(V2)Wire up recipe page** — view_recipe.html needs to fetch from GET /recipe/{id}
      and populate all fields. Pass recipe id via URL param when clicking a card:
      `window.location.href = /recipe?id=${recipe.id}`
- [ ] **Meal type + cuisine tags** — recipes are currently unfiltered. Add tags for:
      meal type (breakfast, lunch, dinner, dessert, snack),
      cuisine (Italian, Mexican, Thai, etc).
      Enables filtering and better recommendations. Extract from dataset or add during rescrape
- [ ] **User accounts** — auth system (email/password or OAuth).
      Each user gets their own pantry, preferences, and history.
      Required before DB pantry makes sense

### Scraping
- [ ] **(V2)Rescrape AllRecipes** - (Find a new dataset that provides necessary variable or rescrape) — current dataset is limited and missing fields.
      When scraping collect:
  - [ ] Description field — needed for recipe menu card
  - [ ] Full resolution images saved locally (don't rely on CDN links that break)
  - [ ] User ratings and review count — display as stars on recipe card
  - [ ] Nutrition data per serving:
    - [ ] Fiber (g)
    - [ ] Protein (g)
    - [ ] Calories, carbs, fat
  - [ ] USDA FoodData Central API as second opinion for missing nutrition values
        (https://api.nal.usda.gov/fdc/v1/foods/search)
  - [ ] Meal type and cuisine tags if available on the page
  - [ ] Prep time, cook time, servings

### Matching & Intelligence
- [ ] **Substitution graph** — model ingredient substitutions as a directed graph using NetworkX.
      Enables multi-hop substitution chains:
      user has yogurt → dairy → sour cream → recipe matched. (garlic powder → minced garlic → garlic (clove))
- [ ] **Fuzzy ingredient input (dropdown)** — if user types "chiken" match to "chicken".
      Use difflib or rapidfuzz
- [ ] **"Almost ready" shelf** — surface recipes needing only 1-2 more items.
      Show cheapest missing ingredients to buy. Core value prop for budget users
- [ ] **Cuisine preference learning** — track what cuisines user cooks,
      infer implied pantry (users that like Chinese Cuisine will probably have rice vinegar etc.)
- [ ] **Collaborative filtering** — "users with similar taste also liked..."
      Needs user data first
- [ ] **Excluded ingredients** — already in frontend (✗ button), needs to be wired
      into matching engine to filter out recipes containing excluded ingredients entirely
- [ ] **Using Today / expiring soon** — separate section from full pantry.
      Ingredients marked expiring drive the search. Needs DB for expiry date storage

### Canonical Map
- [ ] Expand from top 1000 to top 3000-5000 phrases — run incrementally (1000/day on Gemini free tier)
- [ ] Fix remaining noise: section headers, brand names, temperature strings
- [ ] Add more FOOD_NOUNS to POS exception list as edge cases are found
- [ ] Rerun with corrected prompt — current partial map (11/20 batches) needs completing

---

## Known Bugs

- [ ] **1. Dropdown shows compound tags** — /ingredients endpoint returns all unique base tags
      including compounds like "apple juice", "lemon juice" when user types "lemon".
      Should filter more intelligently or only return single-word ingredients in suggestions

---

## Ideas Parking Lot

- "Surprise me" button — random high-coverage recipe from current pantry
- Meal planning mode — plan a week of recipes, generate one consolidated shopping list
- "Cook mode" — step by step instructions with timers, hands-free friendly
- Receipt / barcode scanner for auto-populating pantry
- Budget mode — given $X, what ingredients should I buy to unlock the most recipes?

---

## Notes

