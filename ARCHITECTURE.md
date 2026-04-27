# 🏛️ Architecture Knowledge Hub for PFE (VIC - ISCAE / ESEN)

## 1. Vue Système Globale

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           KNOWLEDGE HUB FOR PFE                             │
│                    (Plateforme Intelligente de Gestion des PFE)            │
│                          Master VIC - ISCAE / ESEN                          │
└─────────────────────────────────────────────────────────────────────────────┘

                                    │
                    ┌───────────────┴───────────────┐
                    │                           │
            ┌───────▼───────┐           ┌───────▼───────┐
            │   FRONTEND    │           │    BACKEND    │
            │  Next.js 14   │◄─────────►│   FastAPI     │
            │   (TypeScript)│           │   (Python)   │
            └───────────────┘           └──────┬───────┘
                                              │
                    ┌─────────────────────────┼─────────────────────────┐
                    │                         │                         │
            ┌───────▼───────┐         ┌───────▼───────┐         ┌───────▼───────┐
            │   SUPABASE    │         │    OLLAMA      │         │   SERVICES    │
            │  (Existant)  │         │  (IA Locale)   │         │   (PDF, AI)   │
            │              │         │               │         │               │
            │ • PostgreSQL │         │ • Embeddings  │         │ • PDF Parser  │
            │ • Auth       │         │ • LLM Local    │         │ • Text Extract│
            │ • Storage    │         │ • RAG Pipeline│         │ • Chunking    │
            │ • pgvector   │         │               │         │ • Summarizer  │
            └───────────────┘         └───────────────┘         └───────────────┘
```

## 2. Architecture des Données

### 2.1 Modèle de Base de Données (Supabase PostgreSQL)

```sql
-- Tables principales (à créer dans Supabase existant)

-- Domaine VIC
CREATE TYPE domaine_vic AS ENUM (
    'intelligence_competitive',
    'veille_strategique',
    'management_information',
    'analyse_strategique',
    'intelligence_economique',
    'gestion_connaissance',
    'data_intelligence',
    'securite_informationnelle'
);

-- Rôles utilisateur
CREATE TYPE user_role AS ENUM ('etudiant', 'administrateur', 'visiteur');

-- Statut du PFE
CREATE TYPE pfe_status AS ENUM ('en_attente', 'en_traitement', 'complete', 'erreur');

-- Table: pfe_documents
CREATE TABLE pfe_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    titre TEXT NOT NULL,
    auteur TEXT NOT NULL,
    email_auteur TEXT,
    annee INTEGER NOT NULL CHECK (annee BETWEEN 2014 AND 2026),
    institution TEXT NOT NULL CHECK (institution IN ('ISCAE', 'ESEN')),
    domaine_vic domaine_vic NOT NULL,
    mots_cles TEXT[],
    resume TEXT,
    methodology TEXT,
    file_path TEXT,
    file_size BIGINT,
    status pfe_status DEFAULT 'en_attente',
    embedding_id UUID,
    created_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table: pfe_embeddings (pgvector)
CREATE TABLE pfe_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pfe_id UUID REFERENCES pfe_documents(id) ON DELETE CASCADE,
    embedding VECTOR(1536),
    model_used TEXT DEFAULT 'mxbai-embed-large',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table: user_profiles
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name TEXT,
    role user_role DEFAULT 'visiteur',
    institution TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table: analytics_events
