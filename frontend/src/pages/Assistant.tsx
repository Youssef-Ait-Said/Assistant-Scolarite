import { useEffect, useRef, useState, type FormEvent, type KeyboardEvent } from "react";
import { poserQuestion } from "../api/client";
import type { Echange } from "../types";
import { messageDErreur } from "../utils";
import { useTypes } from "../hooks/useTypes";
import Parametres from "../components/Parametres";
import Reponse from "../components/Reponse";
import SourceCard from "../components/SourceCard";

export default function Assistant() {
  const [question, setQuestion] = useState("");
  const [echanges, setEchanges] = useState<Echange[]>([]);
  const [chargement, setChargement] = useState(false);
  const [topK, setTopK] = useState(5);
  const [type, setType] = useState("");
  const [actifId, setActifId] = useState<number | null>(null);        // échange dont on affiche les sources
  const [sourceChoisie, setSourceChoisie] = useState<number | null>(null);
  const types = useTypes();
  const fin = useRef<HTMLDivElement>(null);
  const panneau = useRef<HTMLElement>(null);

  const actif = echanges.find((e) => e.id === actifId);
  const sources = actif?.reponse?.found ? actif.reponse.sources : [];

  // Défile vers la dernière question
  useEffect(() => {
    if (echanges.length > 0) fin.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }, [echanges]);

  // Défile vers la source citée dans le panneau
  useEffect(() => {
    if (sourceChoisie === null) return;
    panneau.current
      ?.querySelector(`[data-source="${sourceChoisie}"]`)
      ?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }, [sourceChoisie, actifId]);

  async function envoyer(e: FormEvent) {
    e.preventDefault();
    const texte = question.trim();
    if (!texte || chargement) return;

    const id = Date.now();
    setEchanges((liste) => [...liste, { id, question: texte }]);
    setQuestion("");
    setChargement(true);
    try {
      const reponse = await poserQuestion(texte, topK, type);
      setEchanges((liste) => liste.map((x) => (x.id === id ? { ...x, reponse } : x)));
      setActifId(id);
      setSourceChoisie(null);
    } catch (err) {
      setEchanges((liste) =>
        liste.map((x) => (x.id === id ? { ...x, erreur: messageDErreur(err) } : x))
      );
    } finally {
      setChargement(false);
    }
  }

  function toucheEntree(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      e.currentTarget.form?.requestSubmit();
    }
  }

  function montrerSources(id: number, numero: number | null) {
    setActifId(id);
    setSourceChoisie(numero);
  }

  return (
    <section className="assistant">
      <h1>Assistant Scolarité</h1>
      <p className="intro">
        Posez une question sur le règlement des études, les stages, la mobilité internationale ou la
        vie étudiante. Les réponses s'appuient uniquement sur les documents officiels de l'École.
      </p>

      <div className="assistant-grille">
        <div className="conversation">
          <div className="echanges" aria-live="polite">
            {echanges.length === 0 && <p className="vide">Aucune question pour le moment.</p>}

            {echanges.map((x) => (
              <div key={x.id} className="echange">
                <div className="question">
                  <span className="etiquette">Question</span>
                  <p>{x.question}</p>
                </div>

                {!x.reponse && !x.erreur && (
                  <div className="chargement">
                    <span className="rond" /> Recherche en cours…
                  </div>
                )}

                {x.erreur && (
                  <div className="message erreur" role="alert">
                    {x.erreur}
                  </div>
                )}

                {x.reponse &&
                  (x.reponse.found ? (
                    <div className={"message reponse" + (x.id === actifId ? " active" : "")}>
                      <span className="etiquette">Réponse</span>
                      <Reponse
                        texte={x.reponse.answer}
                        nbSources={x.reponse.sources.length}
                        onCitation={(n) => montrerSources(x.id, n)}
                      />
                      {x.reponse.invalid_citations.length > 0 && (
                        <p className="avertissement">
                          Certaines citations ne correspondent à aucune source.
                        </p>
                      )}
                      <button className="lien-sources" onClick={() => montrerSources(x.id, null)}>
                        Afficher les sources
                      </button>
                    </div>
                  ) : (
                    <div className="message refus">
                      <span className="etiquette">Information non disponible</span>
                      <p>{x.reponse.answer}</p>
                    </div>
                  ))}
              </div>
            ))}
            <div ref={fin} />
          </div>

          <form className="saisie" onSubmit={envoyer}>
            <Parametres topK={topK} type={type} types={types} onTopK={setTopK} onType={setType} />
            <label htmlFor="question">Votre question</label>
            <textarea
              id="question"
              rows={3}
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={toucheEntree}
              placeholder="Exemple : quelle est la durée minimale d'un PFE ?"
            />
            <button type="submit" disabled={chargement || !question.trim()}>
              {chargement ? "Envoi en cours…" : "Envoyer"}
            </button>
          </form>
        </div>

        <aside className="panneau-sources" ref={panneau}>
          <h2>Sources</h2>
          {sources.length === 0 ? (
            <p className="vide">Les sources de la réponse sélectionnée s'affichent ici.</p>
          ) : (
            sources.map((s) => <SourceCard key={s.id} source={s} surligne={s.id === sourceChoisie} />)
          )}
        </aside>
      </div>
    </section>
  );
}