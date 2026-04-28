from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from uuid import UUID
from app.models.ai import (
    SummaryResponse, KeywordsResponse, DomainClassificationResponse,
    StateOfArtResponse, EmbeddingResponse, ProcessingStatus, AIAnalysisResponse
)
from app.models.pfe import StateOfArtRequest
from app.services.ai_service import get_hybrid_ai_service, HybridAIService
from app.services.supabase_service import get_supabase_service, SupabaseService
from app.services.storage_service import get_storage_service, StorageService
from app.deps import get_current_user, get_optional_user


router = APIRouter(prefix="/ai", tags=["AI"])


@router.get("/test")
async def ai_test(
    ai_service: HybridAIService = Depends(get_hybrid_ai_service)
):
    """Test AI providers"""
    status = await ai_service.check_availability()
    
    test_prompt = "Dis 'OK' en français"
    answer = await ai_service._generate(test_prompt, max_tokens=10)
    
    return {
        "status": status,
        "test_prompt": test_prompt,
        "test_answer": answer,
        "success": bool(answer)
    }


@router.get("/status")
async def ai_status(
    ai_service: HybridAIService = Depends(get_hybrid_ai_service)
):
    """Vérifie le statut du service AI (local ou cloud)"""
    status = await ai_service.check_availability()
    return status


@router.post("/generate-summary")
async def generate_summary(
    pfe_id: UUID,
    ai_service: HybridAIService = Depends(get_hybrid_ai_service),
    supabase_service: SupabaseService = Depends(get_supabase_service),
    current_user: dict = Depends(get_current_user)
):
    pfe = await supabase_service.get_pfe(pfe_id)
    if not pfe:
        raise HTTPException(status_code=404, detail="PFE not found")
    
    text = pfe.get("resume") or pfe.get("mots_cles", [])
    if isinstance(text, list):
        text = " ".join(text)
    
    summary = await ai_service.generate_summary(text or "")
    
    if summary:
        await supabase_service.supabase.table("pfe_documents").update({
            "resume": summary
        }).eq("id", str(pfe_id)).execute()
    
    status = await ai_service.check_availability()
    return SummaryResponse(
        pfe_id=pfe_id,
        summary=summary or "No summary generated",
        model_used=status.get("active_model", "hybrid")
    )


@router.post("/generate-keywords")
async def generate_keywords(
    pfe_id: UUID,
    ai_service: HybridAIService = Depends(get_hybrid_ai_service),
    supabase_service: SupabaseService = Depends(get_supabase_service),
    current_user: dict = Depends(get_current_user)
):
    pfe = await supabase_service.get_pfe(pfe_id)
    if not pfe:
        raise HTTPException(status_code=404, detail="PFE not found")
    
    text = pfe.get("resume") or ""
    keywords = await ai_service.generate_keywords(text)
    
    if keywords:
        await supabase_service.supabase.table("pfe_documents").update({
            "mots_cles": keywords
        }).eq("id", str(pfe_id)).execute()
    
    status = await ai_service.check_availability()
    return KeywordsResponse(
        pfe_id=pfe_id,
        keywords=keywords or [],
        model_used=status.get("active_model", "hybrid")
    )


@router.post("/classify-domain")
async def classify_domain(
    pfe_id: UUID,
    ai_service: HybridAIService = Depends(get_hybrid_ai_service),
    supabase_service: SupabaseService = Depends(get_supabase_service),
    current_user: dict = Depends(get_current_user)
):
    pfe = await supabase_service.get_pfe(pfe_id)
    if not pfe:
        raise HTTPException(status_code=404, detail="PFE not found")
    
    text = f"{pfe.get('titre', '')} {pfe.get('resume', '')}"
    classification = await ai_service.classify_domain(text)
    
    if classification:
        await supabase_service.supabase.table("pfe_documents").update({
            "domaine_vic": classification.get("domaine")
        }).eq("id", str(pfe_id)).execute()
    
    status = await ai_service.check_availability()
    return DomainClassificationResponse(
        pfe_id=pfe_id,
        suggested_domain=classification.get("domaine", "unknown") if classification else "unknown",
        confidence=classification.get("confiance", 0.0) if classification else 0.0,
        model_used=status.get("active_model", "hybrid")
    )


