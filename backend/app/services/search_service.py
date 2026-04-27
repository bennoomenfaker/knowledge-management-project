from typing import Optional, List
from app.core.supabase_client import create_client, SupabaseClient
import os
import json
import httpx
import numpy as np


def get_search_supabase() -> SupabaseClient:
    url = "http://localhost:54321"
    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU"
    return create_client(url, key)


class SearchService:
    def __init__(self, supabase: SupabaseClient = None):
        self.supabase = supabase or get_search_supabase()
    
    async def full_text_search(
        self,
        query: str,
        filters: Optional[dict] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[dict]:
        try:
            base_query = self.supabase.table("pfe_documents").select("*")
            
            search_terms = query.lower().split()
            response = base_query.execute()
            
            data = response.get("data", [])
            if not data:
                return []
            
            results = []
            for item in data:
                searchable_text = f"{item.get('titre', '')} {item.get('resume', '')} {item.get('mots_cles', [])}".lower()
                
                if any(term in searchable_text for term in search_terms):
                    if filters:
                        if "annee" in filters and item.get("annee") != filters["annee"]:
                            continue
                        if "domaine_vic" in filters and item.get("domaine_vic") != filters["domaine_vic"]:
                            continue
                        if "institution" in filters and item.get("institution") != filters["institution"]:
                            continue
                    
                    results.append(item)
            
            results.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            return results[offset:offset + limit]
        except Exception as e:
            print(f"Full-text search error: {e}")
            return []
    
    async def semantic_search(
        self,
        query: str,
        limit: int = 5,
        filters: Optional[dict] = None
    ) -> List[dict]:
        try:
            embedding = await self._generate_embedding(query)
            if not embedding:
                return []
            
            embeddings_data = self.supabase.table("pfe_embeddings").select("*").execute()
            
            if not embeddings_data.get("data", []):
                return []
            
            pfe_ids = [e["pfe_id"] for e in embeddings_data.get("data", [])]
            pfe_data = {}
            
            if pfe_ids:
                pfe_response = self.supabase.table("pfe_documents").select("*").in_("id", pfe_ids).execute()
                if pfe_response.data:
                    for pfe in pfe_response.data:
                        pfe_data[pfe["id"]] = pfe
            
            similarities = []
            import numpy as np
            
            query_vec = np.array(embedding)
            query_norm = np.linalg.norm(query_vec)
            
            for emb in embeddings_data.get("data", []):
                if emb.get("embedding"):
                    emb_vec = np.array(emb["embedding"])
                    
                    cosine_sim = np.dot(query_vec, emb_vec) / (query_norm * np.linalg.norm(emb_vec) + 1e-8)
                    
                    pfe_id = emb["pfe_id"]
                    if pfe_id in pfe_data:
                        pfe = pfe_data[pfe_id]
                        
                        if filters:
                            if "annee" in filters and pfe.get("annee") != filters["annee"]:
                                continue
                            if "domaine_vic" in filters and pfe.get("domaine_vic") != filters["domaine_vic"]:
                                continue
                            if "institution" in filters and pfe.get("institution") != filters["institution"]:
                                continue
                        
                        similarities.append({
                            "pfe": pfe,
                            "similarity": float(cosine_sim)
                        })
            
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            return similarities[:limit]
        except Exception as e:
            print(f"Semantic search error: {e}")
            return []
    
    async def hybrid_search(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[dict] = None
    ) -> dict:
        try:
            full_text_results = await self.full_text_search(query, filters, limit)
            semantic_results = await self.semantic_search(query, limit, filters)
            
            combined = {}
            
            for pfe in full_text_results:
                pfe_id = pfe["id"]
                if pfe_id in combined:
                    combined[pfe_id]["pfe"]["score"] += 0.5
                else:
                    combined[pfe_id] = {"pfe": pfe, "score": 0.5}
            
            for item in semantic_results:
                pfe_id = item["pfe"]["id"]
                if pfe_id in combined:
                    combined[pfe_id]["pfe"]["score"] += item["similarity"]
                    combined[pfe_id]["similarity"] = item["similarity"]
                else:
                    combined[pfe_id] = {"pfe": item["pfe"], "score": item["similarity"], "similarity": item["similarity"]}
            
            results = list(combined.values())
            results.sort(key=lambda x: x.get("score", 0), reverse=True)
            
            return {
                "results": [r["pfe"] for r in results[:limit]],
                "total": len(results)
            }
        except Exception as e:
            print(f"Hybrid search error: {e}")
            return {"results": [], "total": 0}
    
    async def _generate_embedding(self, text: str) -> Optional[List[float]]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ollama_url}/api/embeddings",
                    json={"model": self.embedding_model, "prompt": text}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("embedding")
                return None
        except Exception as e:
            print(f"Embedding error: {e}")
            return None


def get_search_service() -> SearchService:
    return SearchService()