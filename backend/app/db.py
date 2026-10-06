from supabase import create_client, Client
from .config import settings

supabase: Client = create_client(settings.supabase_url, settings.supabase_service_role_key)

def current_user(access_token: str):
    result = supabase.auth.get_user(access_token)
    return result.user
