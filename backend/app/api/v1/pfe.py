import uuid
import json
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.deps import get_current_user
from app.models.pfe import PFECreate, PFEUpdate, PFEResponse, UploadResponse, MessageResponse
from app.services.supabase_service import get_supabase_service, SupabaseService
from app.services.storage_service import get_storage_service, StorageService
from app.services.document_service import get_document_service, DocumentService
from app.services.ai_service import get_hybrid_ai_service, HybridAIService


router = APIRouter(prefix="/pfe", tags=["PFE"])


@router.post("/upload", response_model=UploadResponse)
async def upload_pfe(
    file: UploadFile = File(...),
    metadata: str = File(...),
    supabase_service: SupabaseService = Depends(get_supabase_service),
    storage_service: StorageService = Depends(get_storage_service),
    document_service: DocumentService = Depends(get_document_service),
    ai_service: HybridAIService = Depends(get_hybrid_ai_service),
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
    
    # Upload réussit - PAS de traitement IA automatique
    # L'IA peut être lancée manuellement plus tard
    
    return UploadResponse(
        pfe_id=pfe_id,
        message="PFE uploaded successfully.",
        status="uploaded"
    )


async def process_pfe_async(pfe_id, pdf_content, document_service, ai_service, supabase_service):
    try:
        await supabase_service.update_pfe_status(pfe_id, "en_traitement")
        
        text = await document_service.extract_text_from_pdf(pdf_content)
        
        if text:
            summary = await ai_service.generate_summary(text)
            keywords = await ai_service.generate_keywords(text)
            classification = await ai_service.classify_domain(text)
            problematic = await ai_service.generate_problematic(text)
            
            update_data = {}
            if summary:
                update_data["resume"] = summary
            if keywords:
                update_data["mots_cles"] = keywords
            if classification:
                update_data["domaine_vic"] = classification.get("domaine")
            if problematic:
                update_data["problematic"] = problematic
            
            if update_data:
                supabase_service.supabase.table("pfe_documents").update(update_data).eq("id", pfe_id).execute()
        
        embedding = await ai_service.generate_embedding(text[:2000] if text else "")
        if embedding:
            emb_list = embedding.tolist() if hasattr(embedding, 'tolist') else embedding
            supabase_service.supabase.table("pfe_embeddings").insert({
                "pfe_id": pfe_id,
                "embedding": str(emb_list),
                "model_used": "hybrid"
            }).execute()
        
        await supabase_service.update_pfe_status(pfe_id, "complete")
    except Exception as e:
        print(f"Processing error: {e}")
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