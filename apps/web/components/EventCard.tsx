type VerificationMetadata = {
  source_url?: string;
  source_excerpt?: string;
  confidence_score?: number;
  confidence_level?: string;
  last_verified_at?: string;
  verification_freshness?: string;
};

type Call = VerificationMetadata & {
  status: string;
  call_type: string;
  title?: string;
  opens_at?: string;
  deadline_at?: string;
  extended_deadline_at?: string;
  timezone?: string;
  submission_url?: string;
};

type Registration = VerificationMetadata & {
  registration_type: string;
  title?: string;
  status: string;
  opens_on?: string;
  deadline_on?: string;
  timezone?: string;
  registration_url?: string;
};

type Resource = VerificationMetadata & {
  role: string;
  label: string;
  url: string;
  is_primary?: boolean;
};

type Event = {
  name: string;
  acronym?: string;
  slug: string;
  description?: string;
  tags: string;
  organizer?: string;
  city?: string;
  country_code?: string;
  region?: string;
  start_date?: string;
  end_date?: string;
  event_status: string;
  official_url: string;
  source_type?: string;
  confidence_score?: number;
  confidence_level?: string;
  verified?: boolean;
  last_verified_at?: string;
  verification_freshness?: string;
  calls: Call[];
  registrations: Registration[];
  resources: Resource[];
};

const SUBMISSION_STATUS_LABELS: Record<string, string> = {
  open: 'Submissão aberta',
  extended: 'Prazo prorrogado',
  upcoming: 'Submissão futura',
  closed: 'Submissão encerrada',
  rolling: 'Submissão contínua',
  conflicting: 'Informação conflitante',
  unknown: 'Situação da submissão não confirmada',
};

const REGISTRATION_STATUS_LABELS: Record<string, string> = {
  not_announced: 'Inscrição ainda não anunciada',
  open: 'Inscrição aberta',
  upcoming: 'Inscrição futura',
  closed: 'Inscrição encerrada',
  conflicting: 'Informação conflitante',
  unknown: 'Situação da inscrição não confirmada',
};

const EVENT_STATUS_LABELS: Record<string, string> = {
  upcoming: 'Evento futuro',
  ongoing: 'Evento em andamento',
  finished: 'Evento realizado',
  unknown: 'Data não confirmada',
};

const CONFIDENCE_LABELS: Record<string, string> = {
  high: 'Confiança alta',
  medium: 'Confiança média',
  low: 'Confiança baixa',
  unknown: 'Confiança não calculada',
};

const FRESHNESS_LABELS: Record<string, string> = {
  current: 'Verificação recente',
  aging: 'Rever em breve',
  stale: 'Verificação desatualizada',
  unknown: 'Ainda não verificado',
};

const SUBMISSION_PRIORITY = ['extended', 'open', 'upcoming', 'rolling', 'conflicting', 'unknown', 'closed'];
const REGISTRATION_PRIORITY = ['open', 'upcoming', 'conflicting', 'unknown', 'not_announced', 'closed'];

function formatCalendarDate(value?: string) {
  if (!value) return null;
  const parsed = value.includes('T') ? new Date(value) : new Date(`${value}T12:00:00Z`);
  return parsed.toLocaleDateString('pt-BR', { timeZone: 'UTC' });
}

function formatVerificationDate(value?: string) {
  if (!value) return 'data não registrada';
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return 'data inválida';
  return parsed.toLocaleString('pt-BR', {
    dateStyle: 'short',
    timeStyle: 'short',
  });
}

function formatEventPeriod(start?: string, end?: string) {
  const startLabel = formatCalendarDate(start);
  const endLabel = formatCalendarDate(end);
  if (!startLabel) return 'Data do evento ainda não confirmada';
  if (!endLabel || end === start) return startLabel;
  return `${startLabel} a ${endLabel}`;
}

function formatConfidence(score?: number) {
  if (score === undefined || score === null || Number.isNaN(score)) return null;
  return `${Math.round(Math.max(0, Math.min(1, score)) * 100)}%`;
}

function sourceHost(url?: string) {
  if (!url) return 'fonte não cadastrada';
  try {
    return new URL(url).hostname.replace(/^www\./, '');
  } catch {
    return url;
  }
}

function lowercaseFirst(value: string) {
  return value ? value.charAt(0).toLocaleLowerCase('pt-BR') + value.slice(1) : value;
}

function aggregateStatus(items: Array<{ status: string }>, priority: string[]) {
  return [...items].sort((a, b) => priority.indexOf(a.status) - priority.indexOf(b.status))[0]?.status;
}

const RESOURCE_ORDER = [
  'submission',
  'registration',
  'programme',
  'timetable',
  'contributions',
  'proceedings',
  'important_dates',
  'authors',
  'payment',
  'other',
];

