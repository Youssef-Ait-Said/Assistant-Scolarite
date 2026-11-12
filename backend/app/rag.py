"""Chaîne RAG : recherche -> contrôle du seuil -> prompt -> LLM -> vérification des citations."""
import re, time
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import GoogleGenerativeAI

from app import config
from app.store import rechercher

REFUS = "Je ne trouve pas cette information dans les documents de l'École."

# Le prompt est écrit par nous (consigne du TP). Aucune règle propre à ce corpus :
# la règle des versions est générale (document le plus récent qui se déclare modificatif).
SYSTEM_PROMPT = f"""Tu es l'Assistant Scolarité de l'École d'Ingénieurs Hélianthe (EIH). \
Tu réponds aux questions des étudiants.

Règles à respecter strictement :
1. Réponds UNIQUEMENT à partir des fragments fournis ci-dessous. N'utilise aucune autre connaissance.
2. Cite chaque affirmation avec le numéro du fragment qui la justifie, sous la forme [1], [2].
3. Si les fragments ne contiennent pas la réponse, réponds exactement : « {REFUS} » et rien d'autre.
4. Chaque fragment est présenté avec sa référence, son type, sa date et son statut. Si deux fragments \
donnent des règles différentes sur le même point, retiens celle du document le plus récent qui se \
déclare modificatif (voir son statut), et signale explicitement que la règle a changé.
5. Réponds en français, de façon courte et claire.

Fragments :
{{context}}"""


PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{question}")
])


class LLMError(Exception):
    """ Le LLM ne répond pas (l'API renvoie alors une erreur 502)"""


def chaine():
    llm = GoogleGenerativeAI(model = config.CHAT_MODEL, temperature=0)
    return PROMPT | llm | StrOutputParser()


def formater_contexte(resultats):       #resultats : chunk
    blocs = []
    for i, (doc, score) in enumerate(resultats, start=1):
        m = doc.metadata
        blocs.append(f"[{i}] (ref. {m['reference']} | date : {m['date']} | statut : {m['statut']})\n"
                     f"{doc.page_content}")
    return "\n\n".join(blocs)


def verifier_citation(reponse, nb_chunks):
    """Renvoie les numéros cités par le LLM qui ne correspondent a aucun chunk fourni."""
    cites = {int(n) for n in re.findall(r"\[(\d+)\]", reponse)}
    return sorted(n for n in cites if n < 1 or n > nb_chunks)


def vers_source(rang, doc, score, complet=False):
    m = doc.metadata
    texte = doc.page_content if complet else doc.page_content[:300]
    return {"id" : rang, "chunk_id" : m["id"], "file" : m["file"], "reference" : m["reference"],
            "type" : m["type"], "date" : m["date"], "page" : int(m["page"]),
            "section" : m["section"], "excerpt" : texte, "score" : score
            }


def repondre(question, top_k=5, type_doc=None, collection=None):
    debut = time.perf_counter()
    resultats = rechercher(question, top_k, type_doc, collection)
    sources, invalides, found, answer = [], [], False, REFUS

    # Contrôle 1 : seuil de score. Trop faible -> refus SANS appeler le LLM.
    if resultats and max(score for chunk, score in resultats) >= config.SEUIL_SCORE:
        try:
            reponse = chaine().invoke({"context" : formater_contexte(resultats), "question" : question})
        except Exception as e:
            import traceback
            traceback.print_exc()   # affiche la vraie erreur dans le terminal
            raise LLMError(str(e)) from e
        reponse = reponse.strip()
        if REFUS not in reponse:
            found, answer = True, reponse
            sources = [vers_source(i, d, s) for i, (d, s) in enumerate(resultats, start=1)]

            # Contrôle 2 : chaque numéro cité doit correspondre à un chunk fourni.
            invalides = verifier_citation(reponse, len(resultats))

    return {"answer" : answer, "found" : found, "sources" : sources,
            "invalid_citations" : invalides,
            "latency_ms" : int((time.perf_counter() - debut) * 1000)
            }