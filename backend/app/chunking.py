import json, re, pathlib
from app.extract import extraire_corpus

# Une ligne est un titre si elle commence par : "Article 6", "Titre III",
TITRE = re.compile(r"^(Article \d+|Titre [IVX]+|\d+(\.\d+)*\.?\s+[A-ZÀ-Ý]|Q\d+\.)") 


def couper_fixe(texte, taille = 500, chevauchement = 100):
    """Stratégie (a) : coupe tous les 'taille' caractères, avec chevauchement."""
    if chevauchement >= taille:
        raise ValueError("le chevauchement doit etre plus petit que la taille")
    fragments, debut = [], 0
    while debut < len(texte):
        fragments.append(texte[debut : debut+taille])  #[debut, fin] , fin exclut
        if debut + taille >= len(texte):    #Fin du texte
            break
        debut += taille - chevauchement      #on avance
    return fragments

def couper_structure(texte):
    """Stratégie (b) : un nouveau fragment à chaque titre. Renvoie (titre, texte)."""
    blocs, titre, lignes = [], "", []
    for ligne in  texte.splitlines():
        ligne = ligne.strip()
        if TITRE.match(ligne):
            if len(lignes) > 1:     # Le bloc en cours a du contenu : on le ferme
                blocs.append((titre, " ".join(lignes)))
                lignes = []
             # sinon (titre seul, ex: "Titre III") : on le garde avec l'article suivant
            titre = ligne
            lignes.append(ligne)
    if lignes:
        blocs.append((titre, " ". join(lignes)))
    return blocs

def decouper(docs, strategie = "fixe", taille = 500, chevauchement = 100):
    fragments = []
    for d in docs:
        m = d["metadata"]
        for p in d["pages"]:
            if strategie == "fixe":
                morceaux = [("", t) for t in couper_fixe(p["text"], taille, chevauchement)]
            elif strategie == "structurel":
                morceaux = couper_structure(p["text"])
            else:
                raise ValueError("stratégie inconue : " + strategie)
            #chaque ligne de tableau = un fragment
            morceaux += [("Tableau", ligne) for ligne in p["table_rows"]]

            for n, (section, contenu) in enumerate(morceaux):
                if not contenu.strip():
                    continue
                fragments.append({
                    "id" : f"{m['reference']}-p{p['page']}-{strategie}-{n}",
                    "texte" : contenu,
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
            json.dumps(frags, ensure_ascii=False, indent=2,), encoding="utf-8")
        print(strat, ":", len(frags), "fragments")