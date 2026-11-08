"""API FastAPI. Toutes les routes sont préfixées par /api ; la documentation est sur /docs."""
from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app import config, rag, store
from app.chunking import decouper
from app.extract import extraire_corpus
from app.models import (AskRequest, AskResponse, DocumentInfo, HealthResponse, IngestRequest, 
                        IngestResponse, SearchRequest, SearchResponse)

app = FastAPI(title="Assistant Scolrité - EIH", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter(prefix="/api")

ERREUR_BASE = "La base vectorielle est indisponible"


@router.get("/health", response_model=HealthResponse)
def health():
    try:
        return {"status" : "ok", "chunks" : store.nb_fragments()}
    except Exception:
        raise HTTPException(status_code=503, detail=ERREUR_BASE)


@router.post("/ingest", response_model=IngestResponse)
def ingest(req : IngestRequest):
    """(Ré)indexation. Relancer ne crée jamais de doublons (ids stables)."""
    docs = extraire_corpus()
    if not docs:
        raise HTTPException(status_code=422, detail=f"Aucun PDF trouvé dans {config.CORPUS_DIR}")
    fragments = decouper(docs, req.strategie, req.taille, req.chevauchement)
    try:
        total = store.ingerer(fragments, rebuild=req.reset)
    except Exception:
        raise HTTPException(status_code=503, detail=ERREUR_BASE)
    return {"strategie" : req.strategie, "documents" : len(docs), "chunks_indexes" : total}


@router.get("/documents", response_model=list[DocumentInfo])
def documents():
    try:
        return store.lister_documents()
    except Exception:
        raise HTTPException(status_code=503, detail=ERREUR_BASE)


@router.post("/search", response_model=SearchResponse)
def search(req : SearchRequest):
    """Recherche seule, sans LLM : Fragments bruts et scores"""
    try:
        resultats = store.rechercher(req.question, req.top_k, req.filters.type)
    except Exception:
        raise HTTPException(status_code=503, detail=ERREUR_BASE)
    return {"results" : [rag.vers_source(i, doc, score, complet=True)
                           for i, (doc, score) in enumerate(resultats, start=1)]
            }


@router.post("/ask", response_model=AskResponse)
def ask(req : AskRequest):
    try:
        return rag.repondre(req.question, req.top_k, req.filters.type)
    except rag.LLMError:
        raise HTTPException(status_code=502, detail="Le modèle de langage ne répond pas.")
    except Exception:
        raise HTTPException(status_code=503, detail=ERREUR_BASE)


app.include_router(router)