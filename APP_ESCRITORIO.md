# Markdown PDF Designer

## Qué Es

Markdown PDF Designer es una app de escritorio local para generar PDF de
apuntes a partir de archivos Markdown, ajustando el resultado a necesidades de
diseño concretas.

Su objetivo no es sustituir al Markdown ni convertir la herramienta en un
editor complejo. La idea principal es facilitar este flujo:

```text
abrir o arrastrar Markdown
revisar opcionalmente el contenido
elegir estilo visual
generar PDF
ver el resultado dentro de la app
```

La app está creada con Python y PySide6.

## Estructura visual deseada

La app se organiza con una vista previa PDF permanente a la derecha y un panel
de trabajo cambiante a la izquierda.

```text
panel izquierdo cambiante | vista previa PDF
```

El panel izquierdo tiene dos secciones y un botón de ayuda:

- `Markdown`: abrir o arrastrar Markdown, revisar contenido y generar PDF.
- `Diseño`: elegir plantilla visual y ajustar fuente, tamaño, colores y espacios
  antes de volver a generar.
- `Ayuda`: mostrar en el visor el flujo básico, el Markdown recomendado y el
  papel de las plantillas sin cambiar el panel izquierdo activo.

La vista previa no es una pestaña separada: debe estar siempre disponible para
comprobar el PDF real generado.

## Principio de Diseño

La herramienta mantiene separado:

```text
contenido != presentación
```

El Markdown debe describir la estructura del apunte:

```markdown
# Título

## Sección

Texto, listas, tablas, código y bloques destacados.
```

La apariencia del PDF se controla desde plantillas Typst y desde opciones de la
app, no desde marcas visuales incrustadas en el Markdown.

## Estado actual

La app permite:

- abrir un archivo `.md`;
- arrastrar un archivo `.md`;
- crear un Markdown nuevo sin elegir ubicación hasta guardar o generar;
- ver y editar opcionalmente el contenido;
- preguntar antes de generar si hay cambios sin guardar;
- elegir tipo de fuente;
- elegir tamaño base del texto;
- elegir color del texto normal;
- elegir color de fondo de la página del PDF;
- ajustar interlineado y espacio entre párrafos;
- elegir márgenes laterales y verticales en centímetros;
- elegir tamaño de títulos de nivel 1, 2 y 3;
- elegir colores para títulos de nivel 1, 2 y 3;
- elegir colores independientes para negrita y cursiva;
- elegir fuente, tamaño y fondo de los bloques de código;
- elegir texto, fondo, borde y espaciado de bloques destacados;
- elegir texto, espaciado, bordes y cabecera de tablas;
- elegir si las tablas se ajustan al contenido o usan el ancho disponible;
- consultar las opciones de diseño agrupadas por secciones compactas;
- elegir una plantilla visual predefinida desde `Diseño`;
- cargar en `Diseño` los ajustes base de la plantilla seleccionada;
- crear una nueva plantilla desde los ajustes visuales actuales;
- guardar cambios sobre una plantilla personalizada existente;
- recordar la última plantilla seleccionada;
- corregir automáticamente el espacio entre párrafos para que no quede por debajo del interlineado;
- aplicar reglas propias a los títulos para evitar justificación, sangría heredada y guionado automático;
- evitar cambios accidentales en controles numéricos al usar la rueda del ratón;
- generar el PDF;
- mostrar el PDF generado dentro de la propia app;
- abrir el PDF en el visor externo de Windows.
- cambiar entre secciones `Markdown` y `Diseño` en el panel izquierdo;
- mostrar la ayuda en el área de vista previa sin abandonar `Markdown` o `Diseño`;
- explicar en la ayuda los botones de `Markdown`, el flujo de plantillas y las
  secciones modificables de `Diseño`;
- mantener visible la ayuda al alternar entre `Markdown` y `Diseño`;
- usar `Ayuda` como interruptor para volver al PDF o a la guía inicial;
- desactivar visualmente `Ayuda` cuando vuelve el PDF al generar;
- mantener arriba la fila de selección de Markdown en `Markdown`;
- colocar `Abrir` junto a la caja de ruta y `Nuevo` después;
- mostrar en `Diseño` siempre `Generar PDF` como acción inferior;
- permitir pulsar `Generar PDF` desde `Diseño` y avisar si falta un Markdown;
- controlar el color de fondo del documento PDF desde `Diseño`;
- controlar el modo de ancho de tablas desde `Diseño`;
- proteger cambios sin guardar en plantillas personalizadas al cerrar o cambiar de plantilla;
- resaltar en los desplegables la opción seleccionada y la opción bajo el mouse;
- mostrar iconos SVG en las acciones principales y parámetros compactos en `Diseño`;
- mostrar una guía breve en el visor cuando todavía no hay PDF cargado.

## Relación Con La Versión Portable

La app Python y la versión portable por `.bat` deben evolucionar de forma
separada.

```text
crear_pdf.bat
templates/apuntes.typ
```

pertenecen a la versión portable básica.

```text
app/main.py
app/pdf_builder.py
app/templates/*.typ
```

pertenecen a la app de escritorio.

Las plantillas creadas por el usuario se guardan como datos de usuario en la
carpeta histórica de la aplicación:

```text
%APPDATA%\pdf_apuntes\templates
```

Esto permite mejorar la app sin romper el flujo simple:

```powershell
.\crear_pdf.bat .\ejemplos\archivo.md
```

