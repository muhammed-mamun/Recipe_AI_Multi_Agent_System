from phi.agent import Agent
from backend.model import get_model
from backend.agents.chef import chef_logic
from backend.agents.support import get_support_agent
from backend.agents.product import product_search_logic

def get_orchestrator_agent():
    return Agent(
        name="Orchestrator",
        model=get_model(),
        description="You are a friendly AI assistant for Chaldal - Bangladesh's leading online grocery platform. You help customers with recipes, products, and support.",
        instructions=[
            "If the user asks about cooking, recipes, or mentions ingredients they have, route to the Chef Logic.",
            "If the user asks about policies, delivery, refunds, or support, route to the Support Agent.",
            "If the user asks about specific product price or availability, classify as PRODUCT_QUERY.",
            "For general greetings and chat, be warm, welcoming, and helpful.",
            "Use emojis appropriately to make responses engaging (🛍️ 👨‍🍳 📦 🎉 😊).",
            "Keep responses friendly and conversational.",
            "Always offer to help with recipes, products, or support questions."
        ],
        markdown=True
    )

def handle_request(user_query: str):
    agent = get_orchestrator_agent()
    
    # Intent classification
    classification_prompt = f"""
    Classify the following user query into one of these categories:
    
    1. COOKING_QUERY - User wants recipe suggestions, cooking ideas, or meal planning
       Examples: 
       - "I have chicken and rice, what can I cook?"
       - "Show me fish recipes"
       - "What can I make for dinner?"
       - "I want to cook something with potato"
       - "Suggest me a dessert recipe"
       - "How to make tehari?"
       - "Give me a recipe for breakfast"
    
    2. PRODUCT_QUERY - User asks about specific product price, availability, or wants to buy something
       Examples:
       - "How much does tomato cost?"
       - "Is chicken available?"
       - "Show me vegetables"
    
    3. SUPPORT_QUERY - User asks about policies, delivery, refunds, or customer service
       Examples:
       - "What is your return policy?"
       - "How long does delivery take?"
       - "How do I get a refund?"
    
    4. OTHER - General greetings, thanks, or casual conversation
       Examples:
       - "Hello"
       - "Thank you"
       - "Who are you?"
    
    User Query: "{user_query}"
    
    Return ONLY the category name (COOKING_QUERY, PRODUCT_QUERY, SUPPORT_QUERY, or OTHER).
    """
    
    try:
        response = agent.run(classification_prompt)
        intent = response.content.strip()
    except Exception as e:
        print(f"Error during intent classification: {e}")
        # Get the actual model being used
        import os
        model_name = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-exp:free")
        # Return a helpful error message
        return f"""### ⚠️ Service Temporarily Unavailable

I'm having trouble connecting to the AI service right now. This could be due to:

- **API Key Issues**: The OpenRouter API key may be invalid or expired
- **Model Availability**: The selected model ({model_name}) may not be available
- **Rate Limits**: API quota may have been exceeded

**Please check:**
1. Your `OPENROUTER_API_KEY` in the `.env` file
2. Try switching to a free model like `google/gemini-2.0-flash-exp:free`
3. Check your OpenRouter dashboard for API status

**Meanwhile, you can:**
- 📞 Call **16716** for immediate assistance
- 🌐 Visit **chaldal.com** to browse products
- 📱 Use our mobile app

Sorry for the inconvenience! 😊"""
    
    if "COOKING_QUERY" in intent:
        return chef_logic(user_query)
    elif "SUPPORT_QUERY" in intent:
        support_agent = get_support_agent()
        try:
            return support_agent.run(user_query).content
        except Exception as e:
            print(f"Error in support agent: {e}")
            return "I'm having trouble processing your request. Please try again or contact support at 16716."
    elif "PRODUCT_QUERY" in intent:
        # Route to product search agent
        return product_search_logic(user_query)
    else:
        # General chat
        try:
            return agent.run(f"Answer this user query politely: {user_query}").content
        except Exception as e:
            print(f"Error in general chat: {e}")
            return "I'm having trouble processing your request. Please try again or contact support at 16716."
