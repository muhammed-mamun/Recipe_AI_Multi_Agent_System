import { Clock, Users, Star, ShoppingCart } from 'lucide-react';
import type { RecipeResult, MissingIngredient } from '../types';

interface RecipeCardProps {
  recipe: RecipeResult;
  missingIngredients?: MissingIngredient[];
}

export function RecipeCard({ recipe, missingIngredients = [] }: RecipeCardProps) {
  const totalCost = missingIngredients.reduce(
    (sum, ing) => sum + ing.price * ing.quantity,
    0
  );

  const handleBuyMissingItems = () => {
    alert(
      `Adding ${missingIngredients.length} items to cart (Total: ৳${totalCost.toFixed(2)})\n\n${missingIngredients
        .map(ing => `• ${ing.name} (${ing.quantity} ${ing.unit}) - ৳${(ing.price * ing.quantity).toFixed(2)}`)
        .join('\n')}`
    );
  };

  return (
    <div className="bg-gray-50 rounded-xl overflow-hidden border border-gray-200 hover:shadow-lg transition-shadow">
      <div className="relative h-40">
        <img
          src={recipe.image_url}
          alt={recipe.title}
          className="w-full h-full object-cover"
        />
        <div className="absolute top-2 right-2 bg-white px-2 py-1 rounded-full flex items-center space-x-1 shadow-md">
          <Star className="h-4 w-4 text-yellow-500 fill-current" />
          <span className="text-sm font-semibold text-gray-700">{recipe.rating.toFixed(1)}</span>
        </div>
      </div>

      <div className="p-4 space-y-3">
        <h4 className="font-bold text-gray-900 text-base line-clamp-2">{recipe.title}</h4>
        <p className="text-xs text-gray-600 line-clamp-2">{recipe.description}</p>

        <div className="flex items-center justify-between text-xs text-gray-500">
          <div className="flex items-center space-x-1">
            <Clock className="h-4 w-4" />
            <span>{recipe.prep_time + recipe.cook_time} min</span>
          </div>
          <div className="flex items-center space-x-1">
            <Users className="h-4 w-4" />
            <span>{recipe.servings} servings</span>
          </div>
          <div className="px-2 py-1 bg-orange-100 text-orange-700 rounded-full font-medium">
            {recipe.difficulty}
          </div>
        </div>

        {missingIngredients.length > 0 && (
          <div className="pt-3 border-t border-gray-200 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-gray-700">Missing Ingredients:</span>
              <span className="text-sm font-bold text-orange-600">৳{totalCost.toFixed(2)}</span>
            </div>
            <div className="space-y-1 max-h-20 overflow-y-auto">
              {missingIngredients.slice(0, 3).map((ing, index) => (
                <div key={index} className="text-xs text-gray-600 flex justify-between">
                  <span>• {ing.name}</span>
                  <span className="font-medium">৳{(ing.price * ing.quantity).toFixed(2)}</span>
                </div>
              ))}
              {missingIngredients.length > 3 && (
                <div className="text-xs text-gray-500 italic">
                  +{missingIngredients.length - 3} more items
                </div>
              )}
            </div>
            <button
              onClick={handleBuyMissingItems}
              className="w-full bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white font-semibold py-2 px-4 rounded-lg flex items-center justify-center space-x-2 transition-all duration-300 transform hover:scale-105 shadow-md"
            >
              <ShoppingCart className="h-4 w-4" />
              <span className="text-sm">Buy Missing Items</span>
            </button>
          </div>
        )}

        {missingIngredients.length === 0 && (
          <div className="pt-3 border-t border-gray-200">
            <div className="bg-green-50 text-green-700 px-3 py-2 rounded-lg text-center text-xs font-semibold">
              ✓ You have all ingredients!
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