CREATE TABLE analytics_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type TEXT NOT NULL,
    event_data JSONB,
    user_id UUID REFERENCES auth.users(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index pgvector pour recherche sémantique
CREATE INDEX pfe_embeddings_idx ON pfe_embeddings USING ivfflat (embedding vector_cosine_ops);

-- Index pour performance
CREATE INDEX pfe_annee_idx ON pfe_documents(annee);
CREATE INDEX pfe_domaine_idx ON pfe_documents(domaine_vic);
CREATE INDEX pfe_institution_idx ON pfe_documents(institution);
```

### 2.2 Storage Supabase

```
bucket: pfe-documents/
├── {user_id}/
│   ├── {pfe_id}.pdf
│   └── thumbnails/
└── public/
    └── master-vic/
```

## 3. Architecture Backend (FastAPI)

### 3.1 Structure des Modules

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # Entry point FastAPI
│   ├── config.py                  # Configuration
│   ├── deps.py                    # Dependencies injection
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py            # Supabase auth integration
│   │   │   ├── pfe.py             # CRUD PFE
│   │   │   ├── search.py          # Recherche full/semantic
│   │   │   ├── analytics.py       # Analytics endpoints
│   │   │   ├── ai.py              # AI pipeline endpoints
│   │   │   └── master_vic.py      # Master VIC info
│   │   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── security.py            # JWT/Supabase auth
│   │   └── supabase.py            # Supabase client
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── pfe.py                 # PFE schemas
│   │   ├── user.py                # User schemas
│   │   ├── analytics.py           # Analytics schemas
│   │   └── ai.py                  # AI schemas
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── supabase_service.py    # DB operations
│   │   ├── storage_service.py     # File storage
│   │   ├── document_service.py   # PDF processing
│   │   ├── ai_service.py          # Ollama integration
│   │   ├── search_service.py       # PostgreSQL + pgvector
│   │   └── analytics_service.py  # Analytics
│   │
│   └── utils/
│       ├── __init__.py
│       ├── pdf_extractor.py      # PDF text extraction
│       ├── text_chunker.py       # Text chunking
│       └── helpers.py            # Helpers
│
├── requirements.txt
├── Dockerfile
└── .env.example
```

### 3.2 Pipeline IA (Ollama)

```python
# Flow: Upload PFE → Extract → Embed → Store → Search

1. Upload PDF
      ↓
2. Extract Text (PyMuPDF)
      ↓
3. Generate Summary (Ollama/llama3)
      ↓
4. Extract Keywords (Ollama)
      ↓
5. Classify Domain (Ollama)
      ↓
6. Generate Embeddings (Ollama/mxbai-embed-large)
      ↓
7. Store in pgvector
      ↓
8. Search/Retrieve ready
```

## 4. Architecture Frontend (Next.js)

### 4.1 Structure des Pages

```
frontend/
├── app/
│   ├── layout.tsx                # Root layout
│   ├── page.tsx                  # Landing page
│   ├── globals.css
│   │
│   ├── (auth)/
│   │   ├── login/
│   │   │   └── page.tsx
│   │   └── register/
│   │       └── page.tsx
│   │
│   ├── (dashboard)/
│   │   ├── layout.tsx            # Dashboard layout
│   │   ├── page.tsx              # Analytics dashboard
│   │   │
│   │   ├── pfe/
│   │   │   ├── page.tsx          # List PFE
│   │   │   ├── [id]/
│   │   │   │   └── page.tsx       # Detail PFE
│   │   │   └── upload/
│   │   │       └── page.tsx       # Upload PFE
│   │   │
│   │   ├── search/
│   │   │   ├── page.tsx          # Search interface
│   │   │   └── result/
│   │   │       └── page.tsx
│   │   │
│   │   ├── analytics/
│   │   │   └── page.tsx          # Analytics
│   │   │
│   │   └── master-vic/
│   │       └── page.tsx          # Master VIC info
│   │
│   └── api/
│       └── [...routes]/
│           └── route.ts          # API routes
│
├── components/
│   ├── ui/                       # Shadcn UI components
│   ├── layout/
│   │   ├── Navbar.tsx
│   │   ├── Sidebar.tsx
│   │   └── Footer.tsx
│   ├── pfe/
│   │   ├── PFECard.tsx
│   │   ├── PFEUpload.tsx
│   │   └── PFEList.tsx
│   ├── search/
│   │   ├── SearchBar.tsx
│   │   └── SearchResults.tsx
│   ├── analytics/
│   │   ├── Charts.tsx
│   │   └── Stats.tsx
│   ├── master-vic/
│   │   ├── Timeline.tsx
│   │   └── InfoCards.tsx
│   └── auth/
│       ├── AuthGuard.tsx
│       └── LoginForm.tsx
│
├── lib/
│   ├── supabase.ts               # Supabase client
│   ├── ollama.ts                 # Ollama client
│   └── utils.ts
│
├── hooks/
│   ├── useAuth.ts
│   ├── usePFE.ts
│   └── useSearch.ts
│
├── store/
│   └── auth-store.ts
│
├── types/
│   ├── pfe.ts
│   ├── user.ts
│   └── analytics.ts
│
├── public/
│   └── images/
│       └── master-vic/
│
├── package.json
├── tailwind.config.ts
├── tsconfig.json
├── next.config.js
└── Dockerfile
```

## 5. Architecture Docker

### 5.1 Services Custom (docker-compose.yml)

```yaml
version: '3.8'

services:
  # Backend FastAPI
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - OLLAMA_BASE_URL=${OLLAMA_BASE_URL:-http://ollama:11434}
    depends_on:
      - ollama
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  # Frontend Next.js
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_SUPABASE_URL=${SUPABASE_URL}
      - NEXT_PUBLIC_SUPABASE_KEY=${SUPABASE_KEY}
    volumes:
      - ./frontend:/app
      - /app/node_modules
      - /app/.next
    command: npm run dev

  # Ollama (IA Locale)
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama-data:/root/.ollama
    deploy:
      resources:
        limits:
          memory: 16G
          cpus: '4'

volumes:
  ollama-data:
```

### 5.2 Services Existants (Déjà en place)

- Supabase (PostgreSQL + pgvector + Auth + Storage)
- pgAdmin

## 6. Architecture RAG (Retrieval Augmented Generation)

```
┌─────────────────────────────────────────────────────────────┐
│                        RAG PIPELINE                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Input: Sujet de recherche                                  │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────────┐                                        │
│  │ Query Embedding │ ◄── Ollama/mxbai-embed-large          │
│  └────────┬────────┘                                        │
│           │                                                 │
│           ▼                                                 │
│  ┌─────────────────┐                                        │
│  │ Vector Search   │ ◄── pgvector (cosine similarity)     │
│  │ (Top K = 5)     │                                        │
│  └────────┬────────┘                                        │
│           │                                                 │
│           ▼                                                 │
│  ┌─────────────────┐                                        │
│  │ Context + Docs  │ ◄── Retrieved PFE summaries          │
│  └────────┬────────┘                                        │
│           │                                                 │
│           ▼                                                 │
│  ┌─────────────────┐                                        │
│  │ LLM Generation  │ ◄── Ollama/llama3                      │
│  │ (State of Art)  │                                        │
│  └────────┬────────┘                                        │
│           │                                                 │
│           ▼                                                 │
│  Output: State of l'art généré                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 7. API Endpoints

### 7.1 Auth (Supabase)

- `POST /api/v1/auth/login` - Login avec Supabase
- `POST /api/v1/auth/register` - Register
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/logout` - Logout

### 7.2 PFE

- `POST /api/v1/pfe/upload` - Upload nouveau PFE
- `GET /api/v1/pfe` - Liste PFE (paginated)
- `GET /api/v1/pfe/{id}` - Détail PFE
- `PUT /api/v1/pfe/{id}` - Update PFE
- `DELETE /api/v1/pfe/{id}` - Delete PFE

### 7.3 Search

- `POST /api/v1/search/full-text` - Recherche PostgreSQL
- `POST /api/v1/search/semantic` - Recherche pgvector
- `POST /api/v1/search/hybrid` - Recherche hybride

### 7.4 AI / RAG

- `POST /api/v1/ai/generate-summary` - Générer résumé
- `POST /api/v1/ai/generate-keywords` - Générer mots-clés
- `POST /api/v1/ai/classify-domain` - Classifier domaine
- `POST /api/v1/ai/state-of-art` - Générer état de l'art (RAG)

### 7.5 Analytics

- `GET /api/v1/analytics/overview` - Vue d'ensemble
- `GET /api/v1/analytics/domains` - Répartition domaines
- `GET /api/v1/analytics/timeline` - Timeline évolution
- `GET /api/v1/analytics/emerging` - Sujets émergents
- `GET /api/v1/analytics/gaps` - Lacunes de recherche
- `GET /api/v1/analytics/comparison` - Comparison ISCAE/ESEN

### 7.6 Master VIC

- `GET /api/v1/master-vic/info` - Informations générales
- `GET /api/v1/master-vic/timeline` - Timeline
- `GET /api/v1/master-vic/competences` - Compétences
- `GET /api/v1/master-vic/debouches` - Débouchés

## 8. Security

### 8.1 Authentication

- Supabase Auth (JWT)
- Role-based access control (RBAC)
- Row Level Security (RLS) dans PostgreSQL

### 8.2 Authorization

```
Visiteur:
  - Voir pageMasterVIC
  - Recherche basique
  - Voir analytics globales

Étudiant:
  - Toutes les permissions Visiteur
  - Upload PFE (son propre)
  - Voir ses propres PFE
  - Recherche avancée

Administrateur:
  - Toutes les permissions Étudiant
  - CRUD tous les PFE
  - Analytics complète
  - Gestion utilisateurs
```

### 8.3 Data Security

- RLS sur toutes les tables
- Storage rules : uniquement propriétaire ou admin
- Rate limiting sur API endpoints

## 9. Scalabilité

### 9.1 Horizontal Scaling

- Backend stateless (FastAPI)
- Sessions dans Supabase
- Fichiers dans Supabase Storage

### 9.2 Vertical Scaling

- Ollama : GPUs additionnels
- PostgreSQL : scaling via Supabase Cloud

### 9.3 Caching

- Redis pour sessions (optionnel)
- CDN pour assets Next.js

## 10. Monitoring & Logs

- Health check `/health`
- Metrics `/metrics`
- Structured logging (JSON)
- Error tracking (Sentry)

---

## Conclusion

Cette architecture fournit une plateforme complète, scalable et prête pour la production qui :

1. ✅ S'intègre à l'infrastructure Supabase existante
2. ✅ Utilise Ollama pour l'IA locale
3. ✅ Offre recherche sémantique via pgvector
4. ✅ Dashboard analytics complet
5. ✅ Section Master VIC institutionnelle
6. ✅ Pipeline RAG pour état de l'art
7. ✅ Authentification via Supabase existant
8. ✅ Prête pour mémoire PFE Master VIC