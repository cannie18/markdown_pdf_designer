// Plantilla inicial de la app Python.
// Esta plantilla es independiente de templates/apuntes.typ, que pertenece a
// la version portable por .bat.
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
  lang: "es",
)

// Parrafos.
#set par(
  justify: true,
  leading: 0.62em,
  spacing: 0.82em,
)

// Titulos.
#set heading(numbering: none)

#show heading.where(level: 1): it => block(
  below: 1.1em,
  text(size: __H1_SIZE__pt, weight: "bold", fill: rgb("__H1_COLOR__"), it.body),
)

#show heading.where(level: 2): it => block(
  above: 1.2em,
  below: 0.55em,
  text(size: __H2_SIZE__pt, weight: "bold", fill: rgb("__H2_COLOR__"), it.body),
)

#show heading.where(level: 3): it => block(
  above: 0.9em,
  below: 0.35em,
  text(size: __H3_SIZE__pt, weight: "bold", fill: rgb("__H3_COLOR__"), it.body),
)

// Enfasis.
#show strong: it => text(weight: "bold", fill: rgb("__H1_COLOR__"), it.body)
#show emph: it => text(style: "italic", it.body)

// Listas.
#set list(indent: 1.2em, body-indent: 0.55em)
#set enum(indent: 1.2em, body-indent: 0.7em)

// Cajas destacadas.
#show quote: it => block(
  above: 0.9em,
  below: 0.9em,
  inset: (x: 0.9em, y: 0.75em),
  radius: 3pt,
  stroke: (left: 3pt + rgb("#2e6f73")),
  fill: rgb("#eef6f4"),
  it.body,
)

// Codigo.
#show raw.where(block: true): it => block(
  above: 0.8em,
  below: 0.8em,
  inset: 0.8em,
  radius: 3pt,
  fill: rgb("#f4f1ec"),
  text(font: "Consolas", size: 9pt, it),
)

// Tablas.
#set table(
  inset: 7pt,
  stroke: rgb("#c8d0d8"),
)

$for(header-includes)$
$header-includes$

$endfor$

$body$
