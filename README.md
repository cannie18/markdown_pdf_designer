# markdown_pdf_designer

Herramienta local para convertir apuntes en Markdown a PDF:

```text
Markdown -> Pandoc -> Typst -> PDF
```

## Modos de uso

La herramienta puede funcionar de dos formas.

### Modo instalado

Usa `pandoc` y `typst` instalados en Windows:

- `pandoc` disponible en `PATH` o instalado en `%LOCALAPPDATA%\Pandoc`.
- `typst` disponible en `PATH`.

### Modo portable

Usa ejecutables incluidos dentro del propio proyecto:

```text
bin/
├── pandoc/
│   └── pandoc.exe
└── typst/
    └── typst.exe
```

`crear_pdf.bat` busca primero esos binarios locales. Si existen, los usa antes
que cualquier instalación del sistema.

Los binarios locales no se suben a GitHub porque están ignorados en
`.gitignore`. Esto mantiene el repositorio ligero, pero permite copiar la
carpeta local completa a otro equipo para trabajar sin instalar dependencias.

La versión portable por `.bat` y la app de escritorio evolucionan separadas. En
ambos casos se mantiene la idea base: delegar la conversión y la maquetación en
Pandoc y Typst, evitando un preprocesador lleno de expresiones regulares.

## Probar en Windows

Desde PowerShell o `cmd.exe`:

```bat
cd ruta\a\markdown_pdf_designer
crear_pdf.bat ejemplos\prueba_apuntes.md
```

Resultado esperado:

```text
ejemplos\prueba_apuntes.pdf
```

Si `typst` no está disponible, el script generará igualmente:

```text
ejemplos\prueba_apuntes.typ
```

Ese archivo permite comprobar la salida de Pandoc antes de añadir Typst al
modo instalado o al modo portable.

## App de escritorio

La app Python se llama Markdown PDF Designer. Vive en `app/` y usa sus propias
plantillas en `app/templates/`. Esto evita que los cambios de la app rompan la
versión portable por `.bat`.

Para abrirla:

```bat
abrir_app.bat
```

También puedes arrastrar un archivo Markdown sobre `abrir_app.bat`.

La app permite, de momento:

- crear un Markdown nuevo sin elegir ubicación hasta guardarlo o generar PDF;
- abrir un archivo `.md`;
- arrastrar un archivo `.md`;
- elegir entre los últimos Markdown usados desde el desplegable de ruta;
- cargar el Markdown directamente en el editor al abrirlo;
- guardar o guardar como el Markdown;
- generar el PDF con un botón;
- ver el PDF generado dentro de la propia app;
- abrir el PDF generado en el visor predeterminado de Windows;
- mostrar iconos SVG en las acciones principales y en los parámetros de Diseño;
- consultar la ayuda integrada en el visor sin abandonar `Markdown` o `Diseño`;
- consultar ayuda detallada sobre botones de Markdown, plantillas y secciones de Diseño;
- ver una guía breve en el visor cuando todavía no hay PDF cargado;
- elegir fuente, tamaño base, márgenes, tamaños de títulos y colores antes de generar;
- elegir el color de fondo de la página del PDF;
- definir colores independientes para títulos, negrita y cursiva;
- ajustar interlineado, espaciado entre párrafos y estilos de código;
- ajustar texto, fondo, borde y espaciado de bloques destacados;
- ajustar texto, espaciado, bordes y cabecera de tablas;
- elegir si las tablas se ajustan al contenido o usan el ancho disponible;
- elegir una plantilla visual predefinida;
- crear una nueva plantilla desde los ajustes visuales actuales;
- guardar cambios sobre una plantilla personalizada existente;
- cargar en `Diseño` los ajustes base de la plantilla seleccionada;
- recordar la última plantilla seleccionada;
- mantener el espacio entre párrafos igual o superior al interlineado;
- evitar que los títulos hereden justificación, sangría o guionado automático;
- evitar cambios accidentales en controles numéricos al usar la rueda del ratón;
- recordar posición, monitor y tamaño de ventana;
- mantener un ancho mínimo usable para controles y dejar que la vista previa use el espacio restante;
- mantener siempre arriba la fila de selección de Markdown en `Markdown`;
- resaltar en los desplegables la opción seleccionada y la opción bajo el mouse.

Las opciones visuales de la app se aplican generando una plantilla Typst
temporal a partir de la plantilla elegida en `app/templates/`. La plantilla
portable `templates/apuntes.typ` no se modifica.

