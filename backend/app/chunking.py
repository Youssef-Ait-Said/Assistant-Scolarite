"""Découpage en fragments : 2 stratégies configurables.
(a) taille fixe avec chevauchement (splitter LangChain du TP)
(b) structurel, écrit à la main : un fragment par article / section / question de la FAQ
Les lignes de tableau sont toujours des fragments à part."""
import json, re, pathlib
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app import config
from app.extract import extraire_corpus


def est_titre(ligne):
    """Dit si une ligne est un titre."""
    if ligne.startswith("Article ") or ligne.startswith("Titre "):
        return True                           # "Article 6 — ...", "Titre III — ..."
    if ligne.startswith("Q") and ligne[1:2].isdigit():
        return True                           # "Q4. J'ai été malade..."
    premier_mot = ligne.split(" ")[0]         # "5.3" dans "5.3 Durée et période"
    parties = premier_mot.split(".")
    return len(parties) >= 2 and all(p.isdigit() for p in parties)


def couper_fixe(texte, taille=500, chevuchement=100):
    """Stratégie (a) : taille fixe avec chevauchement."""
    if chevuchement >= taille:
        raise ValueError("le chevauchement doit être plus petit que la taille")
    splitter = RecursiveCharacterTextSplitter(chunk_size = taille, chunk_overlap = chevuchement)
    return splitter.split_text(texte)


def couper_structurel(texte):
    """Stratégie (b) : un fragment par titre. Renvoie une liste de (titre, texte)."""
    blocs = []
    titre = ""
    lignes = []
    for ligne in texte.splitlines():
        ligne = ligne.strip()
        if est_titre(ligne) and len(lignes) > 1:     # nouveau titre : on ferme le bloc d'avant
            blocs.append((titre, " ".join(lignes)))
            lignes = []
        if est_titre(ligne):
            titre = ligne
        lignes.append(ligne)
    if lignes:
        blocs.append((titre, " ".join(lignes)))  # Le dernier bloc
    return blocs


def decouper(docs, strategie=None, taille=None, chevauchement=None):
    strategie = strategie or config.STRATEGIE
    taille =  taille or config.CHUNK_SIZE
    chevauchement = chevauchement or config.CHUNK_OVERLAP
    if strategie not in ("fixe", "structurel"):
        raise ValueError("Stratégie inconnue: " + strategie)

    fragments = []
    for d in docs:
        m = d["metadata"]
        for p in d["pages"]:
            if strategie == "fixe":
                morceaux = [("", t) for t in couper_fixe(p["text"], taille, chevauchement)]
            else:
                morceaux = couper_structurel(p["text"])
            for ligne in p["table_rows"]:           # Chaque ligne de tableau = un fragment
                morceaux.append(("Tableau", ligne))

            for n, (section, contenu) in enumerate(morceaux):
                if contenu.strip() == "":
                    continue
                fragments.append({
                    "id" : f"{m['reference']}-p{p['page']}-{strategie}-{n}",
                    "text" : contenu,
                    "file" : m["file"],
                     "reference" : m["reference"],
                     "type" : m["type"],
                     "date" : m["date"],
                     "version" : m["version"],
                     "statut" : m["statut"],
                     "page" : p["page"],
                     "section" : section,
                     "strategie" : strategie
                })
    return fragments


if __name__ == "__main__":
    docs = extraire_corpus()
    for strat in ["fixe", "structurel"]:
        frags = decouper(docs, strat)
        pathlib.Path(f"fragments_{strat}.json").write_text(
            json.dumps(frags, ensure_ascii=False, indent=2), encoding="utf-8")
        print(strat, ":", len(frags), "fragments")