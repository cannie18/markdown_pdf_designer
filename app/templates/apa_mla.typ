// Plantilla para ensayo universitario tipo APA / MLA.
// Usa interlineado amplio, margenes de una pulgada y texto alineado a la izquierda.
$definitions.typst()$

#set page(
  paper: "a4",
  margin: (x: __PAGE_MARGIN_X__mm, y: __PAGE_MARGIN_Y__mm),
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
  justify: false,
  first-line-indent: 1.27cm,
  leading: __PAR_LEADING__em,
  spacing: __PAR_SPACING__em,
)

#set heading(numbering: none)
#show heading: set par(justify: false, first-line-indent: 0em, leading: 0.72em)
#show heading: set text(hyphenate: false)

#show heading.where(level: 1): it => block(
  above: 0.8em,
  below: 0.9em,
  align(center, text(size: __H1_SIZE__pt, weight: "bold", fill: rgb("__H1_COLOR__"), it.body)),
)

#show heading.where(level: 2): it => block(
  above: 1em,
  below: 0.65em,
  text(size: __H2_SIZE__pt, weight: "bold", fill: rgb("__H2_COLOR__"), it.body),
)

#show heading.where(level: 3): it => block(
  above: 0.8em,
  below: 0.55em,
  text(size: __H3_SIZE__pt, weight: "bold", style: "italic", fill: rgb("__H3_COLOR__"), it.body),
)

#show strong: it => text(weight: "bold", fill: rgb("__BOLD_COLOR__"), it.body)
#show emph: it => text(style: "italic", fill: rgb("__ITALIC_COLOR__"), it.body)

#set list(indent: 1.25cm, body-indent: 0.55em)
#set enum(indent: 1.25cm, body-indent: 0.7em)

#show quote: it => block(
  above: 0.6em,
  below: 0.6em,
  inset: (left: 1.27cm),
  it.body,
)

#show raw.where(block: true): it => block(
  above: 0.8em,
  below: 0.8em,
  inset: 0.8em,
  fill: rgb("__CODE_BACKGROUND_COLOR__"),
  text(font: "__CODE_FONT__", size: __CODE_FONT_SIZE__pt, it),
)

#set table(
  inset: __TABLE_INSET__pt,
  stroke: rgb("__TABLE_STROKE_COLOR__"),
)
#show table.cell.where(y: 0): set table.cell(fill: rgb("__TABLE_HEADER_BACKGROUND_COLOR__"))
#show table.cell.where(y: 0): set text(weight: "bold", fill: rgb("__TABLE_HEADER_TEXT_COLOR__"))

$for(header-includes)$
$header-includes$

$endfor$

$body$

