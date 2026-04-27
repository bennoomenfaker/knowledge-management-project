import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    supabase_url: str = "http://localhost:54321"
    supabase_key: str = ""
    supabase_anon_key: str = ""
    
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "opencode"
    ollama_embedding_model: str = "mxbai-embed-large"
    
    lmstudio_base_url: str = "http://localhost:1234"
    lmstudio_model: str = "deepseek-r1-distill-qwen-1.5b"
    
    use_cloud_api: bool = False
    cloud_provider: str = "deepseek"
    deepseek_api_key: str = ""
    google_api_key: str = ""
    
    jwt_secret: str = "dev-secret"
    environment: str = "development"
    
    class Config:
        env_file = ".env"
        extra = "allow"


def get_settings() -> Settings:
    return Settings(
        supabase_url="http://localhost:54321",
        supabase_key=os.environ.get("SUPABASE_KEY", ""),
        supabase_anon_key=os.environ.get("SUPABASE_ANON_KEY", ""),
        ollama_base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
        ollama_model=os.environ.get("OLLAMA_MODEL", "opencode"),
        ollama_embedding_model=os.environ.get("OLLAMA_EMBEDDING_MODEL", "mxbai-embed-large"),
        use_cloud_api=os.environ.get("USE_CLOUD_API", "false").lower() == "true",
        cloud_provider=os.environ.get("CLOUD_PROVIDER", "deepseek"),
        deepseek_api_key=os.environ.get("DEEPSEEK_API_KEY", ""),
        google_api_key=os.environ.get("GOOGLE_API_KEY", ""),
        jwt_secret=os.environ.get("JWT_SECRET", "dev-secret"),
        environment=os.environ.get("ENVIRONMENT", "development"),
    )