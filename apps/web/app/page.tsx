import EventCard from '../components/EventCard';
import Newsletter from '../components/Newsletter';

type SearchParams = Promise<{
  q?: string;
  submission_status?: string;
  registration_status?: string;
  area?: string;
  region?: string;
  event_status?: string;
}>;

async function getEvents(params: {
  q?: string;
  submission_status?: string;
  registration_status?: string;
  area?: string;
  region?: string;
  event_status?: string;
}) {
  const base = process.env.INTERNAL_API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
  const query = new URLSearchParams({ limit: '30' });

  if (params.q?.trim()) query.set('q', params.q.trim());
  if (params.submission_status && params.submission_status !== 'all') {
    query.set('submission_status', params.submission_status);
  }
  if (params.registration_status && params.registration_status !== 'all') {
    query.set('registration_status', params.registration_status);
  }
  if (params.area && params.area !== 'all') query.set('area', params.area);
  if (params.region && params.region !== 'all') query.set('region', params.region);

  const temporalFilter = params.event_status || 'active';
  if (temporalFilter === 'all') {
    query.set('include_finished', 'true');
  } else if (temporalFilter !== 'active') {
    query.set('event_status', temporalFilter);
  }

  try {
    const response = await fetch(`${base}/events?${query.toString()}`, { cache: 'no-store' });
    if (!response.ok) return { items: [], total: 0 };
    return response.json();
  } catch {
    return { items: [], total: 0 };
  }
}

export default async function Home({ searchParams }: { searchParams: SearchParams }) {
  const params = await searchParams;
  const data = await getEvents(params);
  const temporalFilter = params.event_status || 'active';
  const sectionTitle = temporalFilter === 'finished'
    ? 'Eventos realizados'
    : temporalFilter === 'ongoing'
      ? 'Eventos em andamento'
      : temporalFilter === 'upcoming'
        ? 'Próximos eventos'
        : 'Oportunidades monitoradas';

  return (
    <main>
      <section className="hero">
        <span className="pill">Física de Altas Energias · CERN · Colisões de Partículas</span>
        <h1>Encontre onde seu próximo trabalho científico pode ser apresentado.</h1>
        <p>
          Congressos, simpósios, workshops e escolas com chamadas de resumos e artigos,
          prazos verificados e links para a fonte oficial.
        </p>
      </section>

      <form className="filters" method="get" action="/">
        <input
          name="q"
          defaultValue={params.q || ''}
          placeholder="Buscar por tema, evento ou colaboração"
          aria-label="Buscar eventos"
        />

        <select
          name="event_status"
          defaultValue={temporalFilter}
          aria-label="Situação temporal do evento"
        >
          <option value="active">Futuros e em andamento</option>
          <option value="upcoming">Somente eventos futuros</option>
          <option value="ongoing">Eventos em andamento</option>
          <option value="finished">Eventos realizados</option>
          <option value="unknown">Data ainda não confirmada</option>
          <option value="all">Todos os eventos</option>
        </select>

        <select
          name="submission_status"
          defaultValue={params.submission_status || 'all'}
          aria-label="Situação da submissão"
        >
          <option value="all">Todas as submissões</option>
          <option value="open">Submissões abertas</option>
          <option value="extended">Prazos prorrogados</option>
          <option value="upcoming">Submissões futuras</option>
          <option value="closed">Submissões encerradas</option>
          <option value="unknown">Situação não confirmada</option>
        </select>

        <select
          name="registration_status"
          defaultValue={params.registration_status || 'all'}
          aria-label="Situação da inscrição"
        >
          <option value="all">Todas as inscrições</option>
          <option value="open">Inscrições abertas</option>
          <option value="upcoming">Inscrições futuras</option>
          <option value="closed">Inscrições encerradas</option>
          <option value="not_announced">Ainda não anunciadas</option>
          <option value="unknown">Situação não confirmada</option>
        </select>

        <select name="region" defaultValue={params.region || 'all'} aria-label="Região">
          <option value="all">Todas as regiões</option>
          <option value="latin-america">América Latina</option>
          <option value="other">Outras regiões</option>
          <option value="unknown">Região não confirmada</option>
        </select>

        <select name="area" defaultValue={params.area || 'all'} aria-label="Área científica">
          <option value="all">Todas as áreas</option>
          <option value="high-energy-physics">Física de Altas Energias</option>
          <option value="detectors">Detectores e calorimetria</option>
          <option value="astroparticle-physics">Astropartículas</option>
          <option value="theoretical-hep">HEP teórica</option>
          <option value="scientific-computing">Computação científica</option>
        </select>

        <button className="button search-button" type="submit">Buscar</button>
        {(params.q || params.submission_status || params.registration_status || params.area || params.region || params.event_status) && (
          <a className="clear-button" href="/">Limpar filtros</a>
        )}
      </form>

      <h2 className="section-title">{sectionTitle}</h2>

      {data.items.length ? (
        <section className="grid">
          {data.items.map((event: any) => <EventCard key={event.slug} event={event} />)}
        </section>
      ) : (
        <div className="card">
          <h3>Nenhum evento encontrado</h3>
          <p>Altere os filtros ou aguarde a próxima coleta das fontes oficiais.</p>
        </div>
      )}

      <Newsletter />
    </main>
  );
}
