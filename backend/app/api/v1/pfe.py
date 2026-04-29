import uuid
import json
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.deps import get_current_user
from app.models.pfe import PFECreate, PFEUpdate, PFEResponse, UploadResponse, MessageResponse
from app.services.supabase_service import get_supabase_service, SupabaseService
from app.services.storage_service import get_storage_service, StorageService
from app.services.document_service import get_document_service, DocumentService
from app.services.ai_analysis_engine import AIAnalysisEngine
from app.services.gemini_service import analyze_text as gemini_analyze


router = APIRouter(prefix="/pfe", tags=["PFE"])


@router.post("/upload", response_model=UploadResponse)
async def upload_pfe(
    file: UploadFile = File(...),
    metadata: str = File(...),
    supabase_service: SupabaseService = Depends(get_supabase_service),
    storage_service: StorageService = Depends(get_storage_service),
    document_service: DocumentService = Depends(get_document_service),
    current_user: dict = Depends(get_current_user)
):
    try:
        meta = json.loads(metadata)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid metadata format")
    
    pfe_id = uuid.uuid4()
    pdf_content = await file.read()
    file_size = len(pdf_content)
    
    try:
        file_path = await storage_service.upload_file(
            file_content=pdf_content,
            file_name=file.filename or f"{pfe_id}.pdf",
            user_id=current_user.get("id", "anonymous"),
            pfe_id=str(pfe_id)
        )
    except Exception as e:
        print(f"Storage upload error: {e}")
        file_path = None
    
    try:
        pfe_dict = PFECreate(**meta).model_dump()
    except Exception as e:
        print(f"PFE validation error: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid metadata: {str(e)}")
    pfe_dict["id"] = str(pfe_id)
    pfe_dict["file_path"] = file_path or ""
    pfe_dict["file_size"] = file_size
    pfe_dict["status"] = "en_attente"
    pfe_dict["created_by"] = current_user.get("id", "")
    
    try:
        result = supabase_service.supabase.table("pfe_documents").insert(pfe_dict).execute()
        print(f"Insert result: {result}")
        if not result.get("data"):
            raise HTTPException(status_code=500, detail="Failed to create PFE record")
    except Exception as e:
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    return UploadResponse(
        pfe_id=pfe_id,
        message="PFE uploaded successfully. Use POST /api/v1/pfe/{pfe_id}/analyze to start AI analysis.",
        status="en_attente"
    )


