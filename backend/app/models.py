"""Modèles Pydantic : ils vérifient les données reçues (une erreur donne automatiquement un 422)."""
from typing import Literal
from pydantic import BaseModel, Field, field_validator, model_validator

class Filters(BaseModel):
    type: str | None = None         # ex : "Règlement officiel" (voir GET /api/documents)


class QuestionRequest(BaseModel):
    question : str
    top_k : int = Field(5, ge=1, le=20)
    filters : Filters = Field(default_factory=Filters)

    @field_validator("question")
    @classmethod
    def question_non_vide(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("La question ne doit pas être vide")
        return v


class SearchRequest(QuestionRequest):
    pass


class AskRequest(QuestionRequest):
    pass


class IngestRequest(BaseModel):
    strategie : Literal["fixe", "structurel"] = "structurel"
    taille : int = Field(500, ge=100, le=5000)
    chevauchement : int = Field(100, ge=0)
    reset : bool = True         # True : on repart d'une base vide (sans doublon dans tous les cas)

    @model_validator(mode="after")
    def chevauchement_valide(self):
        if self.chevauchement >= self.taille:
            raise ValueError("le chevauchement doit être plus petit que la taille")
        return self


class Source(BaseModel):
    id : int                # numéro affiché dans la réponse : [1], [2]...
    chunk_id : str
    file : str
    reference : str
    type : str = ""
    date : str
    page : int
    section : str
    excerpt : str
    score : float


class AskResponse(BaseModel):
    answer : str
    found : bool
    sources : list[Source]
    invalid_citations : list[int]
    latency_ms : int


class SearchResponse(BaseModel):
    results : list[Source]


class IngestResponse(BaseModel):
    strategie : str
    documents : int
    chunks_indexes : int


class DocumentInfo(BaseModel):
    file : str
    reference : str
    type : str
    date : str
    version : str
    statut : str
    chunks :int


class HealthResponse(BaseModel):
    status : str
    chunks : int