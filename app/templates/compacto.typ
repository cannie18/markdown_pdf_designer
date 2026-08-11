// Plantilla compacta de la app Python.
// Usa dos columnas para ahorrar espacio sin cambiar el contenido Markdown.
$definitions.typst()$

// Pagina.
#set page(
  paper: "a4",
  margin: (x: __PAGE_MARGIN_X__mm, y: __PAGE_MARGIN_Y__mm),
  numbering: "1",
  number-align: bottom + center,
)

// Texto base.
// Estos valores los rellena la app antes de llamar a Pandoc.
#set text(
  font: "__BODY_FONT__",
  size: __BODY_FONT_SIZE__pt,
  fill: rgb("__BODY_COLOR__"),
  lang: "es",
)

// Parrafos.
#set par(
  justify: true,
  leading: __PAR_LEADING__em,
  spacing: __PAR_SPACING__em,
)

// Titulos.
#set heading(numbering: none)

#show heading.where(level: 1): it => block(
  above: 0.2em,
  below: 0.7em,
  [
    #text(size: __H1_SIZE__pt, weight: "bold", fill: rgb("__H1_COLOR__"), it.body)
    #v(0.15em)
    #line(length: 100%, stroke: 0.5pt + rgb("__H1_COLOR__"))
  ],
)

#show heading.where(level: 2): it => block(
  above: 0.8em,
  below: 0.35em,
  text(size: __H2_SIZE__pt, weight: "bold", fill: rgb("__H2_COLOR__"), it.body),
)

#show heading.where(level: 3): it => block(
  above: 0.55em,
  below: 0.2em,
  text(size: __H3_SIZE__pt, weight: "bold", fill: rgb("__H3_COLOR__"), it.body),
)

// Enfasis.
#show strong: it => text(weight: "bold", fill: rgb("__BOLD_COLOR__"), it.body)
#show emph: it => text(style: "italic", fill: rgb("__ITALIC_COLOR__"), it.body)

// Listas.
#set list(indent: 1em, body-indent: 0.45em)
#set enum(indent: 1em, body-indent: 0.55em)

// Cajas destacadas.
#show quote: it => block(
  above: 0.55em,
  below: 0.55em,
  inset: (x: 0.65em, y: 0.5em),
  radius: 2pt,
  stroke: (left: 2pt + rgb("__H2_COLOR__")),
  fill: rgb("#f5f7f8"),
  it.body,
)

// Codigo.
#show raw.where(block: true): it => block(
  above: 0.55em,
  below: 0.55em,
  inset: 0.55em,
  radius: 2pt,
  fill: rgb("__CODE_BACKGROUND_COLOR__"),
  text(font: "__CODE_FONT__", size: __CODE_FONT_SIZE__pt, it),
)

// Tablas.
#set table(
  inset: 5pt,
  stroke: rgb("#c8d0d8"),
)

$for(header-includes)$
$header-includes$

$endfor$

#columns(2, gutter: 14pt)[
$body$
]
