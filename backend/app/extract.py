"""Extraction des PDF : métadonnées, texte par page, lignes de tableau, en-têtes retirés."""
import json, re, pathlib
from collections import Counter
import pdfplumber

from app import config

MOIS = {"janvier":1,"février":2,"mars":3,"avril":4,"mai":5,"juin":6,
        "juillet":7,"août":8,"septembre":9,"octobre":10,"novembre":11,"décembre":12}


def date_iso(texte):
    """'15 juin 2026' -> '2026-06-15'"""
    m = re.search(r"(\d{1,2})(?:er)?\s+(\w+)\s+(\d{4})", texte or "")
    if not m or m.group(2).lower() not in MOIS:
        return ""
    jour, mois, annee = m.groups()
    return f"{annee}-{MOIS[mois.lower()]:02d}-{int(jour):02d}"


def nettoyer(cellule):
    # Remplace les retours à la ligne et les espaces multiples par un seul espace
    return re.sub(r"\s+", " ", cellule or "").strip()


def lire_metadonnees(pdf):
    """Lit le tableau de la page 1 (référence, date, version, statut, ...)"""
    tables = pdf.pages[0].extract_tables()
    interne = pdf.metadata or {}
    infos = {}
    if tables:
        infos = {nettoyer(l[0]): nettoyer(l[1])
                 for l in tables[0] if l and l[0] and len(l) > 1}
    return {
        "reference": infos.get("Référence", ""),
        "type": infos.get("Type de document", ""),
        "date": date_iso(infos.get("Date de publication", "") or interne.get("Subject", "")),
        "version": infos.get("Version", ""),
        "statut": infos.get("Statut", ""),
        "titre": interne.get("Title", ""),
    }


def hors_tableaux(page, bboxes):
    # """Garde le texte de la page SANS les tableaux (on les traite à part)."""
    # bboxes = les rectangles (x0, haut, x1, bas) où se trouvent les tableaux
    def garder(obj):
        if obj.get("object_type") != "char":
            return True
        cx = (obj["x0"] + obj["x1"]) / 2
        cy = (obj["top"] + obj["bottom"]) / 2
        return not any(x0 <= cx <= x1 and t <= cy <= b for x0, t, x1, b in bboxes)  #on garde le caractère seulement s’il n’est dans aucun tableau.
    return page.filter(garder)


def lignes_de_tableau(table):
    """Chaque ligne est recollée à ses en-têtes : 'Date : ... — Événement : ...'"""
    lignes = [[nettoyer(c) for c in row] for row in table if row and any(row)]
    if len(lignes) < 2:
        return []
    entetes, resultat = lignes[0], []
    for row in lignes[1:]:
        morceaux = [f"{h} : {v}" for h, v in zip(entetes, row) if v]
        if morceaux:
            resultat.append(" — " .join(morceaux))
    return resultat


def cle_ligne(ligne):
    # Remplace tous les chiffres par '#' : "Page 1/4" et "Page 2/4" deviennent identiques
    return re.sub(r"\d+", "#", ligne.strip())


def lignes_repetees(pages_texte):
    """trouve les en-têtes et pieds de page (lignes présentes sur au moins la moitié des pages)"""
    """Le compteur est pour detecter les entetes qui se repetent dans chaque pages -- Compter = détecter les en-têtes."""
    n = len(pages_texte)
    if n < 2:
        return set()
    compteur = Counter()
    for texte in pages_texte:
        for cle in {cle_ligne(l) for l in texte.splitlines() if l.strip()}:
            compteur[cle] += 1
    return {cle for cle, c in compteur.items() if c >= max(2, n / 2)}


def extraire_pdf(chemin):
    chemin = pathlib.Path(chemin)
    with pdfplumber.open(chemin) as pdf:
        meta = lire_metadonnees(pdf)
        meta["file"] = chemin.name
        textes, tableaux = [], []
        for i, page in enumerate(pdf.pages):
            trouves = page.find_tables()
            bboxes = [t.bbox for t in trouves]
            textes.append(hors_tableaux(page, bboxes).extract_text() or "")
            lignes = []
            for j, t in enumerate(trouves):
                if i == 0 and j == 0:   # tableau des métadonnées(premier tab de chaque pdf), déjà lu
                    continue
                lignes += lignes_de_tableau(t.extract())
            tableaux.append(lignes)

    a_enlever = lignes_repetees(textes)
    pages = []
    for i, texte in enumerate(textes):
        # on garde seulement les lignes qui ne sont PAS des en-têtes répétés
        propre = "\n".join(l for l in texte.splitlines() if cle_ligne(l) not in a_enlever)
        propre = propre.replace("(cid:127)", "•")
        pages.append({"page": i + 1, "text": propre.strip(), "table_rows": tableaux[i]})
    return {"metadata": meta, "pages": pages}


def extraire_corpus(dossier=None):
    dossier = pathlib.Path(dossier or config.CORPUS_DIR)
    return [extraire_pdf(p) for p in sorted(dossier.glob("*.pdf"))]     #glog(renvoie les chemins des fichiers qui se terminent par .pdf)


if __name__ == "__main__":
    docs = extraire_corpus()
    pathlib.Path("extraction.json").write_text(
        json.dumps(docs, ensure_ascii=False, indent=2), encoding="utf-8")
    for d in docs:
        m = d["metadata"]
        nb_lignes = sum(len(p["table_rows"]) for p in d["pages"])
        print(m["file"], "|", m["reference"], "|", m["date"], "|", nb_lignes, "lignes de tableau")