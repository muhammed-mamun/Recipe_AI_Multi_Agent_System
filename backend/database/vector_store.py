from langchain_community.vectorstores import SupabaseVectorStore
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
import os
import sys

# Handle imports for both direct execution and module import
try:
    from backend.database.connection import get_supabase_client
except ModuleNotFoundError:
    from database.connection import get_supabase_client

def get_vector_store():
    supabase = get_supabase_client()
    # FastEmbedEmbeddings runs locally and is free.
    # Default model: BAAI/bge-small-en-v1.5 (384 dimensions)
    # NOTE: You must update your Supabase table to support 384 dimensions or use a model with 1536 dimensions.
    # OpenAI uses 1536. BAAI uses 384.
    # Let's use a model that is compatible or update the schema.
    # For simplicity, let's stick to standard FastEmbed which is 384.
    # WE MUST UPDATE SCHEMA.SQL TO 384 DIMENSIONS.
    embeddings = FastEmbedEmbeddings()
    
    vector_store = SupabaseVectorStore(
        client=supabase,
        embedding=embeddings,
        table_name="documents",
        query_name="match_documents",
    )
    return vector_store

def add_recipes(texts: list[str], metadatas: list[dict]):
    vector_store = get_vector_store()
    vector_store.add_texts(texts=texts, metadatas=metadatas)

def search_recipes(query: str, k: int = 5) -> str:
    """
    Search for recipes using direct Supabase query
    
    Args:
        query: Search term for recipes
        k: Number of recipes to return
        
    Returns:
        Formatted string with recipe details
    """
    try:
        # Fallback to direct Supabase query
        print("Searching recipes...")
        supabase = get_supabase_client()
        embeddings = FastEmbedEmbeddings()
        
        # Generate embedding for query
        query_embedding = list(embeddings.embed_query(query))
        
        # Call the match function directly
        result = supabase.rpc(
            'match_documents',
            {
                'query_embedding': query_embedding,
                'match_threshold': 0.0,
                'match_count': k
            }
        ).execute()
        
        if not result.data:
            return "No recipes found matching your query."
        
        # Format as string
        output = f"Found {len(result.data)} recipe(s):\n\n"
        
        for i, row in enumerate(result.data, 1):
            metadata = row['metadata']
            output += f"{'='*60}\n"
            output += f"Recipe {i}: {metadata.get('title', 'Unknown')}\n"
            output += f"{'='*60}\n"
            
            if 'description' in metadata:
                output += f"Description: {metadata['description']}\n\n"
            
            if 'ingredients' in metadata:
                output += "Ingredients:\n"
                for ing in metadata['ingredients']:
                    output += f"  - {ing}\n"
                output += "\n"
            
            if 'instructions' in metadata:
                output += f"Instructions:\n{metadata['instructions']}\n\n"
        
        return output
        
    except Exception as e:
        print(f"Error searching recipes: {e}")
        return f"Error searching recipes: {str(e)}"
