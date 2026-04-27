from typing import Optional, List
from pydantic import BaseModel
from uuid import UUID


class SummaryResponse(BaseModel):
    pfe_id: UUID
    summary: str
    model_used: str


class KeywordsResponse(BaseModel):
    pfe_id: UUID
    keywords: List[str]
    model_used: str


class DomainClassificationResponse(BaseModel):
    pfe_id: UUID
    suggested_domain: str
    confidence: float
    model_used: str


class StateOfArtResponse(BaseModel):
    sujet: str
    synthesis: str
    concepts_cles: List[str]
    sources: List[dict]
    model_used: str


class EmbeddingResponse(BaseModel):
    pfe_id: UUID
    embedding_id: UUID
    model_used: str


class ProcessingStatus(BaseModel):
    pfe_id: UUID
    status: str
    message: Optional[str] = None


class AIAnalysisRequest(BaseModel):
    pfe_id: UUID
    question: str


class AIAnalysisResponse(BaseModel):
    pfe_id: UUID
    question: str
    answer: str
    model_used: str