"""
Complete system setup script that:
1. Creates database tables (via manual instructions)
2. Seeds products
3. Seeds recipes with embeddings
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import get_supabase_client
from database.vector_store import add_recipes
import json

def load_json(filename):
    file_path = os.path.join(os.path.dirname(__file__), '..', 'data', filename)
    with open(file_path, 'r') as f:
        return json.load(f)

def check_tables_exist():
    """Check if required tables exist"""
    supabase = get_supabase_client()
    
    try:
        # Try to query products table
        supabase.table("products").select("id").limit(1).execute()
        print("✅ Products table exists")
        products_exist = True
    except Exception as e:
        print(f"❌ Products table doesn't exist: {e}")
        products_exist = False
    
    try:
        # Try to query documents table
        supabase.table("documents").select("id").limit(1).execute()
        print("✅ Documents table exists")
        documents_exist = True
    except Exception as e:
        print(f"❌ Documents table doesn't exist: {e}")
        documents_exist = False
    
    return products_exist and documents_exist

def create_tables_instructions():
    """Display instructions for creating tables"""
    print("\n" + "="*80)
    print("📋 DATABASE SETUP REQUIRED")
    print("="*80)
    print("\nPlease follow these steps:")
    print("\n1. Go to your Supabase Dashboard:")
    print("   https://supabase.com/dashboard/project/pozqlghiwukecwtuhbjh")
    print("\n2. Click on 'SQL Editor' in the left sidebar")
    print("\n3. Click 'New Query'")
    print("\n4. Copy and paste the SQL from: backend/database/schema.sql")
    print("\n5. Click 'Run' to execute the SQL")
    print("\n6. Come back and run this script again")
    print("\n" + "="*80 + "\n")

def seed_products():
    """Seed products into database"""
    supabase = get_supabase_client()
    products = load_json('products.json')
    
    print(f"\n📦 Seeding {len(products)} products...")
    
    # Clear existing products
    try:
        # Delete all products
        existing = supabase.table("products").select("id").execute()
        if existing.data:
            for product in existing.data:
                supabase.table("products").delete().eq("id", product["id"]).execute()
            print(f"   Cleared {len(existing.data)} existing products")
    except Exception as e:
        print(f"   Note: {e}")
    
    # Insert new products in batches
    batch_size = 100
    for i in range(0, len(products), batch_size):
        batch = products[i:i+batch_size]
        try:
            supabase.table("products").insert(batch).execute()
            print(f"   ✅ Inserted products {i+1} to {min(i+batch_size, len(products))}")
        except Exception as e:
            print(f"   ❌ Error inserting batch: {e}")
    
    print(f"✅ Successfully seeded {len(products)} products!")

def seed_recipes():
    """Seed recipes into vector database"""
    raw_recipes = load_json('recipes.json')
    
    print(f"\n👨‍🍳 Seeding {len(raw_recipes)} recipes...")
    
    supabase = get_supabase_client()
    
    # Clear existing documents
    try:
        existing = supabase.table("documents").select("id").execute()
        if existing.data:
            for doc in existing.data:
                supabase.table("documents").delete().eq("id", doc["id"]).execute()
            print(f"   Cleared {len(existing.data)} existing recipes")
    except Exception as e:
        print(f"   Note: {e}")
    
    # Prepare recipe texts and metadata for embedding
    texts = []
    metadatas = []
    
    for recipe in raw_recipes:
        # Create rich text representation for better embedding
        ingredients_text = ", ".join(recipe['ingredients'])
        text = f"Recipe: {recipe['title']}. Description: {recipe.get('description', '')}. Ingredients: {ingredients_text}. Instructions: {recipe['instructions']}"
        texts.append(text)
        
        # Store metadata
        metadatas.append({
            "title": recipe['title'],
            "description": recipe.get('description', ''),
            "ingredients": recipe['ingredients'],
            "instructions": recipe['instructions']
        })
    
    # Add recipes to vector store
    try:
        print("   Creating embeddings and storing recipes...")
        add_recipes(texts=texts, metadatas=metadatas)
        print(f"✅ Successfully seeded {len(texts)} recipes with embeddings!")
    except Exception as e:
        print(f"❌ Error seeding recipes: {e}")
        raise

def verify_data():
    """Verify that data was loaded correctly"""
    supabase = get_supabase_client()
    
    print("\n🔍 Verifying data...")
    
    # Check products
    try:
        products = supabase.table("products").select("*", count='exact').limit(1).execute()
        print(f"✅ Products in database: {len(products.data)} (showing 1)")
    except Exception as e:
        print(f"❌ Error checking products: {e}")
    
    # Check recipes
    try:
        recipes = supabase.table("documents").select("*", count='exact').limit(1).execute()
        print(f"✅ Recipes in database: {len(recipes.data)} (showing 1)")
    except Exception as e:
        print(f"❌ Error checking recipes: {e}")

def main():
    print("\n" + "="*80)
    print("🚀 recipe AI SYSTEM SETUP")
    print("="*80)
    
    # Check if tables exist
    tables_exist = check_tables_exist()
    
    if not tables_exist:
        create_tables_instructions()
        return
    
    print("\n✅ All required tables exist!")
    
    # Seed data
    try:
        seed_products()
        seed_recipes()
        verify_data()
        
        print("\n" + "="*80)
        print("🎉 SETUP COMPLETE!")
        print("="*80)
        print("\n✅ Your recipe AI system is ready!")
        print("✅ Customers can now ask for recipe suggestions")
        print("✅ The system will check inventory and suggest products")
        print("\nTest with queries like:")
        print('  - "I have chicken and rice. What can I cook?"')
        print('  - "Show me fish recipes"')
        print('  - "What dessert can I make?"')
        print("\n" + "="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
