from app.extract import date_iso, lignes_de_tableau, lignes_repetees, cle_ligne


def test_date_iso():
    assert date_iso("15 juin 2026") == "2026-06-15"
    assert date_iso("1er septembre 2026") == "2026-09-01"
    assert date_iso("pas de date") == ""


def test_lignes_de_tableau_recolle_les_en_tetes():
    table = [["Date", "Événement"],
             ["12 février 2027", "Date limite d'inscription au rattrapage"]]
    assert lignes_de_tableau(table) == [
        "Date : 12 février 2027 — Événement : Date limite d'inscription au rattrapage"]


def test_lignes_repetees_detecte_les_en_tetes():
    pages = ["École EIH\nArticle 1 — Objet\nPage 1/3", "École EIH\nArticle 5 — Présence\nPage 2/3",
             "École EIH\nArticle 9 — Absence\nPage 3/3"]
    repetees = lignes_repetees(pages)
    assert cle_ligne("École EIH") in repetees
    assert cle_ligne("Page 1/3") in repetees
    assert cle_ligne("Article 1 — Objet") not in repetees