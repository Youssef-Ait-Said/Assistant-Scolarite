"""Teste Chroma pour de vrai (dans un dossier temporaire), avec de faux embeddings : pas besoin de clé Gemini."""
import pytest
from langchain_core.embeddings import DeterministicFakeEmbedding

from app import config, store

FRAGMENTS = [
    {"id": "A-p1-structurel-0", "text": "Article 6 justification des absences", "file": "a.pdf",
     "reference": "REF-A", "type": "Règlement", "date": "2026-07-10", "version": "1.0",
     "statut": "En vigueur", "page": 1, "section": "Article 6", "strategie": "structurel"},
    {"id": "A-p1-structurel-1", "text": "Article 7 seuil d'absences", "file": "a.pdf",
     "reference": "REF-A", "type": "Règlement", "date": "2026-07-10", "version": "1.0",
     "statut": "En vigueur", "page": 1, "section": "Article 7", "strategie": "structurel"},
    {"id": "B-p1-structurel-0", "text": "Durée du PFE", "file": "b.pdf",
     "reference": "REF-B", "type": "Guide", "date": "2026-06-15", "version": "3.0",
     "statut": "En vigueur", "page": 1, "section": "5.3", "strategie": "structurel"},
]


@pytest.fixture(autouse=True)
def base_temporaire(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DB_DIR", tmp_path / "chroma_db")
    monkeypatch.setattr("langchain_google_genai.GoogleGenerativeAIEmbeddings",
                        lambda model=None: DeterministicFakeEmbedding(size=32))


def test_vers_documents():
    docs, ids = store.vers_documents(FRAGMENTS)
    assert ids[0] == "A-p1-structurel-0"
    assert docs[0].page_content == "Article 6 justification des absences"
    assert "text" not in docs[0].metadata


def test_ingestion_idempotente():
    assert store.ingerer(FRAGMENTS, rebuild=True) == 3
    assert store.ingerer(FRAGMENTS) == 3          # relancer ne crée pas de doublons
    assert store.nb_fragments() == 3


def test_lister_documents_regroupe_par_document():
    store.ingerer(FRAGMENTS, rebuild=True)
    docs = store.lister_documents()
    assert [d["reference"] for d in docs] == ["REF-A", "REF-B"]
    assert docs[0]["chunks"] == 2 and docs[1]["chunks"] == 1


def test_rechercher_score_et_filtre_par_type():
    store.ingerer(FRAGMENTS, rebuild=True)
    resultats = store.rechercher("Article 6 justification des absences", k=3)
    doc, score = resultats[0]
    assert doc.metadata["id"] == "A-p1-structurel-0"   # le texte identique est le plus proche
    assert score > 0.99
    seulement_guide = store.rechercher("absences", k=3, type_doc="Guide")
    assert [d.metadata["reference"] for d, _ in seulement_guide] == ["REF-B"]