// Plantilla para informes ejecutivos y documentos corporativos.
// Usa bloques de titulo, callouts y tablas sobrias.
$definitions.typst()$

#set page(
  paper: "a4",
  margin: (x: __PAGE_MARGIN_X__mm, y: __PAGE_MARGIN_Y__mm),
  fill: rgb("__PAGE_BACKGROUND_COLOR__"),
  numbering: "1",
  number-align: bottom + center,
)

#set text(
  font: "__BODY_FONT__",
  size: __BODY_FONT_SIZE__pt,
  fill: rgb("__BODY_COLOR__"),
  lang: "es",
)

#set par(
  justify: true,
  leading: 1.5em,
  spacing: __PAR_SPACING__em,
)

#set heading(numbering: none)
#show heading: set par(justify: false, first-line-indent: 0em, leading: 0.72em)
#show heading: set text(hyphenate: false)

#show heading.where(level: 1): it => block(
  above: 0.5em,
  below: 1em,
  width: 100%,
  inset: (x: 0.9em, y: 0.65em),
  radius: 2pt,
  fill: rgb("__H1_COLOR__"),
  text(size: __H1_SIZE__pt, weight: "bold", fill: white, it.body),
)

#show heading.where(level: 2): it => block(
  above: 1.1em,
  below: 0.55em,
  [
    #text(size: __H2_SIZE__pt, weight: "bold", fill: rgb("__H2_COLOR__"), it.body)
    #v(0.15em)
    #line(length: 100%, stroke: 1.1pt + rgb("__H2_COLOR__"))
  ],
)

#show heading.where(level: 3): it => block(
  above: 0.8em,
  below: 0.3em,
  text(size: __H3_SIZE__pt, weight: "bold", fill: rgb("__H3_COLOR__"), it.body),
)

#show strong: it => text(weight: "bold", fill: rgb("__BOLD_COLOR__"), it.body)
#show emph: it => text(style: "italic", fill: rgb("__ITALIC_COLOR__"), it.body)

#set list(indent: 1.2em, body-indent: 0.55em)
#set enum(indent: 1.2em, body-indent: 0.7em)

#show quote: it => block(
  above: 0.9em,
  below: 0.9em,
  inset: (x: __QUOTE_INSET__em, y: __QUOTE_INSET__em),
  radius: 3pt,
  stroke: (left: 4pt + rgb("__QUOTE_BORDER_COLOR__")),
  fill: rgb("__QUOTE_BACKGROUND_COLOR__"),
  text(size: __QUOTE_TEXT_SIZE__pt, fill: rgb("__QUOTE_TEXT_COLOR__"), it.body),
)
#show raw.where(block: true): it => block(
  above: 0.8em,
  below: 0.8em,
  inset: 0.8em,
  radius: 3pt,
  fill: rgb("__CODE_BACKGROUND_COLOR__"),
  text(font: "__CODE_FONT__", size: __CODE_FONT_SIZE__pt, it),
)

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

