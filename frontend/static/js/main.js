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
    chip.setAttribute('data-ingredient', ingredient);

    // clicking the chip body toggles included/excluded
    // clicking the small × removes it from the pantry entirely
    chip.innerHTML = `
        <span class="chip-label">${ingredient}</span>
        <button class="remove-btn" title="Remove from pantry" aria-label="Remove ${ingredient}">×</button>
    `;

    // toggle include/exclude — click anywhere on the label
    chip.querySelector('.chip-label').addEventListener('click', () => {
        const item = pantry.find(i => i.name === ingredient);
        if (!item) return; // guard: ingredient no longer in pantry

        if (item.state === 'included') {
            item.state = 'excluded';
            chip.className = 'chip excluded';
        } else {
            item.state = 'included';
            chip.className = 'chip included';
        }
        fetchRecipes();
    });

    // permanent remove — small × button, with a "sure?" confirm step
    const removeBtn = chip.querySelector('.remove-btn');
    removeBtn.addEventListener('click', (e) => {
        e.stopPropagation(); // don't also trigger the toggle above

        // already in "confirm" state? second click actually deletes
        if (removeBtn.classList.contains('confirming')) {
            pantry = pantry.filter(i => i.name !== ingredient);
            chip.remove();
            fetchRecipes();
            return;
        }

        // first click — arm it, show confirm state briefly
        removeBtn.classList.add('confirming');
        removeBtn.textContent = '✓?';
        removeBtn.title = 'Click again to confirm removal';

        // auto-reset if they don't confirm within 3s
        clearTimeout(removeBtn._resetTimer);
        removeBtn._resetTimer = setTimeout(() => {
            removeBtn.classList.remove('confirming');
            removeBtn.textContent = '×';
            removeBtn.title = `Remove ${ingredient}`;
        }, 3000);
    });
 // ← this line was missing before
    
    if (tagContainer) {
        tagContainer.appendChild(chip);
    } else {
        console.error('tagContainer missing');
    }
    return chip;
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
    console.log("---------------------------------------Rendered recipes:", recipes);
    
    resultsContainer.innerHTML = ''; // clear previous results

    recipes.forEach(recipe => {
        const card = document.createElement('div');
        card.className = 'recipe-card';
        card.innerHTML = `
            <h3>${recipe.title}</h3>
            <p>${Math.round(recipe.coverage * 100)}% match</p>
            <!-- <p>Ingredients: ${recipe.ingredients.join(', ')}</p> -->
            <p>Missing: ${recipe.missing.join(', ')}</p>
            <!--<p>Matched: ${recipe.matched.join(', ')}</p> -->
            ${recipe.picture_link ? `<img src="${recipe.picture_link}" alt="${recipe.title}" class="recipe-img">` : '<div class="recipe-img-placeholder">🍽️</div>'}
        `;
        // <p>${recipe.description}</p>
        resultsContainer.appendChild(card);
        console.log(recipe.id)
        card.addEventListener('click', () => {
            window.location.href = `/recipe?id=${recipe.id}`;
        });

    });
}

// // DROPDOWN AUTOCOMPLETE LOGIC
// let allIngredients = []; // store the full list

// // fetch all ingredients on page load
// const loadIngredients = async () => {
//     const res = await fetch('/ingredients');
//     allIngredients = await res.json();
// };

let ingredientCache = [];

async function initCache() {
  const res = await fetch('/ingredients/common');
  ingredientCache = await res.json();
}

initCache(); // call on page load

// filter as user types
ingredientInput.addEventListener('input', () => {
    const query = ingredientInput.value.trim().toLowerCase();
    if (query.length < 1) {
        datalist.innerHTML = '';
        return;
    }
    
    const cacheResults = fuzzySearch(ingredientCache, query);

    if (cacheResults.length >= 10) {
        datalist.innerHTML = cacheResults.slice(0, 10)
            .map(i => `<option value="${i}">`)
            .join('');
        return;
    }
    // Cache couldn't fill slots — hit API for the rest
    const needed = 10 - cacheResults.length;
    const excludeIds = cacheResults.map(i => i.id);
    


    // const matches = ingredientCache
    //     .filter(i => 
    //         i.toLowerCase().includes(query) && // match anywhere in the string  
    //             !pantry.some(p => p.name === i)
    //     )  // any ingredient containing what user typed
    //     .slice(0, 10);                   // limit to 10 suggestions


});

addTagButton.addEventListener('click', addTag);
ingredientInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') addTag();
});
prepopulatePantry();
loadIngredients();