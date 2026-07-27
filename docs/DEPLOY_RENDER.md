# Implantação do HEP Conference Hub no Render

Esta configuração publica a versão demonstrativa do portal com três recursos:

- `hep-conference-hub-web-ncevidanes`: servidor Next.js;
- `hep-conference-hub-api-ncevidanes`: API FastAPI;
- `hep-conference-hub-db-ncevidanes`: PostgreSQL gerenciado.

Redis, Celery e o crawler periódico permanecem fora desta primeira implantação.
Localmente, eles continuam disponíveis pelo `docker-compose.yml`.

## Arquivo de infraestrutura

O arquivo `render.yaml`, na raiz do repositório, define os três recursos. A API
recebe `DATABASE_URL` diretamente do banco. O frontend recebe a URL pública da
API por `API_EXTERNAL_URL`.

A API converte automaticamente URLs `postgresql://` e `postgres://` para o
dialeto SQLAlchemy `postgresql+psycopg://`.

## Criar o Blueprint

1. Entre no painel do Render e conecte sua conta do GitHub.
2. Escolha **New > Blueprint**.
3. Selecione `ncevidanes/hep-conference-hub`.
4. Confirme que o caminho do Blueprint é `render.yaml`.
5. Revise os três recursos e aplique o Blueprint.
6. Aguarde o banco, a API e o frontend concluírem a implantação.

A API usa `SEED_ON_STARTUP=true`. Em cada inicialização ela cria o esquema e
carrega o catálogo verificado somente quando a tabela de eventos está vazia.
Assim, reinicializações não duplicam registros e um banco novo é inicializado
automaticamente.

## URLs esperadas

Os nomes propostos produzem endereços semelhantes a:

- `https://hep-conference-hub-api-ncevidanes.onrender.com`;
- `https://hep-conference-hub-web-ncevidanes.onrender.com`.

Se um nome já estiver ocupado, altere o campo `name` em `render.yaml`. Mantenha
a referência `fromService.name` igual ao novo nome da API.

## Verificação

```bash
bash scripts/verify_render.sh \
  https://hep-conference-hub-api-ncevidanes.onrender.com \
  https://hep-conference-hub-web-ncevidanes.onrender.com
```

Também podem ser testados diretamente:

```bash
curl https://hep-conference-hub-api-ncevidanes.onrender.com/health
curl https://hep-conference-hub-web-ncevidanes.onrender.com/api/health
```

## Atualizações

Depois que o Blueprint estiver ligado à branch `main`, novos commits relevantes
disparam builds automáticos dos serviços correspondentes ao monorepo.

## Limitações da demonstração gratuita

- serviços web gratuitos entram em suspensão após período de inatividade;
- o primeiro acesso pode aguardar o despertar da API e do frontend;
- as horas gratuitas são compartilhadas pelo workspace;
- o PostgreSQL gratuito tem capacidade e duração limitadas;
- não há shell interativo nos serviços web gratuitos;
- o crawler automático, Celery worker e Celery beat exigem uma etapa posterior.

Para operação contínua, migre o banco para um plano persistente antes de seu
vencimento e avalie manter pelo menos a API em uma instância que não suspenda.
