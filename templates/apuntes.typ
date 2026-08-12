// Definiciones internas que Pandoc necesita para algunos elementos Typst.
$definitions.typst()$

// Configuracion general de pagina.
// Cambia aqui tamano de papel, margenes y numeracion.
#set page(
  paper: "a4",
  margin: (x: 22mm, y: 20mm),
  numbering: "1",
  number-align: bottom + center,
)

// Texto base del documento.
// Ajusta aqui fuente principal, tamano general e idioma.
#set text(
  font: "Arial",
  size: 10.5pt,
  lang: "es",
)

// Parrafos.
// Controla justificacion, interlineado y separacion entre parrafos.
#set par(
  justify: true,
  leading: 0.62em,
  spacing: 0.82em,
)

// Titulos.
// Pandoc convierte #, ## y ### de Markdown en headings de nivel 1, 2 y 3.
#set heading(numbering: none)

// Titulo principal: Markdown "# Titulo".
#show heading.where(level: 1): it => block(
  below: 1.1em,
  text(size: 24pt, weight: "bold", fill: rgb("#1f3552"), it.body),
)

// Titulo de segundo nivel: Markdown "## Seccion".
#show heading.where(level: 2): it => block(
  above: 1.2em,
  below: 0.55em,
  text(size: 16pt, weight: "bold", fill: rgb("#2e6f73"), it.body),
)

// Titulo de tercer nivel: Markdown "### Subseccion".
#show heading.where(level: 3): it => block(
  above: 0.9em,
  below: 0.35em,
  text(size: 12.5pt, weight: "bold", fill: rgb("#7a3f3f"), it.body),
)

// Titulos secundarios.
#show heading.where(level: 4): it => block(
  above: 0.7em,
  below: 0.25em,
  text(size: 11.2pt, weight: "bold", fill: rgb("#7a3f3f"), it.body),
)

#show heading.where(level: 5): it => block(
  above: 0.55em,
  below: 0.2em,
  text(size: 11pt, weight: "bold", fill: rgb("#7a3f3f"), it.body),
)

#show heading.where(level: 6): it => block(
  above: 0.45em,
  below: 0.15em,
  text(size: 10.5pt, style: "italic", fill: rgb("#7a3f3f"), it.body),
)
// Enfasis.
#show strong: it => text(weight: "bold", fill: rgb("#1f3552"), it.body)
#show emph: it => text(style: "italic", it.body)
// Enlaces.
#show link: it => text(fill: rgb("#0057b8"), underline(it))

// Listas.
// Markdown "- item" y "1. item".
#set list(indent: 1.2em, body-indent: 0.55em)
#set enum(indent: 1.2em, body-indent: 0.7em)

// Cajas destacadas.
// Markdown "> texto" se convierte en quote.
#show quote: it => block(
  above: 0.9em,
  below: 0.9em,
  inset: (x: 0.9em, y: 0.75em),
  radius: 3pt,
  stroke: (left: 3pt + rgb("#2e6f73")),
  fill: rgb("#eef6f4"),
  it.body,
)

// Bloques de codigo.
// Markdown con triple backtick, por ejemplo ```python.
#show raw.where(block: true): it => block(
  above: 0.8em,
  below: 0.8em,
  inset: 0.8em,
  radius: 3pt,
  fill: rgb("#f4f1ec"),
  text(font: "Consolas", size: 9pt, it),
)

// Tablas.
// Estilo base para tablas generadas desde Markdown.
#set table(
  inset: 7pt,
  stroke: rgb("#c8d0d8"),
)

// Inclusiones avanzadas de Pandoc.
// Permite anadir codigo Typst desde metadatos o parametros de Pandoc.
$for(header-includes)$
$header-includes$

$endfor$

// Contenido principal convertido desde Markdown.
$body$
