export default function SectionIndisponible({ titre }: { titre: string }) {
  return (
    <section>
      <h1>{titre}</h1>
      <p className="vide">Cette section n'est pas disponible dans cette version du portail.</p>
    </section>
  );
}