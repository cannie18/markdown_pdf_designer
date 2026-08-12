// Plantilla inicial de la app Python.
// Esta plantilla es independiente de templates/apuntes.typ, que pertenece a
// la version portable por .bat.
$definitions.typst()$

// Pagina.
#set page(
  paper: "a4",
  margin: (x: __PAGE_MARGIN_X__mm, y: __PAGE_MARGIN_Y__mm),
  fill: rgb("__PAGE_BACKGROUND_COLOR__"),
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
#show heading: set par(justify: false, first-line-indent: 0em, leading: 0.72em)
#show heading: set text(hyphenate: false)

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

// Titulos secundarios.
#show heading.where(level: 4): it => block(
  above: 0.7em,
  below: 0.25em,
  text(size: (__BODY_FONT_SIZE__pt * 1.02), weight: "bold", fill: rgb("__H3_COLOR__"), it.body),
)

#show heading.where(level: 5): it => block(
  above: 0.55em,
  below: 0.2em,
  text(size: __BODY_FONT_SIZE__pt, weight: "bold", fill: rgb("__H3_COLOR__"), it.body),
)

#show heading.where(level: 6): it => block(
  above: 0.45em,
  below: 0.15em,
  text(size: (__BODY_FONT_SIZE__pt * 0.95), style: "italic", fill: rgb("__H3_COLOR__"), it.body),
)
// Enfasis.
#show strong: it => text(weight: "bold", fill: rgb("__BOLD_COLOR__"), it.body)
#show emph: it => text(style: "italic", fill: rgb("__ITALIC_COLOR__"), it.body)
// Enlaces.
#show link: it => text(fill: rgb("#0057b8"), underline(it))

// Listas.
#set list(indent: 1.2em, body-indent: 0.55em)
#set enum(indent: 1.2em, body-indent: 0.7em)

// Cajas destacadas.
#show quote: it => block(
  above: 0.9em,
  below: 0.9em,
  inset: (x: __QUOTE_INSET__em, y: __QUOTE_INSET__em),
  radius: 3pt,
  stroke: (left: 4pt + rgb("__QUOTE_BORDER_COLOR__")),
  fill: rgb("__QUOTE_BACKGROUND_COLOR__"),
  text(size: __QUOTE_TEXT_SIZE__pt, fill: rgb("__QUOTE_TEXT_COLOR__"), it.body),
)
// Codigo.
#show raw.where(block: true): it => block(
  above: 0.8em,
  below: 0.8em,
  inset: 0.8em,
  radius: 3pt,
  fill: rgb("__CODE_BACKGROUND_COLOR__"),
  text(font: "__CODE_FONT__", size: __CODE_FONT_SIZE__pt, it),
)

// Tablas.
#set table(
  inset: __TABLE_INSET__pt,
  stroke: rgb("__TABLE_STROKE_COLOR__"),
  fill: (_, y) => if y == 0 { rgb("__TABLE_HEADER_BACKGROUND_COLOR__") },
)
#show table.cell: set text(size: __TABLE_TEXT_SIZE__pt, fill: rgb("__TABLE_TEXT_COLOR__"))
#show table.cell.where(y: 0): set text(weight: "bold", fill: rgb("__TABLE_HEADER_TEXT_COLOR__"))

$for(header-includes)$
$header-includes$

$endfor$

$body$

