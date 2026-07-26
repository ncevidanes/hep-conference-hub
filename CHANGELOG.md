# Changelog

Todas as mudanças relevantes deste projeto serão documentadas neste arquivo.

O formato segue as ideias de *Keep a Changelog* e o versionamento segue
*Semantic Versioning*.

## [1.0.0] — 2026-07-26

### Adicionado

- portal Next.js para consulta e filtragem de eventos;
- API FastAPI com PostgreSQL e documentação OpenAPI;
- crawler Scrapy para páginas oficiais e páginas internas;
- processamento assíncrono com Celery e Redis;
- separação entre estado do evento, submissão e inscrição;
- recursos específicos de submissão, inscrição, programa, cronograma,
  contribuições e proceedings;
- metadados de evidência, confiança e última verificação;
- descoberta e catálogo de eventos da América Latina;
- suíte de testes unitários;
- documentação técnica em PDF e LaTeX;
- metadados de citação e publicação para GitHub e Zenodo.

### Limitações conhecidas

- autenticação administrativa ainda não implementada;
- newsletter ainda requer double opt-in, cancelamento e provedor transacional;
- resultados do crawler necessitam fluxo de staging e revisão editorial;
- observabilidade, backups e testes de integração ainda são itens de produção.
