from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import auth, pfe, search, analytics, ai, master_vic


app = FastAPI(
    title="Knowledge Hub for PFE API",
    description="API for managing PFE documents with AI-powered features",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(pfe.router, prefix="/api/v1")
app.include_router(search.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(ai.router, prefix="/api/v1")
app.include_router(master_vic.router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Knowledge Hub for PFE API"}


@app.get("/")
async def root():
    return {
        "name": "Knowledge Hub for PFE (VIC - ISCAE/ESEN)",
        "version": "1.0.0",
        "description": "Plateforme intelligente de gestion des PFE"
    }