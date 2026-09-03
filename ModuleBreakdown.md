### Module 1 — Frontend Redesign
> Multi-page app structure with proper UX and design system.

- [ ] Define color palette, typography scale, and spacing system
- [ ] Restructure pages — home/discovery page as entry point, current main_page becomes pantry/search
- [ ] Popular recipes on home page based on aggregate data
- [ ] Beautify ingredient dropdown — custom dropdown replacing native datalist, keyboard navigation
- [ ] Flexible top_n — "show more" button or slider replacing fixed top 10

---

### Module 2 — Database & Persistence
> SQLite to start, PostgreSQL later. Drives pantry persistence and user history.

- [ ] Set up SQLite schema — users, pantry (ingredients + quantities + expiry), saved recipes, cook history
- [ ] Migrate pantry from session state to DB
- [ ] "Using Today" / expiring soon section — ingredients marked expiring drive the search
- [ ] Wire excluded ingredients into matching engine — filter recipes containing excluded ingredients entirely

---

### Module 3 — User Accounts
> Auth system required before per-user pantry makes sense.

- [ ] Email/password auth or OAuth
- [ ] Per-user pantry, preferences, and history
- [ ] Saved recipes per user
- [ ] Cuisine preference tracking

---

### Module 4 — Data Rescrape & Enrichment
> Current dataset is limited. Collect missing fields.

- [ ] Rescrape AllRecipes — collect description, prep/cook time, servings, meal type, cuisine tags
- [ ] Full resolution images saved locally — don't rely on CDN links that break
- [ ] User ratings and review count
- [ ] Nutrition data per serving — calories, protein, fiber, carbs, fat
- [ ] USDA FoodData Central API as fallback for missing nutrition values
- [ ] Expand canonical map from top 1000 to top 3000-5000 phrases — run incrementally

---

### Module 5 — Matching Intelligence
> Smarter ingredient matching and recipe recommendations.

- [ ] Fuzzy ingredient input — match "chiken" to "chicken" using rapidfuzz
- [ ] Substitution graph — model ingredient substitutions as directed graph using NetworkX
- [ ] "Almost ready" shelf — recipes needing only 1-2 more items with cheapest buy suggestions
- [ ] Collaborative filtering — "users with similar taste also liked..." (requires user data)
- [ ] Cuisine preference learning — infer implied pantry from cuisine history

---

### Module 6 — Bug Fixes & Polish
> Known bugs and small improvements.

- [ ] Fix dropdown showing compound tags — filter /ingredients endpoint more intelligently
- [ ] Fix remaining canonical map noise — section headers, brand names, temperature strings
- [ ] Add more FOOD_NOUNS to POS exception list as edge cases surface
- [ ] Complete canonical map — currently 11/20 batches done