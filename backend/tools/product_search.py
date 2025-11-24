"""
Product search functionality
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from backend.database.connection import get_supabase_client
except ModuleNotFoundError:
    from database.connection import get_supabase_client

def search_products(query: str, category: str = None, limit: int = 10):
    """
    Search for products by name or category
    
    Args:
        query: Search term (e.g., "chicken", "meat", "vegetables")
        category: Optional category filter
        limit: Maximum number of results
    
    Returns:
        List of matching products with name, price, stock_quantity, category
    """
    supabase = get_supabase_client()
    
    try:
        # Build query
        query_builder = supabase.table("products").select("*")
        
        # Search in name or category
        if query:
            query_lower = query.lower()
            # Use ilike for case-insensitive search
            query_builder = query_builder.or_(f"name.ilike.%{query_lower}%,category.ilike.%{query_lower}%")
        
        # Filter by category if specified
        if category:
            query_builder = query_builder.eq("category", category)
        
        # Order by stock quantity (show in-stock items first)
        query_builder = query_builder.order("stock_quantity", desc=True).limit(limit)
        
        response = query_builder.execute()
        
        return response.data if response.data else []
        
    except Exception as e:
        print(f"Error searching products: {e}")
        return []

def get_products_by_category(category: str):
    """
    Get all products in a specific category
    
    Args:
        category: Category name (e.g., "Meat", "Fish", "Vegetables")
    
    Returns:
        List of products in that category
    """
    return search_products(query="", category=category, limit=50)

def get_available_products(query: str = None):
    """
    Get only in-stock products
    
    Args:
        query: Optional search term
    
    Returns:
        List of available (in-stock) products
    """
    supabase = get_supabase_client()
    
    try:
        query_builder = supabase.table("products").select("*").gt("stock_quantity", 0)
        
        if query:
            query_lower = query.lower()
            query_builder = query_builder.or_(f"name.ilike.%{query_lower}%,category.ilike.%{query_lower}%")
        
        query_builder = query_builder.order("name")
        
        response = query_builder.execute()
        return response.data if response.data else []
        
    except Exception as e:
        print(f"Error getting available products: {e}")
        return []
