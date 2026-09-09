from config import Settings
from supabase import Client, create_client

url = Settings.supabase_url 
key = Settings.supabase_publishable_key

supa: Client = create_client(url, key)
