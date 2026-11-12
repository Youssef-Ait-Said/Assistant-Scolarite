import type { Source } from "../types";
import { formaterDate } from "../utils";

interface Props {
  source: Source;
  surligne?: boolean;
}

// Une source : document, section, page, date, score et extrait (tout ce que le TP demande)
export default function SourceCard({ source, surligne = false }: Props) {
  const pourcentage = Math.round(Math.max(0, Math.min(1, source.score)) * 100);

  return (
    <article data-source={source.id} className={"source" + (surligne ? " surlignee" : "")}>
      <header className="source-entete">
        <span className="source-numero">{source.id}</span>
        <div className="source-titre">
          <strong>{source.file}</strong>
          <span className="source-reference">{source.reference}</span>
        </div>
      </header>

      <div className="source-puces">
        {source.type && <span className="puce">{source.type}</span>}
        <span className="puce">Page {source.page}</span>
        {source.date && <span className="puce">{formaterDate(source.date)}</span>}
      </div>

      {source.section && <div className="source-section">{source.section}</div>}

      <p className="source-extrait">{source.excerpt}</p>

      <div className="source-score" title="Similarité entre la question et ce passage (1 = identique)">
        <span className="source-score-barre"><span style={{ width: pourcentage + "%" }} /></span>
        <span className="source-score-valeur">Score {source.score.toFixed(2)}</span>
      </div>
    </article>
  );
}
