import React from 'react';
import clsx from 'clsx';
import { Bot, User } from 'lucide-react';
import { RecipeCard } from './RecipeCard';

interface Message {
    role: 'user' | 'agent';
    content: string;
}

interface ChatMessageProps {
    message: Message;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
    const isUser = message.role === 'user';

    // Parse content for Recipe Card data
    // Expected format from Agent: ... [BUY_BUTTON_DATA: { ... }] ...
    // This is a simplified parser. In production, use structured output from LLM.

    let content = message.content;
    let recipeData = null;

    // Regex to find the JSON block
    const jsonMatch = content.match(/\[BUY_BUTTON_DATA: (\{.*?\})\]/);

    if (jsonMatch) {
        try {
            // The agent might return multiple recipes. This simple parser handles one or needs adjustment.
            // For the prototype, let's assume the agent returns a structured JSON or we parse the text carefully.
            // Actually, the agent prompt asked to return text + JSON string.
            // Let's just try to parse the JSON if present.
            // But wait, the prompt said "For each recipe...". So there might be multiple.

            // Let's just render the text for now, and if we find the special tag, we try to render a card.
            // A better way is to have the agent return a list of objects.
            // For this prototype, let's just clean the text and show the raw text, 
            // but if we can parse it into a card, great.

            // Let's assume the agent returns markdown and we just render markdown.
            // But we want the interactive button.

            // Let's stick to text rendering for the main content, and maybe extract the "Buy" data to show a button below.
            // pass
        } catch (e) {
            console.error("Failed to parse recipe data", e);
        }
    }

    // To make it robust for the demo:
    // We will split the content by the special marker.
    const parts = content.split(/\[BUY_BUTTON_DATA: (\{.*?\})\]/);

    return (
        <div className={clsx("flex gap-3 max-w-3xl mx-auto p-4", isUser ? "flex-row-reverse" : "flex-row")}>
            <div className={clsx("w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0", isUser ? "bg-blue-500" : "bg-green-500")}>
                {isUser ? <User size={16} className="text-white" /> : <Bot size={16} className="text-white" />}
            </div>

            <div className={clsx("flex-1 rounded-lg p-4", isUser ? "bg-blue-50" : "bg-white border border-gray-100 shadow-sm")}>
                <div className="prose text-sm text-gray-800 whitespace-pre-wrap">
                    {parts.map((part, i) => {
                        if (part.trim().startsWith('{') && part.trim().endsWith('}')) {
                            try {
                                const data = JSON.parse(part);
                                // We need to map this data to RecipeCardProps
                                // The agent returns { 'items': [...], 'total': ... }
                                // But RecipeCard needs title, instructions etc.
                                // The agent prompt asked to "Display... Recipe Name...".
                                // So the text part contains the details.
                                // The JSON only contains the buy data.

                                // This is a bit disjointed. 
                                // Let's just show a "Buy Missing Ingredients" button for this block.
                                return (
                                    <div key={i} className="mt-2 p-3 bg-yellow-50 border border-yellow-100 rounded-md flex justify-between items-center">
                                        <div>
                                            <p className="font-bold text-yellow-800">Missing Ingredients Bundle</p>
                                            <p className="text-xs text-yellow-600">{data.items.map((x: any) => x.name).join(', ')}</p>
                                        </div>
                                        <button
                                            className="bg-yellow-500 text-white px-3 py-1 rounded text-sm font-bold hover:bg-yellow-600"
                                            onClick={() => alert(`Buying bundle for ৳${data.total}`)}
                                        >
                                            Buy for ৳{data.total}
                                        </button>
                                    </div>
                                );
                            } catch (e) {
                                return null;
                            }
                        } else {
                            return <span key={i}>{part}</span>;
                        }
                    })}
                </div>
            </div>
        </div>
    );
};

export default ChatMessage;
