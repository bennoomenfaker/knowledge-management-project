import os
from typing import Optional, List, Any
from uuid import UUID
from app.core.supabase_client import create_client, SupabaseClient


def get_supabase() -> SupabaseClient:
    url = "http://localhost:54321"
    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU"
    return create_client(url, key)


class SupabaseService:
    def __init__(self, supabase: SupabaseClient = None):
        self.supabase = supabase or get_supabase()
    
    async def create_pfe(self, pfe_data: dict, user_id: str) -> dict:
        data = pfe_data.copy() if isinstance(pfe_data, dict) else {}
        data["created_by"] = user_id
        
        response = self.supabase.table("pfe_documents").insert(data).execute()
        return response.get("data", [{}])[0] if response.get("data") else {}
    
    async def get_pfe(self, pfe_id: str) -> Optional[dict]:
        response = self.supabase.table("pfe_documents").select("*").eq("id", pfe_id).execute()
        data = response.get("data", [])
        return data[0] if data else None
    
    async def get_all_pfe(self, limit: int = 50, offset: int = 0, filters: Optional[dict] = None) -> List[dict]:
        query = self.supabase.table("pfe_documents").select("*")
        
        if filters:
            if "annee" in filters:
                query = query.eq("annee", filters["annee"])
            if "domaine_vic" in filters:
                query = query.eq("domaine_vic", filters["domaine_vic"])
            if "institution" in filters:
                query = query.eq("institution", filters["institution"])
            if "auteur" in filters:
                query = query.ilike("auteur", f"%{filters['auteur']}%")
        
        query = query.order("created_at", desc=True).range(offset, offset + limit - 1)
        response = query.execute()
        return response.get("data", [])
    
    async def update_pfe(self, pfe_id: str, pfe_data: dict) -> Optional[dict]:
        update_data = {k: v for k, v in pfe_data.items() if v is not None}
        update_data["updated_at"] = "now"
        
        response = self.supabase.table("pfe_documents").update(update_data).eq("id", pfe_id).execute()
        data = response.get("data", [])
        return data[0] if data else None
    
    async def delete_pfe(self, pfe_id: str) -> bool:
        response = self.supabase.table("pfe_documents").delete().eq("id", pfe_id).execute()
        return bool(response.get("data"))
    
    async def count_pfe(self, filters: Optional[dict] = None) -> int:
        query = self.supabase.table("pfe_documents").select("*")
        
        if filters:
            if "annee" in filters:
                query = query.eq("annee", filters["annee"])
            if "domaine_vic" in filters:
                query = query.eq("domaine_vic", filters["domaine_vic"])
            if "institution" in filters:
                query = query.eq("institution", filters["institution"])
        
        response = query.execute()
        return len(response.get("data", []))
    
    async def get_pfe_by_user(self, user_id: str) -> List[dict]:
        response = self.supabase.table("pfe_documents").select("*").eq("created_by", user_id).execute()
        return response.get("data", [])
    
    async def update_pfe_status(self, pfe_id: str, status: str) -> bool:
        response = self.supabase.table("pfe_documents").update({"status": status}).eq("id", pfe_id).execute()
        return bool(response.get("data"))
    
    async def get_user_profile(self, user_id: str) -> Optional[dict]:
        response = self.supabase.table("user_profiles").select("*").eq("id", user_id).execute()
        data = response.get("data", [])
        return data[0] if data else None
    
    async def create_user_profile(self, user_id: str, full_name: Optional[str] = None, institution: Optional[str] = None) -> dict:
        data = {"id": user_id, "role": "visiteur"}
        if full_name:
            data["full_name"] = full_name
        if institution:
            data["institution"] = institution
        
        response = self.supabase.table("user_profiles").insert(data).execute()
        return response.get("data", [{}])[0]
    
    async def update_user_profile(self, user_id: str, role: str, full_name: Optional[str] = None, institution: Optional[str] = None) -> dict:
        update_data = {"role": role}
        if full_name:
            update_data["full_name"] = full_name
        if institution:
            update_data["institution"] = institution
        
        response = self.supabase.table("user_profiles").update(update_data).eq("id", user_id).execute()
        return response.get("data", [{}])[0]


_supabase_service: Optional[SupabaseService] = None


def get_supabase_service() -> SupabaseService:
    global _supabase_service
    if _supabase_service is None:
        _supabase_service = SupabaseService()
    return _supabase_service