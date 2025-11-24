import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load .env from backend directory
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(backend_dir, '.env'))

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env")

supabase: Client = create_client(url, key)

def get_supabase_client() -> Client:
    return supabase
