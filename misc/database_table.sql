
CREATE TABLE Ingredients (
    ingredient_id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    calories_per_100g DECIMAL(5,2),
    protein_per_100g DECIMAL(5,2),
    fiber_per_100g DECIMAL(5,2),
    standard_unit VARCHAR(20) -- e.g., 'grams', 'ml'
);

CREATE TABLE Users (
    user_id INT PRIMARY KEY,
    username VARCHAR(100),
    protein_goal_grams INT,
    fiber_goal_grams INT,
    calorie_limit INT,
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
CREATE TABLE Recipes (
    recipe_id INT PRIMARY KEY,
    title VARCHAR(255),
    cuisine_type VARCHAR(50),
    instructions TEXT,
    base_popularity_score INT -- usage count
);

-- 6. RECIPE INGREDIENTS
-- Links recipes to ingredients with required amounts.
CREATE TABLE Recipe_Ingredients (
    recipe_id INT,
    ingredient_id INT,
    amount_required DECIMAL(8,2),
    unit_required VARCHAR(20),
    is_optional BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (recipe_id) REFERENCES Recipes(recipe_id),
    FOREIGN KEY (ingredient_id) REFERENCES Ingredients(ingredient_id)
);
