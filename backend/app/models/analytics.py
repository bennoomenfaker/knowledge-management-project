from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class DomainStats(BaseModel):
    domaine_vic: str
    count: int
    percentage: float


class YearStats(BaseModel):
    annee: int
    count: int


class InstitutionStats(BaseModel):
    institution: str
    count: int
    percentage: float


class EmergingTopic(BaseModel):
    topic: str
    count: int
    trend: str


class GapAnalysis(BaseModel):
    domaine_vic: str
    missing_keywords: List[str]
    opportunity_score: float


class AnalyticsOverview(BaseModel):
    total_pfe: int
    total_auteurs: int
    annee_min: int
    annee_max: int
    domains_count: int
    institutions_count: int


class AnalyticsTimeline(BaseModel):
    years: List[YearStats]


class AnalyticsDomains(BaseModel):
    domains: List[DomainStats]


class AnalyticsInstitutions(BaseModel):
    institutions: List[InstitutionStats]


class AnalyticsEmerging(BaseModel):
    topics: List[EmergingTopic]


class AnalyticsGaps(BaseModel):
    gaps: List[GapAnalysis]


class ComparisonResult(BaseModel):
    iscae_count: int
    esen_count: int
    common_domains: List[str]
    unique_iscae: List[str]
    unique_esen: List[str]


class ChartData(BaseModel):
    labels: List[str]
    values: List[int]