const FALLBACK_RESOURCE_LABELS: Record<string, string> = {
  submission: 'Chamada de trabalhos',
  registration: 'Inscrição',
  programme: 'Programa científico',
  timetable: 'Cronograma',
  contributions: 'Lista de contribuições',
  proceedings: 'Proceedings',
  important_dates: 'Datas importantes',
  authors: 'Informações para autores',
  payment: 'Pagamento',
  other: 'Mais informações',
};

function buildResourceLinks(event: Event, calls: Call[], registrations: Registration[]) {
  const links: Resource[] = [...(event.resources || [])];
  const existingRoles = new Set(links.map((resource) => resource.role));

  if (!existingRoles.has('submission')) {
    for (const call of calls) {
      if (call.submission_url) {
        links.push({ role: 'submission', label: 'Chamada de trabalhos', url: call.submission_url });
      }
    }
  }
  if (!existingRoles.has('registration')) {
    for (const registration of registrations) {
      if (registration.registration_url) {
        links.push({ role: 'registration', label: 'Inscrição', url: registration.registration_url });
      }
    }
  }

  const byUrl = new Map<string, Resource>();
  for (const link of links) {
    if (!link.url || link.url === event.official_url) continue;
    const current = byUrl.get(link.url);
    if (!current || (link.is_primary && !current.is_primary)) {
      byUrl.set(link.url, link);
    }
  }

  return [...byUrl.values()].sort((a, b) => {
    const roleOrder = RESOURCE_ORDER.indexOf(a.role) - RESOURCE_ORDER.indexOf(b.role);
    if (roleOrder !== 0) return roleOrder;
    if (Boolean(a.is_primary) !== Boolean(b.is_primary)) return a.is_primary ? -1 : 1;
    return a.label.localeCompare(b.label, 'pt-BR');
  });
}

function EvidenceItem({ title, evidence }: { key?: string; title: string; evidence: VerificationMetadata }) {
  const confidence = evidence.confidence_level || 'unknown';
  const freshness = evidence.verification_freshness || 'unknown';
  const score = formatConfidence(evidence.confidence_score);

  return (
    <li className="evidence-item">
      <div className="evidence-title-row">
        <strong>{title}</strong>
        <span className={`audit-pill confidence-${confidence}`}>
          {CONFIDENCE_LABELS[confidence] || confidence}{score ? ` · ${score}` : ''}
        </span>
        <span className={`audit-pill freshness-${freshness}`}>
          {FRESHNESS_LABELS[freshness] || freshness}
        </span>
      </div>
      <p className="evidence-meta">
        Verificado em {formatVerificationDate(evidence.last_verified_at)}
        {evidence.source_url && (
          <>
            {' · '}
            <a href={evidence.source_url} target="_blank" rel="noopener noreferrer">
              {sourceHost(evidence.source_url)}
            </a>
          </>
        )}
      </p>
      {evidence.source_excerpt && <blockquote>{evidence.source_excerpt}</blockquote>}
    </li>
  );
}

