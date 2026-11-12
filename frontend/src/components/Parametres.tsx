import { useState } from "react";

interface Props {
  topK: number;
  type: string;
  types: string[];
  onTopK: (valeur: number) => void;
  onType: (valeur: string) => void;
}

// Les deux réglages : nombre de passages retenus (top_k) et filtre par type de document
export default function Parametres({ topK, type, types, onTopK, onType }: Props) {
  // Ce que l'utilisateur tape (peut être vide un instant) ; topK ne reçoit que des valeurs valides
  const [saisie, setSaisie] = useState(String(topK));

  function changer(valeur: string) {
    setSaisie(valeur);
    const n = Number(valeur);
    if (Number.isInteger(n) && n >= 1 && n <= 20) onTopK(n);
  }

  return (
    <div className="parametres">
      <label>
        Nombre de passages retenus
        <input
          type="number"
          min={1}
          max={20}
          value={saisie}
          onChange={(e) => changer(e.target.value)}
          onBlur={() => setSaisie(String(topK))}
        />
      </label>
      <label>
        Type de document
        <select value={type} onChange={(e) => onType(e.target.value)}>
          <option value="">Tous les documents</option>
          {types.map((t) => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>
      </label>
    </div>
  );
}