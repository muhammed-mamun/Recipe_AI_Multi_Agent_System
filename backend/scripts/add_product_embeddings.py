#!/usr/bin/env python3
"""
Add embeddings to products for semantic search
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_community.embeddings.fastembed import FastEmbedEmbeddings

try:
    from database.connection import get_supabase_client
except:
    from backend.database.connection import get_supabase_client

def add_product_embeddings():
    """Add embeddings to all products"""
    print("\n" + "="*80)
    print("🔄 ADDING EMBEDDINGS TO PRODUCTS")
    print("="*80)
    
    supabase = get_supabase_client()
    embeddings = FastEmbedEmbeddings()
    
    # Get all products
    response = supabase.table("products").select("*").execute()
    products = response.data
    
    print(f"\nFound {len(products)} products")
    print("Generating embeddings...")
    
    updated_count = 0
    
    for i, product in enumerate(products, 1):
        # Create searchable text from product name and category
        # This allows semantic search like "chicken meat" to find "Chicken (Broiler)"
        search_text = f"{product['name']} {product.get('category', '')} {product.get('description', '')}"
        
        # Generate embedding
        embedding_vector = list(embeddings.embed_query(search_text))
        
        # Update product with embedding
        supabase.table("products").update({
            "embedding": embedding_vector
        }).eq("id", product["id"]).execute()
        
        print(f"   ✅ [{i}/{len(products)}] {product['name']}")
        updated_count += 1
    
    print(f"\n✅ Successfully added embeddings to {updated_count} products!")
    return updated_count

def verify_embeddings():
    """Verify embeddings were added"""
    print("\n" + "="*80)
    print("🔍 VERIFYING EMBEDDINGS")
    print("="*80)
    
    supabase = get_supabase_client()
    
    # Check products with embeddings
    products = supabase.table("products").select("id, name, embedding").limit(5).execute()
    
    products_with_embeddings = [p for p in products.data if p.get('embedding')]
    
    print(f"\n   ✅ Products with embeddings: {len(products_with_embeddings)}/5 (sample)")
    
    if products_with_embeddings:
        print(f"   Example: {products_with_embeddings[0]['name']}")
        print(f"   Embedding dimension: {len(products_with_embeddings[0]['embedding'])}")

def main():
    print("\n" + "="*80)
    print("🚀 PRODUCT EMBEDDINGS GENERATOR")
    print("="*80)
    print("\nThis will add AI-powered vector embeddings to all products")
    print("for semantic search capabilities.")
    print("\n" + "="*80)
    
    try:
        count = add_product_embeddings()
        verify_embeddings()
        
        print("\n" + "="*80)
        print("🎉 COMPLETE!")
        print("="*80)
        print(f"\n✅ Added embeddings to {count} products")
        print("\n🤖 Product search now supports:")
        print("   • Semantic search (e.g., 'chicken meat' finds all chicken types)")
        print("   • Category-aware search")
        print("   • Natural language queries")
        print("\n" + "="*80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
