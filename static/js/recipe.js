// --- 1. Define Data Structures for FastAPI Interaction ---

// Matches the pydantic model expected by FastAPI for creation
interface IngredientCreate {
    item: string;
    quantity: string;
}

interface RecipeCreate {
    title: string;
    description: string;
    prepTime: string;
    cookTime: string;
    servings: number;
    ingredients: IngredientCreate[];
    instructions: string[];
}

// Matches the full Recipe model returned by FastAPI
interface RecipeResponse {
    id: number;
    title: string;
    description: string;
    prepTime: string;
    cookTime: string;
    servings: number;
    ingredients: IngredientCreate[];
    instructions: string[];
}

// --- 2. Constants and Helper Functions ---
const FASTAPI_URL = "http://127.0.0.1:8000/recipes"; // Assuming your endpoint is '/recipes'

// Helper to get form value or throw error for required fields
function getRequiredValue(id: string): string {
    const input = document.getElementById(id) as HTMLInputElement | HTMLTextAreaElement;
    if (!input || !input.value.trim()) {
        throw new Error(`Required field missing: ${id}`);
    }
    return input.value.trim();
}

// Helper to parse multi-line input into an array of strings (e.g., instructions)
function parseMultiLineInput(id: string): string[] {
    const value = getRequiredValue(id);
    return value.split('\n')
        .map(line => line.trim())
        .filter(line => line.length > 0);
}

// Helper to get ingredients (simplified for this example, assumes 'Item, Quantity' per line)
function parseIngredientsInput(id: string): IngredientCreate[] {
    const lines = parseMultiLineInput(id);
    return lines.map(line => {
        const parts = line.split(',').map(p => p.trim());
        return {
            item: parts[0] || 'Unknown Item',
            quantity: parts[1] || 'As needed'
        };
    });
}

// --- 3. Core Submission Logic ---

async function submitRecipe(event: Event): Promise<void> {
    event.preventDefault(); // Stop the form from submitting normally
    
    const statusElement = document.getElementById('status-message') as HTMLElement;
    const form = document.getElementById('recipe-form') as HTMLFormElement;

    if (!form) return;

    statusElement.textContent = "Submitting recipe...";
    statusElement.className = "text-yellow-600";
    
    try {
        // Construct the payload from form data
        const payload: RecipeCreate = {
            title: getRequiredValue('recipe-title'),
            description: getRequiredValue('recipe-description'),
            prepTime: getRequiredValue('prep-time'),
            cookTime: getRequiredValue('cook-time'),
            servings: parseInt(getRequiredValue('servings'), 10),
            ingredients: parseIngredientsInput('ingredients-input'),
            instructions: parseMultiLineInput('instructions-input')
        };
        
        console.log("Sending Payload:", payload);

        // API Call with Fetch
        const response = await fetch(FASTAPI_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                // FastAPI accepts CORS preflight, but in a real app,
                // you might need authorization headers here (e.g., 'Authorization': 'Bearer ...')
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            // Handle HTTP errors (4xx, 5xx)
            const errorData = await response.json();
            throw new Error(`FastAPI Error: ${response.status} - ${JSON.stringify(errorData)}`);
        }

        const newRecipe: RecipeResponse = await response.json();
        
        // Success feedback
        statusElement.textContent = `Success! Recipe "${newRecipe.title}" (ID: ${newRecipe.id}) created on the server.`;
        statusElement.className = "text-green-600 font-bold";
        
        // Optionally, clear the form after success
        form.reset();

    } catch (error) {
        // Handle network errors or custom errors thrown above
        const errorMessage = error instanceof Error ? error.message : "An unknown error occurred.";
        statusElement.textContent = `Submission failed: ${errorMessage}`;
        statusElement.className = "text-red-600 font-bold";
        console.error("Submission Error:", error);
    }
}

// --- 4. Event Listener Setup ---

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('recipe-form');
    if (form) {
        form.addEventListener('submit', submitRecipe);
    } else {
        console.error("Recipe form element not found.");
    }
});