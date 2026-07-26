# Publicação no GitHub e no Zenodo

## Metadados adotados

- repositório: `ncevidanes/hep-conference-hub`;
- versão inicial: `1.0.0`;
- tag: `v1.0.0`;
- título: *HEP Conference Hub: An Auditable Portal for Discovering and Monitoring High-Energy Physics Events*;
- autor: Nelson Cevidanes Nascimento de Assis;
- licença proposta: MIT;
- tipo no Zenodo: Software;
- acesso: aberto.

Revise nome, ORCID e licença antes da primeira release. O ORCID foi
intencionalmente omitido porque não foi fornecido.

## 1. Verificação local

```bash
bash scripts/pre_release_check.sh
```

## 2. Autenticação no GitHub

```bash
gh auth status
```

## 3. Criar e enviar o repositório

Na raiz:

```bash
bash scripts/publish_github.sh
```

O script cria `ncevidanes/hep-conference-hub`, configura `origin`, faz o primeiro commit e envia
a branch `main`. Caso o repositório já exista, ele apenas configura/verifica o
remote e envia a branch.

## 4. Ativar a integração com o Zenodo

Antes de criar a release:

1. entre no Zenodo;
2. vincule a conta do GitHub;
3. abra o menu **GitHub**;
4. selecione **Sync now**;
5. localize `ncevidanes/hep-conference-hub`;
6. habilite o repositório.

## 5. Criar a primeira release

Somente depois de habilitar o repositório no Zenodo:

```bash
bash scripts/create_release.sh
```

O script cria a tag anotada `v1.0.0`, envia a tag e publica a GitHub
Release usando `RELEASE_NOTES_v1.0.0.md`.

## 6. Conferir o Zenodo

A integração processará a release e criará um registro de software com DOI.
Revise:

- título;
- autor;
- versão;
- descrição;
- licença;
- palavras-chave;
- arquivos arquivados;
- DOI da versão e DOI conceitual.

## 7. Inserir o DOI no repositório

Depois que o Zenodo atribuir o DOI:

1. acrescente o badge do DOI no `README.md`;
2. acrescente o DOI em `CITATION.cff`;
3. acrescente o DOI em `codemeta.json`;
4. faça um commit na branch `main`.

Não altere retroativamente a tag já arquivada. Os metadados atualizados serão
incorporados integralmente na próxima release.

## Badge

Substitua `ZENODO_RECORD_ID`:

```markdown
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.ZENODO_RECORD_ID.svg)](https://doi.org/10.5281/zenodo.ZENODO_RECORD_ID)
```

## Citação temporária

Nelson Cevidanes Nascimento de Assis. *HEP Conference Hub: An Auditable Portal for Discovering and Monitoring High-Energy Physics Events*. Version 1.0.0, 2026. Software.

Após a publicação, use a citação gerada no registro Zenodo.
