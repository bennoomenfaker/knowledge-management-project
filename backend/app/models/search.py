"""
Search response models for the Document Intelligence Engine
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class SearchResultItem(BaseModel):
    """Individual search result with highlighted sections"""
    pfe: Dict[str, Any]
    relevance_score: float = 0.0
    highlighted_sections: Optional[Dict[str, str]] = None
    snippet: Optional[str] = None


class GlobalSearchResponse(BaseModel):
    """Response for global search endpoint"""
    results: List[SearchResultItem]
    total: int
    query: str


class SectionSearchRequest(BaseModel):
    """Request to search within specific sections"""
    query: str
    sections: List[str] = ["problematic", "solution", "resume", "summary"]
    limit: int = 20


class TfIdfRequest(BaseModel):
    """Request for TF-IDF ranking"""
    query: str
    documents: List[Dict[str, Any]]
    limit: int = 20
