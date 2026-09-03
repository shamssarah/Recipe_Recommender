// Renders a recipe from /recipe endpoint using the WiseCook data schema.

const app = document.getElementById('app');
prepTime = document.getElementById('prep-time');
cookTime = document.getElementById('cook-time');
totalTime = document.getElementById('total-time');
servings = document.getElementById('servings');
ingredientsList = document.getElementById('ingredients-list');
instructionsList = document.getElementById('instructions-list');

// document.getElementById('calories').textContent = data.calories ?? '—';
// document.getElementById('protein').textContent = data.protein ? `${data.protein}g` : '—';
// document.getElementById('carbs').textContent = data.carbs ? `${data.carbs}g` : '—';
// document.getElementById('fat').textContent = data.fat ? `${data.fat}g` : '—';
// document.getElementById('fiber').textContent = data.fiber ? `${data.fiber}g` : '—';
// document.getElementById('rating').textContent = data.rating ?? '—';
// document.getElementById('difficulty').textContent = data.difficulty ?? '—';
// --- additional fields (add these after servings.textContent) ---
   

// ── Helpers ────────────────────────────────────────────────

/** Format a cleaned_ingredient into a quantity string, e.g. "2 tbsp" */
function fmtQty(ing) {
    const parts = [ing.quantity, ing.unit].filter(Boolean);
    return parts.join(' ');
}

/** Split instruction string on newlines, filter blank lines */
function splitInstructions(instructions) {
    if (Array.isArray(instructions)) {
        return instructions.map(s => s.trim()).filter(Boolean);
    }
    return instructions.split('\n').map(s => s.trim()).filter(Boolean);
}

// ── Render ─────────────────────────────────────────────────

// const loadRecipe = async () => {
async function loadRecipe() {
    console.log('loadRecipe called');
    console.log('id:', new URLSearchParams(window.location.search).get('id'));
    
    const params = new URLSearchParams(window.location.search);
    const id = params.get('id');

    if (!id) {                          // ← guard added
        renderError('No recipe ID provided.');
        return;
    }

    const response = await fetch(`/recipe/${id}`);

    if (!response.ok) {                 // ← check before .json()
        const err = await response.json().catch(() => ({}));
        renderError(err.detail ?? 'Recipe not found.');
        return;
    }

    if (response.ok) {
        console.log('Recipe data fetched successfully');
        const data = await response.json();
        console.log('loading cuisine');
        prepTime.textContent = data.prep_time ?? '—';
        cookTime.textContent = data.cook_time ?? '—';
        totalTime.textContent = data.total_time ?? '—';
        servings.textContent = data.servings ?? '—';
        console.log('loading cuisine');

        document.getElementById('cuisine').textContent =
            (data.cuisine_list && data.cuisine_list.length) ? data.cuisine_list.join(', ') : '—';

        document.getElementById('description').textContent = data.description ?? '';
        
        data.cleaned_ingredients.forEach(ing => {
            const li = document.createElement('li');
            li.textContent = `${fmtQty(ing)} ${ing.ingredient}`;
            ingredientsList.appendChild(li);
        });
        data.instructions.forEach(step => {
            const li = document.createElement('li');
            li.textContent = step;
            instructionsList.appendChild(li);
        });
    } else {
        console.error('Failed to load recipe');
    }  

    // ── Animate in ──────────────────────────────────────────

    // Image fade
    const img = document.getElementById('recipe-image');
    if (img) {
        if (img.complete) {
            img.classList.add('loaded');
        } else {
            img.onload = () => img.classList.add('loaded');
            img.onerror = () => img.style.display = 'none';
        }
    }

    // Staggered reveal
    requestAnimationFrame(() => {
        document.getElementById('hero-title')?.classList.add('visible');
        document.getElementById('tag-strip')?.classList.add('visible');
        setTimeout(() => document.getElementById('stats-bar')?.classList.add('visible'), 60);
        setTimeout(() => document.getElementById('ing-col')?.classList.add('visible'), 120);
        setTimeout(() => document.getElementById('inst-col')?.classList.add('visible'), 200);
    });
}


function renderError(msg) {
    app.innerHTML = `
        <div class="state-msg">
            <p style="margin-bottom:.5rem">⚠️</p>
            <p>${msg}</p>
            <p style="margin-top:1rem;font-size:.85rem">
                <a href="/" style="color:var(--accent)">← Back to search</a>
            </p>
        </div>`;
}

document.addEventListener('DOMContentLoaded', loadRecipe);
