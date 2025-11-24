"""
Script to set up the database tables in Supabase.
Run this before seeding data.
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import get_supabase_client

def setup_tables():
    """Execute the schema.sql file to create tables"""
    supabase = get_supabase_client()
    
    # Read schema file
    schema_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'schema.sql')
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    
    print("Creating tables in Supabase...")
    print("Note: You need to run this SQL manually in the Supabase SQL Editor:")
    print("\n" + "="*80)
    print(schema_sql)
    print("="*80 + "\n")
    
    print("\n1. Go to your Supabase project: https://pozqlghiwukecwtuhbjh.supabase.co")
    print("2. Navigate to SQL Editor")
    print("3. Copy and paste the SQL above")
    print("4. Click 'Run' to execute")
    print("\nAfter that, run: python backend/scripts/seed_data.py")

if __name__ == "__main__":
    setup_tables()
