import type { Source } from "../types";
import { formaterDate } from "../utils";

interface Props {
  source: Source;
  surligne?: boolean;
}

// Une source : document, section, page, date, score et extrait
export default function SourceCard({ source, surligne = false }: Props) {
  return (
    <article data-source={source.id} className={"source" + (surligne ? " surlignee" : "")}>
      <h4>
        <span className="source-numero">[{source.id}]</span> {source.file}
      </h4>
      <dl className="source-infos">
        <div><dt>Référence</dt><dd>{source.reference}</dd></div>
        <div><dt>Section</dt><dd>{source.section || "—"}</dd></div>
        <div><dt>Page</dt><dd>{source.page}</dd></div>
        <div><dt>Date</dt><dd>{formaterDate(source.date)}</dd></div>
        <div><dt>Score</dt><dd>{source.score.toFixed(2)}</dd></div>
      </dl>
      <p className="source-extrait">{source.excerpt}</p>
    </article>
  );
}

// Affiche une source avec tout ce que le TP demande : document, section, page, date, score, extrait.
//Utilisée dans le panneau de l’assistant et dans l’écran de recherche.