async def process_pfe_with_engine(pfe_id, pdf_content, document_service, supabase_service):
    """Process PFE using the new AI Analysis Engine with fallback chain"""
    from app.services.ai_analysis_engine import AIAnalysisEngine
    engine = AIAnalysisEngine()
    
    try:
        await supabase_service.update_pfe_status(pfe_id, "en_traitement")
        
        # Extract text from PDF
        text = await document_service.extract_text_from_pdf(pdf_content)
        if not text:
            print(f"[Engine] No text extracted from PDF")
            await supabase_service.update_pfe_status(pfe_id, "erreur")
            return
            
        text_clean = document_service.clean_text(text)
        
        # Run AI Analysis Engine (Gemini → DeepSeek → LM Studio)
        import asyncio
        analysis = await engine.analyze_pfe(text_clean, max_summary_words=150)
        
        update_data = {}
        if analysis:
            print(f"[Engine] Analysis complete")
            if analysis.get("summary"):
                update_data["summary"] = analysis["summary"]
                print(f"[Engine] Summary: {len(analysis['summary'])} chars")
            if analysis.get("keywords"):
                update_data["keywords"] = analysis["keywords"] if isinstance(analysis["keywords"], list) else []
                print(f"[Engine] Keywords: {len(analysis['keywords'])} items")
            if analysis.get("problematic"):
                update_data["problematic"] = analysis["problematic"]
            if analysis.get("solution"):
                update_data["solutions"] = analysis["solution"]
            if analysis.get("state_of_art"):
                update_data["state_of_art"] = analysis["state_of_art"]
        else:
            print(f"[Engine] AI analysis failed, falling back to individual services")
            # Fallback to individual Gemini service
            gemini_result = await asyncio.to_thread(gemini_analyze, text_clean)
            if gemini_result:
                update_data["summary"] = gemini_result.get("summary")
                update_data["keywords"] = gemini_result.get("keywords")
        
        # Also run existing hybrid AI service for resume, methodology, etc.
        from app.services.ai_service import get_hybrid_ai_service
        ai_service = get_hybrid_ai_service()
        
        import asyncio
        summary_task = ai_service.generate_summary(text_clean)
        keywords_task = ai_service.generate_keywords(text_clean)
        problematic_task = ai_service.generate_problematic(text_clean)
        methodology_task = ai_service.extract_methodology(text_clean)
        solutions_task = ai_service.generate_solutions(text_clean)
        
        summary, keywords, problematic, methodology, solutions = await asyncio.gather(
            summary_task, keywords_task, problematic_task, 
            methodology_task, solutions_task, return_exceptions=True
        )
        
        if summary and not isinstance(summary, Exception):
            update_data["resume"] = summary
        if keywords and not isinstance(keywords, Exception) and "keywords" not in update_data:
            update_data["mots_cles"] = keywords if isinstance(keywords, list) else []
        if problematic and not isinstance(problematic, Exception) and "problematic" not in update_data:
            update_data["problematic"] = problematic
        if methodology and not isinstance(methodology, Exception):
            update_data["methodology"] = methodology
        if solutions and not isinstance(solutions, Exception) and "solutions" not in update_data:
            update_data["solutions"] = solutions
        
        # State of art
        try:
            docs = supabase_service.supabase.table("pfe_documents").select("titre,auteur,annee,resume").limit(5).execute()
            if docs.data:
                state_of_art = await ai_service.generate_state_of_art(text_clean[:500], docs.data)
                if state_of_art and "state_of_art" not in update_data:
                    update_data["state_of_art"] = state_of_art
        except Exception as e:
            print(f"State of art error: {e}")
        
        if update_data:
            supabase_service.supabase.table("pfe_documents").update(update_data).eq("id", pfe_id).execute()
            print(f"[Engine] Updated PFE {pfe_id} with {len(update_data)} fields")
        
        # Embedding
        try:
            embedding = await ai_service.generate_embedding(text_clean[:2000])
            if embedding:
                emb_list = embedding.tolist() if hasattr(embedding, 'tolist') else embedding
                supabase_service.supabase.table("pfe_embeddings").insert({
                    "pfe_id": pfe_id,
                    "embedding": str(emb_list),
                    "model_used": "hybrid"
                }).execute()
        except Exception as e:
            print(f"Embedding save error: {e}")
        
        await supabase_service.update_pfe_status(pfe_id, "complete")
        print(f"[Engine] Processing PFE {pfe_id} completed successfully")
        
    except Exception as e:
        print(f"Processing error: {e}")
        import traceback
        traceback.print_exc()
        await supabase_service.update_pfe_status(pfe_id, "erreur")


@router.get("", response_model=list[PFEResponse])
async def list_pfe(
    limit: int = 50,
    offset: int = 0,
    annee: int = None,
    domaine_vic: str = None,
    institution: str = None,
    supabase_service: SupabaseService = Depends(get_supabase_service),
    current_user: dict = Depends(get_current_user)
):
    filters = {}
    if annee:
        filters["annee"] = annee
    if domaine_vic:
        filters["domaine_vic"] = domaine_vic
    if institution:
        filters["institution"] = institution
    
    pfe_list = await supabase_service.get_all_pfe(limit, offset, filters if filters else None)
    return pfe_list


