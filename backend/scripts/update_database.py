import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from typing import List, Dict, Any, Optional
import json

# Add project root to path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

# Load environment variables
load_dotenv(os.path.join(project_root, '.env'))

# Sample data for recipes (we'll use existing products)
SAMPLE_RECIPES = [
    {
        "name": "Chicken Biryani",
        "description": "Aromatic basmati rice cooked with tender chicken pieces and a blend of spices",
        "ingredients": [
            {"name": "Basmati Rice", "quantity": 2, "unit": "cups"},
            {"name": "Chicken Breast", "quantity": 500, "unit": "g"},
            {"name": "Onion", "quantity": 2, "unit": "medium"},
            {"name": "Tomato", "quantity": 3, "unit": "medium"},
            {"name": "Vegetable Oil", "quantity": 3, "unit": "tbsp"},
            {"name": "Salt", "quantity": 1, "unit": "tsp"},
        ],
        "instructions": [
            "Marinate chicken with yogurt and spices for 1 hour.",
            "Soak basmati rice for 30 minutes.",
            "Fry onions until golden brown and set aside.",
            "Cook chicken with tomatoes and spices until tender.",
            "Parboil rice and layer it with the chicken.",
            "Cook on low heat for 20-25 minutes.",
            "Garnish with fried onions and serve hot."
        ],
        "prep_time": 45,
        "cooking_time": 40,
        "serving_size": 4,
        "image_url": "https://example.com/chicken-biryani.jpg"
    },
    {
        "name": "Egg Fried Rice",
        "description": "Quick and delicious egg fried rice with vegetables",
        "ingredients": [
            {"name": "Basmati Rice", "quantity": 2, "unit": "cups", "cooked": True},
            {"name": "Eggs (Dozen)", "quantity": 3, "unit": "large"},
            {"name": "Onion", "quantity": 1, "unit": "medium"},
            {"name": "Vegetable Oil", "quantity": 2, "unit": "tbsp"},
            {"name": "Salt", "quantity": 0.5, "unit": "tsp"},
        ],
        "instructions": [
            "Heat oil in a pan and scramble the eggs. Set aside.",
            "In the same pan, sauté onions until translucent.",
            "Add cooked rice and stir well.",
            "Add the scrambled eggs back to the pan.",
            "Season with salt and stir-fry for 5 minutes.",
            "Serve hot with soy sauce or ketchup."
        ],
        "prep_time": 10,
        "cooking_time": 15,
        "serving_size": 2,
        "image_url": "https://example.com/egg-fried-rice.jpg"
    }
]

SAMPLE_POLICIES = [
    {
        "title": "Return Policy",
        "content": "We accept returns within 7 days of delivery for damaged or incorrect items. Please contact our customer support with your order number and details of the issue.",
        "category": "returns"
    },
    {
        "title": "Delivery Information",
        "content": "Standard delivery takes 2-3 business days. Express delivery is available for an additional charge. We deliver to all major cities in Bangladesh.",
        "category": "delivery"
    },
    {
        "title": "Quality Guarantee",
        "content": "We guarantee the quality of all our products. If you're not satisfied with the quality, please contact us within 24 hours of delivery for a replacement or refund.",
        "category": "quality"
    }
]

