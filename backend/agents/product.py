"""
Product Agent - Handles product search and availability queries
"""
from phi.agent import Agent
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from backend.model import get_model
    from backend.tools.product_search import search_products, get_available_products
except ModuleNotFoundError:
    from model import get_model
    from tools.product_search import search_products, get_available_products

def get_product_agent():
    return Agent(
        name="Product Agent",
        model=get_model(),
        description="You are a friendly, enthusiastic Product Search Agent for Chaldal - Bangladesh's leading online grocery platform.",
        instructions=[
            "You help customers discover products with warmth and excitement!",
            "Use the search_products and get_available_products tools to find items.",
            "Create visually stunning responses with emojis, cards, and clear sections.",
            "Start responses with a friendly greeting or acknowledgment.",
            "Group products by category with beautiful headers.",
            "For each product, show:",
            "  - Product name in **bold**",
            "  - Price in ৳ (Bangladeshi Taka)",
            "  - Stock status with ✅ (available) or ❌ (out of stock)",
            "  - Stock quantity for available items",
            "Use category-specific emojis:",
            "  - Fish/Seafood: 🐟 🦐 🦞",
            "  - Meat: 🥩 🍗 🥓",
            "  - Vegetables: 🥬 🍅 🥔 🧅 🌶️ 🥕",
            "  - Fruits: 🍎 🍌 🍊 🥭",
            "  - Dairy: 🥛 🧀 🥚",
            "  - Grains/Rice: 🍚 🌾",
            "  - General: 🛒 💰 ✨ 🎉",
            "Add helpful context like 'Fresh arrivals!' or 'Limited stock!'",
            "End with friendly offers like suggesting recipes or adding to cart.",
            "If products are out of stock, be empathetic and suggest alternatives.",
            "Keep the tone conversational, warm, and helpful - like a friendly shopkeeper!",
            "Use line breaks and spacing to make responses easy to scan."
        ],
        tools=[search_products, get_available_products],
        markdown=True,
        show_tool_calls=False
    )

def product_search_logic(user_query: str):
    """
    Handle product search queries with beautiful, engaging responses
    """
    try:
        agent = get_product_agent()
        
        prompt = f"""
        Customer Query: "{user_query}"
        
        Help this customer find amazing products! Use the search tools to find matching items.
        
        Create a beautiful, engaging response following this structure:
        
        1. **Friendly Opening** (1 line)
           - Acknowledge their request warmly
           - Example: "Great choice! Here's what we have for fish today 🐟"
        
        2. **Product Showcase**
           Use this exact format:
           
           ### 🐟 [Category Name] Products
           
           **✨ Available Now:**
           - **Product Name (size/unit)** - ৳Price (Stock: X units) ✅
           - **Product Name (size/unit)** - ৳Price (Stock: X units) ✅
           
           **📦 Currently Out of Stock:**
           - **Product Name (size/unit)** - ৳Price ❌
           - **Product Name (size/unit)** - ৳Price ❌
        
        3. **Helpful Context** (1-2 lines)
           - Add friendly commentary about availability
           - Example: "Fresh arrivals daily! 🌊" or "Limited stock on premium items!"
        
        4. **Call to Action** (1-2 lines)
           - Offer to help add to cart, suggest recipes, or provide more info
           - Example: "Want me to suggest some delicious fish recipes? 👨‍🍳 Or shall I help you add these to your cart? 🛒"
        
        Make it feel personal, warm, and helpful - like chatting with a friendly shopkeeper who knows their products!
        """
        
        response = agent.run(prompt)
        return response.content
        
    except Exception as e:
        print(f"Error in product search: {e}")
        return """### 🛍️ Oops! Having Trouble Accessing Products

I'd love to help you find what you're looking for, but I'm having trouble connecting to our product database right now. 😔

**Here's what you can do:**
- 📱 **Browse our mobile app** - Full catalog available
- 🌐 **Visit chaldal.com** - Shop online anytime
- 📞 **Call 16716** - Our team is ready to help!

**Or I can help you with:**
- 👨‍🍳 Recipe suggestions based on ingredients
- 🚚 Delivery timing and areas  
- 💳 Return & refund policies
- ❓ Any questions about Chaldal

What would you like to know? I'm here to help! 😊"""