export default function EventCard({ event }: { event: Event }) {
  const calls = event.calls || [];
  const registrations = event.registrations || [];
  const submissionStatus = aggregateStatus(calls, SUBMISSION_PRIORITY);
  const registrationStatus = aggregateStatus(registrations, REGISTRATION_PRIORITY);
  const activeRegistration = [...registrations].sort((a, b) => {
    const statusOrder = REGISTRATION_PRIORITY.indexOf(a.status) - REGISTRATION_PRIORITY.indexOf(b.status);
    if (statusOrder !== 0) return statusOrder;
    return (b.deadline_on || '').localeCompare(a.deadline_on || '');
  })[0];

  const resourceLinks = buildResourceLinks(event, calls, registrations);
  const confidence = event.confidence_level || 'unknown';
  const freshness = event.verification_freshness || 'unknown';
  const confidenceScore = formatConfidence(event.confidence_score);

  return (
    <article className={`card event-${event.event_status}`}>
      <div className="status-row">
        <span className={`pill event-status ${event.event_status}`}>
          {EVENT_STATUS_LABELS[event.event_status] || event.event_status}
        </span>
        <span className={`pill submission-status ${submissionStatus || 'unknown'}`}>
          {submissionStatus
            ? SUBMISSION_STATUS_LABELS[submissionStatus] || submissionStatus
            : 'Submissão não cadastrada'}
        </span>
        <span className={`pill registration-status ${registrationStatus || 'unknown'}`}>
          {registrationStatus
            ? activeRegistration?.title
              ? `${activeRegistration.title}: ${lowercaseFirst(REGISTRATION_STATUS_LABELS[registrationStatus] || registrationStatus)}`
              : REGISTRATION_STATUS_LABELS[registrationStatus] || registrationStatus
            : 'Inscrição não cadastrada'}
        </span>
        <span className="pill">{event.acronym || 'Evento'}</span>
      </div>

      <div className="verification-summary" aria-label="Situação da verificação dos dados">
        <span className={`audit-pill freshness-${freshness}`}>
          {FRESHNESS_LABELS[freshness] || freshness}
        </span>
        <span className={`audit-pill confidence-${confidence}`}>
          {CONFIDENCE_LABELS[confidence] || confidence}{confidenceScore ? ` · ${confidenceScore}` : ''}
        </span>
        <span className="verification-date">
          {event.verified ? 'Dados verificados' : 'Dados ainda não confirmados'} · {formatVerificationDate(event.last_verified_at)}
        </span>
      </div>

      <h3>{event.name}</h3>
      <p>{event.description}</p>

      <p className="event-date">Evento: {formatEventPeriod(event.start_date, event.end_date)}</p>

      <div className="opportunity-details">
        <div className="opportunity-block">
          <h4>Submissão de trabalhos</h4>
          {calls.length ? (
            <ul className="registration-list">
              {calls
                .slice()
                .sort((a, b) => (a.deadline_at || '').localeCompare(b.deadline_at || ''))
                .map((call) => {
                  const deadline = call.extended_deadline_at || call.deadline_at;
                  return (
                    <li key={`${call.call_type}-${deadline || call.title}`}>
                      <strong>{call.title || 'Submissão'}:</strong>{' '}
                      {lowercaseFirst(SUBMISSION_STATUS_LABELS[call.status] || call.status)}
                      {call.opens_at && ` · abertura em ${formatCalendarDate(call.opens_at)}`}
                      {deadline && ` · prazo em ${formatCalendarDate(deadline)}`}
                      {!deadline && call.status === 'closed' && ' · data do encerramento não localizada'}
                    </li>
                  );
                })}
            </ul>
          ) : (
            <p className="muted">Informação de submissão ainda não cadastrada.</p>
          )}
        </div>

        <div className="opportunity-block">
          <h4>Inscrição no evento</h4>
          {registrations.length ? (
            <ul className="registration-list">
              {registrations
                .slice()
                .sort((a, b) => (a.opens_on || a.deadline_on || '').localeCompare(b.opens_on || b.deadline_on || ''))
                .map((item) => (
                  <li key={`${item.registration_type}-${item.deadline_on || item.title}`}>
                    <strong>{item.title || 'Inscrição'}:</strong>{' '}
                    {lowercaseFirst(REGISTRATION_STATUS_LABELS[item.status] || item.status)}
                    {item.opens_on && ` · abertura em ${formatCalendarDate(item.opens_on)}`}
                    {item.deadline_on && ` · prazo em ${formatCalendarDate(item.deadline_on)}`}
                  </li>
                ))}
            </ul>
          ) : (
            <p className="muted">Informação de inscrição ainda não cadastrada.</p>
          )}
        </div>
      </div>

      <p className="small">{[
        event.city,
        event.country_code,
        event.region === 'latin-america' ? 'América Latina' : null,
        event.organizer,
      ].filter(Boolean).join(' · ')}</p>

      <div className="card-actions" aria-label="Links específicos do evento">
        <a className="button" href={event.official_url} target="_blank" rel="noopener noreferrer">
          Página oficial
        </a>
        {resourceLinks.map((resource) => (
          <a
            key={`${resource.role}-${resource.url}`}
            className={`button secondary resource-${resource.role}`}
            href={resource.url}
            target="_blank"
            rel="noopener noreferrer"
            title={resource.source_excerpt || FALLBACK_RESOURCE_LABELS[resource.role]}
          >
            {resource.label || FALLBACK_RESOURCE_LABELS[resource.role] || 'Mais informações'}
          </a>
        ))}
      </div>

      <details className="audit-panel">
        <summary>Fontes e auditoria dos dados</summary>
        <div className="audit-content">
          <div className="audit-overview">
            <p><strong>Fonte principal:</strong> <a href={event.official_url} target="_blank" rel="noopener noreferrer">{sourceHost(event.official_url)}</a></p>
            <p><strong>Método:</strong> {event.source_type || 'não informado'}</p>
            <p><strong>Última verificação:</strong> {formatVerificationDate(event.last_verified_at)}</p>
          </div>

          {calls.length > 0 && (
            <section className="evidence-section">
              <h5>Submissões</h5>
              <ul className="evidence-list">
                {calls.map((call) => (
                  <EvidenceItem key={`${call.call_type}-${call.source_url}`} title={call.title || call.call_type} evidence={call} />
                ))}
              </ul>
            </section>
          )}

          {registrations.length > 0 && (
            <section className="evidence-section">
              <h5>Inscrições</h5>
              <ul className="evidence-list">
                {registrations.map((registration) => (
                  <EvidenceItem
                    key={`${registration.registration_type}-${registration.source_url}`}
                    title={registration.title || registration.registration_type}
                    evidence={registration}
                  />
                ))}
              </ul>
            </section>
          )}

          {event.resources?.length > 0 && (
            <section className="evidence-section">
              <h5>Links e páginas internas</h5>
              <ul className="evidence-list">
                {event.resources.map((resource) => (
                  <EvidenceItem key={`${resource.role}-${resource.url}`} title={resource.label} evidence={resource} />
                ))}
              </ul>
            </section>
          )}
        </div>
      </details>
    </article>
  );
}
