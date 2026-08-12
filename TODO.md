# TODO

## Estado Actual

- App principal: `app/main.py`.
- Generación PDF: `app/pdf_builder.py`.
- Plantillas dinámicas de la app: `app/templates/*.typ`.
- Flujo portable independiente: `crear_pdf.bat` + `templates/apuntes.typ`.
- No romper el flujo portable al tocar la app.
- En Python se está usando indentación de dos espacios y, cuando se puede, comillas simples.

## Hecho

- App de escritorio básica con PySide6.
- Abrir, crear, arrastrar, editar, cerrar, guardar y guardar como Markdown.
- `Nuevo` abre un Markdown sin guardar y pide ubicación al guardar o generar PDF.
- Generar PDF desde la app sin abrir consola visible.
- Mostrar vista previa del PDF dentro de la app.
- Abrir el PDF generado en el visor predeterminado de Windows.
- Recordar tamaño, posición y monitor de la ventana.
- Panel izquierdo con ancho mínimo basado en la fila de botones Markdown.
- Fila de ruta, `Nuevo` y `Abrir` siempre arriba en `Markdown`.
- `Abrir` queda junto a la caja de ruta y `Nuevo` después.
- Botones de navegación `Markdown` y `Diseño` sobre un `QStackedWidget`.
- Botón `Ayuda` integrado junto a `Markdown` y `Diseño`, con contenido mostrado en el visor.
- `Ayuda` funciona como interruptor: muestra instrucciones y permite volver al PDF o a la guía inicial.
- `Ayuda` se desactiva visualmente al generar y mostrar un PDF.
- Ayuda ampliada con guía rápida, botones de `Markdown`, flujo de plantillas y secciones de `Diseño`.
- Guía breve en el visor cuando todavía no hay PDF cargado.
- Selector de plantillas predefinidas.
- Carga automática en `Diseño` de los valores base de la plantilla seleccionada.
- Creación de plantillas personalizadas desde los ajustes actuales de `Diseño`.
- Actualización de plantillas personalizadas sin crear copias nuevas.
- Protección de cambios sin guardar en plantillas personalizadas al cerrar o cambiar de plantilla.
- Plantillas personalizadas guardadas en `%APPDATA%\pdf_apuntes\templates` por compatibilidad histórica.
- Persistencia de la última plantilla seleccionada.
- Controles numéricos protegidos frente a cambios accidentales con la rueda del ratón.
- Opciones de bloques destacados:
  - espacio interno;
  - color del borde;
  - color de fondo;
  - color del texto;
  - tamaño del texto.
- Opciones de tablas:
  - espacio de celdas;
  - modo de ancho: contenido o ancho disponible;
  - color de bordes;
  - color del texto;
  - tamaño del texto;
  - color de fondo de cabecera;
  - color del texto de cabecera.
- Opción de color de fondo de página del PDF.
- Corrección de textos visibles de la app a español de España.
- Resaltado de opción seleccionada y opción bajo el mouse en desplegables.
- Parámetros de `Diseño` reorganizados en filas compactas con iconos y tooltips.
- Títulos Markdown de nivel 4, 5 y 6 diferenciados visualmente en las plantillas.
- Enlaces Markdown con formato visual diferenciado en el PDF.
- Separación entre plantillas de app y plantilla portable.
- Primera fase de plantillas predefinidas:
  - `Estudio`;
  - `LaTeX clásico`;
  - `Ensayo APA / MLA`;
  - `Informe ejecutivo`;
  - `Manual técnico`;
  - `Accesibilidad y neurodivergencia`;
  - `Manuscrito / novela`;
  - `Profesional`;
  - `Compacto`.
- Correcciones recientes de plantillas:
  - `Ensayo APA / MLA` tiene jerarquía real de títulos;
  - `Ensayo APA / MLA` ya no usa espacio entre párrafos igual a cero;
  - `Manuscrito / novela` ya no empieza con el título a mitad de página;
  - los títulos no heredan justificación, sangría ni guionado automático;
  - el espacio entre párrafos no puede quedar por debajo del interlineado.

## Opciones De Diseño

