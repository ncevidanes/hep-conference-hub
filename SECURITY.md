# Política de segurança

## Relato responsável

Não publique credenciais, dados pessoais ou detalhes exploráveis em issues
públicas. Entre em contato com o mantenedor por um canal privado do GitHub.

## Escopo sensível

- autenticação e painel administrativo;
- banco PostgreSQL e backups;
- Redis e filas Celery;
- dados de assinantes da newsletter;
- tokens de GitHub, Zenodo e provedores de e-mail;
- importação automatizada de conteúdo externo.

## Práticas obrigatórias

- não versionar `.env`;
- usar segredos do GitHub Actions;
- rotacionar tokens expostos;
- restringir portas em produção;
- manter dependências atualizadas;
- validar e sanitizar dados coletados;
- aplicar política LGPD antes de uso público da newsletter.
