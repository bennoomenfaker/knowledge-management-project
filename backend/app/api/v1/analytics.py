from fastapi import APIRouter, Depends
from app.models.analytics import (
    AnalyticsOverview, AnalyticsTimeline, AnalyticsDomains,
    AnalyticsInstitutions, AnalyticsEmerging, AnalyticsGaps, ComparisonResult
)
from app.services.analytics_service import get_analytics_service, AnalyticsService
from app.deps import get_current_user


router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview", response_model=AnalyticsOverview)
async def get_overview(
    analytics_service: AnalyticsService = Depends(get_analytics_service),
    current_user: dict = Depends(get_current_user)
):
    data = await analytics_service.get_overview()
    return AnalyticsOverview(**data)


@router.get("/timeline", response_model=AnalyticsTimeline)
async def get_timeline(
    analytics_service: AnalyticsService = Depends(get_analytics_service),
    current_user: dict = Depends(get_current_user)
):
    data = await analytics_service.get_year_stats()
    return AnalyticsTimeline(years=data)


@router.get("/domains", response_model=AnalyticsDomains)
async def get_domains(
    analytics_service: AnalyticsService = Depends(get_analytics_service),
    current_user: dict = Depends(get_current_user)
):
    data = await analytics_service.get_domain_stats()
    return AnalyticsDomains(domains=data)


@router.get("/institutions", response_model=AnalyticsInstitutions)
async def get_institutions(
    analytics_service: AnalyticsService = Depends(get_analytics_service),
    current_user: dict = Depends(get_current_user)
):
    data = await analytics_service.get_institution_stats()
    return AnalyticsInstitutions(institutions=data)


@router.get("/emerging", response_model=AnalyticsEmerging)
async def get_emerging(
    analytics_service: AnalyticsService = Depends(get_analytics_service),
    current_user: dict = Depends(get_current_user)
):
    data = await analytics_service.get_emerging_topics()
    return AnalyticsEmerging(topics=data)


@router.get("/gaps", response_model=AnalyticsGaps)
async def get_gaps(
    analytics_service: AnalyticsService = Depends(get_analytics_service),
    current_user: dict = Depends(get_current_user)
):
    data = await analytics_service.get_gaps_analysis()
    return AnalyticsGaps(gaps=data)


@router.get("/comparison", response_model=ComparisonResult)
async def get_comparison(
    analytics_service: AnalyticsService = Depends(get_analytics_service),
    current_user: dict = Depends(get_current_user)
):
    data = await analytics_service.get_comparison()
    return ComparisonResult(**data)