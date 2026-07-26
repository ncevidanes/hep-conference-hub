# HEP Conference Hub - documentação em LaTeX

## Estrutura

- `main.tex`: arquivo principal;
- `preambulo.tex`: pacotes e configurações tipográficas;
- `capitulos/`: capítulos da documentação;
- `apendices/`: apêndices operacionais;
- `figuras/`: diagramas extraídos da versão DOCX.

## Compilação

```bash
latexmk -pdf main.tex
```

Alternativamente:

```bash
pdflatex main.tex
pdflatex main.tex
```

O documento utiliza a classe `abntex2` e foi preparado para TeX Live.
