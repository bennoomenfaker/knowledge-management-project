#!/usr/bin/env python3
"""
Script de test pour vérifier la connectivité AI Hybride
Lance ce script pour tester Ollama et API cloud sans démarrer le projet complet
"""
import asyncio
import os
import sys

# Ajoute le chemin backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def test_hybrid_ai():
    print("=" * 60)
    print("TEST HYBRIDE AI - Knowledge Hub for PFE")
    print("=" * 60)
    
    # Import après path setup
    from app.services.ai_service import get_hybrid_ai_service
    
    ai = get_hybrid_ai_service()
    
    print("\n[1] Vérification disponibilité...")
    status = await ai.check_availability()
    print(f"  - Ollama local: {'✓' if status['local_available'] else '✗'}")
    print(f"  - Modèles locaux: {status['local_models']}")
    print(f"  - Mode cloud: {'✓' if status['use_cloud'] else '✗'}")
    print(f"  - Provider cloud: {status['cloud_provider']}")
    print(f"  - Modèle actif: {status['active_model']}")
    
    if not status['local_available'] and not ai.use_cloud:
        print("\n⚠️ ATTENTION: Ollama non disponible et cloud non configuré!")
        print("   Configurez USE_CLOUD_API=true et une clé API dans .env")
    
    print("\n[2] Test génération résumé...")
    test_text = "La veille stratégique est un processus continu de collecte, d'analyse et de diffusion d'informations sur l'environnement concurrentiel."
    summary = await ai.generate_summary(test_text, max_length=200)
    print(f"  Résumé: {summary[:100] if summary else 'ÉCHOUÉ'}...")
    
    print("\n[3] Test classification domaine...")
    classification = await ai.classify_domain(test_text)
    print(f"  Domaine: {classification}")
    
    print("\n[4] Test embeddings...")
    embedding = await ai.generate_embedding("intelligence compétitive")
    print(f"  Embedding: {len(embedding) if embedding else 0} dimensions")
    
    print("\n[5] Vérification santé Ollama...")
    healthy = await ai.check_ollama_health()
    print(f"  Ollama healthy: {'✓' if healthy else '✗'}")
    
    print("\n" + "=" * 60)
    print("TEST TERMINÉ")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_hybrid_ai())