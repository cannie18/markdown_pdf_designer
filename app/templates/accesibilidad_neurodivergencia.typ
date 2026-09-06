// Plantilla de accesibilidad para dislexia, TDA y TDAH.
// Prioriza alineacion izquierda, aire visual y bajo deslumbramiento.
$definitions.typst()$

#set page(
  paper: "a4",
  __PAGE_HEIGHT_OPTION__
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
  above: 1.8em,
  below: 0.9em,
  breakable: false,
  [
    #text(size: __H1_SIZE__pt, weight: "bold", fill: rgb("__H1_COLOR__"), it.body)
    #v(0.28em)
    #line(length: 100%, stroke: 2.2pt + rgb("__H1_COLOR__"))
  ],
)

#show heading.where(level: 2): it => block(
  above: 2em,
  below: 0em,
  breakable: false,
  [
    #text(size: __H2_SIZE__pt, weight: "bold", fill: rgb("__H2_COLOR__"), it.body)
    #v(0.06em)
    #line(length: 100%, stroke: 1.5pt + rgb("__H2_COLOR__"))
    #v(1em)
  ],
)

#show heading.where(level: 3): it => block(
  above: 1.55em,
  below: 0em,
  breakable: false,
  [
    #text(size: __H3_SIZE__pt, weight: "bold", fill: rgb("__H3_COLOR__"), it.body)
    #v(0.05em)
    #line(length: 100%, stroke: 0.9pt + rgb("__H3_COLOR__"))
    #v(0.8em)
  ],
)

// Titulos secundarios.
#show heading.where(level: 4): it => block(
  above: 1em,
  below: 0em,
  [
    #text(size: (__BODY_FONT_SIZE__pt * 1.02), weight: "bold", fill: rgb("__H3_COLOR__"), it.body)
    #v(0.5em)
  ],
)

#show heading.where(level: 5): it => block(
  above: 0.85em,
  below: 0em,
  [
    #text(size: __BODY_FONT_SIZE__pt, weight: "bold", fill: rgb("__H3_COLOR__"), it.body)
    #v(0.4em)
  ],
)

#show heading.where(level: 6): it => block(
  above: 0.7em,
  below: 0em,
  [
    #text(size: (__BODY_FONT_SIZE__pt * 0.95), style: "italic", fill: rgb("__H3_COLOR__"), it.body)
    #v(0.35em)
  ],
)
// Enfasis.
#show strong: it => text(weight: "bold", fill: rgb("__BOLD_COLOR__"), it.body)
#show emph: it => text(weight: "bold", fill: rgb("__ITALIC_COLOR__"), it.body)
// Enlaces.
#show link: it => text(fill: rgb("#0057b8"), underline(it))

#set list(
  indent: 1.3em,
  body-indent: 0.7em,
  spacing: __PAR_SPACING__em,
)
#set enum(
  indent: 1.3em,
  body-indent: 0.8em,
  spacing: __PAR_SPACING__em,
)
#show list: it => block(below: __PAR_SPACING__em, it)
#show enum: it => block(below: __PAR_SPACING__em, it)

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
  above: 1em,
  below: 1em,
  inset: 0.95em,
  radius: 4pt,
  fill: rgb("__CODE_BACKGROUND_COLOR__"),
  text(font: "__CODE_FONT__", size: __CODE_FONT_SIZE__pt, fill: rgb("#263638"), it),
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

