import { useState, type ReactNode } from "react";
import { SECTIONS, type SectionId } from "../sections";

interface Props {
  actif: SectionId;
  onChoisir: (id: SectionId) => void;
  children: ReactNode;
}

export default function Layout({ actif, onChoisir, children }: Props) {
  const [menuOuvert, setMenuOuvert] = useState(false);
  const groupes = [...new Set(SECTIONS.map((s) => s.groupe))];

  return (
    <div className="page">
      <header className="entete">
        <div className="entete-contenu">
          <div>
            <div className="ecole">École d'Ingénieurs Hélianthe</div>
            <div className="portail">Portail étudiant</div>
          </div>
          <button
            className="bouton-menu"
            onClick={() => setMenuOuvert(!menuOuvert)}
            aria-expanded={menuOuvert}
          >
            Menu
          </button>
        </div>
      </header>

      <div className="corps">
        <nav className={"navigation" + (menuOuvert ? " ouverte" : "")} aria-label="Navigation principale">
          {groupes.map((groupe) => (
            <div key={groupe || "general"} className="groupe">
              {groupe && <div className="groupe-titre">{groupe}</div>}
              <ul>
                {SECTIONS.filter((s) => s.groupe === groupe).map((s) => (
                  <li key={s.id}>
                    <button
                      className={s.id === actif ? "lien actif" : "lien"}
                      onClick={() => {
                        onChoisir(s.id);
                        setMenuOuvert(false);
                      }}
                    >
                      {s.titre}
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </nav>
        <main className="contenu">{children}</main>
      </div>

      <footer className="pied">École d'Ingénieurs Hélianthe — Portail étudiant 2026-2027</footer>
    </div>
  );
}