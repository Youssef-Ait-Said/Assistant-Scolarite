export type SectionId = 
| "accueil" | "dossier" | "emploi" | "notes" | "calendrier"
| "stages" | "mobilite" | "vie"
| "assistant" | "documents" | "recherche";

export interface Section {
    id : SectionId;
    titre : string;
    groupe : string;
}

// Les sections du portail, dans l'ordre du menu
export const SECTIONS: Section[] = [
  { id: "accueil", titre: "Accueil", groupe: "" },
  { id: "dossier", titre: "Mon dossier", groupe: "Scolarité" },
  { id: "emploi", titre: "Emploi du temps", groupe: "Scolarité" },
  { id: "notes", titre: "Notes et résultats", groupe: "Scolarité" },
  { id: "calendrier", titre: "Calendrier académique", groupe: "Scolarité" },
  { id: "stages", titre: "Stages et PFE", groupe: "Parcours" },
  { id: "mobilite", titre: "Mobilité internationale", groupe: "Parcours" },
  { id: "vie", titre: "Vie étudiante", groupe: "Parcours" },
  { id: "assistant", titre: "Assistant Scolarité", groupe: "Services" },
  { id: "documents", titre: "Documents officiels", groupe: "Services" },
  { id: "recherche", titre: "Recherche (débogage)", groupe: "Services" },
];

// La liste des rubriques du menu. 
// Pour en ajouter ou renommer une, tu modifies seulement ce fichier.