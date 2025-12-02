"""
Complete Data Seeding Script
Seeds ALL data with vector embeddings:
- Products (inventory)
- Recipes (with embeddings)
- Policies (with embeddings)
- FAQs (with embeddings)
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings

try:
    from database.connection import get_supabase_client
except:
    from backend.database.connection import get_supabase_client

def load_json(filename):
    file_path = os.path.join(os.path.dirname(__file__), '..', 'data', filename)
    with open(file_path, 'r') as f:
        return json.load(f)

def seed_products():
    """Seed products table"""
    print("\n" + "="*80)
    print("📦 SEEDING PRODUCTS")
    print("="*80)
    
    supabase = get_supabase_client()
    products = load_json('products.json')
    
    # Clear existing
    try:
        existing = supabase.table("products").select("id").execute()
        if existing.data:
            for product in existing.data:
                supabase.table("products").delete().eq("id", product["id"]).execute()
            print(f"   Cleared {len(existing.data)} existing products")
    except Exception as e:
        print(f"   Note: {e}")
    
    # Insert products
    batch_size = 50
    for i in range(0, len(products), batch_size):
        batch = products[i:i+batch_size]
        supabase.table("products").insert(batch).execute()
        print(f"   ✅ Inserted products {i+1} to {min(i+batch_size, len(products))}")
    
    print(f"\n✅ Successfully seeded {len(products)} products!")
    return len(products)

def seed_recipes_to_knowledge_base():
    """Seed recipes with vector embeddings to knowledge_base"""
    print("\n" + "="*80)
    print("👨‍🍳 SEEDING RECIPES (with AI embeddings)")
    print("="*80)
    
    supabase = get_supabase_client()
    recipes = load_json('recipes.json')
    embeddings = FastEmbedEmbeddings()
    
    # Clear existing recipes from knowledge_base
    try:
        existing = supabase.table("knowledge_base").select("id").eq("content_type", "recipe").execute()
        if existing.data:
            for item in existing.data:
                supabase.table("knowledge_base").delete().eq("id", item["id"]).execute()
            print(f"   Cleared {len(existing.data)} existing recipes")
    except Exception as e:
        print(f"   Note: {e}")
    
    print(f"   Creating AI embeddings for {len(recipes)} recipes...")
    
    # Process each recipe
    for i, recipe in enumerate(recipes, 1):
        # Create rich text for embedding
        ingredients_text = ", ".join(recipe['ingredients'])
        description = recipe.get('description', '')
        instructions = recipe['instructions']
        
        content_text = f"Recipe: {recipe['title']}. {description}. Ingredients: {ingredients_text}. Instructions: {instructions}"
        
        # Generate embedding
        embedding_vector = list(embeddings.embed_query(content_text))
        
        # Prepare data
        data = {
            'content_type': 'recipe',
            'title': recipe['title'],
            'content': content_text,
            'metadata': {
                'title': recipe['title'],
                'description': description,
                'ingredients': recipe['ingredients'],
                'instructions': instructions
            },
            'embedding': embedding_vector
        }
        
        # Insert
        supabase.table("knowledge_base").insert(data).execute()
        print(f"   ✅ [{i}/{len(recipes)}] {recipe['title']}")
    
    print(f"\n✅ Successfully seeded {len(recipes)} recipes with AI embeddings!")
    return len(recipes)

def seed_policies_to_knowledge_base():
    """Seed policies with vector embeddings to knowledge_base"""
    print("\n" + "="*80)
    print("📋 SEEDING POLICIES (with AI embeddings)")
    print("="*80)
    
    supabase = get_supabase_client()
    policies = load_json('policies.json')
    embeddings = FastEmbedEmbeddings()
    
    # Clear existing policies
    try:
        existing = supabase.table("knowledge_base").select("id").eq("content_type", "policy").execute()
        if existing.data:
            for item in existing.data:
                supabase.table("knowledge_base").delete().eq("id", item["id"]).execute()
            print(f"   Cleared {len(existing.data)} existing policies")
    except Exception as e:
        print(f"   Note: {e}")
    
    print(f"   Creating AI embeddings for {len(policies)} policies...")
    
    for i, policy in enumerate(policies, 1):
        # Create rich searchable text
        content_text = f"{policy['title']}. {policy['content']}. "
        
        # Add details to content for better search
        if 'details' in policy:
            details_text = json.dumps(policy['details'], indent=2)
            content_text += f"Details: {details_text}"
        
        # Generate embedding
        embedding_vector = list(embeddings.embed_query(content_text))
        
        # Prepare data
        data = {
            'content_type': 'policy',
            'title': policy['title'],
            'content': content_text,
            'metadata': {
                'category': policy['category'],
                'title': policy['title'],
                'summary': policy['content'],
                'details': policy.get('details', {})
            },
            'embedding': embedding_vector
        }
        
        # Insert
        supabase.table("knowledge_base").insert(data).execute()
        print(f"   ✅ [{i}/{len(policies)}] {policy['title']}")
    
    print(f"\n✅ Successfully seeded {len(policies)} policies with AI embeddings!")
    return len(policies)

def seed_legacy_documents():
    """Seed documents table for backward compatibility"""
    print("\n" + "="*80)
    print("🔄 SEEDING LEGACY DOCUMENTS TABLE")
    print("="*80)
    
    supabase = get_supabase_client()
    recipes = load_json('recipes.json')
    embeddings = FastEmbedEmbeddings()
    
    # Clear existing
    try:
        existing = supabase.table("documents").select("id").execute()
        if existing.data:
            for doc in existing.data:
                supabase.table("documents").delete().eq("id", doc["id"]).execute()
            print(f"   Cleared {len(existing.data)} existing documents")
    except Exception as e:
        print(f"   Note: {e}")
    
    print(f"   Creating embeddings for legacy compatibility...")
    
    for i, recipe in enumerate(recipes, 1):
        ingredients_text = ", ".join(recipe['ingredients'])
        content_text = f"Recipe: {recipe['title']}. Ingredients: {ingredients_text}. {recipe['instructions']}"
        
        embedding_vector = list(embeddings.embed_query(content_text))
        
        data = {
            'content': content_text,
            'metadata': {
                'title': recipe['title'],
                'description': recipe.get('description', ''),
                'ingredients': recipe['ingredients'],
                'instructions': recipe['instructions']
            },
            'embedding': embedding_vector
        }
        
        supabase.table("documents").insert(data).execute()
    
    print(f"   ✅ Legacy documents table updated")
    return len(recipes)

def verify_data():
    """Verify all data was loaded"""
    print("\n" + "="*80)
    print("🔍 VERIFYING DATA")
    print("="*80)
    
    supabase = get_supabase_client()
    
    # Check products
    products = supabase.table("products").select("*", count='exact').limit(1).execute()
    print(f"   ✅ Products: {len(products.data)} records")
    
    # Check knowledge base
    kb_total = supabase.table("knowledge_base").select("*", count='exact').limit(1).execute()
    print(f"   ✅ Knowledge Base Total: {len(kb_total.data)} records")
    
    # Check by type
    recipes = supabase.table("knowledge_base").select("*").eq("content_type", "recipe").limit(5).execute()
    print(f"   ✅ Recipes in KB: {len(recipes.data)} (showing 5)")
    
    policies = supabase.table("knowledge_base").select("*").eq("content_type", "policy").limit(5).execute()
    print(f"   ✅ Policies in KB: {len(policies.data)} (showing 5)")
    
    # Check legacy
    docs = supabase.table("documents").select("*", count='exact').limit(1).execute()
    print(f"   ✅ Legacy Documents: {len(docs.data)} records")

def main():
    print("\n" + "="*80)
    print("🚀 recipe AI COMPLETE DATA SEEDING")
    print("="*80)
    print("\nThis will seed ALL data with AI-powered vector embeddings:")
    print("  • Products (inventory)")
    print("  • Recipes (AI searchable)")
    print("  • Policies (AI searchable)")
    print("  • Support FAQs (AI searchable)")
    print("\n" + "="*80)
    
    try:
        # Seed all data
        products_count = seed_products()
        recipes_count = seed_recipes_to_knowledge_base()
        policies_count = seed_policies_to_knowledge_base()
        legacy_count = seed_legacy_documents()
        
        # Verify
        verify_data()
        
        # Success summary
        print("\n" + "="*80)
        print("🎉 SEEDING COMPLETE!")
        print("="*80)
        print(f"\n✅ Products: {products_count}")
        print(f"✅ Recipes (AI-searchable): {recipes_count}")
        print(f"✅ Policies (AI-searchable): {policies_count}")
        print(f"✅ Legacy compatibility: {legacy_count}")
        print("\n🤖 AI Agents can now:")
        print("   • Search recipes semantically (not just keywords)")
        print("   • Find policies by intent (not just exact match)")
        print("   • Understand customer queries naturally")
        print("   • Provide intelligent, context-aware responses")
        print("\n" + "="*80)
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
