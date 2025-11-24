"""
Create tables directly using psycopg2 connection string from Supabase
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
except ImportError:
    print("❌ psycopg2 not installed. Installing...")
    os.system("pip install psycopg2-binary")
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from dotenv import load_dotenv

# Load environment
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(backend_dir, '.env'))

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# Extract connection details from URL
# Format: https://pozqlghiwukecwtuhbjh.supabase.co
project_ref = SUPABASE_URL.replace('https://', '').replace('.supabase.co', '')

# Construct PostgreSQL connection string
# Supabase uses standard PostgreSQL on port 5432
conn_string = f"postgresql://postgres:[YOUR-DB-PASSWORD]@db.{project_ref}.supabase.co:5432/postgres"

print("="*80)
print("🔧 DIRECT DATABASE TABLE CREATION")
print("="*80)
print("\nNote: This method requires your database password.")
print("You can find it in Supabase Dashboard > Settings > Database > Connection String")
print("\nAlternatively, use the SQL Editor method (easier):")
print("1. Go to: https://supabase.com/dashboard/project/pozqlghiwukecwtuhbjh/sql")
print("2. Copy SQL from: backend/database/schema.sql")
print("3. Click 'Run'")
print("\n" + "="*80)
