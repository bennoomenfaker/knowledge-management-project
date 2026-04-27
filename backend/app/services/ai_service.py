from typing import Optional, List
import json
import re
import httpx
import os
from app.config import get_settings


settings = get_settings()

AVAILABLE_LOCAL_MODELS = ["opencode", "openclaude", "pi", "llama3", "mistral", "codellama"]
FALLBACK_MODELS = ["deepseek-chat", "gemini-2.0-flash"]


class HybridAIService:
    def __init__(self):
        # Configuration LM Studio (GGUF local) - Priorité 1
        self.lmstudio_base_url = os.environ.get("LMSTUDIO_BASE_URL", "http://localhost:1234")
        self.lmstudio_model = os.environ.get("LMSTUDIO_MODEL", "deepseek-r1-distill-qwen-1.5b")
        
        # Configuration Ollama (local) - Priorité 2
        self.ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        self.local_model = os.environ.get("OLLAMA_MODEL", "opencode")
        self.embedding_model = os.environ.get("OLLAMA_EMBEDDING_MODEL", "mxbai-embed-large")
        
        # Configuration API Cloud (fallback)
        self.use_cloud = os.environ.get("USE_CLOUD_API", "false").lower() == "true"
        self.cloud_provider = os.environ.get("CLOUD_PROVIDER", "deepseek")
        self.deepseek_key = os.environ.get("DEEPSEEK_API_KEY", "")
        self.google_key = os.environ.get("GOOGLE_API_KEY", "")
        
        self._local_available = None
        self._lmstudio_available = None
        self._available_models = []
    
    async def check_availability(self) -> dict:
        """Vérifie les services disponibles"""
        lmstudio_status = await self._check_lmstudio()
        local_status = await self._check_local_ollama()
        local_models = await self._list_local_models() if local_status else []
        
        return {
            "lmstudio_available": lmstudio_status,
            "local_available": local_status,
            "local_models": local_models,
            "use_cloud": self.use_cloud or (not lmstudio_status and not local_status),
            "cloud_provider": self.cloud_provider if self.use_cloud or (not lmstudio_status and not local_status) else None,
            "active_model": self._determine_best_model(local_models, lmstudio_status, local_status)
        }
    
    async def _check_lmstudio(self) -> bool:
        """Vérifie si LM Studio est disponible"""
        if self._lmstudio_available is not None:
            return self._lmstudio_available
        
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                response = await client.get(f"{self.lmstudio_base_url}/v1/models")
                self._lmstudio_available = response.status_code == 200
                print(f"[AI] LM Studio: {'✓ Disponible' if self._lmstudio_available else '✗ Non disponible'}")
                return self._lmstudio_available
        except Exception as e:
            print(f"[AI] LM Studio non joignable: {e}")
            self._lmstudio_available = False
            return False
    
    async def _check_local_ollama(self) -> bool:
        """Vérifie si Ollama local est disponible"""
        if self._local_available is not None:
            return self._local_available
        
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                response = await client.get(f"{self.ollama_base_url}/api/tags")
                self._local_available = response.status_code == 200
                print(f"[AI] Ollama local: {'✓ Disponible' if self._local_available else '✗ Non disponible'}")
                return self._local_available
        except Exception as e:
            print(f"[AI] Ollama local non joignable: {e}")
            self._local_available = False
            return False
    
    async def _list_local_models(self) -> List[str]:
        """Liste les modèles Ollama disponibles"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.ollama_base_url}/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    models = [m["name"] for m in data.get("models", [])]
                    print(f"[AI] Modèles locaux: {models}")
                    return models
                return []
        except Exception as e:
            print(f"[AI] Erreur listage modèles: {e}")
            return []
    
    def _determine_best_model(self, local_models: List[str], lmstudio_available: bool, ollama_available: bool) -> str:
        """Détermine le meilleur modèle à utiliser"""
        # Priorité 1: LM Studio
        if lmstudio_available:
            print(f"[AI] Utilisation LM Studio: {self.lmstudio_model}")
            return f"lmstudio:{self.lmstudio_model}"
        
        # Priorité 2: Ollama local
        if ollama_available:
            for preferred in AVAILABLE_LOCAL_MODELS:
                if preferred in local_models:
                    print(f"[AI] Utilisation Ollama: {preferred}")
                    return preferred
            
            if local_models:
                print(f"[AI] Utilisation Ollama: {local_models[0]}")
                return local_models[0]
        
        # Priorité 3: API Cloud
        print(f"[AI] Fallback vers API cloud: {self._get_cloud_model()}")
        return self._get_cloud_model()
    
    def _get_cloud_model(self) -> str:
        """Retourne le modèle cloud configuré"""
        if self.cloud_provider == "google":
            return "gemini-2.0-flash"
        return "deepseek-chat"
    
    async def generate_summary(self, text: str, max_length: int = 500) -> Optional[str]:
        prompt = f"Résumez le texte suivant en français en environ {max_length} caractères:\n\n{text[:3000]}\n\nRésumé:"
        return await self._generate(prompt)
    
    async def generate_problematic(self, text: str, max_length: int = 200) -> Optional[str]:
        prompt = f"Formulez la problématique centrale de ce texte en une phrase en français (max {max_length} caractères):\n\n{text[:3000]}\n\nProblématique:"
        return await self._generate(prompt, max_tokens=max_length)
    
    async def generate_keywords(self, text: str, max_keywords: int = 10) -> Optional[List[str]]:
        prompt = f"Extrairez les {max_keywords} mots-clés du texte suivant en format JSON:\n\n{text[:3000]}\n\nMots-clés (JSON):"
        response = await self._generate(prompt)
        if response:
            try:
                keywords = json.loads(response)
                return keywords if isinstance(keywords, list) else []
            except json.JSONDecodeError:
                import re
                return re.findall(r'"([^"]+)"', response)[:max_keywords]
        return []
    
    async def classify_domain(self, text: str) -> Optional[dict]:
        domains = [
            "intelligence_competitive", "veille_strategique", "management_information",
            "analyse_strategique", "intelligence_economique", "gestion_connaissance",
            "data_intelligence", "securite_informationnelle"
        ]
        prompt = f"Classifiez dans: {', '.join(domains)}. JSON: {{\"domaine\": \"...\", \"confiance\": 0.95}}\n\n{text[:2000]}\n\nJSON:"
        response = await self._generate(prompt)
        if response:
            try:
                return json.loads(response)
            except:
                return {"domaine": domains[0], "confiance": 0.5}
        return None
    
    async def generate_embedding(self, text: str) -> Optional[List[float]]:
        # Essayer LM Studio d'abord
        lmstudio_ok = await self._check_lmstudio()
        if lmstudio_ok:
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        f"{self.lmstudio_base_url}/v1/embeddings",
                        json={"model": self.lmstudio_model, "input": text[:2000]}
                    )
                    if response.status_code == 200:
                        return response.json().get("data", [{}])[0].get("embedding")
            except Exception as e:
                print(f"[AI] Embedding LM Studio échoué: {e}")
        
        # Fallback Ollama
        local_ok = await self._check_local_ollama()
        if local_ok:
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        f"{self.ollama_base_url}/api/embeddings",
                        json={"model": self.embedding_model, "prompt": text[:2000]}
                    )
                    if response.status_code == 200:
                        return response.json().get("embedding")
            except Exception as e:
                print(f"[AI] Embedding Ollama échoué: {e}")
        
        print("[AI] Embedding: tous les services ont échoué, retour None")
        return None
    
    async def generate_simple_summary(self, text: str, max_length: int = 500) -> Optional[str]:
        """Génère un résumé simple sans utiliser LM Studio - pour tests"""
        prompt = f"""Résume en 2-3 phrases ce texte en français:\n\n{text[:1500]}\n\nRésumé:"""
        return await self._generate(prompt, max_tokens=max_length)
    
    async def generate_state_of_art(self, contexte: str, documents: List[dict]) -> Optional[str]:
        sources = "\n\n".join([
            f"Doc {i+1}: {d.get('titre', 'N/A')} - {d.get('auteur', 'N/A')} ({d.get('annee', 'N/A')})\nRésumé: {d.get('resume', 'N/A')[:300]}"
            for i, d in enumerate(documents[:5])
        ])
        prompt = f"État de l'art sur: {contexte}\n\n{sources}\n\nSynthèse:"
        return await self._generate(prompt)
    
    async def extract_concepts_cles(self, text: str) -> Optional[List[str]]:
        prompt = f"Concepts clés en JSON:\n\n{text[:2000]}\n\nJSON:"
        response = await self._generate(prompt)
        if response:
            try:
                return json.loads(response)
            except:
                return []
        return []
    
    async def _generate(self, prompt: str, max_tokens: int = 2000) -> Optional[str]:
        # Priorité 1: LM Studio (local, privé et rapide)
        lmstudio_ok = await self._check_lmstudio()
        if lmstudio_ok:
            try:
                response = await self._generate_lmstudio(prompt, max_tokens)
                if response:
                    return response
            except Exception as e:
                print(f"[AI] LM Studio échoué: {e}")
        
        # Priorité 2: Ollama local
        local_ok = await self._check_local_ollama()
        if local_ok:
            try:
                response = await self._generate_local(prompt, max_tokens)
                if response:
                    return response
            except Exception as e:
                print(f"[AI] Ollama échoué: {e}")
        
        # Priorité 3: API Cloud (fallback)
        if self.use_cloud or (self.deepseek_key or self.google_key):
            try:
                response = await self._generate_cloud(prompt, max_tokens)
                if response:
                    print(f"[AI] Réponse via Cloud API")
                    return response
            except Exception as e:
                print(f"[AI] Cloud échoué: {e}")
        
        return None
    
    async def _generate_lmstudio(self, prompt: str, max_tokens: int) -> Optional[str]:
        """Génère via LM Studio (API OpenAI compatible)"""
        try:
            async with httpx.AsyncClient(timeout=180.0) as client:
                response = await client.post(
                    f"{self.lmstudio_base_url}/v1/chat/completions",
                    json={
                        "model": self.lmstudio_model,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": max_tokens,
                        "temperature": 0.7
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    content = re.sub(r'<think>[\s\S]*?</think>\s*', '', content)
                    content = re.sub(r'\*\*([^*]+)\*\*', r'\1', content)
                    content = content.replace('洗净', '').strip()
                    print(f"[AI] Réponse générée via LM Studio")
                    return content.strip()
        except Exception as e:
            print(f"[AI] LM Studio API error: {e}")
        return None
    
    async def _generate_local(self, prompt: str, max_tokens: int) -> Optional[str]:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.ollama_base_url}/api/generate",
                json={
                    "model": self.local_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"num_predict": max_tokens}
                }
            )
            if response.status_code == 200:
                data = response.json()
                print(f"[AI] Réponse générée via Ollama local")
                return data.get("response")
        return None
    
    async def _generate_cloud(self, prompt: str, max_tokens: int) -> Optional[str]:
        if self.cloud_provider == "deepseek" and self.deepseek_key:
            return await self._generate_deepseek(prompt, max_tokens)
        elif self.cloud_provider == "google" and self.google_key:
            return await self._generate_google(prompt, max_tokens)
        print("[AI] Aucune clé API cloud configurée")
        return None
    
    async def _generate_deepseek(self, prompt: str, max_tokens: int) -> Optional[str]:
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.deepseek_key}"},
                    json={
                        "model": "deepseek-chat",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": max_tokens
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    print(f"[AI] Réponse générée via DeepSeek")
                    return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"[AI] DeepSeek API error: {e}")
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
                    print(f"[AI] Réponse générée via Google Gemini")
                    return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            print(f"[AI] Google API error: {e}")
        return None
    
    async def check_ollama_health(self) -> bool:
        return await self._check_local_ollama()
    
    async def check_lmstudio_health(self) -> bool:
        return await self._check_lmstudio()


_hybrid_service: Optional[HybridAIService] = None


def get_hybrid_ai_service() -> HybridAIService:
    global _hybrid_service
    if _hybrid_service is None:
        _hybrid_service = HybridAIService()
    return _hybrid_service