@router.get("/{pfe_id}", response_model=PFEResponse)
async def get_pfe(
    pfe_id: UUID,
    supabase_service: SupabaseService = Depends(get_supabase_service),
    storage_service: StorageService = Depends(get_storage_service)
):
    pfe = await supabase_service.get_pfe(str(pfe_id))
    if not pfe:
        raise HTTPException(status_code=404, detail="PFE not found")
    
    if pfe.get("file_path"):
        try:
            file_url = await storage_service.get_file_url(pfe["file_path"])
            if file_url:
                pfe["file_url"] = file_url
        except Exception as e:
            print(f"Error getting file URL: {e}")
    
    return pfe


@router.put("/{pfe_id}", response_model=PFEResponse)
async def update_pfe(
    pfe_id: UUID,
    pfe_data: PFEUpdate,
    supabase_service: SupabaseService = Depends(get_supabase_service),
    current_user: dict = Depends(get_current_user)
):
    existing = await supabase_service.get_pfe(str(pfe_id))
    if not existing:
        raise HTTPException(status_code=404, detail="PFE not found")
    
    updated = await supabase_service.update_pfe(str(pfe_id), pfe_data.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=500, detail="Failed to update PFE")
    return updated


@router.delete("/{pfe_id}", response_model=MessageResponse)
async def delete_pfe(
    pfe_id: UUID,
    supabase_service: SupabaseService = Depends(get_supabase_service),
    storage_service: StorageService = Depends(get_storage_service),
    current_user: dict = Depends(get_current_user)
):
    existing = await supabase_service.get_pfe(str(pfe_id))
    if not existing:
        raise HTTPException(status_code=404, detail="PFE not found")
    
    if existing.get("file_path"):
        await storage_service.delete_file(existing["file_path"])
    
    deleted = await supabase_service.delete_pfe(str(pfe_id))
    if not deleted:
        raise HTTPException(status_code=500, detail="Failed to delete PFE")
    
    return MessageResponse(message="PFE deleted successfully")


@router.post("/{pfe_id}/analyze", response_model=MessageResponse)
async def analyze_pfe_with_ai(
    pfe_id: UUID,
    supabase_service: SupabaseService = Depends(get_supabase_service),
    storage_service: StorageService = Depends(get_storage_service),
    document_service: DocumentService = Depends(get_document_service),
    current_user: dict = Depends(get_current_user)
):
    """Manually trigger AI analysis for a PFE (LM Studio Qwen → Gemini → DeepSeek)"""
    pfe = await supabase_service.get_pfe(str(pfe_id))
    if not pfe:
        raise HTTPException(status_code=404, detail="PFE not found")
    
    if not pfe.get("file_path"):
        raise HTTPException(status_code=400, detail="No file attached to this PFE")
    
    try:
        # Download PDF from storage
        file_content = await storage_service.download_file(pfe["file_path"])
        if not file_content:
            raise HTTPException(status_code=500, detail="Failed to download PDF")
        
        # Extract text
        text = await document_service.extract_text_from_pdf(file_content)
        if not text:
            raise HTTPException(status_code=500, detail="Failed to extract text from PDF")
        
        text_clean = document_service.clean_text(text)
        
        # Run AI analysis with engine (Qwen first)
        engine = AIAnalysisEngine()
        result = await engine.analyze_pfe(text_clean)
        
        if not result:
            raise HTTPException(status_code=500, detail="AI analysis failed - all providers unavailable")
        
        # Update database
        update_data = {}
        if result.get("summary"):
            update_data["resume"] = result.get("summary")
        if result.get("keywords"):
            update_data["mots_cles"] = result.get("keywords") if isinstance(result.get("keywords"), list) else []
        if result.get("problematic"):
            update_data["problematic"] = result.get("problematic")
        
        if update_data:
            supabase_service.supabase.table("pfe_documents").update(update_data).eq("id", str(pfe_id)).execute()
        
        return MessageResponse(message=f"Analyse IA terminée avec succès via {result.get('provider', 'AI')}")
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")