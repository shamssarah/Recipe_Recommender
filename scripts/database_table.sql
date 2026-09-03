
CREATE TABLE Ingredient (
    ingredient_id INT PRIMARY KEY,
    canonical_name VARCHAR(255) NOT NULL,
    base_category VARCHAR(255) NOT NULL,
    specific_category VARCHAR(255),
    calories_per_100g DECIMAL(5,2),
    protein_per_100g DECIMAL(5,2),
    fiber_per_100g DECIMAL(5,2),
    carbs_per_100g DECIMAL (5,2),
    fat_per_100g DECIMAL (5,2),
    standard_unit VARCHAR(20), -- e.g., 'grams', 'ml'
    usda_cached_at TIMESTAMP
);


CREATE TABLE User (
    user_id INT PRIMARY KEY,
    username VARCHAR(100),
    email VARCHAR(255) NOT NULL,
    password TEXT,
    protein_goal_grams INT,
    fiber_goal_grams INT,
    calorie_limit INT

);

-- 4. USER PANTRY (Inventory)
CREATE TABLE User_Pantry (
    pantry_id INT PRIMARY KEY,
    user_id INT,
    ingredient_id INT,
    quantity DECIMAL(8,2), -- NULL if user didn't specify
    unit VARCHAR(20),
    is_staple BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (ingredient_id) REFERENCES Ingredients(ingredient_id)
);

-- 5. RECIPES
CREATE TABLE Recipe (
    recipe_id INT PRIMARY KEY,
    title VARCHAR(255),
    description TEXT,
    instruction TEXT,
    prep_time  INT,
    cook_time INT,
    is_vegetarian BOOLEAN,
    is_vegan BOOLEAN,
    is_dairy_free BOOLEAN,
    is_nut_free BOOLEAN,
    base_popularity_score INT -- usage count
);

CREATE TABLE Recipe_Cuisine (
    recipe_id   INT REFERENCES Recipe,
    cuisine     VARCHAR(100),
    PRIMARY KEY (recipe_id, cuisine)
);

-- 6. RECIPE INGREDIENTS
-- Links recipes to ingredients with required amounts.
CREATE TABLE Recipe_Ingredient (
    recipe_id INT,
    ingredient_id INT,
    amount_required DECIMAL(8,2),
    unit_required VARCHAR(20),
    is_optional BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (recipe_id) REFERENCES Recipes(recipe_id),
    FOREIGN KEY (ingredient_id) REFERENCES Ingredients(ingredient_id)
);
