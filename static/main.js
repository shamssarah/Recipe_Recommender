document.addEventListener('DOMContentLoaded', () => {
    const ingredientInput = document.getElementById('ingredient-input');
    const addTagButton = document.getElementById('add-tag-button');
    const filterButton = document.getElementById('filter-button');
    const tagContainer = document.getElementById('tag-container');
    const recipeItems = document.querySelectorAll('.recipe-item');

    // --- 1. Add Tags Functionality ---
    const addTags = () => {
        // Get input value and split it by commas or spaces
        let ingredients = ingredientInput.value
            .split(/[\s,]+/) // Split by comma or one or more spaces
            .map(tag => tag.trim().toLowerCase()) // Clean up and normalize text
            .filter(tag => tag.length > 0); // Remove empty strings

        ingredients.forEach(ingredient => {
            // Check if tag already exists to prevent duplicates
            if (!document.querySelector(`[data-ingredient="${ingredient}"]`)) {
                
                // Create the tag element (a span)
                const tag = document.createElement('span');
                tag.classList.add('tag');
                tag.setAttribute('data-ingredient', ingredient);
                tag.innerHTML = `${ingredient} <button class="remove-tag">x</button>`;
                
                // Add an event listener to the remove button
                tag.querySelector('.remove-tag').addEventListener('click', () => {
                    tag.remove(); // Remove the tag when 'x' is clicked
                    filterRecipes(); // Re-run the filter after a tag is removed
                });

                tagContainer.appendChild(tag);
            }
        });

        ingredientInput.value = ''; // Clear the input field
        filterRecipes(); // Run the filter immediately after adding new tags
    };

    // Attach event listeners for adding tags
    addTagButton.addEventListener('click', addTags);
    ingredientInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault(); // Prevent form submission
            addTags();
        }
    });

    // --- 2. Filter Recipes Functionality ---
    const filterRecipes = () => {
        // 1. Get all active tags from the tag container
        const activeTags = Array.from(tagContainer.querySelectorAll('.tag'))
            .map(tag => tag.getAttribute('data-ingredient'));

        // If there are no active tags, show all recipes
        if (activeTags.length === 0) {
            recipeItems.forEach(item => item.style.display = 'block');
            return;
        }

        // 2. Iterate over all recipe items and check for a match
        recipeItems.forEach(item => {
            const recipeTagsString = item.getAttribute('data-tags');
            // Convert the recipe's ingredient list into an array of lowercase strings
            const recipeTags = recipeTagsString.split(',').map(tag => tag.trim().toLowerCase());

            // Check if *all* activeTags are present in the recipeTags array (AND logic)
            // You can change this to 'OR' logic if you want a recipe to show if it has *any* of the tags.
            const matchesAllTags = activeTags.every(activeTag => 
                recipeTags.includes(activeTag)
            );

            // 3. Display or hide the recipe item
            if (matchesAllTags) {
                item.style.display = 'block'; // Show item
            } else {
                item.style.display = 'none';  // Hide item
            }
        });
    };

    // Attach event listener for the main filter button (optional, as tags add already triggers it)
    filterButton.addEventListener('click', filterRecipes);
});