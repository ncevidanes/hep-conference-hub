# HEP Conference Hub

MVP para reunir congressos, simpósios, workshops e escolas com submissão de trabalhos em:

- física de altas energias;
- CERN e experimentos do LHC;
- colisões de partículas;
- ATLAS, CMS, ALICE e LHCb;
- detectores, calorimetria e instrumentação;
- computação científica, ROOT, Geant4, HPC e IA para HEP.

## Componentes

- `apps/api`: FastAPI, SQLAlchemy e PostgreSQL;
- `apps/web`: Next.js;
- `apps/crawler`: Scrapy, com spider inicial para CERN Indico;
- `worker` e `beat`: Celery para atualização de status e coletas agendadas;
- Redis: fila e backend das tarefas;
- painel administrativo inicial;
- assinatura de newsletter.

## Executar

Requisitos: Docker e Docker Compose.

```bash
cp .env.example .env
docker compose up --build -d
docker compose exec api python -m app.seed
```

Acesse:

- Portal: `http://localhost:3000`
- API: `http://localhost:8000/docs`
- Saúde: `http://localhost:8000/health`
- Painel: `http://localhost:3000/admin`

## Rodar crawler localmente

```bash
cd apps/crawler
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
scrapy crawl cern_indico
```

A saída será criada em `apps/crawler/output/events.jsonl`.

## Importante

Os registros de referência do `seed.py` usam fontes oficiais e conservam URL, trecho, confiança e data de verificação. Eles ainda não substituem a coleta automatizada e a revisão editorial. Para produção, implemente:

1. importação dos candidatos do crawler para uma tabela de staging;
2. armazenamento do HTML/trecho usado como evidência;
3. confirmação por fonte oficial;
4. autenticação e autorização do painel;
5. double opt-in e cancelamento da newsletter;
6. provedor transacional de e-mail;
7. política LGPD, termos e canal de correção;
8. rate limit, observabilidade, backup e testes de integração;
9. Playwright apenas para páginas que exigem JavaScript;
10. cadastro configurável de fontes e frequência de coleta.

## Fluxo de produção recomendado

`fonte -> crawler -> staging -> normalização -> deduplicação -> confiança -> revisão -> publicação -> alerta`

## Correção dos dados demonstrativos antigos

A versão corrigida substitui os prazos artificiais por registros verificáveis e links diretos.
Depois de atualizar os arquivos, execute:

```bash
docker compose up --build -d api web
docker compose exec api python -m app.seed
```

O `seed` agora funciona como atualização: corrige registros já existentes e remove as chamadas demonstrativas antigas.


## Prioridade 1 — situação temporal do evento

A API agora calcula `event_status` independentemente do estado da submissão:

- `upcoming`: evento futuro;
- `ongoing`: evento em andamento;
- `finished`: evento realizado;
- `unknown`: data ainda não confirmada.

Por padrão, `GET /api/v1/events` exclui eventos realizados do radar principal. Para consultá-los, use `event_status=finished` ou `include_finished=true`.

## Prioridade 2 — submissão versus inscrição

A aplicação agora trata três dimensões independentes:

- `event_status`: situação temporal do evento;
- `submission_status`: situação da chamada de trabalhos;
- `registration_status`: situação de cada fase de inscrição.

As inscrições são normalizadas em `registration_windows`. Cada linha representa
uma fase específica, como inscrição antecipada ou regular. Assim, o encerramento
da fase antecipada não é confundido com o encerramento de todas as inscrições.

O caso de referência ICHEP 2026 registra, com evidência da página oficial:

- submissão de resumos encerrada, mesmo sem uma data de encerramento publicada no bloco consultado;
- abertura das inscrições em 10/01/2026;
- inscrição antecipada encerrada em 15/05/2026;
- inscrição regular encerrada em 23/07/2026.

Após aplicar a atualização:

```bash
docker compose up --build -d api worker beat web
docker compose exec api python -m app.seed
```

A tabela `registration_windows` é criada automaticamente na inicialização da API.
Não é necessário remover o volume PostgreSQL.

