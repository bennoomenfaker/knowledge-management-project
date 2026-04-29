"""
AI Analysis Engine - Fallback Chain: Gemini → DeepSeek → LM Studio
Returns structured JSON: {summary, problematic, solution, keywords, state_of_art}
"""
import os
import json
import asyncio
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Try importing Gemini SDK
try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("google.genai not installed")

# Try importing httpx for cloud APIs
try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


class AIAnalysisEngine:
    """
    Priority chain: LM Studio (Qwen) (1) → Gemini (2) → DeepSeek (3)
    All methods return structured JSON or None
    """
    
    def __init__(self):
        # Load from environment - check both possible env var names
        self.gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        self.lm_studio_ports = [1234, 1235, 1236, 1237]
        self.lm_studio_model = os.getenv("LMSTUDIO_MODEL", "qwen2.5-coder-1.5b")
        self._lm_url = None
        
        # Log available providers
        logger.info(f"AI Engine initialized - LM Studio (Qwen): {self.lm_studio_model}, Gemini: {bool(self.gemini_key)}, DeepSeek: {bool(self.deepseek_key)}, LM Studio ports: {self.lm_studio_ports}")
        
    async def analyze_pfe(self, text: str, max_summary_words: int = 150) -> Optional[Dict[str, Any]]:
        """
        Main entry point: Run full PFE analysis with fallback chain.
        Priority: LM Studio (Qwen) (1) → Gemini (2) → DeepSeek (3)
        Returns: {summary, problematic, solution, keywords, state_of_art}
        """
        # Build prompt for structured extraction
        prompt = self._build_analysis_prompt(text[:15000], max_summary_words)
        
        # Try LM Studio local first (Priority 1) - Qwen
        logger.info("🔄 Trying LM Studio (Qwen) local first...")
        lm_url = await self._find_lm_studio()
        if lm_url:
            # Try qwen2.5-coder first (faster), then other models
            for model in [self.lm_studio_model, "mistral-7b-instruct-v0.3-bnb-wesh-lora", "deepseek-r1-distill-qwen-1.5b"]:
                if self._is_model_available(model):
                    result = await self._try_lm_studio_with_model(lm_url, prompt, model)
                    if result:
                        logger.info(f"✅ Analysis via LM Studio ({model})")
                        return result
        
        # Try Gemini (Priority 2)
        if self.gemini_key and GEMINI_AVAILABLE:
            result = await self._try_gemini(prompt)
            if result:
                logger.info("✅ Analysis via Gemini API")
                return result
        
        # Try DeepSeek (Priority 3)
        if self.deepseek_key and HTTPX_AVAILABLE:
            result = await self._try_deepseek(prompt)
            if result:
                logger.info("✅ Analysis via DeepSeek API")
                return result
        
        logger.error("❌ All AI providers failed")
        return None
    
    def _build_analysis_prompt(self, text: str, max_words: int) -> str:
        return f"""Analyze this PFE (Projet de Fin d'Études) document and return ONLY valid JSON with these keys:

- "summary": Concise summary in French (maximum {max_words} words)
- "problematic": The main research problem/question in French (1-2 sentences)
- "solution": The proposed solution(s) in French (2-3 sentences)
- "keywords": Array of 5-10 relevant French keywords
- "state_of_art": Brief state of the art in French (3-4 sentences)

Document text:
{text}

IMPORTANT: Return ONLY the JSON object, no markdown, no code blocks, no extra text."""
    
    async def _try_gemini(self, prompt: str) -> Optional[Dict[str, Any]]:
        try:
            client = genai.Client(api_key=self.gemini_key)
            response = await asyncio.to_thread(
                lambda: client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                )
            )
            return json.loads(response.text.strip())
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            return None
    
    async def _try_deepseek(self, prompt: str) -> Optional[Dict[str, Any]]:
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.deepseek_key}"},
                    json={
                        "model": "deepseek-chat",
                        "messages": [{"role": "user", "content": prompt}],
                        "response_format": {"type": "json_object"},
                        "temperature": 0.3
                    }
                )
                if resp.status_code == 200:
                    content = resp.json()["choices"][0]["message"]["content"]
                    return json.loads(content)
        except Exception as e:
            logger.error(f"DeepSeek error: {e}")
        return None
    
    async def _find_lm_studio(self) -> Optional[str]:
        if self._lm_url:
            return self._lm_url
        if not HTTPX_AVAILABLE:
            return None
        for port in self.lm_studio_ports:
            try:
                async with httpx.AsyncClient(timeout=2.0) as client:
                    r = await client.get(f"http://localhost:{port}/v1/models")
                    if r.status_code == 200:
                        self._lm_url = f"http://localhost:{port}"
                        self._lm_models = [m["id"] for m in r.json().get("data", [])]
                        logger.info(f"LM Studio found on port {port} with models: {self._lm_models}")
                        return self._lm_url
            except Exception:
                continue
        return None
    
    def _is_model_available(self, model_name: str) -> bool:
        """Check if a specific model is available in LM Studio"""
        if hasattr(self, '_lm_models') and self._lm_models:
            return model_name in self._lm_models
        return True  # Assume available if we don't know
    
    async def _try_lm_studio_with_model(self, base_url: str, prompt: str, model: str) -> Optional[Dict[str, Any]]:
        """Try LM Studio with a specific model"""
        try:
            # Set shorter timeout for faster models like qwen
            timeout = 30.0 if "qwen" in model else 120.0
            async with httpx.AsyncClient(timeout=timeout) as client:
                logger.info(f"Trying LM Studio model: {model} (timeout: {timeout}s)")
                resp = await client.post(
                    f"{base_url}/v1/chat/completions",
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.3,
                        "max_tokens": 1000
                    }
                )
                if resp.status_code == 200:
                    content = resp.json()["choices"][0]["message"]["content"]
                    # Clean LM Studio output (remove think tags, etc.)
                    content = content.replace("<think>", "").replace("</think>", "")
                    content = content.strip()
                    
                    # Try to parse JSON
                    try:
                        # Remove any markdown/code blocks
                        if content.startswith("```json"):
                            content = content[7:]
                        if content.startswith("```"):
                            content = content[3:]
                        if content.endswith("```"):
                            content = content[:-3]
                        content = content.strip()
                        
                        result = json.loads(content)
                        if "summary" in result and "keywords" in result:
                            return result
                        else:
                            logger.warning(f"Invalid JSON structure from {model}: {result.keys() if isinstance(result, dict) else 'not dict'}")
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON parse error from {model}: {e} - Content: {content[:200]}")
                else:
                    logger.error(f"LM Studio {model} returned HTTP {resp.status_code}: {resp.text[:100]}")
        except httpx.TimeoutException:
            logger.warning(f"Timeout waiting for {model}")
        except Exception as e:
            logger.error(f"LM Studio {model} error: {e}")
        return None
