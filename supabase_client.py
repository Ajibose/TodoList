import config
from supabase import Client, create_client


settings = config.settings

url = settings.supabase_url
key = settings.supabase_publishable_key

supa: Client = create_client(url, key)
