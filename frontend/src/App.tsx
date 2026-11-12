import { useState } from "react";
import Layout from "./components/Layout";
import { SECTIONS, type SectionId } from "./sections";
import Accueil from "./pages/Accueil";
import Assistant from "./pages/Assistant";
import Documents from "./pages/Documents";
import Recherche from "./pages/Recherche";
import SectionIndisponible from "./pages/SectionIndisponible";

const SECTIONS_ACTIVES: SectionId[] = ["accueil", "assistant", "documents", "recherche"];

export default function App() {
  const [section, setSection] = useState<SectionId>("accueil");
  const titre = SECTIONS.find( (s) => s.id === section)?.titre ?? "";

  return (
    <Layout actif={section} onChoisir={setSection}>
      {section === "accueil" && <Accueil onOuvrir={setSection}/>}
      {/* L'assistant reste monté (seulement caché) pour garder l'historique de la session */}
      <div hidden={section !== "assistant"}>
        <Assistant />
      </div>
      {section === "documents" && <Documents />}
      {section === "recherche" && <Recherche />}
      {!SECTIONS_ACTIVES.includes(section) && <SectionIndisponible titre={titre} />}
    </Layout>
  );
}


/**Le chef d’orchestre : il garde en mémoire la rubrique ouverte et affiche la bonne page. 
 * L’assistant est seulement caché quand tu changes de rubrique, pour ne pas perdre l’historique. */

/**
L'assistant reste toujours monté dans le DOM.
  - Si section === "assistant" : il est visible.
  - Sinon : il est masqué.
Pourquoi ?
  -> Pour conserver son état interne, notamment l'historique des questions et des réponses. */