### Testes

Execute no contêiner da API, que já possui SQLAlchemy e python-dateutil:

```bash
docker compose run --rm --no-deps \
  -v "$PWD/apps/api/app:/app/app:ro" \
  -v "$PWD/apps/crawler:/app/crawler:ro" \
  -v "$PWD/tests:/app/tests:ro" \
  api \
  sh -lc 'PYTHONPATH=/app:/app/crawler python -m unittest discover -s /app/tests -v'
```

### Coletor específico do ICHEP 2026

```bash
cd apps/crawler
scrapy crawl ichep_2026
```

O item gerado mantém separadamente `submission_status` e a lista
`registrations`, com as evidências textuais usadas na extração.

## Prioridade 3 — coleta de páginas internas e datas específicas

O crawler deixou de depender somente da página inicial. Ele agora:

1. classifica links internos como `call_for_abstracts`, `important_dates`,
   `registration`, `authors`, `newsletter`, `programme` ou `proceedings`;
2. segue apenas páginas relevantes do domínio oficial e, quando configurado,
   páginas vinculadas do mesmo evento no CERN Indico;
3. extrai candidatos de prazo com URL, trecho, função da página, fuso horário e
   confiança;
4. mantém divergências entre fontes em `conflicts`, sem apagar silenciosamente
   uma das datas;
5. grava as páginas individuais em `output/pages.jsonl` e o resultado
   consolidado em `output/events_aggregated.json`.

### Caso de referência: ICHEP 2026

```bash
cd apps/crawler
scrapy crawl ichep_2026
```

O coletor visita, entre outras páginas relevantes:

- página oficial;
- datas importantes;
- orientações de inscrição;
- visão geral do evento no Indico;
- chamada de resumos;
- formulário de inscrição.

O registro de referência passa a distinguir:

- abertura de submissões em 01/12/2025;
- prazo de resumo para apresentação oral em 09/02/2026;
- prazo de resumo para pôster em 16/02/2026;
- inscrição antecipada até 15/05/2026;
- inscrição regular até 23/07/2026;
- fase presencial a partir de 24/07/2026;
- formulário de inscrição disponível até 30/07/2026.

A página `important-days.html` e a chamada do Indico podem apresentar datas
não idênticas para apresentações orais. O agregador conserva essa divergência
no bloco `conflicts`, priorizando a fonte de maior confiança apenas para a
visualização resumida.

### Coletor genérico de páginas internas

```bash
cd apps/crawler
scrapy crawl event_site \
  -a url=https://evento.org \
  -a event_key=evento-2027 \
  -a name="Evento 2027" \
  -a acronym="EVT 2027" \
  -a timezone=Europe/Zurich
```

### Testes

```bash
docker compose run --rm --no-deps \
  -v "$PWD/apps/api/app:/app/app:ro" \
  -v "$PWD/apps/crawler:/app/crawler:ro" \
  -v "$PWD/tests:/app/tests:ro" \
  api \
  sh -lc 'PYTHONPATH=/app:/app/crawler python -m unittest discover -s /app/tests -v'
```

A Prioridade 3 possui 25 testes no conjunto completo das prioridades 1–3.

## Prioridade 4 — links funcionais específicos

Os eventos agora possuem recursos auditáveis classificados por função:

- `submission`: chamada ou página de submissão;
- `registration`: inscrição;
- `programme`: visão do programa científico;
- `timetable`: cronograma detalhado;
- `contributions`: lista de contribuições;
- `proceedings`: instruções ou publicação dos anais.

A API devolve esses links em `resources`. O frontend os apresenta em ordem
funcional e só usa os URLs antigos de `calls` e `registrations` como fallback.
O crawler distingue programa, cronograma e lista de contribuições e inclui uma
lista consolidada de `resources` em `output/events_aggregated.json`.

Depois de atualizar o código:

```bash
docker compose up --build -d api web
docker compose exec api python -m app.seed
```

A tabela `event_resources` é criada automaticamente pelo SQLAlchemy na
inicialização da API; não é necessário apagar o volume do PostgreSQL.

