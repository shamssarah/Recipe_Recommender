const ingredientInput = document.getElementById('ingredient-input');
const addTagButton = document.getElementById('add-tag-button');
const tagContainer = document.getElementById('tag-container');
const resultsContainer = document.getElementById('results-container');
const datalist = document.getElementById('ingredient-suggestions');
// each ingredient is now an object with name and state
let pantry = [];

// let pantry = [
//     { name: "chicken", state: "included" },
//     { name: "garlic",  state: "excluded" },
//     { name: "rice",    state: "includ ed" }
// ];

const prepopulatePantry = () => {
    const initialIngredients = [
        { name: "salt", state: "included" },
        { name: "water",  state: "included" },
        { name: "black pepper",    state: "included" },
        { name: "oil", state: "included" },
        { name: "sugar", state: "included" },
        { name: "flour", state: "included" },
        { name: "butter", state: "included" },
        { name: "eggs", state: "included" },
        { name: "milk", state: "included" },
        { name: "vegetable oil", state: "included" },
        { name: "garlic", state: "included" }
    ];

    pantry.push(...initialIngredients);
    initialIngredients.forEach(ingredient => renderChip(ingredient.name));
    fetchRecipes();
}

const addTag = () => {
    const ingredient = ingredientInput.value.trim().toLowerCase();

    if (!ingredient) return;
    if (pantry.find(i => i.name === ingredient)) return; // check by name not value

    // push an object instead of a string
    pantry.push({ name: ingredient, state: "included" });

    renderChip(ingredient);
    ingredientInput.value = '';
    fetchRecipes();
};

const renderChip = (ingredient) => {
    const chip = document.createElement('span');
    chip.className = 'chip included';
    chip.setAttribute('data-ingredient', ingredient); // so we can find it later

    chip.innerHTML = `
        ${ingredient}
        <button class="exclude-btn">✗</button>
        <button class="remove-btn">x</button>
    `;

    // exclude button — toggles between included/excluded
    chip.querySelector('.exclude-btn').addEventListener('click', () => {
        const item = pantry.find(i => i.name === ingredient);
        if (item.state === 'included') {
            item.state = 'excluded';
            chip.className = 'chip excluded'; // CSS can style this differently
        } else {
            item.state = 'included';
            chip.className = 'chip included';
        }
        fetchRecipes(); // refresh results
    });

    // remove button — removes from pantry entirely
    chip.querySelector('.remove-btn').addEventListener('click', () => {
        pantry = pantry.filter(i => i.name !== ingredient);
        chip.remove();
        fetchRecipes();
        console.log(pantry);
    });

    tagContainer.appendChild(chip);
};

// your turn — write fetchRecipes and renderRecipes below
const fetchRecipes = async () => {
    // hint: filter pantry by state before sending
    const included = pantry
        .filter(i => i.state === 'included')
        .map(i => i.name);

    const excluded = pantry
        .filter(i => i.state === 'excluded')
        .map(i => i.name);

    
    const response = await fetch('/match',{
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ ingredients: included, excluded: excluded })
    });
    if (response.ok) {
        const data = await response.json();
        renderRecipes(data);
    } else {
        console.error('Failed to fetch recipes');
    }   
};

const renderRecipes = (recipes) => {
    resultsContainer.innerHTML = ''; // clear previous results

    recipes.forEach(recipe => {
        const card = document.createElement('div');
        card.className = 'recipe-card';
        card.innerHTML = `
            <h3>${recipe.title}</h3>
            <p>${Math.round(recipe.coverage * 100)}% match</p>
            <!-- <p>Ingredients: ${recipe.ingredients.join(', ')}</p> -->
            <p>Missing: ${recipe.missing.join(', ')}</p>
            <!-- <p>Matched: ${recipe.matched.join(', ')}</p> -->
            ${recipe.picture_link ? `<img src="${recipe.picture_link}" alt="${recipe.title}" class="recipe-img">` : '<div class="recipe-img-placeholder">🍽️</div>'}
        `;
        // <p>${recipe.description}</p>
        resultsContainer.appendChild(card);
    });
};

// DROPDOWN AUTOCOMPLETE LOGIC
let allIngredients = []; // store the full list

// fetch all ingredients on page load
const loadIngredients = async () => {
    const res = await fetch('/ingredients');
    allIngredients = await res.json();
};

// filter as user types
ingredientInput.addEventListener('input', () => {
    const query = ingredientInput.value.trim().toLowerCase();
    if (query.length < 1) {
        datalist.innerHTML = '';
        return;
    }
    
    const matches = allIngredients
        .filter(i => i.includes(query))  // any ingredient containing what user typed
        .slice(0, 10);                   // limit to 10 suggestions

    datalist.innerHTML = matches
        .map(i => `<option value="${i}">`)
        .join('');
});

addTagButton.addEventListener('click', addTag);
ingredientInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') addTag();
});
prepopulatePantry();
loadIngredients();