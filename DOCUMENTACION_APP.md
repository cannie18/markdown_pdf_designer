# Markdown PDF Designer

## Resumen

Markdown PDF Designer es una aplicación local de escritorio para convertir
documentos Markdown en PDF mediante este flujo:

```text
Markdown -> Pandoc -> Typst -> PDF
```

La app está desarrollada en Python con PySide6. Su objetivo es permitir que el
usuario escriba contenido limpio en Markdown y controle la presentación final
del PDF desde plantillas y opciones visuales, sin convertir el editor en un
procesador de textos complejo.

## Objetivo Del Producto

La aplicación busca resolver un flujo concreto:

1. Abrir, crear o arrastrar un archivo Markdown.
2. Revisar o editar el contenido.
3. Elegir una plantilla visual.
4. Ajustar parámetros de diseño.
5. Generar una vista previa PDF.
6. Exportar el PDF final solo cuando el resultado sea correcto.

La separación principal del proyecto es:

```text
contenido != presentación
```

El Markdown describe estructura y contenido. Las plantillas Typst y los
controles de la app definen la apariencia.

## Interfaz

La ventana principal se divide en dos zonas:

```text
panel izquierdo de trabajo | visor derecho de vista previa
```

El panel izquierdo contiene las secciones `Markdown` y `Diseño`, además del
botón `Ayuda`. La vista previa del PDF permanece a la derecha para revisar el
resultado real.

### Markdown

La sección `Markdown` permite:

- crear un Markdown nuevo;
- abrir un archivo `.md` o `.markdown`;
- arrastrar un Markdown desde el explorador;
- elegir documentos recientes desde la caja de ruta;
- editar el contenido;
- guardar cambios;
- guardar el Markdown como otro archivo;
- cerrar el Markdown actual;
- generar una vista previa PDF;
- abrir la vista previa actual en el visor predeterminado de Windows;
- guardar la vista previa como PDF definitivo.

La fila de ruta, `Abrir` y `Nuevo` permanece siempre arriba, tanto si hay un
documento cargado como si no.

### Diseño

La sección `Diseño` permite configurar la salida PDF. Los parámetros se agrupan
por secciones compactas con iconos y tooltips.

Secciones disponibles:

- `Plantilla visual`: selector de plantilla base y gestión de plantillas
  personalizadas.
- `Página`: márgenes laterales, márgenes verticales, fondo de página y modo de
  documento continuo.
- `Texto`: fuente, tamaño, color, interlineado, espaciado entre párrafos,
  tamaños y colores de títulos, negrita y cursiva.
- `Código`: fuente, tamaño y fondo de bloques de código.
- `Bloques`: estilo de citas y bloques destacados.
- `Tablas`: espaciado de celdas, modo de ancho, tamaño/color de texto, bordes y
  colores de cabecera.

Desde `Diseño` siempre está disponible `Generar PDF`. Los botones propios de
edición del Markdown, como `Cerrar`, `Guardar` y `Guardar como`, no aparecen en
esta sección.

### Ayuda

El botón `Ayuda` funciona como interruptor. Al pulsarlo, la ayuda aparece en el
visor derecho. El usuario puede cambiar entre `Markdown` y `Diseño` sin cerrar
la ayuda.

La ayuda solo desaparece cuando:

- el usuario vuelve a pulsar `Ayuda`;
- se genera una nueva vista previa PDF.

## Flujo De Generación Y Exportación

`Generar PDF` no guarda directamente el PDF final junto al Markdown. La app
genera una vista previa temporal en:

```text
tmp/preview/preview.pdf
```

Ese archivo temporal se sobrescribe en cada generación. Esto permite probar
plantillas y parámetros sin llenar carpetas con PDFs intermedios.

Cuando el resultado es correcto, el usuario usa `Guardar PDF como` para exportar
la vista previa actual a la ruta que elija.

`Abrir PDF en Windows` abre la vista previa temporal actual con el visor
predeterminado del sistema.

## Modo Paginado Y Modo Continuo

La app permite elegir entre:

- PDF paginado normal, con páginas A4 o A5 según la plantilla;
- documento continuo, donde Typst usa `height: auto` para crear una página alta
  de altura automática.

El modo continuo se activa en `Diseño > Página` mediante el control `Documento
continuo`.

Técnicamente el resultado sigue siendo un PDF, pero en vez de dividir el
contenido automáticamente en páginas, lo coloca en una página vertical larga.

Si el Markdown contiene saltos manuales con:

```markdown
<!-- pagebreak -->
```

esos saltos se respetan también en modo continuo.

## Plantillas

Las plantillas predefinidas viven en:

```text
app/templates/
```

Plantillas actuales:

- `Estudio`: apuntes claros y equilibrados.
- `LaTeX clásico`: estilo académico sobrio.
- `Ensayo APA / MLA`: trabajos universitarios con márgenes e interlineado
  amplio.
- `Informe ejecutivo`: documento corporativo con títulos destacados.
- `Manual técnico`: documentación técnica con código protagonista.
- `Accesibilidad y neurodivergencia`: lectura accesible, sans-serif, aire
  amplio y fondo suave.
- `Manuscrito / novela`: formato A5 para lectura prolongada.
- `Profesional`: informe sobrio de uso general.
- `Compacto`: dos columnas y menor consumo de páginas.

La ficha completa de estilos de `Accesibilidad y neurodivergencia` está en
`docs/plantilla_accesibilidad_neurodivergencia.md`.

Las plantillas personalizadas se crean desde la app y se guardan fuera del
repositorio, en:

```text
%APPDATA%\pdf_apuntes\templates
```

