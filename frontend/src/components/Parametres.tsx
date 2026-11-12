interface Props {
  topK: number;
  type: string;
  types: string[];
  onTopK: (valeur: number) => void;
  onType: (valeur: string) => void;
}

const MIN = 1;
const MAX = 20;

// Les deux réglages demandés par le TP : nombre de passages retenus (top_k) et filtre par type
export default function Parametres({ topK, type, types, onTopK, onType }: Props) {
  function changer(valeur: number) {
    if (valeur >= MIN && valeur <= MAX) onTopK(valeur);
  }

  return (
    <div className="parametres">
      <div className="parametre">
        <span className="parametre-nom" title="Nombre de passages (fragments) envoyés au modèle pour répondre">
          Passages retenus
        </span>
        <div className="compteur" role="group" aria-label="Nombre de passages retenus">
          <button type="button" onClick={() => changer(topK - 1)} disabled={topK <= MIN} aria-label="Moins">−</button>
          <input
            type="number"
            min={MIN}
            max={MAX}
            value={topK}
            onChange={(e) => changer(Number(e.target.value))}
            aria-label="Nombre de passages retenus"
          />
          <button type="button" onClick={() => changer(topK + 1)} disabled={topK >= MAX} aria-label="Plus">+</button>
        </div>
      </div>

      <div className="parametre">
        <span className="parametre-nom" title="Limiter la recherche à un type de document">Type de document</span>
        <select value={type} onChange={(e) => onType(e.target.value)} aria-label="Type de document">
          <option value="">Tous les documents</option>
          {types.map((t) => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>
      </div>
    </div>
  );
}
