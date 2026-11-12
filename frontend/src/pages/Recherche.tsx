import { useState, type FormEvent } from "react";
import { rechercher } from "../api/client";
import type { Source } from "../types";
import { useTypes } from "../hooks/useTypes";
import { messageDErreur } from "../utils";
import Parametres from "../components/Parametres";
import SourceCard from "../components/SourceCard";

// Mode débogage : les passages bruts et leurs scores, sans rédaction de réponse
export default function Recherche() {
    const [question, setQuestion] = useState("");
    const [topk, setTopK] = useState(5);
    const [type, setType] = useState("");
    const [resultats, setResultats] = useState<Source[] | null>(null);
    const [chargement, setChargement] = useState(false);
    const [erreur, setErreur] = useState("");
    const types = useTypes();

    async function lancer(e: FormEvent) {
        e.preventDefault();
        if (!question.trim() || chargement) return;
        setChargement(true);
        setErreur("");
        try {
            const reponse = await rechercher(question.trim(), topk, type);
            setResultats(reponse.results);
        } catch (err) {
            setResultats(null);
            setErreur(messageDErreur(err));
        } finally {
            setChargement(false)
        }
    }

    
    return (
        <section>
            <h1>Recherche (débogage)</h1>
            <p className="intro">
                Affiche les passages trouvés par la recherche et leurs scores, sans rédaction de réponse.
            </p>

            <form className="saisie boite" onSubmit={lancer}>
                <Parametres topK={topk} type={type} types={types} onTopK={setTopK} onType={setType}/>
                <label htmlFor="recherche">Question</label>
                <input id="recherche" value={question} onChange={ (e) => setQuestion(e.target.value)} />
                <button type="submit" disabled={chargement || !question.trim()}>
                    {chargement ? "Recherche en cours..." : "Rechercher"}
                </button>
            </form>

            {erreur && <div className="message erreur" role="alert">{erreur}</div>}
            {resultats && resultats.length === 0 && <p className="vide">Aucun passage trouvé.</p>}
            <div className="resultats">
                {resultats?.map( (s) => <SourceCard key={s.chunk_id} source={s}/>)}
            </div>
        </section>
    );
}

/**L’écran de recherche en mode débogage (consigne du TP) : appelle POST /api/search et affiche les chunks bruts avec leur score. 
 * C’est aussi l’écran qui me servira à régler le seuil. */