class DatabaseUpdater:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.product_name_to_id = {}
    
    def connect(self):
        """Connect to the PostgreSQL database."""
        db_url = os.getenv("SUPABASE_DB_URL")
        if not db_url:
            raise ValueError("SUPABASE_DB_URL environment variable not set")
        
        self.conn = psycopg2.connect(db_url)
        self.conn.autocommit = True
        self.cursor = self.conn.cursor()
        print("Connected to the database")
    
    def close(self):
        """Close the database connection."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("Database connection closed")
    
    def check_tables(self):
        """Check if required tables exist and update them if needed."""
        print("Checking database tables...")
        
        # Check products table
        self.cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'products'
        """)
        existing_columns = {row[0] for row in self.cursor.fetchall()}
        
        # Add missing columns to products table
        if 'description' not in existing_columns:
            print("Adding description column to products table...")
            self.cursor.execute("""
                ALTER TABLE products 
                ADD COLUMN IF NOT EXISTS description TEXT
            """)
        
        if 'image_url' not in existing_columns:
            print("Adding image_url column to products table...")
            self.cursor.execute("""
                ALTER TABLE products 
                ADD COLUMN IF NOT EXISTS image_url TEXT
            """)
        
        if 'embedding' not in existing_columns:
            print("Adding embedding column to products table...")
            self.cursor.execute("""
                ALTER TABLE products 
                ADD COLUMN IF NOT EXISTS embedding vector(384)
            """)
        
        if 'updated_at' not in existing_columns:
            print("Adding updated_at column to products table...")
            self.cursor.execute("""
                ALTER TABLE products 
                ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW()
            """)
        
        # Create recipes table if it doesn't exist
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS recipes (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name TEXT NOT NULL,
                description TEXT,
                ingredients JSONB NOT NULL,
                instructions TEXT[] NOT NULL,
                prep_time INTEGER,
                cooking_time INTEGER,
                serving_size INTEGER,
                image_url TEXT,
                embedding VECTOR(384),
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)
        
        # Create policies table if it doesn't exist
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS policies (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT,
                embedding VECTOR(384),
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)
        
        # Create indexes for better performance
        print("Creating indexes...")
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_products_embedding 
            ON products USING ivfflat (embedding vector_cosine_ops)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_recipes_embedding 
            ON recipes USING ivfflat (embedding vector_cosine_ops)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_policies_embedding 
            ON policies USING ivfflat (embedding vector_cosine_ops)
        """)
        
        print("Database tables are up to date")
    
    def get_product_id_by_name(self, name: str) -> Optional[str]:
        """Get product ID by name."""
        if not self.product_name_to_id:
            self.cursor.execute("SELECT id, name FROM products")
            self.product_name_to_id = {name.lower(): id for id, name in self.cursor.fetchall()}
        
        return self.product_name_to_id.get(name.lower())
    
    def seed_sample_data(self):
        """Seed the database with sample recipes and policies."""
        print("\nSeeding sample recipes...")
        
        # Seed recipes
        for recipe_data in SAMPLE_RECIPES:
            # Check if recipe already exists
            self.cursor.execute(
                "SELECT id FROM recipes WHERE name = %s",
                (recipe_data["name"],)
            )
            if self.cursor.fetchone():
                print(f"Recipe '{recipe_data['name']}' already exists, skipping...")
                continue
            
            # Process ingredients to include product IDs
            ingredients = []
            for ing in recipe_data["ingredients"]:
                product_id = self.get_product_id_by_name(ing["name"])
                if not product_id:
                    print(f"Warning: Product '{ing['name']}' not found, skipping...")
                    continue
                
                ingredients.append({
                    "product_id": product_id,
                    "name": ing["name"],
                    "quantity": ing["quantity"],
                    "unit": ing["unit"],
                    "cooked": ing.get("cooked", False)
                })
            
            if not ingredients:
                print(f"Warning: No valid ingredients found for recipe '{recipe_data['name']}', skipping...")
                continue
            
            # Insert recipe
            self.cursor.execute("""
                INSERT INTO recipes (
                    name, description, ingredients, instructions, 
                    prep_time, cooking_time, serving_size, image_url
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                recipe_data["name"],
                recipe_data["description"],
                json.dumps(ingredients),
                recipe_data["instructions"],
                recipe_data["prep_time"],
                recipe_data["cooking_time"],
                recipe_data["serving_size"],
                recipe_data["image_url"]
            ))
            
            recipe_id = self.cursor.fetchone()[0]
            print(f"Added recipe: {recipe_data['name']} (ID: {recipe_id})")
        
        # Seed policies
        print("\nSeeding policies...")
        for policy_data in SAMPLE_POLICIES:
            # Check if policy already exists
            self.cursor.execute(
                "SELECT id FROM policies WHERE title = %s",
                (policy_data["title"],)
            )
            if self.cursor.fetchone():
                print(f"Policy '{policy_data['title']}' already exists, skipping...")
                continue
            
            # Insert policy
            self.cursor.execute("""
                INSERT INTO policies (title, content, category)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (
                policy_data["title"],
                policy_data["content"],
                policy_data["category"]
            ))
            
            policy_id = self.cursor.fetchone()[0]
            print(f"Added policy: {policy_data['title']} (ID: {policy_id})")
        
        print("\nSample data seeding completed!")

def main():
    updater = DatabaseUpdater()
    
    try:
        # Connect to the database
        updater.connect()
        
        # Check and update tables
        updater.check_tables()
        
        # Seed sample data
        updater.seed_sample_data()
        
        print("\nDatabase update completed successfully!")
        
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        sys.exit(1)
    finally:
        # Close the database connection
        updater.close()

if __name__ == "__main__":
    main()
