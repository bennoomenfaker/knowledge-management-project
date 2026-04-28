from typing import Optional, List
import json
import re
import httpx
import os
import asyncio
from app.config import get_settings


settings = get_settings()

# Ports LM Studio à tester (dans l'ordre)
LM_STUDIO_PORTS = [1234, 1235, 1236, 1237]
LM_STUDIO_MODELS =  ['qwen2.5-coder-1.5b', 'deepseek-r1-distill-qwen-1.5b', 'mistral-7b-instruct-v0.3-bnb-wesh-lora', 'text-embedding-nomic-embed-text-v1.5']


class HybridAIService:
    def __init__(self):
        # Configuration API Cloud (Priorité 1 et 2)
        self.deepseek_key = os.environ.get("DEEPSEEK_API_KEY", "")
        self.google_key = os.environ.get("GOOGLE_API_KEY", "")
        
        # Configuration LM Studio (Priorité 3 - Fallback local)
        self.lm_studio_ports = LM_STUDIO_PORTS
        self.lm_studio_models = LM_STUDIO_MODELS
        self.lm_studio_model = os.environ.get("LMSTUDIO_MODEL", LM_STUDIO_MODELS[0])
        
        self._lm_studio_url = None
        self._lm_studio_models = None
        
    async def _find_lm_studio(self) -> Optional[str]:
        """Trouve un serveur LM Studio actif parmi les ports disponibles"""
        if self._lm_studio_url:
            return self._lm_studio_url
        
        for port in self.lm_studio_ports:
            url = f"http://localhost:{port}"
            try:
                async with httpx.AsyncClient(timeout=2.0) as client:
                    response = await client.get(f"{url}/v1/models")
                    if response.status_code == 200:
                        data = response.json()
                        models = [m.get("id") for m in data.get("data", [])]
                        print(f"[AI] LM Studio trouvé sur port {port} avec modèles: {models}")
                        self._lm_studio_url = url
                        self._lm_studio_models = models
                        return url
            except Exception:
                continue
        
        return None

    async def check_availability(self) -> dict:
        """Vérifie les services disponibles - Priorité: DeepSeek → Gemini → LM Studio"""
        deepseek_ok = bool(self.deepseek_key)
        gemini_ok = bool(self.google_key)
        lm_studio_url = await self._find_lm_studio()
        
        available_models = []
        active_model = None
        use_cloud = False
        
        # Priorité 1: DeepSeek
        if deepseek_ok:
            available_models.append("deepseek-chat")
            active_model = "deepseek-chat"
            use_cloud = True
        
        # Priorité 2: Gemini
        if gemini_ok:
            available_models.append("gemini-2.0-flash")
            if not active_model:
                active_model = "gemini-2.0-flash"
                use_cloud = True
        
        # Priorité 3: LM Studio
        if lm_studio_url and self._lm_studio_models:
            available_models.extend(self._lm_studio_models)
            if not active_model:
                active_model = self._lm_studio_models[0] if self._lm_studio_models else self.lm_studio_model
        
        return {
            "deepseek_available": deepseek_ok,
            "gemini_available": gemini_ok,
            "lm_studio_available": lm_studio_url is not None,
            "lm_studio_url": lm_studio_url,
            "lm_studio_models": self._lm_studio_models or [],
            "available_models": available_models,
            "active_model": active_model,
            "use_cloud": use_cloud,
            "priority": "DeepSeek → Gemini → LM Studio"
        }

    async def _generate_with_retry(self, func, *args, max_retries: int = 2, **kwargs) -> Optional[str]:
        """Exécute avec retry et exponential backoff"""
        for attempt in range(max_retries + 1):
            try:
                result = await func(*args, **kwargs)
                if result:
                    return result
            except Exception as e:
                print(f"[AI] Tentative {attempt + 1}/{max_retries + 1} échouée: {e}")
                if attempt < max_retries:
                    await asyncio.sleep(2 ** attempt)
        return None

    async def _generate(self, prompt: str, max_tokens: int = 2000) -> Optional[str]:
        """Génération - LM Studio local en premier, puis cloud APIs"""
        
        # Test LM Studio FIRST (local = plus rapide)
        lm_url = await self._find_lm_studio()
        if lm_url and self._lm_studio_models:
            for model in self._lm_studio_models:
                try:
                    response = await self._generate_lm_studio_model(lm_url, model, prompt, max_tokens)
                    if response:
                        print(f"[AI] Success via LM Studio {model}")
                        return response
                except Exception as e:
                    print(f"[AI] LM {model}: {e}")
                    continue
        
        # DeepSeek cloud
        if self.deepseek_key:
            try:
                response = await self._generate_deepseek(prompt, max_tokens)
                if response:
                    return response
            except Exception as e:
                print(f"[AI] DeepSeek: {e}")
        
        # Gemini cloud  
        if self.google_key:
            try:
                response = await self._generate_google(prompt, max_tokens)
                if response:
                    return response
            except Exception as e:
                print(f"[AI] Gemini: {e}")
        
        print("[AI] All failed")
        return None

    async def _test_deepseek(self, prompt: str, max_tokens: int) -> Optional[str]:
        """Test DeepSeek API avec petit prompt"""
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.deepseek_key}"},
                    json={
                        "model": "deepseek-chat",
                        "messages": [{"role": "user", "content": "Hi"}],
                        "max_tokens": 5
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    print(f"[AI] DeepSeek API working")
                    return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"[AI] DeepSeek test failed: {e}")
        return None

    async def _generate_deepseek(self, prompt: str, max_tokens: int) -> Optional[str]:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.deepseek_key}"},
                    json={
                        "model": "deepseek-chat",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": max_tokens,
                        "temperature": 0.7
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    print(f"[AI] Réponse via DeepSeek API")
                    return data["choices"][0]["message"]["content"].strip()
                else:
                    print(f"[AI] DeepSeek error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"[AI] DeepSeek error: {e}")
        return None

    async def _generate_google(self, prompt: str, max_tokens: int) -> Optional[str]:
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.google_key}",
                    json={"contents": [{"parts": [{"text": prompt}]}]}
                )
                if response.status_code == 200:
                    data = response.json()
                    print(f"[AI] Réponse via Google Gemini API")
                    return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception as e:
            print(f"[AI] Gemini error: {e}")
        return None

    async def _generate_lm_studio(self, base_url: str, prompt: str, max_tokens: int) -> Optional[str]:
        try:
            async with httpx.AsyncClient(timeout=180.0) as client:
                response = await client.post(
                    f"{base_url}/v1/chat/completions",
                    json={
                        "model": self.lm_studio_model,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": max_tokens,
                        "temperature": 0.7
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    # Nettoyage LM Studio
                    content = re.sub(r'<think>[\s\S]*?</think>\s*', '', content)
                    content = re.sub(r'\*\*([^*]+)\*\*', r'\1', content)
                    content = content.replace('洗净', '').strip()
                    print(f"[AI] Réponse via LM Studio ({base_url})")
                    return content
        except Exception as e:
            print(f"[AI] LM Studio error: {e}")
        return None

    async def _generate_lm_studio_model(self, base_url: str, model: str, prompt: str, max_tokens: int) -> Optional[str]:
        """Génère avec un modèle LM Studio spécifique"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{base_url}/v1/chat/completions",
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": min(max_tokens, 500),
                        "temperature": 0.7
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    content = re.sub(r'<think>[\s\S]*?</think>\s*', '', content)
                    content = re.sub(r'\*\*([^*]+)\*\*', r'\1', content)
                    content = content.replace('洗净', '').strip()
                    print(f"[AI] LM ({model}) OK")
                    return content
                else:
                    print(f"[AI] LM {model}: HTTP {response.status_code}")
        except httpx.TimeoutException:
            print(f"[AI] LM {model}: timeout")
        except Exception as e:
            print(f"[AI] LM {model} error: {e}")
        return None

    # === MÉTHODES D'EXTRACTION ===

    async def generate_summary(self, text: str, max_length: int = 500) -> Optional[str]:
        prompt = f"""Résumez ce document PFE en français en {max_length} caractères maximum.
Soignez la clarté et la concision.

Texte:
{text[:4000]}

Résumé:"""
        return await self._generate(prompt, max_tokens=max_length)

    async def generate_problematic(self, text: str, max_length: int = 300) -> Optional[str]:
        prompt = f"""Identifiez et formulez la problématique centrale de ce PFE en une phrase claire en français (max {max_length} caractères).

Texte:
{text[:4000]}

Problématique:"""
        return await self._generate(prompt, max_tokens=max_length)

    async def generate_solutions(self, text: str, max_length: int = 500) -> Optional[str]:
        prompt = f"""Résumez les solutions proposées dans ce PFE en français (max {max_length} caractères).

Texte:
{text[:4000]}

Solutions proposées:"""
        return await self._generate(prompt, max_tokens=max_length)

    async def generate_keywords(self, text: str, max_keywords: int = 10) -> Optional[List[str]]:
        prompt = f"""Extraire les {max_keywords} mots-clés les plus pertinents de ce texte.
Retournez uniquement un tableau JSON valide.

Texte:
{text[:4000]}

Mots-clés (JSON):"""
        response = await self._generate(prompt, max_tokens=500)
        if response:
            try:
                keywords = json.loads(response)
                return keywords if isinstance(keywords, list) else []
            except json.JSONDecodeError:
                return re.findall(r'"([^"]+)"', response)[:max_keywords]
        return []

    async def extract_methodology(self, text: str, max_length: int = 300) -> Optional[str]:
        prompt = f"""Décrivez la méthodologie utilisée dans ce PFE en français (max {max_length} caractères).
Si non explicite, déduisez-la du contenu.

Texte:
{text[:4000]}

Méthodologie:"""
        return await self._generate(prompt, max_tokens=max_length)

    async def extract_concepts_cles(self, text: str) -> Optional[List[str]]:
        prompt = f"""Listez les concepts clés de ce document en JSON.

Texte:
{text[:3000]}

Concepts (JSON):"""
        response = await self._generate(prompt, max_tokens=500)
        if response:
            try:
                return json.loads(response)
            except:
                return []
        return []

    async def generate_state_of_art(self, contexte: str, documents: List[dict]) -> Optional[str]:
        sources = "\n\n".join([
            f"Doc {i+1}: {d.get('titre', 'N/A')} - {d.get('auteur', 'N/A')} ({d.get('annee', 'N/A')})\n{d.get('resume', '')[:400]}"
            for i, d in enumerate(documents[:5])
        ])
        prompt = f"""Rédigez l'état de l'art sur: {contexte}

Sources:
{sources}

État de l'art:"""
        return await self._generate(prompt, max_tokens=2000)

    async def classify_domain(self, text: str) -> Optional[dict]:
        domains = [
            "intelligence_competitive", "veille_strategique", "management_information",
            "analyse_strategique", "intelligence_economique", "gestion_connaissance",
            "data_intelligence", "securite_informationnelle"
        ]
        prompt = f"""Classifiez ce document dans: {', '.join(domains)}
Retournez JSON: {{"domaine": "...", "confiance": 0.95}}

Texte:
{text[:2000]}

JSON:"""
        response = await self._generate(prompt, max_tokens=200)
        if response:
            try:
                return json.loads(response)
            except:
                return {"domaine": domains[0], "confiance": 0.5}
        return None

    async def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Génère un embedding via LM Studio ou APIs"""
        lm_url = await self._find_lm_studio()
        if lm_url:
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        f"{lm_url}/v1/embeddings",
                        json={"model": self.lm_studio_model, "input": text[:2000]}
                    )
                    if response.status_code == 200:
                        return response.json().get("data", [{}])[0].get("embedding")
            except Exception as e:
                print(f"[AI] Embedding LM Studio échoué: {e}")
        
        # Fallback DeepSeek pour embeddings (si supporté)
        print("[AI] Embedding: utilisera recherche texte classique")
        return None


_hybrid_service: Optional[HybridAIService] = None


def get_hybrid_ai_service() -> HybridAIService:
    global _hybrid_service
    if _hybrid_service is None:
        _hybrid_service = HybridAIService()
    return _hybrid_service