@router.post("/state-of-art")
async def generate_state_of_art(
    request: StateOfArtRequest,
    ai_service: HybridAIService = Depends(get_hybrid_ai_service),
    supabase_service: SupabaseService = Depends(get_supabase_service),
    current_user: dict = Depends(get_current_user)
):
    filters = {}
    if request.annee_debut:
        filters["annee"] = request.annee_debut
    if request.institution:
        filters["institution"] = request.institution.value
    
    pfe_list = await supabase_service.get_all_pfe(20, 0, filters if filters else None)
    
    if not pfe_list:
        raise HTTPException(status_code=404, detail="No PFE found for analysis")
    
    synthesis = await ai_service.generate_state_of_art(request.sujet, pfe_list)
    concepts = await ai_service.extract_concepts_cles(synthesis or "") if synthesis else []
    
    sources = [
        {
            "id": pfe.get("id"),
            "titre": pfe.get("titre"),
            "auteur": pfe.get("auteur"),
            "annee": pfe.get("annee")
        }
        for pfe in pfe_list[:5]
    ]
    
    status = await ai_service.check_availability()
    return StateOfArtResponse(
        sujet=request.sujet,
        synthesis=synthesis or "No synthesis generated",
        concepts_cles=concepts or [],
        sources=sources,
        model_used=status.get("active_model", "hybrid")
    )


@router.post("/analyze-pfe")
async def analyze_pfe_post(
    pfe_id: UUID,
    question: str,
    ai_service: HybridAIService = Depends(get_hybrid_ai_service),
    supabase_service: SupabaseService = Depends(get_supabase_service),
    storage_service: StorageService = Depends(get_storage_service),
    current_user: dict = Depends(get_optional_user)
):
    return await analyze_pfe_handler(pfe_id, question, ai_service, supabase_service, storage_service)


@router.get("/analyze-pfe")
async def analyze_pfe_get(
    pfe_id: str,
    question: str = "Donne-moi un résumé du PFE",
    ai_service: HybridAIService = Depends(get_hybrid_ai_service),
    supabase_service: SupabaseService = Depends(get_supabase_service),
    storage_service: StorageService = Depends(get_storage_service)
):
    return await analyze_pfe_handler(UUID(pfe_id), question, ai_service, supabase_service, storage_service)


async def analyze_pfe_handler(
    pfe_id: UUID,
    question: str,
    ai_service: HybridAIService,
    supabase_service: SupabaseService,
    storage_service: StorageService
):
    pfe = await supabase_service.get_pfe(str(pfe_id))
    if not pfe:
        raise HTTPException(status_code=404, detail="PFE not found")
    
    content_parts = []
    
    if pfe.get("resume"):
        content_parts.append(f"Résumé existant: {pfe['resume']}")
    if pfe.get("mots_cles"):
        content_parts.append(f"Mots-clés: {', '.join(pfe['mots_cles']) if isinstance(pfe['mots_cles'], list) else pfe['mots_cles']}")
    if pfe.get("methodology"):
        content_parts.append(f"Méthodologie: {pfe['methodology']}")
    
    content_text = "\n\n".join(content_parts) if content_parts else "Pas de contenu dans la base"
    
    if pfe.get("file_path"):
        try:
            file_content = await storage_service.read_file(pfe["file_path"])
            if file_content:
                from app.services.document_service import get_document_service, DocumentService
                doc_service = get_document_service()
                text = await doc_service.extract_text_from_pdf(file_content)
                if text:
                    if len(text) > 5000:
                        content_text += f"\n\n--- Extrait du document ---\n{text[:5000]}..."
                    else:
                        content_text += f"\n\n--- Contenu du document ---\n{text}"
                else:
                    content_text += f"\n\n[Document PDF présent mais extraction échouée]"
        except Exception as e:
            print(f"Error reading file: {e}")
            content_text += f"\n\n[Erreur lecture document: {str(e)}]"
    
    prompt = f"""Tu es un expert académique. Analyse ce PFE (Projet de Fin d'Études) et réponds à la question en français.
Réponds uniquement avec le texte brut, sans balises dethink, sans asterisques (**), sans formatage Markdown.
Sois concis et précis.

Informations du PFE:
- Titre: {pfe.get('titre', 'N/A')}
- Auteur: {pfe.get('auteur', 'N/A')}  
- Année: {pfe.get('annee', 'N/A')}
- Domaine: {pfe.get('domaine_vic', 'N/A')}

{content_text}

Question: {question}

Réponse:"""

    answer = await ai_service._generate(prompt, max_tokens=1500)
    
    status = await ai_service.check_availability()
    
    return {
        "pfe_id": pfe_id,
        "question": question,
        "answer": answer or "Erreur: tous les fournisseurs IA ont échoué. Vérifiez LM Studio, DeepSeek ou Gemini.",
        "model_used": status.get("active_model", "unknown"),
        "pfe_title": pfe.get("titre")
    }


