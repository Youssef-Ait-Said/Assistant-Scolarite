from fastapi.testclient import TestClient

from app import rag, store
from app.main import app

client = TestClient(app)


def test_question_vide_donne_422():
    assert client.post("/api/search", json={"question": "   "}).status_code == 422
    assert client.post("/api/ask", json={"question": ""}).status_code == 422


def test_ingest_parametres_invalides_donne_422():
    r = client.post("/api/ingest", json={"strategie": "fixe", "taille": 500, "chevauchement": 600})
    assert r.status_code == 422


def test_ask_llm_en_panne_donne_502(monkeypatch):
    def en_panne(*a, **k):
        raise rag.LLMError("down")
    monkeypatch.setattr(rag, "repondre", en_panne)
    assert client.post("/api/ask", json={"question": "Bonjour ?"}).status_code == 502


def test_health_base_indisponible_donne_503(monkeypatch):
    def casse(*a, **k):
        raise RuntimeError("db")
    monkeypatch.setattr(store, "nb_fragments", casse)
    assert client.get("/api/health").status_code == 503


def test_ask_hors_corpus_renvoie_found_false(monkeypatch):
    monkeypatch.setattr(rag, "rechercher", lambda *a, **k: [])
    r = client.post("/api/ask", json={"question": "Quel est le prix d'un repas ?"})
    assert r.status_code == 200
    body = r.json()
    assert body["found"] is False and body["sources"] == []


def test_search_renvoie_la_cle_results(monkeypatch):
    from langchain_core.documents import Document
    doc = Document(page_content="Texte", metadata={
        "id": "X-p1-0", "file": "a.pdf", "reference": "X", "type": "Guide",
        "date": "2026-01-01", "page": 1, "section": ""})
    monkeypatch.setattr(store, "rechercher", lambda *a, **k: [(doc, 0.8)])
    r = client.post("/api/search", json={"question": "Bonjour ?"})
    assert r.status_code == 200
    assert r.json()["results"][0]["reference"] == "X"


def test_ingest_renvoie_la_cle_strategie(monkeypatch):
    from app import main
    monkeypatch.setattr(main, "extraire_corpus", lambda: [{"metadata": {}, "pages": []}])
    monkeypatch.setattr(main, "decouper", lambda *a, **k: [])
    monkeypatch.setattr(store, "ingerer", lambda *a, **k: 0)
    r = client.post("/api/ingest", json={"strategie": "fixe"})
    assert r.status_code == 200
    assert r.json()["strategie"] == "fixe"