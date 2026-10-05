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

El contenido se organiza por tareas. Comienza con una guía rápida numerada y
continúa con apartados independientes para archivos y acciones, escritura
Markdown, imágenes, tablas, funciones especiales, vista previa PDF, secciones
de diseño, plantillas y controles. Cada apartado agrupa sus propias
instrucciones mediante subtítulos y listas, evitando mezclar opciones de temas
distintos.

## Flujo De Generación Y Exportación

### Navegar Del PDF Al Markdown

Un clic normal sobre un bloque de la vista previa coloca el cursor al comienzo
del bloque correspondiente en el editor Markdown y lo resalta durante un
instante. Esta navegación solo está activa cuando el panel izquierdo muestra
`Markdown`. En `Diseño`, pulsar sobre un bloque del PDF no cambia de sección
ni mueve el cursor. El salto no modifica el texto ni selecciona contenido para
sustituirlo al escribir.

En tablas, imágenes, listas y bloques de código se localiza el comienzo del
bloque, no una celda o palabra concreta. Los enlaces conservan su función:
los externos abren su destino y los internos navegan dentro del PDF.

La correspondencia se calcula durante la generación con posiciones reales
de la maquetación, también en documentos continuos y plantillas de columnas.
No hay sincronización automática del scroll. Si el Markdown cambia después
de generar el PDF, el salto queda suspendido hasta regenerarlo o recuperar
exactamente el texto que produjo esa vista previa. Guardar el Markdown
modificado no actualiza por sí solo la correspondencia.

Los márgenes, espacios entre bloques y estructuras que los lectores Markdown
no puedan relacionar con seguridad pueden no responder al clic. Se conserva
el lector Pandoc habitual para generar el contenido; no se cambia el formato
del documento para obtener posiciones. La navegación pertenece a la vista
previa de la app, no al PDF exportado ni al flujo portable.

Ejemplo para probar: `ejemplos/prueba_navegacion_pdf.md`.

### Generar Y Exportar

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
- ajustes individuales de tablas mediante bloques `table-style`;
- citas;
- bloques de código;
- código inline;
- imágenes locales con rutas relativas al Markdown y tamaño mediante atributos;
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

## Estilos Individuales De Tablas

Las tablas normales usan los valores de `Diseño > Tablas`. Para ajustar una
tabla concreta, colócala dentro de un bloque con la clase `table-style`:

```markdown
::: {.table-style font-size=8pt cell-padding=2pt table-width=full columns="1,4,2"}

| ID | Descripción | Estado |
| --- | --- | --- |
| 01 | Texto largo que necesita más espacio. | En curso |

:::
```

Opciones disponibles (todas son opcionales):

| Opción | Ejemplo | Efecto |
| --- | --- | --- |
| `font-size` | `8pt` | Tamaño de letra de las celdas, incluida la cabecera. |
| `cell-padding` | `2pt` | Espacio interno de las celdas. Se admite `0pt`. |
| `table-width` | `full` | Usa el ancho disponible, con columnas iguales si no hay proporciones. |
| `table-width` | `auto` | Ajusta las columnas al contenido. |
| `columns` | `"1,4,2"` | Reparte el ancho disponible en proporciones de 1, 4 y 2 partes. |

Los tamaños se expresan en puntos (`pt`); también se admite un número sin
unidad, que se interpreta como puntos. `columns` requiere un número positivo
por columna. Si lo indicas, sus proporciones tienen prioridad sobre
`table-width` y ocupan el ancho disponible.

Por ejemplo, `::: {.table-style font-size=8pt}` cambia solamente el tamaño de
letra. Las opciones que omitas mantienen los valores generales de Diseño.
Las proporciones de `columns` se indican en el mismo orden que las columnas
de la tabla, de izquierda a derecha.

