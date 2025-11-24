import type { ChatResponse } from '../types';

const API_URL = 'http://localhost:8000';

export async function sendChatMessage(message: string): Promise<ChatResponse> {
    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message }),
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();

        // The backend currently returns a string response. 
        // We need to parse it if it contains structured data (like the Buy Button JSON),
        // or just return it as a message.

        // TODO: The backend agent returns a string. We might need to parse structured data from it
        // if the agent is designed to return JSON embedded in text.
        // For now, we'll just display the text.

        // Check if the response contains the specific JSON marker for buy button
        // "[BUY_BUTTON_DATA: { ... }]"

        let content = data.response;
        let missingIngredients = [];
        let recipes = [];

        // Simple parsing logic if the agent returns structured data in the text
        // This is a basic implementation based on the Chef Agent's prompt instructions
        const buyButtonRegex = /\[BUY_BUTTON_DATA: ({.*?})\]/;
        const match = content.match(buyButtonRegex);

        if (match) {
            try {
                const buyData = JSON.parse(match[1]);
                // We might want to structure this better in the future
                // For now, let's just strip the JSON from the display text
                content = content.replace(match[0], '');

                // If we had a way to pass this data to the UI, we would.
                // The current UI expects 'missingIngredients' array.
                // We might need to adapt the backend to return cleaner JSON.
            } catch (e) {
                console.error("Failed to parse buy button data", e);
            }
        }

        return {
            message: content,
            recipes: [], // Backend doesn't return structured recipes yet, just text
            missingIngredients: [], // Backend doesn't return structured missing ingredients yet
        };

    } catch (error) {
        console.error('Error in AI service:', error);
        return {
            message: "Sorry, I encountered an error connecting to the AI agent. Please ensure the backend is running!",
        };
    }
}

