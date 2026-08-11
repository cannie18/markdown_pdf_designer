// Plantilla de accesibilidad para dislexia, TDA y TDAH.
// Prioriza alineacion izquierda, aire visual y bajo deslumbramiento.
$definitions.typst()$

#let page-background = rgb("#fbf6e8")

#set page(
  paper: "a4",
  margin: (x: __PAGE_MARGIN_X__mm, y: __PAGE_MARGIN_Y__mm),
  fill: page-background,
  numbering: "1",
  number-align: bottom + center,
)

#set text(
  font: "__BODY_FONT__",
  size: __BODY_FONT_SIZE__pt,
  fill: rgb("__BODY_COLOR__"),
  lang: "es",
  tracking: 0.018em,
)

#set par(
  justify: false,
  leading: __PAR_LEADING__em,
  spacing: __PAR_SPACING__em,
)

#set heading(numbering: none)
#show heading: set par(justify: false, first-line-indent: 0em, leading: 0.9em)
#show heading: set text(hyphenate: false, tracking: 0em)

#show heading.where(level: 1): it => block(
  above: 0.2em,
  below: 1.2em,
  breakable: false,
  [
    #text(size: __H1_SIZE__pt, weight: "bold", fill: rgb("__H1_COLOR__"), it.body)
    #v(0.28em)
    #line(length: 100%, stroke: 2.2pt + rgb("__H1_COLOR__"))
  ],
)

#show heading.where(level: 2): it => block(
  above: 1.5em,
  below: 0.9em,
  breakable: false,
  [
    #text(size: __H2_SIZE__pt, weight: "bold", fill: rgb("__H2_COLOR__"), it.body)
    #v(0.22em)
    #line(length: 100%, stroke: 1.5pt + rgb("__H2_COLOR__"))
  ],
)

#show heading.where(level: 3): it => block(
  above: 1.1em,
  below: 0.65em,
  breakable: false,
  [
    #text(size: __H3_SIZE__pt, weight: "bold", fill: rgb("__H3_COLOR__"), it.body)
    #v(0.16em)
    #line(length: 100%, stroke: 0.9pt + rgb("__H3_COLOR__"))
  ],
)

#show strong: it => text(weight: "bold", fill: rgb("__BOLD_COLOR__"), it.body)
#show emph: it => text(weight: "bold", fill: rgb("__ITALIC_COLOR__"), it.body)

#set list(
  indent: 1.3em,
  body-indent: 0.7em,
  spacing: 0.55em,
)
#set enum(
  indent: 1.3em,
  body-indent: 0.8em,
  spacing: 0.55em,
)

#show quote: it => block(
  above: 1em,
  below: 1em,
  inset: (x: 1em, y: 0.85em),
  radius: 4pt,
  stroke: (left: 4pt + rgb("#6aa38f")),
  fill: rgb("#e8f4ec"),
  it.body,
)

#show raw.where(block: true): it => block(
  above: 1em,
  below: 1em,
  inset: 0.95em,
  radius: 4pt,
  fill: rgb("__CODE_BACKGROUND_COLOR__"),
  text(font: "__CODE_FONT__", size: __CODE_FONT_SIZE__pt, fill: rgb("#263638"), it),
)

#set table(
  inset: 9pt,
  stroke: rgb("#b8cbc6"),
)

$for(header-includes)$
$header-includes$

$endfor$

$body$
