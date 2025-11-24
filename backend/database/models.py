from datetime import datetime
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field, UUID4
from enum import Enum
from typing import List, Optional

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category: Optional[str] = None
    image_url: Optional[str] = None
    stock_quantity: int = 0

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Ingredient(BaseModel):
    product_id: UUID4
    quantity: float
    unit: str  # e.g., "g", "ml", "pieces"
    notes: Optional[str] = None

class RecipeBase(BaseModel):
    name: str
    description: Optional[str] = None
    ingredients: List[Dict[str, Any]]  # List of Ingredient dicts
    instructions: List[str]
    prep_time: Optional[int] = None  # in minutes
    cooking_time: Optional[int] = None  # in minutes
    serving_size: Optional[int] = None
    image_url: Optional[str] = None

class RecipeCreate(RecipeBase):
    pass

class Recipe(RecipeBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PolicyBase(BaseModel):
    title: str
    content: str
    category: Optional[str] = None

class PolicyCreate(PolicyBase):
    pass

class Policy(PolicyBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Response models for search results
class ProductSearchResult(Product):
    similarity: float

class RecipeSearchResult(Recipe):
    similarity: float
    matching_ingredients: int
    missing_ingredients: List[Dict[str, Any]]

class PolicySearchResult(Policy):
    similarity: float

# For recipe suggestions
class RecipeSuggestionRequest(BaseModel):
    available_product_ids: List[UUID4] = Field(default_factory=list)
    query: Optional[str] = None
    limit: int = 5
    match_threshold: float = 0.5

class RecipeSuggestionResponse(BaseModel):
    recipe: Recipe
    matching_ingredients: List[Dict[str, Any]]
    missing_ingredients: List[Dict[str, Any]]
    missing_ingredients_cost: float
    similarity: float
