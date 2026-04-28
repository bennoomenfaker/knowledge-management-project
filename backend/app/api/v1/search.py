from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from app.models.pfe import PFESearchRequest, SemanticSearchRequest, PFEResponseWithEmbedding
from app.services.search_service import get_search_service, SearchService
from app.services.supabase_service import get_supabase_service, SupabaseService
from app.deps import get_current_user, get_optional_user


router = APIRouter(prefix="/search", tags=["Search"])


@router.get("/all")
async def get_all_pfe(
    limit: int = 50,
    offset: int = 0,
    domaine_vic: str = Query("", description="Filter by domain"),
    institution: str = Query("", description="Filter by institution"),
    annee: int = Query(None, description="Filter by year"),
    supabase_service: SupabaseService = Depends(get_supabase_service)
):
    """Get all PFE documents with optional filters"""
    filters = {}
    if domaine_vic:
        filters["domaine_vic"] = domaine_vic
    if institution:
        filters["institution"] = institution
    if annee:
        filters["annee"] = annee
    
    pfe_list = await supabase_service.get_all_pfe(limit, offset, filters if filters else None)
    return {"results": pfe_list, "total": len(pfe_list)}


@router.post("/full-text")
async def full_text_search(
    request: PFESearchRequest,
    search_service: SearchService = Depends(get_search_service),
    current_user: dict = Depends(get_current_user)
):
    results = await search_service.full_text_search(
        query=request.query,
        filters=request.filters,
        limit=request.limit,
        offset=request.offset
    )
    return {"results": results, "total": len(results)}


@router.post("/semantic")
async def semantic_search(
    request: SemanticSearchRequest,
    search_service: SearchService = Depends(get_search_service),
    current_user: dict = Depends(get_current_user)
):
    results = await search_service.semantic_search(
        query=request.query,
        limit=request.limit,
        filters=request.filters
    )
    return {"results": results, "total": len(results)}


@router.post("/hybrid")
async def hybrid_search(
    request: PFESearchRequest,
    search_service: SearchService = Depends(get_search_service),
    current_user: dict = Depends(get_current_user)
):
    result = await search_service.hybrid_search(
        query=request.query,
        limit=request.limit,
        filters=request.filters
    )
    return result