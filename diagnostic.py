#!/usr/bin/env python3
"""Script de diagnostic pour Knowledge Hub PFE"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

print("=" * 50)
print("DIAGNOSTIC - Knowledge Hub for PFE")
print("=" * 50)

errors = []

# Test 1: Config
print("\n[1] Test configuration...")
try:
    import app.config
    print("  ✓ Config OK")
except Exception as e:
    errors.append(f"Config: {e}")
    print(f"  ✗ Erreur: {e}")

# Test 2: Core Supabase
print("\n[2] Test Supabase client...")
try:
    import app.core.supabase_client as supabase_core
    print("  ✓ Supabase client OK")
except Exception as e:
    errors.append(f"Supabase: {e}")
    print(f"  ✗ Erreur: {e}")

# Test 3: Models
print("\n[3] Test models...")
try:
    import app.models.pfe
    import app.models.user
    import app.models.analytics
    import app.models.ai
    print("  ✓ Models OK")
except Exception as e:
    errors.append(f"Models: {e}")
    print(f"  ✗ Erreur: {e}")

# Test 4: Services
print("\n[4] Test services...")
try:
    import app.services.supabase_service
    import app.services.storage_service
    import app.services.document_service
    import app.services.ai_service
    import app.services.search_service
    import app.services.analytics_service
    print("  ✓ Services OK")
except Exception as e:
    errors.append(f"Services: {e}")
    print(f"  ✗ Erreur: {e}")

# Test 5: API
print("\n[5] Test API...")
try:
    from app.api.v1 import auth, pfe, search, analytics, ai, master_vic
    print("  ✓ API OK")
except Exception as e:
    errors.append(f"API: {e}")
    print(f"  ✗ Erreur: {e}")

# Test 6: Main
print("\n[6] Test main...")
try:
    import app.main
    print("  ✓ Main OK")
except Exception as e:
    errors.append(f"Main: {e}")
    print(f"  ✗ Erreur: {e}")

print("\n" + "=" * 50)
if errors:
    print(f"ERREURS: {len(errors)}")
    for e in errors:
        print(f"  - {e}")
else:
    print("TOUT OK - Prêt à démarrer!")
print("=" * 50)