## Cómo Genera El PDF La App

La app no transforma manualmente el Markdown con expresiones regulares.

El flujo es:

```text
Markdown
  -> Pandoc
  -> Typst
  -> PDF
```

Cuando el usuario cambia fuente, tamaño, márgenes, títulos, colores, fondo de
página, bloques, tablas o código, Python genera una plantilla Typst temporal a
partir de la plantilla elegida en:

```text
app/templates/
%APPDATA%\pdf_apuntes\templates
```

Esa plantilla temporal se usa solo durante la conversión y se elimina al
terminar.

## Pretensiones

La app quiere convertirse progresivamente en una herramienta sencilla para
crear PDF de estudio con buena maquetación.

## Plantillas iniciales

La primera fase de plantillas predefinidas incluye:

- `Estudio`: apuntes claros y equilibrados.
- `LaTeX clásico`: documentos académicos sobrios, en blanco y negro.
- `Ensayo APA / MLA`: trabajos universitarios con márgenes e interlineado amplio.
- `Informe ejecutivo`: documentos corporativos con títulos fuertes y bloques destacados.
- `Manual técnico`: documentación con código protagonista.
- `Accesibilidad y neurodivergencia`: lectura accesible con fondo suave, aire amplio y énfasis sin cursiva.
- `Manuscrito / novela`: textos largos en formato A5.
- `Profesional`: informe sobrio de uso general.
- `Compacto`: documento de dos columnas para ahorrar páginas.

## Ajustes Recientes

Los últimos ajustes importantes son:

- cada plantilla carga sus valores base en la pestaña `Diseño`;
- la app recuerda la última plantilla seleccionada sin conservar cambios temporales como si fueran valores base;
- las plantillas personalizadas se guardan fuera del repositorio, en `%APPDATA%\pdf_apuntes\templates` por compatibilidad histórica;
- las plantillas personalizadas pueden actualizarse con `Guardar cambios`;
- los controles numéricos de diseño ignoran la rueda del ratón para evitar cambios accidentales;
- `Bloques` permite ajustar espacio interno, color/tamaño del texto, borde y fondo;
- `Tablas` permite ajustar modo de ancho, espacio de celdas, color/tamaño del texto, bordes y cabecera;
- `Página` agrupa márgenes y color de fondo del PDF;
- `Texto` agrupa fuente, tamaño, color, espaciado, títulos y énfasis;
- `Ensayo APA / MLA` usa tamaños distintos para títulos y subtítulos;
- `Ensayo APA / MLA` ya no parte de `Espacio párrafos = 0`;
- `Manuscrito / novela` ya no coloca el primer título a mitad de página;
- las plantillas evitan que los títulos hereden el interlineado grande del texto normal;
- el cuerpo de texto puede seguir justificándose según la plantilla, pero los títulos no;
- el botón `Ayuda` muestra las instrucciones en el visor de la derecha sin cambiar el panel izquierdo y permite volver al PDF;
- `Nuevo` abre un documento sin guardar y pide ubicación al guardar o generar;
- en `Diseño` se ocultan `Cerrar`, `Guardar`, `Guardar como` y `Abrir PDF en Windows`, pero `Generar PDF` permanece visible;
- los cambios de plantillas personalizadas se deben guardar, descartar o cancelar antes de cerrar o cambiar de plantilla;
- los desplegables distinguen visualmente selección y opción bajo el mouse;
- los parámetros de `Diseño` usan iconos SVG cargados desde `assets/icons/` y muestran el texto mediante tooltips;
- los títulos Markdown de nivel 4, 5 y 6 tienen estilos diferenciados;
- los enlaces Markdown se muestran con color y subrayado y conservan el hipervínculo clicable;
- la conversión normaliza HTML inline básico y alertas tipo GitHub antes de generar Typst;
- `[TOC]` genera un índice y `<!-- pagebreak -->` genera un salto de página;
- la ayuda combina una guía rápida con explicaciones detalladas de `Markdown` y `Diseño`;
- el visor vacío muestra una guía breve de primer uso;
- en `Markdown`, la fila de ruta, `Nuevo` y `Abrir` permanece arriba aunque no haya documento abierto;
- la versión portable por `.bat` no se ha tocado.

Objetivos previstos:

- gestión avanzada de plantillas personalizadas;
- galería futura de plantillas con definición rápida y vista previa cacheada;
- estilos para código;
- portada opcional;
- cabecera y pie de página configurables;
- número de página y total de páginas;
- salida a una carpeta elegida por el usuario;
- soporte básico para imágenes locales referenciadas desde Markdown;
- modo debug para conservar `.typ` intermedios;
- mensajes de error más comprensibles;
- empaquetado como `.exe` para usar sin abrir terminal;
- versión portable completa distribuible como `.zip`.

## Cosas que no queremos hacer de momento

- crear un editor Markdown avanzado;
- mezclar la plantilla portable con las plantillas dinámicas de la app;
- volver a convertir Markdown a mano mediante muchas expresiones regulares;
- subir binarios pesados como `pandoc.exe` o `typst.exe` al repositorio Git.

## Criterio de avance

Cada mejora debe ser pequeña y comprobable.

Antes de ampliar la app conviene verificar siempre:

- que la app genera PDF;
- que la vista previa carga el PDF;
- que la versión `crear_pdf.bat` sigue funcionando;
- que las plantillas de la app no rompen las plantillas portables.
