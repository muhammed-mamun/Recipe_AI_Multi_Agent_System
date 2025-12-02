#!/usr/bin/env python3
"""
Seed data to match the user's Supabase schema
Tables: products, recipes, policies (with embeddings)
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

def seed_recipes():
    """Seed recipes table with embeddings"""
    print("\n" + "="*80)
    print("👨‍🍳 SEEDING RECIPES (with AI embeddings)")
    print("="*80)
    
    supabase = get_supabase_client()
    recipes_data = load_json('recipes.json')
    embeddings = FastEmbedEmbeddings()
    
    # Clear existing
    try:
        existing = supabase.table("recipes").select("id").execute()
        if existing.data:
            for recipe in existing.data:
                supabase.table("recipes").delete().eq("id", recipe["id"]).execute()
            print(f"   Cleared {len(existing.data)} existing recipes")
    except Exception as e:
        print(f"   Note: {e}")
    
    print(f"   Creating AI embeddings for {len(recipes_data)} recipes...")
    
    for i, recipe in enumerate(recipes_data, 1):
        # Create rich text for embedding
        ingredients_text = ", ".join(recipe['ingredients'])
        description = recipe.get('description', '')
        instructions = recipe['instructions']
        
        content_text = f"Recipe: {recipe['title']}. {description}. Ingredients: {ingredients_text}. Instructions: {instructions}"
        
        # Generate embedding
        embedding_vector = list(embeddings.embed_query(content_text))
        
        # Prepare data matching the schema
        data = {
            'name': recipe['title'],
            'description': description,
            'ingredients': recipe['ingredients'],  # JSONB
            'instructions': [instructions],  # TEXT[]
            'prep_time': recipe.get('prep_time'),
            'cooking_time': recipe.get('cooking_time'),
            'serving_size': recipe.get('serving_size'),
            'image_url': recipe.get('image_url'),
            'embedding': embedding_vector
        }
        
        # Insert
        supabase.table("recipes").insert(data).execute()
        print(f"   ✅ [{i}/{len(recipes_data)}] {recipe['title']}")
    
    print(f"\n✅ Successfully seeded {len(recipes_data)} recipes with AI embeddings!")
    return len(recipes_data)

def seed_policies():
    """Seed policies table with embeddings"""
    print("\n" + "="*80)
    print("📋 SEEDING POLICIES (with AI embeddings)")
    print("="*80)
    
    supabase = get_supabase_client()
    policies_data = load_json('policies.json')
    embeddings = FastEmbedEmbeddings()
    
    # Clear existing
    try:
        existing = supabase.table("policies").select("id").execute()
        if existing.data:
            for policy in existing.data:
                supabase.table("policies").delete().eq("id", policy["id"]).execute()
            print(f"   Cleared {len(existing.data)} existing policies")
    except Exception as e:
        print(f"   Note: {e}")
    
    print(f"   Creating AI embeddings for {len(policies_data)} policies...")
    
    for i, policy in enumerate(policies_data, 1):
        # Create rich searchable text
        content_text = f"{policy['title']}. {policy['content']}. "
        
        # Add details to content for better search
        if 'details' in policy:
            details_text = json.dumps(policy['details'], indent=2)
            content_text += f"Details: {details_text}"
        
        # Generate embedding
        embedding_vector = list(embeddings.embed_query(content_text))
        
        # Prepare data matching the schema
        data = {
            'title': policy['title'],
            'content': content_text,
            'category': policy.get('category'),
            'embedding': embedding_vector
        }
        
        # Insert
        supabase.table("policies").insert(data).execute()
        print(f"   ✅ [{i}/{len(policies_data)}] {policy['title']}")
    
    print(f"\n✅ Successfully seeded {len(policies_data)} policies with AI embeddings!")
    return len(policies_data)

def verify_data():
    """Verify all data was loaded"""
    print("\n" + "="*80)
    print("🔍 VERIFYING DATA")
    print("="*80)
    
    supabase = get_supabase_client()
    
    # Check products
    products = supabase.table("products").select("*").limit(5).execute()
    print(f"   ✅ Products: {len(products.data)} records (showing 5)")
    if products.data:
        print(f"      Example: {products.data[0]['name']} - ৳{products.data[0]['price']}")
    
    # Check recipes
    recipes = supabase.table("recipes").select("*").limit(5).execute()
    print(f"   ✅ Recipes: {len(recipes.data)} records (showing 5)")
    if recipes.data:
        print(f"      Example: {recipes.data[0]['name']}")
    
    # Check policies
    policies = supabase.table("policies").select("*").limit(5).execute()
    print(f"   ✅ Policies: {len(policies.data)} records (showing 5)")
    if policies.data:
        print(f"      Example: {policies.data[0]['title']}")

def main():
    print("\n" + "="*80)
    print("🚀 recipe AI DATA SEEDING")
    print("="*80)
    print("\nThis will seed data with AI-powered vector embeddings:")
    print("  • Recipes (AI searchable)")
    print("  • Policies (AI searchable)")
    print("  • Products (already loaded)")
    print("\n" + "="*80)
    
    try:
        # Seed data
        recipes_count = seed_recipes()
        policies_count = seed_policies()
        
        # Verify
        verify_data()
        
        # Success summary
        print("\n" + "="*80)
        print("🎉 SEEDING COMPLETE!")
        print("="*80)
        print(f"\n✅ Recipes (AI-searchable): {recipes_count}")
        print(f"✅ Policies (AI-searchable): {policies_count}")
        print("\n🤖 AI Agents can now:")
        print("   • Search recipes semantically")
        print("   • Find policies by intent")
        print("   • Provide intelligent responses")
        print("\n" + "="*80)
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
