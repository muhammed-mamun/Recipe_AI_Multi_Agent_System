import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Add project root to path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from database.operations import DatabaseOperations
from database.models import ProductCreate, RecipeCreate, PolicyCreate, Ingredient
from database.connection import get_supabase_client

# Load environment variables
load_dotenv(os.path.join(project_root, '.env'))

# Sample data
SAMPLE_PRODUCTS = [
    {"name": "Basmati Rice", "description": "Premium quality basmati rice, perfect for biryani and pilaf", "price": 120.0, "category": "Grains", "stock_quantity": 100},
    {"name": "Eggs (Dozen)", "description": "Farm fresh eggs, 12 pieces", "price": 150.0, "category": "Dairy & Eggs", "stock_quantity": 200},
    {"name": "Chicken Breast", "description": "Boneless chicken breast, 1kg pack", "price": 300.0, "category": "Meat & Poultry", "stock_quantity": 50},
    {"name": "Onion", "description": "Fresh red onions, 1kg", "price": 40.0, "category": "Vegetables", "stock_quantity": 300},
    {"name": "Tomato", "description": "Fresh tomatoes, 1kg", "price": 30.0, "category": "Vegetables", "stock_quantity": 250},
    {"name": "Garlic", "description": "Fresh garlic, 100g", "price": 20.0, "category": "Vegetables", "stock_quantity": 150},
    {"name": "Ginger", "description": "Fresh ginger, 100g", "price": 25.0, "category": "Vegetables", "stock_quantity": 120},
    {"name": "Vegetable Oil", "description": "Pure vegetable oil, 1L", "price": 180.0, "category": "Cooking Oil", "stock_quantity": 80},
    {"name": "Salt", "description": "Iodized salt, 1kg", "price": 25.0, "category": "Spices & Seasonings", "stock_quantity": 200},
    {"name": "Turmeric Powder", "description": "Pure turmeric powder, 100g", "price": 40.0, "category": "Spices & Seasonings", "stock_quantity": 150},
]

SAMPLE_RECIPES = [
    {
        "name": "Chicken Biryani",
        "description": "Aromatic basmati rice cooked with tender chicken pieces and a blend of spices",
        "ingredients": [
            {"product_id": "basmati_rice_id", "quantity": 2, "unit": "cups"},
            {"product_id": "chicken_breast_id", "quantity": 500, "unit": "g"},
            {"product_id": "onion_id", "quantity": 2, "unit": "medium"},
            {"product_id": "tomato_id", "quantity": 3, "unit": "medium"},
            {"product_id": "garlic_id", "quantity": 4, "unit": "cloves"},
            {"product_id": "ginger_id", "quantity": 1, "unit": "inch"},
            {"product_id": "vegetable_oil_id", "quantity": 3, "unit": "tbsp"},
            {"product_id": "salt_id", "quantity": 1, "unit": "tsp"},
            {"product_id": "turmeric_powder_id", "quantity": 0.5, "unit": "tsp"},
        ],
        "instructions": [
            "Marinate chicken with yogurt, half of the spices, and salt for 1 hour.",
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
            {"product_id": "basmati_rice_id", "quantity": 2, "unit": "cups", "cooked": True},
            {"product_id": "eggs_id", "quantity": 3, "unit": "large"},
            {"product_id": "onion_id", "quantity": 1, "unit": "medium"},
            {"product_id": "vegetable_oil_id", "quantity": 2, "unit": "tbsp"},
            {"product_id": "salt_id", "quantity": 0.5, "unit": "tsp"},
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

async def run_migration():
    print("Starting database migration...")
    
    # Get database connection parameters from environment
    db_url = os.getenv("SUPABASE_DB_URL")
    if not db_url:
        raise ValueError("SUPABASE_DB_URL environment variable not set")
    
    # Parse the database URL
    from urllib.parse import urlparse
    result = urlparse(db_url)
    username = result.username
    password = result.password
    host = result.hostname
    port = result.port or 5432
    database = result.path[1:]  # Remove leading '/'
    
    # Connect to PostgreSQL
    conn = psycopg2.connect(
        dbname="postgres",  # Connect to default database first
        user=username,
        password=password,
        host=host,
        port=port
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    try:
        # Check if database exists, create if not
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database,))
        if not cursor.fetchone():
            print(f"Creating database {database}...")
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database)))
        
        # Close initial connection and connect to the new database
        cursor.close()
        conn.close()
        
        conn = psycopg2.connect(
            dbname=database,
            user=username,
            password=password,
            host=host,
            port=port
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Run the migration SQL
        migration_path = os.path.join(project_root, "database", "migrations", "20241122_add_products_recipes_tables.sql")
        with open(migration_path, 'r') as f:
            sql_script = f.read()
        
        print("Running migration script...")
        cursor.execute(sql_script)
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        raise
    finally:
        cursor.close()
        conn.close()
    
    return True

async def seed_initial_data():
    print("\nSeeding initial data...")
    db = DatabaseOperations()
    
    try:
        # Add products
        print("Adding products...")
        product_ids = {}
        for product_data in SAMPLE_PRODUCTS:
            # Create a ProductCreate object
            product = ProductCreate(**product_data)
            created_product = await db.create_product(product)
            
            # Store ID for reference in recipes
            product_key = f"{product.name.lower().replace(' ', '_').replace('(', '').replace(')', '')}_id"
            product_ids[product_key] = str(created_product.id)
            print(f"Added product: {created_product.name} (ID: {created_product.id})")
        
        # Add recipes (replace product IDs with actual IDs)
        print("\nAdding recipes...")
        for recipe_data in SAMPLE_RECIPES:
            # Replace product IDs in ingredients
            for ingredient in recipe_data["ingredients"]:
                product_key = ingredient["product_id"]
                if product_key in product_ids:
                    ingredient["product_id"] = product_ids[product_key]
            
            # Create a RecipeCreate object
            recipe = RecipeCreate(**recipe_data)
            created_recipe = await db.create_recipe(recipe)
            print(f"Added recipe: {created_recipe.name} (ID: {created_recipe.id})")
        
        # Add policies
        print("\nAdding policies...")
        for policy_data in SAMPLE_POLICIES:
            policy = PolicyCreate(**policy_data)
            created_policy = await db.create_policy(policy)
            print(f"Added policy: {created_policy.title} (ID: {created_policy.id})")
        
        print("\nData seeding completed successfully!")
        
    except Exception as e:
        print(f"Error during data seeding: {e}")
        raise

async def main():
    try:
        # Run migration
        await run_migration()
        
        # Seed initial data
        await seed_initial_data()
        
        print("\nDatabase setup completed successfully!")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