Las plantillas creadas por el usuario se guardan fuera del código de la app, en
la carpeta de datos histórica de la aplicación:

```text
%APPDATA%\pdf_apuntes\templates
```

## Estructura

```text
markdown_pdf_designer/
├── abrir_app.bat
├── app/
│   ├── main.py
│   ├── pdf_builder.py
│   └── templates/
│       ├── apa_mla.typ
│       ├── compacto.typ
│       ├── estudio.typ
│       ├── informe_ejecutivo.typ
│       ├── latex_clasico.typ
│       ├── manual_tecnico.typ
│       ├── manuscrito_novela.typ
│       ├── profesional.typ
│       └── accesibilidad_neurodivergencia.typ
├── assets/
│   └── icons/
│       └── *.svg
├── crear_pdf.bat
├── bin/
│   ├── pandoc/
│   └── typst/
├── ejemplos/
│   └── prueba_apuntes.md
├── templates/
│   └── apuntes.typ
└── README.md
```

## Próximas mejoras

El flujo principal `Markdown -> PDF` ya funciona. Las próximas mejoras previstas
se centran en la experiencia visual de la app: iconos, organización de controles,
plantillas, portada, cabecera, pie, salida configurable y soporte futuro para
imágenes locales referenciadas desde Markdown.

## Plantillas de la app

Las plantillas disponibles en la app son:

- `Estudio`: equilibrada para apuntes claros.
- `LaTeX clásico`: académica, monocromática y con márgenes amplios.
- `Ensayo APA / MLA`: pensada para trabajos universitarios.
- `Informe ejecutivo`: estilo corporativo con títulos destacados.
- `Manual técnico`: pensada para documentación y bloques de código.
- `Accesibilidad y neurodivergencia`: lectura accesible para dislexia, TDA y TDAH.
- `Manuscrito / novela`: formato A5 para lectura prolongada.
- `Profesional`: informe sobrio de uso general.
- `Compacto`: dos columnas y menor consumo de páginas.

## Estado Para Retomar

Último estado comprobado:

- la app Python genera PDF con todas las plantillas de `app/templates/`;
- las plantillas personalizadas se guardan en `%APPDATA%\pdf_apuntes\templates` por compatibilidad histórica;
- la última plantilla seleccionada se recuerda, pero al abrir la app se cargan los parámetros base de esa plantilla;
- las plantillas personalizadas pueden actualizarse con `Guardar cambios`;
- los controles numéricos de `Diseño` no cambian con la rueda del ratón;
- el botón `Ayuda` funciona como interruptor entre instrucciones y vista previa;
- al generar PDF se desactiva visualmente el botón `Ayuda` y vuelve el visor real;
- la ayuda incluye guía rápida, botones de Markdown, flujo de plantillas y secciones modificables de `Diseño`;
- el visor vacío muestra los primeros pasos antes de generar el primer PDF;
- la fila de ruta, `Nuevo` y `Abrir` permanece arriba en `Markdown`, haya o no documento abierto;
- `Abrir` está junto a la caja de ruta y `Nuevo` después;
- en `Diseño` siempre se muestra `Generar PDF` como acción inferior;
- `Generar PDF` funciona desde `Diseño` y avisa si todavía no hay Markdown;
- `Diseño` permite cambiar el color de fondo del documento PDF;
- las plantillas personalizadas avisan si tienen cambios sin guardar al cerrar o cambiar de plantilla;
- `Diseño` permite controlar texto, fondo, borde y espaciado de bloques destacados;
- `Diseño` permite controlar texto, espaciado, bordes y cabecera de tablas;
- `Diseño` permite elegir el modo de ancho de tablas: contenido o ancho disponible;
- los desplegables distinguen visualmente la opción seleccionada y la opción bajo el mouse;
- los parámetros de `Diseño` se organizan en filas compactas con iconos y tooltips;
- los títulos Markdown de nivel 4, 5 y 6 tienen estilos diferenciados;
- los enlaces Markdown se muestran con color y subrayado;
- la versión portable `crear_pdf.bat` sigue funcionando;
- `Ensayo APA / MLA` tiene jerarquía de títulos y espaciado corregido;
- `Manuscrito / novela` ya no coloca el primer título a mitad de página;
- los títulos de todas las plantillas usan reglas propias para no quedar afectados por el interlineado del texto normal.
