import { useEffect, useState }  from "react";
import { listerDocuments } from "../api/client";

// Charge la liste des types de documents (pour le filtre)
export function useTypes(): string[] {
    const [types, setTypes] = useState<string[]>([]);

    useEffect( () => {
        listerDocuments()
            .then((docs) => setTypes([...new Set(docs.map((d) => d.type))]))
            .catch( () => setTypes([]));
    }, []);
    
    return types;
}


//Un hook qui appelle /api/documents au chargement 
// et en tire la liste des types (sans doublon) pour le menu déroulant du filtre.