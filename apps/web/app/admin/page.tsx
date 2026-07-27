import { getServerApiBase } from '../../lib/api';

async function summary() {
  const base = getServerApiBase();
  try {
    return await (await fetch(`${base}/admin/summary`, { cache: 'no-store' })).json();
  } catch {
    return { events: 0, open_calls: 0, open_registrations: 0, subscribers: 0, needs_review: 0 };
  }
}

export default async function Admin() {
  const s = await summary();
  return (
    <main>
      <h1>Painel administrativo</h1>
      <section className="grid">
        <div className="card"><h2>{s.events}</h2><p>Eventos</p></div>
        <div className="card"><h2>{s.open_calls}</h2><p>Chamadas abertas</p></div>
        <div className="card"><h2>{s.open_registrations}</h2><p>Inscrições abertas</p></div>
        <div className="card"><h2>{s.subscribers}</h2><p>Assinantes</p></div>
        <div className="card"><h2>{s.needs_review}</h2><p>Itens para revisão</p></div>
      </section>
      <section className="card" style={{ marginTop: 24 }}>
        <h2>Próximos módulos</h2>
        <p>Fila de revisão, possíveis duplicatas, falhas de coleta, histórico de alterações e publicação assistida.</p>
      </section>
    </main>
  );
}
