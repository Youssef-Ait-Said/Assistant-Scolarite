
// Les formes des données échangées avec l'API (elles reprennent les modèles du backend)

export interface Source {
    id : number;
    chunk_id :string;
    file : string;
    reference : string;
    type: string;
    date: string;
    page: number;
    section: string;
    excerpt: string;
    score: number;
}

export interface AskResponse {
  answer: string;
  found: boolean;
  sources: Source[];
  invalid_citations: number[];
  latency_ms: number;
}

export interface SearchResponse {
  results: Source[];
}

export interface DocumentInfo {
  file: string;
  reference: string;
  type: string;
  date: string;
  version: string;
  statut: string;
  chunks: number;
}

// Une question posée dans la session, avec sa réponse (ou son erreur)
export interface Echange {
  id: number;
  question: string;
  reponse?: AskResponse;
  erreur?: string;
}