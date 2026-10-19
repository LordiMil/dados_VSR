---
name: gerar-pdf-item
description: Gera um PDF bem formatado a partir de um item .md finalizado do case (ex. Nasser/item<N>-*.md), incluindo o setup de ambiente Windows/MSYS2 para WeasyPrint e a recriação de diagramas mermaid via Graphviz/matplotlib. Use sempre que for gerar ou regenerar um PDF a partir de markdown neste projeto — em especial pelo agente redator-pdf.
---

Esta skill documenta uma receita testada nesta máquina (Windows + Git
Bash/MSYS2) para converter um `.md` de item do case em PDF via
HTML+CSS+WeasyPrint, com diagramas mermaid recriados como imagens (o
ambiente não tem `mmdc`/mermaid-cli nem Node com esse pacote — a tradução
manual é obrigatória, não uma escolha de estilo).

**Regra de ouro**: o Python que já vem no MSYS2/mingw
(`C:\msys64\mingw64\bin\python3.exe`) NÃO serve — não tem pip utilizável
("externally managed", SSL quebrado, `ensurepip` falha). Use sempre um
Python "de verdade" do Windows (CPython oficial), porque os wheels de
WeasyPrint/matplotlib só existem para as tags `cpXXX-win_amd64`.

---

## 1. Setup de ambiente (uma vez por máquina/projeto — venv persistente)

Ao contrário de gerar o PDF em si, este setup **não deve ser refeito a cada
PDF**. Crie o venv uma vez, num local estável do projeto (ex.
`.venv_pdf/` na raiz do repo, fora de `Nasser/`), e reaproveite-o nas
próximas gerações. Só limpe/recrie se o venv corromper.

**1.1 — Descobrir o Python correto** (evite `where python` — pode falhar
dentro do Git Bash; use `find`):
```bash
find /c/Users/$USER/AppData/Local/Programs/Python -maxdepth 2 -iname "python.exe" 2>/dev/null
```
Normalmente resolve para algo como
`C:\Users\<user>\AppData\Local\Programs\Python\Python3XX\python.exe`.

**1.2 — Criar o venv** (se ainda não existir):
```bash
"<caminho-do-python-encontrado-acima>" -m venv /c/Users/<user>/Desktop/agentes-hackathon/.venv_pdf
```

**1.3 — Instalar as libs Python dentro do venv**:
```bash
.venv_pdf/Scripts/python.exe -m pip install --upgrade pip
.venv_pdf/Scripts/python.exe -m pip install weasyprint matplotlib pymupdf
```
(`pymupdf` não é dependência do PDF em si — serve só para o QA visual do
passo 5, renderizando páginas do PDF final em PNG sem depender de
`pdftoppm`/poppler, que apresentou falhas de carregamento de DLL nesta
máquina apesar do `.exe` existir.)

**1.4 — Instalar as dependências de sistema (GTK/Pango/Cairo) e Graphviz
via pacman do MSYS2** — sem isso, `import weasyprint` falha direto com
`OSError: cannot load library 'libgobject-2.0-0'` (é dependência de SO,
não de pip):
```bash
/c/msys64/usr/bin/pacman.exe -Sy --noconfirm
/c/msys64/usr/bin/pacman.exe -S --noconfirm mingw-w64-x86_64-pango mingw-w64-x86_64-cairo mingw-w64-x86_64-gdk-pixbuf2 mingw-w64-x86_64-glib2 mingw-w64-x86_64-harfbuzz mingw-w64-x86_64-fontconfig mingw-w64-x86_64-graphviz
```
(Isso puxa freetype/fribidi/libpng/pixman/libjpeg-turbo/libtiff/libwebp
como dependências automaticamente — não precisa instalar à parte.)

**1.5 — PATH obrigatório em toda chamada que use WeasyPrint, `dot` ou
poppler**: no Windows o carregamento de DLL segue o PATH (não existe
`LD_LIBRARY_PATH`), e o PATH **não persiste entre chamadas do Bash tool**
neste harness — reprefixe em toda invocação relevante:
```bash
PATH="/c/msys64/mingw64/bin:$PATH" .venv_pdf/Scripts/python.exe -c "from weasyprint import HTML; ..."
PATH="/c/msys64/mingw64/bin:$PATH" dot -Tpng -Gdpi=170 diagram.dot -o diagram.png
```
Não é necessário setar `GI_TYPELIB_PATH` nem `FONTCONFIG_PATH` (o cache do
fontconfig é gerado automaticamente pelo hook pós-instalação do pacman).

