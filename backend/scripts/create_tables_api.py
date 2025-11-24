"""
Create tables using Supabase REST API
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from dotenv import load_dotenv

# Load environment variables
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(backend_dir, '.env'))

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

def execute_sql(sql):
    """Execute SQL via Supabase SQL API"""
    url = f"{SUPABASE_URL}/rest/v1/rpc/query"
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }
    
    data = {'query': sql}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code in [200, 201, 204]:
            print(f"✅ Success")
            return True
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    print("Creating tables via direct SQL execution...")
    
    # Create products table
    print("\n1. Creating products table...")
    products_sql = """
    CREATE TABLE IF NOT EXISTS products (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        name TEXT NOT NULL,
        price NUMERIC NOT NULL,
        stock_quantity INT NOT NULL DEFAULT 0,
        category TEXT,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    """
    
    # Since Supabase doesn't allow direct SQL via REST API without setting up a custom function,
    # let's use a different approach - insert dummy data to trigger table creation
    
    print("\n⚠️  Note: Supabase tables must be created via SQL Editor")
    print("\nAutomated table creation via API requires additional setup.")
    print("Please use the SQL Editor method as described in the setup script.")

if __name__ == "__main__":
    main()
