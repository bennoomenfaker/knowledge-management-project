from typing import Optional, List
from app.core.supabase_client import create_client, SupabaseClient
import os
from collections import Counter


def get_analytics_supabase() -> SupabaseClient:
    url = "http://localhost:54321"
    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU"
    return create_client(url, key)


class AnalyticsService:
    def __init__(self, supabase: SupabaseClient = None):
        self.supabase = supabase or get_analytics_supabase()
    
    async def get_overview(self) -> dict:
        try:
            response = self.supabase.table("pfe_documents").select("*").execute()
            pfe_list = response.get("data", [])
            
            if not pfe_list:
                return {
                    "total_pfe": 0,
                    "total_auteurs": 0,
                    "annee_min": 2014,
                    "annee_max": 2026,
                    "domains_count": 0,
                    "institutions_count": 0
                }
            
            years = [p.get("annee") for p in pfe_list if p.get("annee")]
            auteurs = [p.get("auteur") for p in pfe_list if p.get("auteur")]
            domains = [p.get("domaine_vic") for p in pfe_list if p.get("domaine_vic")]
            institutions = [p.get("institution") for p in pfe_list if p.get("institution")]
            
            return {
                "total_pfe": len(pfe_list),
                "total_auteurs": len(set(auteurs)),
                "annee_min": min(years) if years else 2014,
                "annee_max": max(years) if years else 2026,
                "domains_count": len(set(domains)),
                "institutions_count": len(set(institutions))
            }
        except Exception as e:
            print(f"Analytics overview error: {e}")
            return {
                "total_pfe": 0,
                "total_auteurs": 0,
                "annee_min": 2014,
                "annee_max": 2026,
                "domains_count": 0,
                "institutions_count": 0
            }
    
    async def get_domain_stats(self) -> List[dict]:
        try:
            response = self.supabase.table("pfe_documents").select("domaine_vic").execute()
            
            if not response.get("data", []):
                return []
            
            domains = [p.get("domaine_vic") for p in response.get("data", []) if p.get("domaine_vic")]
            total = len(domains)
            
            counter = Counter(domains)
            
            stats = []
            for domain, count in counter.items():
                stats.append({
                    "domaine_vic": domain,
                    "count": count,
                    "percentage": round((count / total) * 100, 2) if total > 0 else 0
                })
            
            stats.sort(key=lambda x: x["count"], reverse=True)
            return stats
        except Exception as e:
            print(f"Domain stats error: {e}")
            return []
    
    async def get_year_stats(self) -> List[dict]:
        try:
            response = self.supabase.table("pfe_documents").select("annee").execute()
            
            if not response.get("data", []):
                return []
            
            years = [p.get("annee") for p in response.get("data", []) if p.get("annee")]
            counter = Counter(years)
            
            result = []
            for year, count in sorted(counter.items()):
                result.append({"annee": year, "count": count})
            
            return result
        except Exception as e:
            print(f"Year stats error: {e}")
            return []
    
    async def get_institution_stats(self) -> List[dict]:
        try:
            response = self.supabase.table("pfe_documents").select("institution").execute()
            
            if not response.get("data", []):
                return []
            
            institutions = [p.get("institution") for p in response.get("data", []) if p.get("institution")]
            total = len(institutions)
            
            counter = Counter(institutions)
            
            stats = []
            for inst, count in counter.items():
                stats.append({
                    "institution": inst,
                    "count": count,
                    "percentage": round((count / total) * 100, 2) if total > 0 else 0
                })
            
            return stats
        except Exception as e:
            print(f"Institution stats error: {e}")
            return []
    
    async def get_emerging_topics(self, top_n: int = 10) -> List[dict]:
        try:
            response = self.supabase.table("pfe_documents").select("mots_cles, annee").execute()
            
            if not response.get("data", []):
                return []
            
            topic_by_year = {}
            for pfe in response.get("data", []):
                annee = pfe.get("annee")
                mots_cles = pfe.get("mots_cles", []) or []
                
                if isinstance(mots_cles, str):
                    import json
                    try:
                        mots_cles = json.loads(mots_cles)
                    except:
                        mots_cles = [mots_cles]
                
                if annee not in topic_by_year:
                    topic_by_year[annee] = []
                
                topic_by_year[annee].extend(mots_cles)
            
            recent_years = sorted(topic_by_year.keys(), reverse=True)[:3]
            older_years = sorted(topic_by_year.keys())[:-3] if len(topic_by_year) > 3 else []
            
            recent_topics = Counter()
            older_topics = Counter()
            
            for year in recent_years:
                recent_topics.update(topic_by_year.get(year, []))
            
            for year in older_years:
                older_topics.update(topic_by_year.get(year, []))
            
            emerging = []
            for topic, recent_count in recent_topics.items():
                older_count = older_topics.get(topic, 0)
                if recent_count > older_count:
                    trend = "up" if recent_count > older_count else "stable"
                    emerging.append({
                        "topic": topic,
                        "count": recent_count,
                        "trend": trend
                    })
            
            emerging.sort(key=lambda x: x["count"], reverse=True)
            return emerging[:top_n]
        except Exception as e:
            print(f"Emerging topics error: {e}")
            return []
    
    async def get_gaps_analysis(self) -> List[dict]:
        try:
            response = self.supabase.table("pfe_documents").select("domaine_vic, mots_cles").execute()
            
            if not response.get("data", []):
                return []
            
            domain_keywords = {}
            for pfe in response.get("data", []):
                domain = pfe.get("domaine_vic")
                keywords = pfe.get("mots_cles", []) or []
                
                if domain:
                    if domain not in domain_keywords:
                        domain_keywords[domain] = []
                    domain_keywords[domain].extend(keywords)
            
            all_keywords = set()
            for keywords in domain_keywords.values():
                all_keywords.update(keywords)
            
            gaps = []
            common_missing = [
                "deep learning", "transformers", "NLP", "graph embeddings",
                "knowledge graphs", "multimodal", "federated learning",
                "explainable AI", "XAI", "AI éthique"
            ]
            
            for domain, keywords in domain_keywords.items():
                existing = set(keywords)
                missing = [kw for kw in common_missing if kw not in existing]
                
                if missing:
                    score = len(missing) / len(common_missing)
                    gaps.append({
                        "domaine_vic": domain,
                        "missing_keywords": missing,
                        "opportunity_score": round(score, 2)
                    })
            
            gaps.sort(key=lambda x: x["opportunity_score"], reverse=True)
            return gaps[:5]
        except Exception as e:
            print(f"Gaps analysis error: {e}")
            return []
    
    async def get_comparison(self) -> dict:
        try:
            iscae_response = self.supabase.table("pfe_documents").select("domaine_vic").eq("institution", "ISCAE").execute()
            esen_response = self.supabase.table("pfe_documents").select("domaine_vic").eq("institution", "ESEN").execute()
            
            iscae_domains = set([p.get("domaine_vic") for p in iscae_response.get("data", []) if p.get("domaine_vic")])
            esen_domains = set([p.get("domaine_vic") for p in esen_response.get("data", []) if p.get("domaine_vic")])
            
            common = iscae_domains & esen_domains
            unique_iscae = iscae_domains - esen_domains
            unique_esen = esen_domains - iscae_domains
            
            return {
                "iscae_count": len(iscae_response.get("data", [])),
                "esen_count": len(esen_response.get("data", [])),
                "common_domains": list(common),
                "unique_iscae": list(unique_iscae),
                "unique_esen": list(unique_esen)
            }
        except Exception as e:
            print(f"Comparison error: {e}")
            return {
                "iscae_count": 0,
                "esen_count": 0,
                "common_domains": [],
                "unique_iscae": [],
                "unique_esen": []
            }


def get_analytics_service() -> AnalyticsService:
    return AnalyticsService()