---

## 2. Recriar diagramas mermaid como imagens

Sem `mmdc` disponível, traduza manualmente cada bloco mermaid:

| Tipo mermaid | Recriar como | Como |
|---|---|---|
| `flowchart` (nós de processo/decisão) | **Graphviz DOT**, renderizado via CLI | Escreva o `.dot` à mão: nó de processo → `shape=box style="filled,rounded"`; decisão (`{}`) → `shape=diamond`; `style X fill:#RRGGBB` do mermaid → `fillcolor="#RRGGBB"` no DOT; aresta com rótulo (`--\|"label"\|`) → `A -> B [label="..."]`. Renderize com `PATH="/c/msys64/mingw64/bin:$PATH" dot -Tpng -Gdpi=170 diagram.dot -o diagram.png`. |
| `xychart-beta` (gráfico de barras) | **matplotlib** | `matplotlib.use("Agg")`; `ax.bar()` chamado uma vez por série, com offset `x ± width/2` para barras lado a lado; rótulos de valor via `ax.annotate`; `plt.savefig(dpi=200)`. Rode com o Python do venv. |
| Layouts de duas colunas/painéis simples (ex. "aprovados vs. descartados") | **HTML/CSS nativo** (flexbox), não imagem | Graphviz tende a gerar imagem excessivamente larga/achatada para esse tipo de layout — mais legível e mais nítido embutir como HTML direto no relatório. |

**Cuidado com proporção**: diagramas `rankdir=LR` com muitos nós em
sequência geram imagens muito largas (ex. 13:1) — ilegíveis quando
encaixadas na largura de uma página impressa. Prefira `rankdir=TB` para
correntes longas, e sempre confira a proporção largura/altura antes de
embutir num PDF de página fixa.

---

## 3. Conversão HTML → PDF (WeasyPrint)

Monte o conteúdo como HTML com CSS embutido — tipografia limpa,
espaçamento consistente, cores discretas — e inclua:
- Capa com título do item;
- Cabeçalho/rodapé com numeração de página;
- Tabelas HTML estilizadas (zebra striping, cabeçalho destacado) para
  dados comparativos;
- Página em modo paisagem (`@page { size: A4 landscape; }` numa classe
  dedicada) para tabelas largas (ex. matrizes de comparação com muitas
  colunas) que não caberiam legíveis em retrato;
- Diagramas/gráficos recriados no passo 2, inseridos como `<img>`.

Converta com:
```bash
PATH="/c/msys64/mingw64/bin:$PATH" .venv_pdf/Scripts/python.exe -c "
from weasyprint import HTML
HTML('relatorio.html').write_pdf('saida.pdf')
"
```

**Convenções de conteúdo deste projeto** (aplicáveis a qualquer
`item<N>-*.md`, não só a um item específico):
- Uma seção "Empresas consideradas e não aprofundadas" (ou equivalente)
  vira uma **tabela própria** (Empresa | Motivo), separada da análise
  principal.
- Uma seção `## Fontes` vira, no PDF, uma seção final de **"Referências"**
  em lista numerada, com fonte + data (e a anotação "sustenta", se
  presente no `.md`).
- Frases de síntese em **negrito** no início de cada seção (quando
  existirem) devem ser destacadas visualmente (ex. callout box ou cor de
  fundo diferenciada) — é o "so what" da seção, deve chamar atenção.

---

## 4. QA visual antes de entregar

Renderize as páginas do PDF final em PNG e inspecione visualmente cabeçalhos,
tabelas, diagramas, gráfico(s), páginas em paisagem e a seção de
referências — confirme que nada quebrou o layout:
```bash
.venv_pdf/Scripts/python.exe -c "
import fitz  # pymupdf
doc = fitz.open('saida.pdf')
for i, page in enumerate(doc):
    page.get_pixmap(dpi=120).save(f'qa_page_{i:02d}.png')
"
```
Leia algumas dessas imagens (capa, uma tabela larga, um diagrama, a última
página) com a ferramenta de leitura de imagem antes de considerar concluído.

---

## 5. Limpeza ao final

Remova **apenas os artefatos intermediários deste PDF específico**
(HTML gerado, PNGs de diagrama, PNGs de QA) — **não delete o venv**
(`.venv_pdf/`) nem os pacotes pacman instalados: eles são reutilizáveis
pela próxima geração de PDF e recriá-los do zero é o custo que esta skill
existe para eliminar. Deixe na pasta de destino (ex. `Nasser/`) apenas o
`.pdf` final.
