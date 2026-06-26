# Responsibility: single Supabase client instances shared across the application
# Admin client uses service_role key — bypasses RLS for backend operations
# Anon client uses anon key — for operations that respect RLS

from functools import lru_cache

from supabase import Client, create_client

from app.config import get_settings


@lru_cache(maxsize=1)
def get_supabase_admin() -> Client:
    """
    Return a Supabase client using the service_role key.
    Use for all backend operations: inserts, updates, storage uploads.
    Cached — only one instance created for the lifetime of the process.
    """
    settings = get_settings()
    return create_client(
        settings.supabase_url,
        settings.supabase_service_role_key,
    )


@lru_cache(maxsize=1)
def get_supabase_anon() -> Client:
    """
    Return a Supabase client using the anon key.
    Use only when RLS enforcement is explicitly required.
    """
    settings = get_settings()
    return create_client(
        settings.supabase_url,
        settings.supabase_anon_key or "",
    )