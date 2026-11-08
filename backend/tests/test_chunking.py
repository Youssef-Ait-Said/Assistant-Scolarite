from app.chunking import couper_fixe, couper_structurel, decouper, est_titre


def test_couper_fixe_taille_et_chevauchement():
    texte = "mot " * 400                       # 1600 caractères
    morceaux = couper_fixe(texte, taille=500, chevauchement=100)
    assert len(morceaux) > 1
    assert all(len(m) <= 500 for m in morceaux)


def test_couper_fixe_refuse_chevauchement_trop_grand():
    import pytest
    with pytest.raises(ValueError):
        couper_fixe("abc", taille=100, chevauchement=100)


def test_couper_structurel_un_fragment_par_article():
    texte = ("Article 5 — Présence\nLa présence est obligatoire.\n"
             "Article 6 — Absences\nToute absence doit être justifiée.")
    blocs = couper_structurel(texte)
    assert len(blocs) == 2
    assert blocs[0][0].startswith("Article 5")
    assert "justifiée" in blocs[1][1]


def test_est_titre():
    assert est_titre("Article 14 — Session de rattrapage")
    assert est_titre("Q4. J'ai été malade le jour d'un examen")
    assert est_titre("5.3 Durée et période")
    assert not est_titre("1. avoir acquis les 180 crédits")
    assert not est_titre("La présence est obligatoire.")


def test_decouper_ajoute_les_metadonnees_et_les_tableaux():
    docs = [{"metadata": {"reference": "REF-1", "file": "a.pdf", "type": "Guide",
                          "date": "2026-01-01", "version": "1.0", "statut": "En vigueur"},
             "pages": [{"page": 2, "text": "Article 1 — Objet\nTexte.",
                        "table_rows": ["Date : 12 février 2027 — Événement : limite"]}]}]
    frags = decouper(docs, "structurel")
    assert len(frags) == 2
    assert frags[0]["id"] == "REF-1-p2-structurel-0"
    assert frags[1]["section"] == "Tableau"
    assert all(f["reference"] == "REF-1" and f["page"] == 2 for f in frags)