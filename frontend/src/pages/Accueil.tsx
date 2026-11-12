import type { SectionId } from "../sections";

export default function Accueil({ onOuvrir }: { onOuvrir: (id: SectionId) => void }) {
  return (
    <section>
      <h1>Bienvenue sur le portail étudiant</h1>
      <p className="intro">
        Retrouvez ici les services de la scolarité, des stages et de la vie étudiante.
      </p>
      <div className="cartes">
        <div className="carte">
          <h2>Assistant Scolarité</h2>
          <p>
            Une question sur le règlement, les stages ou la mobilité ? L'assistant répond à partir
            des documents officiels de l'École.
          </p>
          <button className="bouton" onClick={() => onOuvrir("assistant")}>
            Ouvrir l'assistant
          </button>
        </div>
        <div className="carte">
          <h2>Documents officiels</h2>
          <p>Consultez la liste des documents de référence de l'École.</p>
          <button className="bouton" onClick={() => onOuvrir("documents")}>
            Voir les documents
          </button>
        </div>
      </div>
    </section>
  );
}