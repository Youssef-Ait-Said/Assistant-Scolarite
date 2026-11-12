import { useEffect, useState } from "react";
import type { DocumentInfo } from "../types";
import { listerDocuments } from "../api/client";
import { messageDErreur, formaterDate } from "../utils";


export default function Documents() {
    const [documents, setDocuments] = useState<DocumentInfo[]>([]);
    const [chargement, setChargements] = useState(true);
    const [erreur, setErreurs] = useState("");

    useEffect( () => {
        listerDocuments()
            .then(setDocuments)
            .catch((e) => setErreurs(messageDErreur(e)))
            .finally( () => setChargements(false))
    }, []);


    return (
    <section>
      <h1>Documents officiels</h1>
      <p className="intro">Les documents de référence utilisés par l'assistant.</p>

      {chargement && (
        <div className="chargement">
          <span className="rond" /> Chargement…
        </div>
      )}
      {erreur && <div className="message erreur" role="alert">{erreur}</div>}
      {!chargement && !erreur && documents.length === 0 && (
        <p className="vide">Aucun document indexé.</p>
      )}

      {documents.length > 0 && (
        <div className="table-defilante">
          <table>
            <thead>
              <tr>
                <th>Document</th>
                <th>Référence</th>
                <th>Type</th>
                <th>Date</th>
                <th>Version</th>
                <th>Statut</th>
                <th>Passages</th>
              </tr>
            </thead>
            <tbody>
              {documents.map((d) => (
                <tr key={d.reference}>
                  <td>{d.file}</td>
                  <td>{d.reference}</td>
                  <td>{d.type}</td>
                  <td>{formaterDate(d.date)}</td>
                  <td>{d.version}</td>
                  <td>{d.statut}</td>
                  <td>{d.chunks}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );

}

/**L’écran Documents (consigne du TP) : liste issue de GET /api/documents, avec chargement, erreur et tableau. 
 * « Passages » = le nombre de chunks du document. */