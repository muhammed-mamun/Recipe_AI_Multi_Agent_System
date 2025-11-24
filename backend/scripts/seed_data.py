from backend.database.connection import get_supabase_client
from backend.database.vector_store import add_recipes
import json
import os

def load_json(filename):
    file_path = os.path.join(os.path.dirname(__file__), '..', 'data', filename)
    with open(file_path, 'r') as f:
        return json.load(f)

def seed_products():
    supabase = get_supabase_client()
    
    products = load_json('products.json')
    
    # Clear existing products (for demo purposes)
    try:
        supabase.table("products").delete().gte("created_at", "1970-01-01").execute()
    except Exception as e:
        print(f"Could not clear products: {e}")
    
    # Insert new products
    # Supabase might have a limit on bulk insert, so let's do it in chunks if needed, 
    # but for <100 items it's fine.
    supabase.table("products").insert(products).execute()
    print(f"Seeded {len(products)} products.")

def seed_recipes():
    raw_recipes = load_json('recipes.json')
    
    texts = []
    metadatas = []
    
    for r in raw_recipes:
        # Create a text representation for embedding
        text = f"{r['title']}: Ingredients: {', '.join(r['ingredients'])}. Instructions: {r['instructions']}"
        texts.append(text)
        
        # Metadata for retrieval
        metadatas.append({
            "title": r['title'],
            "ingredients": r['ingredients'],
            # We can store other fields too if needed
        })
    
    supabase = get_supabase_client()
    try:
        supabase.table("documents").delete().gte("id", "00000000-0000-0000-0000-000000000000").execute()
    except Exception as e:
        print(f"Could not clear documents: {e}")
    
    add_recipes(texts=texts, metadatas=metadatas)
    print(f"Seeded {len(texts)} recipes.")

if __name__ == "__main__":
    seed_products()
    seed_recipes()
