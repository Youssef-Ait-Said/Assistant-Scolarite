import time 
from langchain_chroma import Chroma
from langchain_core.documents import Document

from app import config

TAILLE_LOT = 50     # nombre de fragments envoyés à la fois à l'API d'embeddings


def _ouvrir(collection=None, avec_embeddings=True):
    """Ouvre la collection Chroma (la base vectorielle.

    avec_embeddings=True  : Gemini est utilisé pour transformer le texte en nombres.
                            Nécessaire pour ingérer et rechercher.
    avec_embeddings=False : pas de Gemini. Suffisant pour compter ou lister, plus rapide,
                            et ça marche même si Gemini est en panne.
    """
    embeddings = None
    if avec_embeddings:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        embeddings = GoogleGenerativeAIEmbeddings(model = config.EMBEDDING_MODEL)
    return Chroma(
        collection_name = collection or config.COLLECTION_NAME,
        embedding_function = embeddings,
        persist_directory = str(config.DB_DIR),
        collection_metadata = {"hnsw:space": "cosinus"}     #distance cosinus -> score = 1 - distance
    )


def vers_documents(fragments):
    """Nos fragments (dictionnaires) deviennent des Document LangChain + une liste d'ids."""
    docs, ids = [], []
    for f in fragments:
        meta = {k: v for k, v in f.items() if k != "text"}
        docs.append(Document(page_content=f["texte"], metadata=meta))
        ids.append(f["id"])
    return docs, ids


def ingerer(fragments, rebuild=False, collection=None):
    """Indexe les fragments. Idempotent : même id = fragment remplacé, jamais dupliqué."""
    if rebuild:
        _ouvrir(collection, avec_embeddings=False).delete_collection()
    vs = _ouvrir(collection)
    docs, ids = vers_documents(fragments)
    for i in range(0, len(docs), TAILLE_LOT):
        lot_docs, lot_ids = docs[i: i+TAILLE_LOT], ids[i: i+TAILLE_LOT]
        for essai in range(3):           # si l'API limite le débit, on réessaie
            try:
                vs.add_documents(lot_docs, ids=lot_ids)
                break
            except Exception:
                if essai == 2:
                    raise
                time.sleep(10 * (essai + 1))
        time.sleep(0.3)
    return vs._collection.count()


def rechercher(question, k=5, type_doc=None, collection=None):
    """Les k fragments les plus proches : liste de (Document, score). Score = similarité (1 = identique)."""
    vs = _ouvrir(collection)
    filtre = {"type": type_doc} if type_doc else None
    resultats = vs.similarity_search_with_score(question, k=k, filter=filtre)
    return [(doc, round(1 - distance, 4)) for doc, distance in resultats]


def lister_documents(collection=None):
    """Documents indexés, avec leurs métadonnées et leur nombre de fragments."""
    data = _ouvrir(collection, avec_embeddings=False)._collection.get(include=["metadatas"])
    docs= {}
    for m in data.get("metadata"):              # m = les infos d'un fragment
        ref = m["reference"]                    # le document auquel il appartient
        if ref not in docs:                     # premier fragment de ce document : on crée sa fiche
            docs[ref] = {   
                "file" : m["file"],
                "reference" : m["reference"],
                "type" : m["type"],
                "date" : m["date"],
                "version" : m["version"],
                "statut" : m["statut"],
                "chunks": 0
                }
        docs[ref]["chunks"] += 1                # un fragment de plus pour ce document
    return sorted(docs.values(), key=lambda d:d["file"])