from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from app.models.pfe import PFESearchRequest, SemanticSearchRequest, PFEResponseWithEmbedding, PFEResponse
from app.services.search_service import get_search_service, SearchService
from app.services.supabase_service import get_supabase_service, SupabaseService
from app.services.document_intelligence import DocumentIntelligenceEngine
from app.deps import get_current_user, get_optional_user


router = APIRouter(prefix="/search", tags=["Search"])

# Initialize Document Intelligence Engine
doc_intel = DocumentIntelligenceEngine()


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


@router.post("/global")
async def global_search(
    request: PFESearchRequest,
    supabase_service: SupabaseService = Depends(get_supabase_service),
    search_service: SearchService = Depends(get_search_service),
    current_user: dict = Depends(get_optional_user)
):
    """
    Global search across ALL PFE documents.
    Matches: title, abstract, keywords, extracted sections.
    Returns: list of relevant PFEs with highlighted snippets.
    """
    query = request.query
    limit = request.limit
    
    # 1. Get all PFEs from database (or filtered)
    filters = request.filters or {}
    all_pfes = await supabase_service.get_all_pfe(limit=1000, offset=0, filters=filters)
    
    # 2. Add searchable text field (title + resume + problematic + solutions)
    for pfe in all_pfes:
        pfe["search_text"] = " ".join([
            pfe.get("titre", ""),
            pfe.get("resume", "") or "",
            pfe.get("summary", "") or "",
            pfe.get("problematic", "") or "",
            pfe.get("solutions", "") or "",
            " ".join(pfe.get("mots_cles", []) or []),
            " ".join(pfe.get("keywords", []) or [])
        ])
    
    # 3. Rank using Document Intelligence Engine (TF-IDF + section matching)
    ranked_pfes = doc_intel.rank_search_results(query, all_pfes)
    
    # 4. Get top results with highlighted snippets
    top_results = ranked_pfes[:limit]
    
    results = []
    for pfe in top_results:
        if pfe.get("relevance_score", 0) == 0:
            continue
            
        # Extract relevant sections
        sections = {}
        if pfe.get("problematic"):
            sections["problematic"] = doc_intel.highlight_snippet(pfe["problematic"], query)
        if pfe.get("solutions"):
            sections["solution"] = doc_intel.highlight_snippet(pfe["solutions"], query)
        if pfe.get("resume"):
            sections["resume"] = doc_intel.highlight_snippet(pfe["resume"], query)
        if pfe.get("summary"):
            sections["summary"] = doc_intel.highlight_snippet(pfe["summary"], query)
        
        results.append({
            "pfe": pfe,
            "relevance_score": pfe.get("relevance_score", 0),
            "highlighted_sections": sections,
            "snippet": doc_intel.highlight_snippet(pfe.get("search_text", ""), query, snippet_length=300)
        })
    
    return {
        "results": results,
        "total": len(results),
        "query": query
    }
