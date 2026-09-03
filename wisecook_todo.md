# WiseCook — Ship List

Goal: live, clickable demo by start of semester.

## 1. Data & Scope
- [X] Trim dataset down to a curated subset (~500–2000 recipes) instead of the full scrape
- [X] Decide which recipes make the cut (variety of cuisines/ingredients, avoid near-duplicates)
- [X] Don't host recipe images — link out to the original source page instead
- [ ] Add source attribution in README + UI ("recipe data sourced from X, links to original")
- [X] Re-run the canonicalization pipeline once on the trimmed set

## 2. Remove Runtime Dependencies
- [X] Commit the pre-generated `canonical_map.json` and `processed_recipes.json` into `data/`
- [X] Remove them from `.gitignore`
- [X] Update `data_loader.py` so it just reads the committed JSON — no Gemini API call, no Kaggle download at runtime
- [X] Confirm the app boots with zero external API keys required

## 3. Code / Matching Logic
- [ ] Fix the filtering bug (whatever's currently broken in the ingredient → recipe match)
- [X] Sanity-check the `base` vs `specific` ingredient distinction is doing what it's supposed to (e.g. ground chicken vs chicken breast)
- [ ] Spot-check coverage-ratio ranking on 3–4 sample pantries — does "closest match" actually look right?
- [ ] Confirm free-text ingredient input handles messy phrasing reasonably ("2 ripe tomatoes", "leftover chicken")

## 4. Frontend Polish (rudimentary is fine)
- [ ] Clean up basic layout/spacing so it doesn't look unfinished
- [ ] Make sure the "what you have → what you can cook" loop is the obvious first thing a visitor sees
- [ ] Add a way to see *why* a recipe was suggested (e.g. "you have 5 of 6 ingredients")

## 5. Deploy
- [ ] Push to Render (free tier, no card required)
- [ ] Test cold start — ping the URL yourself before sharing so it's warm
- [ ] Confirm it works end-to-end from a fresh browser (not just local dev)

## 6. README Rewrite
- [ ] Lead with the problem, not the mechanics: sale-item / end-of-week fridge framing
- [ ] Add a screenshot or short GIF near the top
- [ ] Add one line honestly addressing Supercook: what's actually different (free-text input, base/specific ingredient matching, coverage-ratio ranking)
- [ ] Move pipeline/architecture details below the fold, not above it

## 7. Launch
- [ ] Pick one channel first (Show HN or a relevant subreddit — not both same day)
- [ ] Draft post title around the specific moment, not the feature ("sad fridge vegetables" angle)
- [ ] Have the link ready and warmed up before posting
- [ ] React to comments/feedback, note anything to fix for round two