## Prioridade 5 — fonte, confiança e última verificação

A API e o portal agora tornam a proveniência dos dados visível. Eventos,
submissões, inscrições e recursos recebem dois campos derivados, sem criar
novas colunas no banco:

- `confidence_level`: `high`, `medium`, `low` ou `unknown`;
- `verification_freshness`: `current`, `aging`, `stale` ou `unknown`.

As faixas adotadas são:

- confiança alta: pontuação maior ou igual a 0,90;
- confiança média: de 0,70 a 0,89;
- confiança baixa: abaixo de 0,70;
- verificação recente: até 7 dias;
- rever em breve: de 8 a 30 dias;
- verificação desatualizada: mais de 30 dias.

Cada cartão exibe um resumo da verificação e um painel recolhível **Fontes e
auditoria dos dados**, contendo:

- URL exata da fonte;
- domínio da fonte;
- trecho usado como evidência;
- data e hora da última verificação;
- grau de confiança e pontuação percentual;
- estado de recência da verificação.

O endpoint administrativo `/api/v1/admin/summary` também informa a quantidade
de eventos verificados e de verificações desatualizadas.

Depois de aplicar a atualização:

```bash
docker compose up --build -d api web
docker compose exec api python -m app.seed
```

Não há migração de banco nesta prioridade. Os valores legíveis são calculados a
partir de `confidence_score` e `last_verified_at`.

### Testes

```bash
docker compose run --rm --no-deps \
  -v "$PWD/apps/api/app:/app/app:ro" \
  -v "$PWD/apps/crawler:/app/crawler:ro" \
  -v "$PWD/tests:/app/tests:ro" \
  api \
  sh -lc 'PYTHONPATH=/app:/app/crawler python -m unittest discover -s /app/tests -v'
```

O conjunto completo das Prioridades 1–5 possui 40 testes.


## Expansão regional — América Latina

O catálogo de referência passa de 4 para 11 eventos, com sete registros
latino-americanos verificados:

- SILAFAE 2026 — Bogotá, Colômbia;
- PHENOEXP 2026 — São Paulo, Brasil;
- RPC 2026 — Rio de Janeiro, Brasil;
- Gamma Connection 2026 — Santiago, Chile;
- PIPI Meeting II — La Plata, Argentina;
- Advances in Quantum Gravity & Strings — La Plata, Argentina;
- RADPyC 2026 — Cidade do México, México.

Os dados regionais ficam isolados em
`apps/api/app/data/latin_america_2026.py`. O `seed.py` continua responsável
apenas pela atualização do banco e combina o catálogo-base com o catálogo
regional.

### Filtro regional

A API aceita:

```text
GET /api/v1/events?region=latin-america
GET /api/v1/events?region=other
GET /api/v1/events?region=unknown
```

O campo `region` é derivado de `country_code`; portanto, esta expansão não cria
nova coluna nem exige migração do PostgreSQL. A interface possui o seletor
**América Latina** e novas áreas para astropartículas e HEP teórica.

### Coleta regional em lote

```bash
cd apps/crawler
scrapy crawl latin_america_events
```

As observações são gravadas em `output/latin_america_pages.jsonl` e o
resultado consolidado em `output/latin_america/events_aggregated.json`.

Esse spider usa o catálogo declarativo em
`conference_crawler/sources/latin_america.py`, segue páginas internas relevantes
e permite domínios oficiais vinculados do mesmo evento, como FisIndico,
Indico Global, Indico UNAM e CTAO Indico.

### Descoberta de novos eventos

```bash
cd apps/crawler
scrapy crawl latin_america_discovery
```

Os candidatos são gravados em `output/latin_america_candidates.jsonl`.

O spider de descoberta acompanha:

- LAA-HECAP, como fonte comunitária especializada em HECAP;
- agenda do CLAF, como calendário regional amplo.

Os itens descobertos são candidatos de staging com confiança moderada. Eles não
são publicados automaticamente sem validação da página oficial.

Atalhos equivalentes:

```bash
make crawl-latam
make crawl-latam-discovery
```
