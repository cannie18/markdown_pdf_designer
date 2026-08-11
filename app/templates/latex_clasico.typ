// Plantilla academica clasica inspirada en LaTeX.
// Prioriza blanco y negro, margenes amplios y numeracion jerarquica.
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
  justify: true,
  leading: __PAR_LEADING__em,
  spacing: __PAR_SPACING__em,
)

#set heading(numbering: "1.1")
#show heading: set par(justify: false, first-line-indent: 0em, leading: 0.72em)
#show heading: set text(hyphenate: false)

#show heading.where(level: 1): it => block(
  above: 1.1em,
  below: 0.8em,
  text(size: __H1_SIZE__pt, weight: "bold", fill: rgb("__H1_COLOR__"), it.body),
)

#show heading.where(level: 2): it => block(
  above: 0.9em,
  below: 0.45em,
  text(size: __H2_SIZE__pt, weight: "bold", fill: rgb("__H2_COLOR__"), it.body),
)

#show heading.where(level: 3): it => block(
  above: 0.7em,
  below: 0.3em,
  text(size: __H3_SIZE__pt, weight: "bold", fill: rgb("__H3_COLOR__"), it.body),
)

#show strong: it => text(weight: "bold", fill: rgb("__BOLD_COLOR__"), it.body)
#show emph: it => text(style: "italic", fill: rgb("__ITALIC_COLOR__"), it.body)

#set list(indent: 1.2em, body-indent: 0.55em)
#set enum(indent: 1.2em, body-indent: 0.7em)

#show quote: it => block(
  above: 0.8em,
  below: 0.8em,
  inset: (x: 1em, y: 0.65em),
  stroke: (left: 1pt + rgb("#000000")),
  it.body,
)

#show raw.where(block: true): it => block(
  above: 0.8em,
  below: 0.8em,
  inset: 0.8em,
  fill: rgb("__CODE_BACKGROUND_COLOR__"),
  stroke: 0.5pt + rgb("#000000"),
  text(font: "__CODE_FONT__", size: __CODE_FONT_SIZE__pt, fill: rgb("__BODY_COLOR__"), it),
)

#set table(
  inset: 6pt,
  stroke: rgb("#000000"),
)

$for(header-includes)$
$header-includes$

$endfor$

$body$
