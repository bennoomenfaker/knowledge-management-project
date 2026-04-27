import os
from typing import Optional, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.supabase_client import create_client, SupabaseClient

def get_supabase() -> SupabaseClient:
    url = "http://localhost:54321"
    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU"
    return create_client(url, key)


security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    supabase: SupabaseClient = Depends(get_supabase)
) -> dict:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    token = credentials.credentials
    try:
        auth_client = supabase.auth
        user_obj = auth_client.get_user(token)
        user_data = user_obj.get("user") if user_obj else None
        if user_data:
            return {"id": user_data.get("id", ""), "email": user_data.get("email", ""), "email_confirmed_at": user_data.get("email_confirmed_at")}
        return {"id": "", "email": ""}
    except Exception as e:
        print(f"Auth error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    supabase: SupabaseClient = Depends(get_supabase)
) -> Optional[dict]:
    if credentials is None:
        return None
    
    try:
        auth = supabase.auth
        user_obj = auth.get_user(credentials.credentials)
        user_data = user_obj.get("user") if user_obj else None
        if user_data:
            return {"id": user_data.get("id", ""), "email": user_data.get("email", ""), "email_confirmed_at": user_data.get("email_confirmed_at")}
        return None
    except Exception:
        return None


def require_role(allowed_roles: list[str]):
    async def role_checker(
        user: dict = Depends(get_current_user),
        supabase: SupabaseClient = Depends(get_supabase)
    ) -> dict:
        return user
    
    return role_checker