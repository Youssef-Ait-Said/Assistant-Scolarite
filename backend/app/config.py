import os 
from pathlib import Path
from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BACKEND_DIR.parent

load_dotenv(ROOT_DIR /".env")

CORPUS_DIR = Path(os.getenv("CORPUS_DIR", ROOT_DIR / "data" / "corpus"))
DB_DIR = Path(os.getenv("DB_DIR", BACKEND_DIR / "chroma_db"))
COLLECTION_NAME = "scolarite"

# Les deux modeles , embeddings + chat
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
CHAT_MODEL = os.getenv("CHAT_MODEL")

SEUIL_SCORE = float(os.getenv("SEUIL_SCORE", "0.65"))  #Similarite minimale pour appeler le LLM
TOP_K = int(os.getenv("TOP_K", "5"))
STRATEGIE = os.getenv("STRATEGIE", "structurel") #fixe ou structurel
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))

# Adresses autorisées à appeler l'API (le frontend)
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS", "http://localhost:4200,http://localhost:5173"
).split(",")