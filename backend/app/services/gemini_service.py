import os
import json
from google import genai
from google.genai import types
from typing import Optional, Dict, List

# Configure Gemini API with new SDK
api_key = os.getenv("GEMINI_API_KEY")

def analyze_text(text: str) -> Optional[Dict[str, any]]:
    """
    Analyze text using Gemini API to extract summary and keywords.
    Returns JSON with 'summary' (max 150 words) and 'keywords' (5-10 strings).
    """
    if not api_key:
        print("[Gemini] GEMINI_API_KEY not set")
        return None
    
    try:
        client = genai.Client(api_key=api_key)
        
        prompt = f"""Analyze the following text and return ONLY valid JSON with exactly these keys:
- "summary": a concise summary in French (maximum 150 words)
- "keywords": an array of 5 to 10 relevant keywords in French

Text to analyze:
{text[:10000]}

Return ONLY the JSON, no markdown, no code blocks, no extra text."""
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        raw = response.text.strip()
        result = json.loads(raw)
        
        # Validate structure
        if "summary" not in result or "keywords" not in result:
            print(f"[Gemini] Invalid response structure: {result}")
            return None
        
        # Ensure keywords is a list
        if not isinstance(result["keywords"], list):
            result["keywords"] = [str(result["keywords"])]
        
        # Limit summary to ~150 words
        words = result["summary"].split()
        if len(words) > 150:
            result["summary"] = " ".join(words[:150]) + "..."
        
        # Limit keywords to 5-10
        result["keywords"] = result["keywords"][:10]
        
        return result
        
    except json.JSONDecodeError as e:
        print(f"[Gemini] JSON parse error: {e} - Raw: {raw[:200]}")
        return None
    except Exception as e:
        print(f"[Gemini] Error: {e}")
        return None
