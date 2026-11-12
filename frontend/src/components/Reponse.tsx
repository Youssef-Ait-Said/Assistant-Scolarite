interface Props {
  texte: string;
  nbSources: number;
  onCitation: (numero: number) => void;
}

// Affiche la réponse : **gras** mis en forme, et citations [1], [2] cliquables
export default function Reponse({ texte, nbSources, onCitation }: Props) {
  const morceaux = texte.split(/(\*\*[^*]+\*\*|\[\d+\])/g);

  return (
    <p className="reponse-texte">
      {morceaux.map((m, i) => {
        if (m.length > 4 && m.startsWith("**") && m.endsWith("**")) {
          return <strong key={i}>{m.slice(2, -2)}</strong>;
        }
        const citation = m.match(/^\[(\d+)\]$/);
        if (citation) {
          const n = Number(citation[1]);
          if (n >= 1 && n <= nbSources) {
            return (
              <button key={i} className="citation" onClick={() => onCitation(n)}>
                [{n}]
              </button>
            );
          }
          return (
            <span key={i} className="citation-invalide" title="Cette citation ne correspond à aucune source">
              [{n}]
            </span>
          );
        }
        return m;
      })}
    </p>
  );
}

/**Découpe la réponse en morceaux : le texte entre ** devient du gras (Gemini en écrit parfois), 
 * et chaque [n] devient un bouton cliquable. 
 * Une citation sans source correspondante est affichée en rouge, non cliquable. */