En modo `auto`, el motor considera tanto los encabezados como el contenido.
Una cabecera larga puede recibir demasiado ancho aunque sus filas contengan
números cortos, mientras otra columna de texto queda estrecha. Evitar el
guionado en los encabezados no corrige por sí solo ese reparto. Para controlar
estos casos, usa `columns` y asigna más espacio a las columnas cuyo contenido
se divide en demasiadas líneas. La mejora del reparto automático para este
tipo de tablas sigue pendiente.

Los encabezados de las tablas priorizan los saltos entre palabras y no usan
guionado automático, tanto en tablas normales como en tablas con estilos
locales. Si una palabra sola supera el ancho de la columna, debes ampliar
esa columna o reducir el tamaño de letra para evitar cortes forzados.

El bloque debe contener exactamente una tabla; deja las explicaciones y los
títulos fuera del bloque. Los ajustes se aplican solo a esa tabla. Sus colores,
bordes y demás estilos siguen usando la plantilla. Las tablas siguientes
recuperan los ajustes generales, y `table-width=auto` local se respeta aunque
en Diseño hayas seleccionado ancho completo.

Para una tabla ancha, prueba primero a reducir el espacio de las celdas y dar
más proporción a las columnas de texto largo. Si hace falta, reduce la letra.
No se garantiza que cualquier tabla quepa sin saltos: muchas columnas o palabras
largas pueden requerir dividir la información. En `Compacto`, el espacio
disponible es el de una columna. Estos ajustes no cambian la orientación de
la página y son una extensión de la app, no del flujo portable por `.bat`.

Puedes probar los casos con `ejemplos/prueba_estilos_tablas.md`.

## Imágenes Y Tamaños

Las rutas de las imágenes locales se resuelven desde la carpeta del Markdown.
Si la imagen está en la misma carpeta, basta con su nombre. También se admiten
subcarpetas, como `imagenes/diagrama.png`.

Añade los atributos de tamaño inmediatamente después de la ruta:

```markdown
![Diagrama](diagrama.png){width=50%}

![Diagrama](imagenes/diagrama.png){width=8cm}

![Diagrama](imagenes/diagrama.png){height=3cm}

![Diagrama](imagenes/diagrama.png){width=8cm height=3cm}
```

`width` indica el ancho y `height` la altura. Se pueden usar unidades como
`cm`, `mm`, `in`, `pt` y `px`. El porcentaje de ancho se refiere al espacio
disponible para el contenido, no al ancho original de la imagen ni al papel
completo. En `Compacto`, se refiere al ancho de la columna.

Para mantener la proporción original, indica solo ancho o solo altura. Si
especificas ambas dimensiones, Typst encaja la imagen en ese espacio y puede
recortar sus bordes. Evita alturas porcentuales en el modo continuo, cuya
altura se calcula automáticamente.

Esta sintaxis usa la extensión de atributos de imágenes de Pandoc; no todos
los visores Markdown muestran estos tamaños. Puedes probarla con
`ejemplos/prueba_tamanos_imagenes.md`.

En la app, las imágenes en su propio párrafo se centran por defecto, con o sin
pie de figura. Puedes elegir la alineación por imagen:

```markdown
![Diagrama](diagrama.png){width=50% align=center}

![Diagrama](diagrama.png){width=50% align=left}

![](diagrama.png){width=50% align=right}
```

Los valores admitidos son `left`, `center` y `right`. La alineación se aplica
dentro del ancho disponible, también en columnas, listas y citas. Las imágenes
insertadas dentro de una frase conservan su posición en el texto. El flujo
portable por `.bat` no aplica esta extensión de alineación de la app.

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
- `app/filters/image_layout.lua`: filtro Pandoc para alinear imágenes aisladas.
- `app/filters/table_layout.lua`: filtro Pandoc para anchos y estilos locales de tablas.
- `app/filters/source_navigation.lua`: relación de bloques con líneas Markdown y marcas de posición.
- `app/source_navigation.py`: mapa de líneas y localización de bloques en páginas y columnas.
- `app/pdf_preview.py`: visor con clic sobre bloques y enlaces.
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