La app protege cambios sin guardar en plantillas personalizadas al cerrar o al
cambiar de plantilla. Las plantillas predefinidas no se sobrescriben desde la
interfaz.

## Markdown Soportado

La conversión principal depende de Pandoc, por lo que la app cubre Markdown
estándar y extensiones habituales.

Casos soportados y ajustados:

- títulos `#` a `######`;
- párrafos;
- negrita y cursiva;
- listas con viñetas;
- listas numeradas;
- listas anidadas;
- enlaces clicables con color y subrayado;
- tablas;
- citas;
- bloques de código;
- código inline;
- metadatos YAML cuando Pandoc los interpreta;
- caracteres Unicode;
- `[TOC]` como índice automático;
- `<!-- pagebreak -->` como salto manual;
- HTML inline básico:
  - `<mark>`;
  - `<br>`;
  - `<strong>` y `<b>`;
  - `<em>` y `<i>`.

Las listas con viñetas y numeradas respetan el espaciado vertical configurado
para el texto del documento. Además, al terminar un bloque de lista se añade un
espacio inferior equivalente al espaciado de párrafo de la plantilla.

Los títulos usan más espacio superior que inferior para separarse del bloque
anterior y quedar asociados al contenido que introducen.

## Alertas Tipo GitHub

La app reconoce alertas tipo GitHub:

```markdown
> [!NOTE]
> Información complementaria.

> [!TIP]
> Consejo práctico.

> [!IMPORTANT]
> Información importante.

> [!WARNING]
> Advertencia.

> [!CAUTION]
> Precaución crítica.
```

Durante la conversión se transforman en bloques visuales con:

- icono SVG;
- borde lateral;
- etiqueta;
- color específico por tipo.

Los iconos están en:

```text
assets/icons/
```

## Sintaxis Especial De La App

### Índice

```markdown
[TOC]
```

Genera un índice Typst.

### Salto De Página

```markdown
<!-- pagebreak -->
```

Genera:

- `#pagebreak()` en plantillas normales;
- `#colbreak()` en plantillas de columnas, como `Compacto`.

## Arquitectura Del Proyecto

Estructura principal:

```text
markdown_pdf_designer/
├── abrir_app.bat
├── app/
│   ├── main.py
│   ├── pdf_builder.py
│   └── templates/
├── assets/
│   └── icons/
├── bin/
│   ├── pandoc/
│   └── typst/
├── crear_pdf.bat
├── ejemplos/
├── templates/
│   └── apuntes.typ
├── README.md
├── APP_ESCRITORIO.md
├── DOCUMENTACION_APP.md
└── TODO.md
```

Archivos clave:

- `app/main.py`: interfaz PySide6, navegación, editor, vista previa y acciones
  de usuario.
- `app/pdf_builder.py`: lógica de conversión Markdown -> Typst -> PDF.
- `app/templates/*.typ`: plantillas dinámicas usadas por la app.
- `templates/apuntes.typ`: plantilla de la versión portable.
- `crear_pdf.bat`: flujo portable básico por consola.
- `abrir_app.bat`: arranque de la app de escritorio.
- `assets/icons/*.svg`: iconos de botones, parámetros y alertas.
- `ejemplos/markdown_referencia_completo.md`: banco de pruebas de Markdown.

## Versión Portable

La versión portable por `.bat` se mantiene separada de la app de escritorio.

Flujo portable:

```text
crear_pdf.bat + templates/apuntes.typ
```

Flujo de app:

```text
app/main.py + app/pdf_builder.py + app/templates/*.typ
```

Esta separación evita que los cambios de interfaz y plantillas dinámicas rompan
el uso básico por consola.

Los binarios locales de Pandoc y Typst pueden estar en:

```text
bin/pandoc/
bin/typst/
```

No se suben al repositorio porque están ignorados por Git.

## Reglas Técnicas Importantes

- No romper `crear_pdf.bat` ni `templates/apuntes.typ` al trabajar en la app.
- Mantener separadas las plantillas portables y las plantillas dinámicas.
- En Python se usa indentación de dos espacios.
- El código favorece cambios pequeños y verificables.
- Las salidas generadas `.pdf` y `.typ` no deben subirse al repositorio.
- `tmp/` se usa para archivos temporales de compilación y vista previa.

## Estado Actual

Estado funcional actual:

- la app genera vista previa PDF desde Markdown;
- la vista previa se sobrescribe en una ruta temporal;
- el usuario puede exportar el PDF final con `Guardar PDF como`;
- todas las plantillas predefinidas compilan;
- existe modo paginado y modo continuo;
- las tablas pueden ajustarse al contenido o al ancho disponible;
- las listas respetan el espaciado vertical del documento;
- las alertas tipo GitHub tienen iconos y colores propios;
- los enlaces conservan hipervínculo clicable;
- `[TOC]` genera índice;
- `<!-- pagebreak -->` genera salto manual;
- la ayuda integrada explica el flujo principal;
- las plantillas personalizadas se guardan fuera del repositorio;
- la versión portable sigue siendo independiente.

## Mejoras Futuras Previstas

Mejoras previstas o pendientes de decidir:

- soporte para imágenes locales referenciadas desde Markdown;
- controles visuales para imágenes;
- portada opcional;
- cabecera y pie de página configurables;
- número de página y total de páginas;
- galería visual de plantillas;
- restaurar valores base de una plantilla;
- guardar ajustes por documento Markdown;
- modo debug para conservar `.typ` intermedios;
- mensajes de error más explicativos;
- empaquetado como `.exe`;
- distribución portable completa como `.zip`.
