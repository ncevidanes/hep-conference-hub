# HEP Conference Hub

**Portal auditável para descoberta, acompanhamento e organização de congressos, simpósios, workshops e escolas de física de altas energias.**

[![CI](https://github.com/ncevidanes/hep-conference-hub/actions/workflows/ci.yml/badge.svg)](https://github.com/ncevidanes/hep-conference-hub/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](CHANGELOG.md)

> DOI do Zenodo: será acrescentado após a publicação da primeira release.

## Objetivo

O HEP Conference Hub reúne, normaliza e apresenta oportunidades científicas em:

- física de altas energias e física de partículas;
- CERN e experimentos do LHC;
- detectores, calorimetria e instrumentação;
- computação científica, ROOT, Geant4, HPC e aprendizado de máquina;
- astropartículas, neutrinos, cosmologia e HEP teórica;
- eventos da América Latina e de outras regiões.

A plataforma separa a situação temporal do evento, a submissão de trabalhos e as fases de inscrição. Cada informação pode conservar fonte, trecho de evidência, confiança e data de verificação.

## Arquitetura

```text
fontes oficiais
      |
      v
Scrapy crawler ---> staging/normalização ---> deduplicação
                                             |
                                             v
                                      FastAPI + PostgreSQL
                                             |
                               +-------------+-------------+
                               |                           |
                               v                           v
                         Next.js portal             Celery + Redis
```

Principais componentes:

- `apps/api`: FastAPI, SQLAlchemy e PostgreSQL;
- `apps/web`: Next.js e TypeScript;
- `apps/crawler`: Scrapy e extratores auditáveis;
- `worker` e `beat`: Celery;
- `redis`: fila e backend de tarefas;
- `tests`: testes de status, extração, deduplicação, recursos, verificação e região.

## Funcionalidades

- pesquisa e filtros por área, região e situação;
- distinção entre evento, submissão e inscrição;
- páginas específicas de submissão, inscrição, programa e proceedings;
- classificação de confiança e recência da verificação;
- registro de divergências entre fontes oficiais;
- catálogo de eventos latino-americanos;
- coleta específica e genérica de páginas internas;
- API REST documentada automaticamente;
- execução integral por Docker Compose.

## Início rápido

```bash
cp .env.example .env
docker compose up --build -d
docker compose exec api python -m app.seed
```

Serviços locais:

- portal: `http://localhost:3000`;
- API e OpenAPI: `http://localhost:8000/docs`;
- saúde: `http://localhost:8000/health`;
- painel inicial: `http://localhost:3000/admin`.

## Testes

```bash
docker compose run --rm --no-deps   -v "$PWD/apps/api/app:/app/app:ro"   -v "$PWD/apps/crawler:/app/crawler:ro"   -v "$PWD/tests:/app/tests:ro"   api   sh -lc 'PYTHONPATH=/app:/app/crawler python -m unittest discover -s /app/tests -v'
```

## Crawler

```bash
cd apps/crawler
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m scrapy list
python -m scrapy crawl latin_america_events
```

## Documentação

- [Documentação técnica em PDF](docs/Documentacao_Tecnica_HEP_Conference_Hub.pdf)
- [Fontes LaTeX da documentação](docs/latex/main.tex)
- [Histórico detalhado da implementação](docs/DEVELOPMENT_HISTORY.md)
- [Guia de publicação no GitHub e Zenodo](docs/PUBLICATION_GITHUB_ZENODO.md)
- [Política de segurança](SECURITY.md)
- [Como contribuir](CONTRIBUTING.md)

## Citação

O arquivo [`CITATION.cff`](CITATION.cff) permite que GitHub, Zenodo, Zotero e outras ferramentas apresentem a citação do software. Antes da atribuição do DOI, use:

> Nelson Cevidanes Nascimento de Assis. *HEP Conference Hub: An Auditable Portal for Discovering and Monitoring High-Energy Physics Events*. Version 1.0.0, 2026. Software.

Depois da publicação no Zenodo, prefira a citação exibida no registro DOI.

## Proveniência e limitações

Os dados demonstrativos e o catálogo inicial usam páginas oficiais e registram URL, evidência e verificação. O portal ainda é um MVP de pesquisa. Para operação pública contínua são necessárias autenticação administrativa, revisão editorial, política LGPD, double opt-in da newsletter, observabilidade, backups e testes de integração.

## Licença

Código distribuído sob a [Licença MIT](LICENSE). Conteúdo produzido por terceiros, nomes de eventos, logotipos e páginas referenciadas permanecem sujeitos aos direitos de seus respectivos titulares.
