from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field
from enum import Enum


class DomaineVIC(str, Enum):
    INTELLIGENCE_COMPETITIVE = "intelligence_competitive"
    VEILLE_STRATEGIQUE = "veille_strategique"
    MANAGEMENT_INFORMATION = "management_information"
    ANALYSE_STRATEGIQUE = "analyse_strategique"
    INTELLIGENCE_ECONOMIQUE = "intelligence_economique"
    GESTION_CONNAISSANCE = "gestion_connaissance"
    DATA_INTELLIGENCE = "data_intelligence"
    SECURITE_INFORMATIONNELLE = "securite_informationnelle"


class TypeVeille(str, Enum):
    STRATEGIQUE = "strategique"
    CONCURRENTIELLE = "concurrentielle"
    REGLEMENTAIRE = "reglementaire"
    TECHNOLOGIQUE = "technologique"
    JURIDIQUE = "juridique"
    COMMERCIALE = "commerciale"
    MARKETING = "marketing"
    ORGANISATIONNELLE = "organisationnelle"


class Institution(str, Enum):
    ISCAE = "ISCAE"
    ESEN = "ESEN"


class PFECreate(BaseModel):
    titre: str = Field(..., min_length=5, max_length=500)
    auteur: str = Field(..., min_length=2, max_length=200)
    email_auteur: Optional[EmailStr] = None
    annee: int = Field(..., ge=2014, le=2026)
    type_veille: Optional[TypeVeille] = None
    domaine_vic: Optional[DomaineVIC] = None
    mots_cles: Optional[list[str]] = None
    resume: Optional[str] = None
    problematic: Optional[str] = None


class PFEUpdate(BaseModel):
    titre: Optional[str] = Field(None, min_length=5, max_length=500)
    auteur: Optional[str] = Field(None, min_length=2, max_length=200)
    email_auteur: Optional[EmailStr] = None
    annee: Optional[int] = Field(None, ge=2014, le=2026)
    type_veille: Optional[TypeVeille] = None
    domaine_vic: Optional[DomaineVIC] = None
    mots_cles: Optional[list[str]] = None
    resume: Optional[str] = None
    problematic: Optional[str] = None


class PFEInDB(BaseModel):
    id: UUID
    titre: str
    auteur: str
    email_auteur: Optional[str] = None
    annee: int
    institution: Optional[str] = None
    type_veille: Optional[str] = None
    domaine_vic: Optional[str] = None
    mots_cles: Optional[list[str]] = None
    resume: Optional[str] = None
    problematic: Optional[str] = None
    methodology: Optional[str] = None
    file_path: Optional[str] = None
    file_url: Optional[str] = None
    file_size: Optional[int] = None
    status: str
    embedding_id: Optional[UUID] = None
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PFEResponse(PFEInDB):
    pass


class PFEResponseWithEmbedding(BaseModel):
    pfe: PFEResponse
    similarity: Optional[float] = None


class PFESearchRequest(BaseModel):
    query: str = Field(..., min_length=2)
    filters: Optional[dict] = None
    limit: int = Field(10, ge=1, le=50)
    offset: int = Field(0, ge=0)


class SemanticSearchRequest(BaseModel):
    query: str = Field(..., min_length=2)
    limit: int = Field(5, ge=1, le=20)
    filters: Optional[dict] = None


class StateOfArtRequest(BaseModel):
    sujet: str = Field(..., min_length=10)
    annee_debut: Optional[int] = Field(None, ge=2014, le=2026)
    annee_fin: Optional[int] = Field(None, ge=2014, le=2026)
    institution: Optional[Institution] = None


class SummaryRequest(BaseModel):
    pfe_id: UUID


class KeywordsRequest(BaseModel):
    pfe_id: UUID


class ClassifyDomainRequest(BaseModel):
    pfe_id: UUID


class UploadResponse(BaseModel):
    pfe_id: UUID
    message: str
    status: str


class MessageResponse(BaseModel):
    message: str