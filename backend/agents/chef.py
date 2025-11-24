from phi.agent import Agent
from backend.model import get_model
from backend.database.vector_store import search_recipes
from backend.tools.inventory import check_inventory
import json

def get_chef_agent():
    return Agent(
        name="Chef Agent",
        model=get_model(),
        description="You are a friendly, enthusiastic Chef that helps customers discover delicious Bangladeshi recipes.",
        instructions=[
            "You help customers find recipes based on what they have or what they want to cook.",
            "Use search_recipes tool to find relevant recipes.",
            "Use check_inventory tool to see which ingredients are available in our store.",
            "Format responses beautifully with emojis and clear sections.",
            "For each recipe, show:",
            "  - Recipe name with emoji",
            "  - Brief description",
            "  - List of ingredients (mark which ones they might need to buy)",
            "  - Simple cooking instructions",
            "  - Missing ingredients with prices and 'Add to Cart' option",
            "Use cooking emojis: 👨‍🍳 🍳 🥘 🍛 🐟 🥩 🍚 🥔 🧅 🌶️ ✨ 💰",
            "Be enthusiastic about food and make customers excited to cook!",
            "Prioritize recipes where we have most ingredients in stock.",
            "End with a friendly offer to help with anything else."
        ],
        tools=[search_recipes, check_inventory], 
        markdown=True,
        show_tool_calls=False
    )

def chef_logic(user_query: str):
    """
    Custom logic to orchestrate the Chef's workflow more explicitly than just LLM tool calling,
    to ensure the 'Marketing Trick' is applied correctly.
    """
    # 1. Search for recipes based on the query
    # We assume the query contains ingredients.
    try:
        recipes = search_recipes(user_query, k=5)
    except Exception as e:
        print(f"Error searching recipes: {e}")
        # Return a helpful message if database is not set up
        return """### 👨‍🍳 Recipe Feature Coming Soon!

I'd love to help you discover amazing recipes with your ingredients! 🥘

However, our recipe database is currently being set up. Once it's ready, I'll be able to:

✨ **Suggest delicious recipes** based on what you have
🛍️ **Find missing ingredients** in our store
💰 **Calculate costs** for ingredients you need
📦 **Add items to cart** with one click

**Meanwhile, I can help you with:**
- 🛒 Product availability and prices
- 📞 Customer support questions
- 🚚 Delivery information
- 💳 Refund and return policies

What else can I assist you with today? 😊"""
    
    agent = get_chef_agent()
    
    prompt = f"""
    Customer Query: "{user_query}"
    
    Help this customer find delicious recipes! Here's what to do:
    
    1. Use search_recipes tool to find relevant recipes based on their query
    2. Show the top 2-3 most relevant recipes
    3. For each recipe, present it beautifully with:
       - An appetizing title with emoji
       - Brief description
       - List of ingredients needed
       - Simple cooking instructions
    
    IMPORTANT: After EACH recipe, add a line that says:
    **🛒 Missing Ingredients for this recipe:**
    Common items you might need: onions, spices, etc.
    
    Then add a special tag: [BUY_RECIPE_X: INGREDIENTS_LIST]
    Where X is the recipe number (1, 2, 3) and INGREDIENTS_LIST is comma-separated ingredients needed for that specific recipe.
    
    Example:
    [BUY_RECIPE_1: Onion, Garam Masala, Ginger, Turmeric]
    
    Format like this:
    
    ### 👨‍🍳 Recipe Suggestions for You!
    
    #### 🍛 Recipe Name 1
    *Brief description*
    
    **Ingredients:**
    - Ingredient 1
    - Ingredient 2
    
    **How to Make:**
    [Instructions]
    
    **🛒 Missing Ingredients for this recipe:**
    [BUY_RECIPE_1: Onion, Garam Masala, Ginger]
    
    ---
    
    #### 🍛 Recipe Name 2
    ...
    [BUY_RECIPE_2: Tomato, Cumin, Yogurt]
    
    Make it exciting and encourage them to cook!
    """
    
    response = agent.run(prompt)
    content = response.content
    
    print(f"\n=== CHEF RESPONSE DEBUG ===")
    print(f"Original content length: {len(content)}")
    
    # Find all [BUY_RECIPE_X: ...] tags and replace with proper JSON
    import re
    import json
    
    # Pattern to find [BUY_RECIPE_1: Onion, Garam Masala, Ginger]
    recipe_pattern = r'\[BUY_RECIPE_(\d+):\s*([^\]]+)\]'
    
    def replace_recipe_tag(match):
        recipe_num = match.group(1)
        ingredients_str = match.group(2).strip()
        
        # Split ingredients by comma
        ingredients_list = [ing.strip() for ing in ingredients_str.split(',')]
        
        print(f"Processing recipe {recipe_num} with ingredients: {ingredients_list}")
        
        try:
            # Use check_inventory to get prices
            inventory_result = check_inventory(ingredients_list)
            
            print(f"Inventory result for recipe {recipe_num}:")
            print(inventory_result)
            
            # Parse prices - check_inventory returns lines like:
            # "  - Onion (Deshi) - ৳110 (Stock: 50)" or "  - Onion (Deshi) - ৳110"
            items = []
            total = 0
            lines = inventory_result.split('\n')
            for line in lines:
                # Match pattern: "  - NAME - ৳PRICE" (with optional stock info)
                if '৳' in line and '-' in line:
                    match_price = re.search(r'-\s*(.+?)\s*-\s*৳(\d+)', line)
                    if match_price:
                        name = match_price.group(1).strip()
                        price = int(match_price.group(2))
                        items.append({"name": name, "price": price})
                        total += price
                        print(f"  Found: {name} - ৳{price}")
            
            if items:
                buy_data = {"items": items, "total": total}
                print(f"Created buy data with {len(items)} items, total: ৳{total}")
                return f"\n\n[BUY_INGREDIENTS: {json.dumps(buy_data)}]"
            else:
                print("No items found in inventory, using fallback")
                # Fallback with estimated prices
                fallback_items = []
                for ing in ingredients_list[:3]:  # Limit to 3 items
                    fallback_items.append({"name": ing, "price": 100})
                fallback_total = len(fallback_items) * 100
                buy_data = {"items": fallback_items, "total": fallback_total}
                return f"\n\n[BUY_INGREDIENTS: {json.dumps(buy_data)}]"
                
        except Exception as e:
            print(f"Error processing recipe {recipe_num}: {e}")
            # Fallback
            fallback_items = [{"name": ing, "price": 100} for ing in ingredients_list[:3]]
            buy_data = {"items": fallback_items, "total": len(fallback_items) * 100}
            return f"\n\n[BUY_INGREDIENTS: {json.dumps(buy_data)}]"
    
    # Replace all recipe tags with proper JSON
    content = re.sub(recipe_pattern, replace_recipe_tag, content)
    
    print(f"Final content length: {len(content)}")
    print(f"Number of BUY_INGREDIENTS tags: {content.count('[BUY_INGREDIENTS:')}")
    print(f"=== END DEBUG ===\n")
    
    return content



