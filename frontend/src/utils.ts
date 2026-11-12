// "2026-10-05" devient "5 octobre 2026"

export function formaterDate(iso : string) : string {
    if (!iso) return "";
    const date = new Date(iso + "T00:00:00");
    return date.toLocaleDateString("fr-FR", { day : "numeric", month : "long", year : "numeric" });
}

export function messageDErreur(e : unknown) : string {
    return e instanceof Error ? e.message : "Une erreur est survenue."
}