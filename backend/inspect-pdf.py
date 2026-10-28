import pdfplumber, pathlib

for pdf_path in sorted(pathlib.Path("../data/corpus").glob("*.pdf")):
    print("=" * 60)
    print(pdf_path.name)
    with pdfplumber.open(pdf_path) as pdf:
        print("Pages :", len(pdf.pages))
        print("Métadonnées PDF :", pdf.metadata)
        page = pdf.pages[0]
        print("--- Début page 1 ---")
        print((page.extract_text() or "")[:600])
        tables = [t for p in pdf.pages for t in p.extract_tables()]
        print("Tableaux trouvés :", len(tables))
        if tables:
            print("Exemple :", tables[0][:3])