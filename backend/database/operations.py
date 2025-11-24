import uuid
from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime
import json
import numpy as np
from supabase import Client
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from .connection import get_supabase_client
from .models import (
    Product, ProductCreate, Recipe, RecipeCreate, Policy, PolicyCreate,
    ProductSearchResult, RecipeSearchResult, PolicySearchResult,
    RecipeSuggestionRequest, RecipeSuggestionResponse, Ingredient
)

# Initialize embeddings
embeddings = FastEmbedEmbeddings()

class DatabaseOperations:
    def __init__(self, supabase: Optional[Client] = None):
        self.supabase = supabase or get_supabase_client()

    # Product Operations
    async def create_product(self, product: ProductCreate) -> Product:
        """Create a new product and generate its embedding."""
        # Generate embedding from product name and description
        text = f"{product.name} {product.description or ''}"
        embedding = await self._get_embedding(text)
        
        # Prepare product data
        product_data = product.dict()
        product_data['embedding'] = embedding
        
        # Insert into database
        result = self.supabase.table('products').insert(product_data).execute()
        return Product(**result.data[0])

    async def get_product(self, product_id: str) -> Optional[Product]:
        """Get a product by ID."""
        result = self.supabase.table('products').select('*').eq('id', product_id).execute()
        return Product(**result.data[0]) if result.data else None

    async def search_products(
        self, 
        query: str, 
        limit: int = 5, 
        match_threshold: float = 0.5
    ) -> List[ProductSearchResult]:
        """Search for products using semantic search."""
        # Get query embedding
        query_embedding = await self._get_embedding(query)
        
        # Call the match_products function in Supabase
        result = self.supabase.rpc(
            'match_products',
            {
                'query_embedding': query_embedding,
                'match_threshold': match_threshold,
                'match_count': limit
            }
        ).execute()
        
        return [ProductSearchResult(**item) for item in result.data]

    # Recipe Operations
    async def create_recipe(self, recipe: RecipeCreate) -> Recipe:
        """Create a new recipe and generate its embedding."""
        # Generate embedding from recipe name, description, and ingredients
        ingredients_text = ', '.join([
            f"{ing['quantity']} {ing['unit']} {ing.get('name', '')}" 
            for ing in recipe.ingredients
        ])
        text = f"{recipe.name} {recipe.description or ''} {ingredients_text}"
        embedding = await self._get_embedding(text)
        
        # Prepare recipe data
        recipe_data = recipe.dict()
        recipe_data['embedding'] = embedding
        
        # Insert into database
        result = self.supabase.table('recipes').insert(recipe_data).execute()
        return Recipe(**result.data[0])

    async def get_recipe(self, recipe_id: str) -> Optional[Recipe]:
        """Get a recipe by ID."""
        result = self.supabase.table('recipes').select('*').eq('id', recipe_id).execute()
        return Recipe(**result.data[0]) if result.data else None

    async def suggest_recipes(
        self, 
        request: RecipeSuggestionRequest
    ) -> List[RecipeSuggestionResponse]:
        """
        Suggest recipes based on available products and optional query.
        
        Args:
            request: RecipeSuggestionRequest containing available product IDs and optional query
            
        Returns:
            List of RecipeSuggestionResponse with recipes and matching/missing ingredients
        """
        if request.query:
            # If there's a text query, use semantic search
            query_embedding = await self._get_embedding(request.query)
            
            # Call the match_recipes function in Supabase with available products
            result = self.supabase.rpc(
                'match_recipes',
                {
                    'query_embedding': query_embedding,
                    'match_threshold': request.match_threshold,
                    'match_count': request.limit,
                    'available_products': [str(id) for id in request.available_product_ids]
                }
            ).execute()
        else:
            # If no query, just get recipes with the most matching ingredients
            result = self.supabase.rpc(
                'match_recipes',
                {
                    'query_embedding': [0.0] * 384,  # Dummy embedding
                    'match_threshold': 0.0,  # Match all
                    'match_count': request.limit,
                    'available_products': [str(id) for id in request.available_product_ids]
                }
            ).execute()
        
        # Process results and calculate missing ingredients cost
        suggestions = []
        for item in result.data:
            recipe = Recipe(**{k: v for k, v in item.items() if k in Recipe.__fields__})
            
            # Calculate total cost of missing ingredients
            missing_ingredients = item.get('missing_ingredients', [])
            missing_cost = 0.0
            
            for ing in missing_ingredients:
                # Get product price if available
                product_id = ing.get('product_id')
                if product_id:
                    product = await self.get_product(product_id)
                    if product and product.price:
                        missing_cost += product.price * float(ing.get('quantity', 1))
            
            # Create response
            suggestions.append(RecipeSuggestionResponse(
                recipe=recipe,
                matching_ingredients=item.get('matching_ingredients', []),
                missing_ingredients=missing_ingredients,
                missing_ingredients_cost=missing_cost,
                similarity=item.get('similarity', 0.0)
            ))
        
        return suggestions

    # Policy Operations
    async def create_policy(self, policy: PolicyCreate) -> Policy:
        """Create a new policy and generate its embedding."""
        # Generate embedding from policy title and content
        text = f"{policy.title} {policy.content}"
        embedding = await self._get_embedding(text)
        
        # Prepare policy data
        policy_data = policy.dict()
        policy_data['embedding'] = embedding
        
        # Insert into database
        result = self.supabase.table('policies').insert(policy_data).execute()
        return Policy(**result.data[0])

    async def search_policies(
        self, 
        query: str, 
        limit: int = 5, 
        match_threshold: float = 0.5
    ) -> List[PolicySearchResult]:
        """Search for policies using semantic search."""
        # Get query embedding
        query_embedding = await self._get_embedding(query)
        
        # Call the match_documents function in Supabase
        result = self.supabase.rpc(
            'match_documents',
            {
                'query_embedding': query_embedding,
                'match_threshold': match_threshold,
                'match_count': limit
            }
        ).execute()
        
        # Convert to PolicySearchResult objects
        policies = []
        for item in result.data:
            policy_data = item.get('metadata', {})
            policy_data['id'] = item['id']
            policy_data['content'] = item['content']
            policy_data['similarity'] = item.get('similarity', 0.0)
            policies.append(PolicySearchResult(**policy_data))
        
        return policies

    # Helper Methods
    async def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for the given text."""
        # Generate embedding using FastEmbed (synchronous for now)
        embedding = embeddings.embed_query(text)
        return list(map(float, embedding))  # Convert numpy types to native Python types

    async def batch_upsert_products(self, products: List[Dict[str, Any]]) -> int:
        """Batch upsert products with their embeddings."""
        # Generate embeddings for all products
        texts = [
            f"{p.get('name', '')} {p.get('description', '')}" 
            for p in products
        ]
        embeddings_list = await embeddings.aembed_documents(texts)
        
        # Add embeddings to product data
        for i, product in enumerate(products):
            product['embedding'] = list(map(float, embeddings_list[i]))
        
        # Upsert in batches
        batch_size = 100
        total_upserted = 0
        
        for i in range(0, len(products), batch_size):
            batch = products[i:i + batch_size]
            result = self.supabase.table('products').upsert(batch).execute()
            total_upserted += len(result.data)
        
        return total_upserted

    async def get_products_by_ids(self, product_ids: List[str]) -> List[Product]:
        """Get multiple products by their IDs."""
        if not product_ids:
            return []
            
        result = self.supabase.table('products')\
            .select('*')\
            .in_('id', product_ids)\
            .execute()
            
        return [Product(**item) for item in result.data]