@router.get("/health")
async def ai_health_check(
    ai_service: HybridAIService = Depends(get_hybrid_ai_service)
):
    status = await ai_service.check_availability()
    return {
        "status": "healthy" if status["local_available"] or status["use_cloud"] else "unhealthy",
        "ollama_available": status["local_available"],
        "use_cloud": status["use_cloud"],
        "provider": status.get("cloud_provider"),
        "active_model": status.get("active_model")
    }


@router.get("/status")
async def ai_status(
    ai_service: HybridAIService = Depends(get_hybrid_ai_service)
):
    status = await ai_service.check_availability()
    return status


@router.post("/generate-summary")
async def generate_summary(
    pfe_id: UUID,
    ai_service: HybridAIService = Depends(get_hybrid_ai_service),
    supabase_service: SupabaseService = Depends(get_supabase_service),
    current_user: dict = Depends(get_current_user)
):
    pfe = await supabase_service.get_pfe(str(pfe_id))
    if not pfe:
        raise HTTPException(status_code=404, detail="PFE not found")
    
    text = pfe.get("resume") or ""
    if not text:
        text = pfe.get("mots_cles", [])
        if isinstance(text, list):
            text = " ".join(text)
    
    summary = await ai_service.generate_summary(text or "", max_length=500)
    
    if summary:
        await supabase_service.supabase.table("pfe_documents").update({
            "resume": summary
        }).eq("id", str(pfe_id)).execute()
    
    status = await ai_service.check_availability()
    return {
        "pfe_id": pfe_id,
        "summary": summary or "Aucun résumé généré",
        "model_used": status.get("active_model", "hybrid")
    }


@router.post("/generate-from-pdf")
async def generate_from_pdf(
    file: UploadFile = File(...),
    ai_service: HybridAIService = Depends(get_hybrid_ai_service)
):
    """Génère résumé, mots-clés et problématique depuis un PDF uploadé"""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Seuls les fichiers PDF sont acceptés")
    
    try:
        pdf_content = await file.read()
        
        from app.services.document_service import get_document_service, DocumentService
        doc_service = get_document_service()
        
        text = await doc_service.extract_text_from_pdf(pdf_content)
        if not text:
            raise HTTPException(status_code=400, detail="Impossible d'extraire le texte du PDF")
        
        text_excerpt = text[:8000]
        
        prompt = f"""Analyse ce mémoire PFE et extrais les informations suivantes en format JSON:
{{
  "resume": "Résumé en 3-4 phrases (200-300 mots)",
  "mots_cles": ["mot1", "mot2", "mot3", "mot4", "mot5"],
  "problematic": "La problématique principale en une phrase"
}}

Texte du PFE:
{text_excerpt}

JSON:"""
        
        response = await ai_service._generate(prompt, max_tokens=2000)
        
        if not response:
            return {"error": "Impossible de générer l'analyse"}
        
        import json
        import re
        try:
            data = json.loads(response)
        except json.JSONDecodeError:
            json_match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group())
                except:
                    data = {"resume": response[:500], "mots_cles": [], "problematic": ""}
            else:
                data = {"resume": response[:500], "mots_cles": [], "problematic": ""}
        
        status = await ai_service.check_availability()
        return {
            "resume": data.get("resume", ""),
            "mots_cles": data.get("mots_cles", []),
            "problematic": data.get("problematic", ""),
            "model_used": status.get("active_model", "hybrid")
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erreur generate-from-pdf: {e}")
        raise HTTPException(status_code=500, detail=str(e))