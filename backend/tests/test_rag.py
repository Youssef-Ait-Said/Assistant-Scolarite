import pytest
from langchain_core.documents import Document

from app import rag


def faux_resultats(score):
    doc = Document(page_content="Texte", metadata={
        "id": "X-p1-0", "file": "a.pdf", "reference": "X", "type": "Guide", "date": "2026-01-01",
        "page": 1, "section": "", "statut": "En vigueur"})
    return [(doc, score)]


def test_refus_hors_corpus_sans_appeler_le_llm(monkeypatch):
    """Score trop faible : refus direct, le LLM ne doit PAS être appelé."""
    monkeypatch.setattr(rag, "rechercher", lambda *a, **k: faux_resultats(0.10))

    def interdit():
        raise AssertionError("le LLM ne devrait pas être appelé")
    monkeypatch.setattr(rag, "chaine", interdit)

    rep = rag.repondre("Quel est le prix d'un repas ?")
    assert rep["found"] is False
    assert rep["answer"] == rag.REFUS
    assert rep["sources"] == []


def test_verifier_citation():
    assert rag.verifier_citation("Oui [1]. Aussi [2] et [7].", 3) == [7]


def test_reponse_avec_citation_invalide_signalee(monkeypatch):
    monkeypatch.setattr(rag, "rechercher", lambda *a, **k: faux_resultats(0.90))

    class FauxLLM:
        def invoke(self, _):
            return "La durée est de 18 semaines [1][5]."
    monkeypatch.setattr(rag, "chaine", lambda: FauxLLM())

    rep = rag.repondre("Durée du PFE ?")
    assert rep["found"] is True
    assert rep["invalid_citations"] == [5]
    assert rep["sources"][0]["id"] == 1


def test_llm_en_panne_leve_llmerror(monkeypatch):
    monkeypatch.setattr(rag, "rechercher", lambda *a, **k: faux_resultats(0.90))

    class LLMCasse:
        def invoke(self, _):
            raise RuntimeError("timeout")
    monkeypatch.setattr(rag, "chaine", lambda: LLMCasse())
    with pytest.raises(rag.LLMError):
        rag.repondre("Question ?")


def test_formater_contexte_garde_tous_les_chunks():
    resultats = faux_resultats(0.9) + faux_resultats(0.8)
    contexte = rag.formater_contexte(resultats)
    assert "[1]" in contexte and "[2]" in contexte