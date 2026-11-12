import type { AskResponse, DocumentInfo, HealthResponse, SearchResponse } from "../types";

// L'adresse de l'API vient de la variable d'environnement VITE_API_URL (fichier .env)
const API_URL: string = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

// Un message clair pour chaque erreur de l'API
function messageErreur(status: number): string {
  switch (status) {
    case 422:
      return "La demande est invalide. Vérifiez que la question n'est pas vide.";
    case 502:
      return "Le service de réponse ne répond pas. Réessayez dans quelques instants.";
    case 503:
      return "La base de documents est indisponible. Vérifiez que le service est démarré et que les documents sont indexés.";
    default:
      return `Une erreur est survenue (code ${status}).`;
  }
}

async function requete<T>(chemin: string, options?: RequestInit): Promise<T> {
  let reponse: Response;
  try {
    reponse = await fetch(`${API_URL}/api${chemin}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
  } catch {
    throw new ApiError(0, "Impossible de joindre le service. Vérifiez qu'il est démarré.");
  }
  if (!reponse.ok) {
    throw new ApiError(reponse.status, messageErreur(reponse.status));
  }
  return (await reponse.json()) as T;
}

function corps(question: string, topK: number, type: string): string {
  return JSON.stringify({ question, top_k: topK, filters: { type: type || null } });
}

export function poserQuestion(question: string, topK: number, type: string) {
  return requete<AskResponse>("/ask", { method: "POST", body: corps(question, topK, type) });
}

export function rechercher(question: string, topK: number, type: string) {
  return requete<SearchResponse>("/search", { method: "POST", body: corps(question, topK, type) });
}

export function listerDocuments() {
  return requete<DocumentInfo[]>("/documents");
}

// État du service (GET /api/health) : affiché dans l'en-tête
export function etatService() {
  return requete<HealthResponse>("/health");
}
