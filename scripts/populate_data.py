import json
import psycopg2
from psycopg2.extras import execute_values
import os

DB_CONFIG = {
    "dbname":   os.getenv("DB_NAME", "your_db_name"),
    "user":     os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
    "host":     os.getenv("DB_HOST", "localhost"),
    "port":     os.getenv("DB_PORT", "5432"),
}

def load_json(path):
    with open(path) as f:
        return json.load(f)

def seed(conn, recipes):
    cur = conn.cursor()
#     INSERT INTO Recipe (
#     title, description, prep_time_min, cook_time_min,
#     difficulty, cook_speed, primary_taste, secondary_taste,
#     main_ingredient, health_level, healthiness_score,
#     is_vegan, is_vegetarian, is_halal, is_kosher,
#     is_nut_free, is_dairy_free, is_gluten_free
# ) VALUES (
#     %(title)s, %(description)s, %(est_prep_time_min)s, %(est_cook_time_min)s,
#     %(difficulty)s, %(cook_speed)s, %(primary_taste)s, %(secondary_taste)s,
#     %(main_ingredient)s, %(health_level)s, %(healthiness_score)s,
#     %(is_vegan)s, %(is_vegetarian)s, %(is_halal)s, %(is_kosher)s,
#     %(is_nut_free)s, %(is_dairy_free)s, %(is_gluten_free)s
# )

    for recipe in recipes:
        # 1. Upsert recipe
        cur.execute("""
            INSERT INTO Recipe (
                title, description, instruction, prep_time, cook_time,
                is_vegan, is_vegetarian, is_nut_free, is_dairy_free
            ) VALUES (
                %(title)s, %(description)s,%(instruction)s, %(prep_time)s, %(cook_time)s,
               
                %(is_vegan)s, %(is_vegetarian)s,
                %(is_nut_free)s, %(is_dairy_free)s
            )
            ON CONFLICT (title) DO UPDATE SET
                updated_at = now() 
            RETURNING recipe_id
        """, recipe)
        recipe_id = cur.fetchone()[0]
        for cuisine in recipe.get("cuisine", []):
            cur.execute("""
                INSERT INTO RecipeCuisine (recipe_id, cuisine)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING
            """, (recipe_id, cuisine))

        # 2. Upsert ingredients + link to recipe
        for ing in recipe.get("ingredients", []):
            cur.execute("""
                INSERT INTO Ingredient (canonical_name, base_category, specific_category)
                VALUES (%(canonical_name)s, %(base_category)s, %(specific_category)s)
                ON CONFLICT (canonical_name) DO NOTHING
                RETURNING ingredient_id
            """, ing)
            row = cur.fetchone()
            if row is None:
                cur.execute("SELECT ingredient_id FROM Ingredient WHERE canonical_name = %s",
                            (ing["canonical_name"],))
                row = cur.fetchone()
            ingredient_id = row[0]

            cur.execute("""
                INSERT INTO Recipe_Ingredient (recipe_id, ingredient_id, quantity, unit)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (recipe_id, ingredient_id) DO NOTHING
            """, (recipe_id, ingredient_id, ing.get("quantity"), ing.get("unit")))




    conn.commit()
    cur.close()
    print(f"Seeded {len(recipes)} recipes.")

if __name__ == "__main__":
    recipes = load_json("data/recipes.json")
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        seed(conn, recipes)
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()