export interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
    recipes?: RecipeResult[];
    missingIngredients?: MissingIngredient[];
}

export interface RecipeResult {
    id: string;
    title: string;
    description: string;
    image_url: string;
    prep_time: number;
    cook_time: number;
    servings: number;
    difficulty: string;
    rating: number;
}

export interface MissingIngredient {
    name: string;
    quantity: number;
    unit: string;
    price: number;
    product_id: string | null;
    in_stock: boolean;
}

export interface ChatResponse {
    message: string;
    recipes?: RecipeResult[];
    missingIngredients?: MissingIngredient[];
}
