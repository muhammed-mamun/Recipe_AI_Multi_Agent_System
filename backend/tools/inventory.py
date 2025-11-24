from backend.database.connection import get_supabase_client

def check_inventory(ingredients: list[str]) -> str:
    """
    Checks the inventory for a list of ingredients.
    Returns a formatted string with available and missing items, and total price.
    
    Args:
        ingredients: List of ingredient names to check
        
    Returns:
        Formatted string with inventory status
    """
    supabase = get_supabase_client()
    
    available_items = []
    missing_items = []
    total_price_missing = 0.0
    
    # Normalize ingredients for simple matching (lowercase)
    # In a real app, this would be more complex (fuzzy matching)
    
    # Fetch all products (simplification for prototype)
    response = supabase.table("products").select("*").execute()
    products = response.data
    
    product_map = {p['name'].lower(): p for p in products}
    
    for ingredient in ingredients:
        ing_lower = ingredient.lower()
        found = False
        for p_name, p_data in product_map.items():
            if ing_lower in p_name or p_name in ing_lower:
                if p_data['stock_quantity'] > 0:
                    available_items.append(p_data)
                    found = True
                    break
        
        if not found:
            # Check if we sell it but it's out of stock, or if we just sell it
            # For the "Buy Missing" feature, we assume we can buy it if it exists in DB
            # If it doesn't exist in DB, we can't buy it.
            # Let's assume if it matches a product name, we can buy it.
             for p_name, p_data in product_map.items():
                if ing_lower in p_name or p_name in ing_lower:
                     missing_items.append(p_data)
                     total_price_missing += float(p_data['price'])
                     found = True
                     break
            
             if not found:
                 # Item not in store at all
                 pass

    # Format as string for the AI agent
    result = f"Inventory Check Results:\n\n"
    
    if available_items:
        result += "✅ Available in stock:\n"
        for item in available_items:
            result += f"  - {item['name']} - ৳{item['price']} (Stock: {item['stock_quantity']})\n"
    
    if missing_items:
        result += "\n🛒 Available to buy:\n"
        for item in missing_items:
            result += f"  - {item['name']} - ৳{item['price']}\n"
        result += f"\n💰 Total cost for missing items: ৳{total_price_missing}"
    
    if not available_items and not missing_items:
        result += "No matching items found in our store."
    
    return result