- Seguir separando opciones básicas y avanzadas para no cargar demasiado la interfaz.
- Mantener dinámicos, como mínimo:
  - fuente principal;
  - tamaño base del texto;
  - colores de títulos;
  - tamaños de títulos;
  - color del texto normal;
  - color de fondo de página;
  - estilos de código;
  - estilos de bloques destacados;
  - color y tamaño de texto en tablas y bloques;
  - estilos de tabla y modo de ancho;
  - espaciados principales;
  - márgenes del documento.
- Revisar si conviene añadir controles para:
  - ancho del borde lateral de bloques destacados;
  - radio de bloques destacados;
  - alineación del cuerpo de texto por plantilla;
  - espaciado de listas;
  - color de enlaces.
- Decidir si cada ajuste se guarda por documento, por plantilla o como preferencia global.

## Plantillas

- Revisar y mejorar la estructura para crear y listar plantillas de la app desde la interfaz.
- Valorar una futura galería de plantillas en grid con definición rápida y vista previa cacheada.
  - Debe permitir comparar plantillas sin convertir manualmente cada documento.
  - La vista puede ser PDF de ejemplo ya generado o imagen derivada del PDF.
  - Debe mostrar componentes clave: títulos, párrafos, listas, tabla, cita, código, negrita y cursiva.
- Mantener separadas las plantillas de la app y la plantilla portable por `.bat`.
- Mejorar las plantillas base:
  - `estudio`;
  - `compacto`;
  - `profesional`;
  - apuntes con portada.
- Preparar futuras plantillas:
  - IEEE doble columna;
  - acta;
  - factura;
  - hoja resumen;
  - currículum;
  - artículo de blog.
- Preparar una pantalla para crear nuevas plantillas desde la interfaz.
- Decidir qué partes de una plantilla se editan con controles y cuáles se editan como código Typst.

## Imágenes

- Preparar soporte futuro para imágenes referenciadas desde Markdown.
- Resolver rutas relativas respecto a la carpeta del `.md`, no respecto a la app.
- Mostrar errores claros si una imagen local no existe.
- Decidir más adelante si se soportan imágenes remotas o si deben descargarse antes.
- Valorar controles de diseño para imágenes:
  - ancho máximo;
  - alineación;
  - espaciado;
  - pie de figura.

## Compatibilidad Markdown

- Revisar soporte de HTML inline y bloques HTML:
  - `<mark>` no se conserva actualmente como resaltado;
  - `<br>` no genera salto visual;
  - `<strong>` dentro de HTML no se convierte en negrita.
- Decidir cómo representar alertas tipo GitHub:
  - `> [!NOTE]`;
  - `> [!WARNING]`.
- Revisar el resultado visual del texto preformateado por sangría de cuatro espacios.
- Mantener `ejemplos/markdown_referencia_completo.md` como banco de pruebas principal.

## Interfaz

- Seguir puliendo el panel izquierdo con scroll y ancho mínimo calculado desde los botones Markdown.
- Valorar una ventana sin barra nativa de Windows al final del desarrollo.
  - Habría que crear botones propios para cerrar, minimizar y maximizar.
  - Habría que implementar arrastre manual de ventana.
- Revisar el comportamiento de la vista previa con PDFs largos.
- Mejorar la sección `Diseño` para que permita regenerar el PDF sin perder contexto.
- Mantener `Generar PDF` siempre visible y usable en `Diseño`.
- Valorar si una galería futura de plantillas debe permitir duplicar y editar plantillas.
- Valorar si algunos botones de acción secundarios deberían pasar a modo solo icono.
- Revisar más adelante si el botón `Ayuda` debe enlazar ejemplos de Markdown.

## Persistencia

- Revisar si conviene añadir un botón para restaurar valores base de la plantilla.
- Revisar si conviene guardar ajustes por archivo Markdown.
- Añadir más adelante una ruta de salida para el PDF.
  - Durante las pruebas, mantener `Generar PDF` sobrescribiendo directamente.
  - En el futuro, preguntar ubicación la primera vez y permitir `Guardar PDF como`.

## Pruebas

- Probar la app en pantalla de 13 o 14 pulgadas.
- Probar con Markdown largo, tablas, código y listas.
- Comprobar que la versión portable con `crear_pdf.bat` sigue funcionando tras cada cambio.
