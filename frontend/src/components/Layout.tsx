import { useEffect, useState, type ReactNode } from "react";
import { SECTIONS, type SectionId } from "../sections";
import { etatService } from "../api/client";

interface Props {
  actif: SectionId;
  onChoisir: (id: SectionId) => void;
  children: ReactNode;
}

// La structure de toutes les pages : en-tête (titre + logo), menu latéral, contenu, pied de page
export default function Layout({ actif, onChoisir, children }: Props) {
  const [menuOuvert, setMenuOuvert] = useState(false);
  const [etat, setEtat] = useState<"inconnu" | "ok" | "hs">("inconnu");
  const [nbPassages, setNbPassages] = useState(0);
  const groupes = [...new Set(SECTIONS.map((s) => s.groupe))];

  // Vérifie l'état de l'API au chargement, puis toutes les 30 secondes
  useEffect(() => {
    function verifier() {
      etatService()
        .then((r) => { setEtat("ok"); setNbPassages(r.chunks); })
        .catch(() => setEtat("hs"));
    }
    verifier();
    const minuteur = setInterval(verifier, 30_000);
    return () => clearInterval(minuteur);
  }, []);

  return (
    <div className="page">
      <header className="entete">
        <div className="entete-contenu">
          <button
            className="bouton-menu"
            onClick={() => setMenuOuvert(!menuOuvert)}
            aria-expanded={menuOuvert}
            aria-label="Ouvrir le menu"
          >
            <span /><span /><span />
          </button>

          <div className="titre-bloc">
            <div className="ecole">École d'Ingénieurs Hélianthe</div>
            <div className="portail">Portail étudiant · 2026-2027</div>
          </div>

          <div className="entete-droite">
            <div className={"etat etat-" + etat} title="État du service de l'assistant">
              <span className="etat-point" />
              {etat === "ok" && <span>Service en ligne · {nbPassages} passages</span>}
              {etat === "hs" && <span>Service indisponible</span>}
              {etat === "inconnu" && <span>Vérification…</span>}
            </div>
            <img className="logo" src="/logo.svg" alt="Logo de l'École d'Ingénieurs Hélianthe" />
          </div>
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
                      aria-current={s.id === actif ? "page" : undefined}
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

      <footer className="pied">
        <span>École d'Ingénieurs Hélianthe — Portail étudiant 2026-2027</span>
        <span className="pied-note">Assistant Scolarité : réponses issues des documents officiels</span>
      </footer>
    </div>
  );
}
