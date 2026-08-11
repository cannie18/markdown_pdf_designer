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
- Generar PDF desde la app sin abrir consola visible.
- Mostrar vista previa del PDF dentro de la app.
- Abrir el PDF generado en el visor predeterminado de Windows.
- Recordar tamaño, posición y monitor de la ventana.
- Panel izquierdo con ancho mínimo basado en la fila de botones Markdown.
- Pestañas `Archivo` y `Diseño`.
- Selector de plantillas predefinidas.
- Carga automática en `Diseño` de los valores base de la plantilla seleccionada.
- Creación de plantillas personalizadas desde los ajustes actuales de `Diseño`.
- Actualización de plantillas personalizadas sin crear copias nuevas.
- Plantillas personalizadas guardadas en `%APPDATA%\pdf_apuntes\templates`.
- Persistencia de la última plantilla y los últimos ajustes visuales usados.
- Corrección de textos visibles de la app a español de España.
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

- Revisar qué opciones visuales deben estar disponibles desde la app.
- Seguir separando opciones básicas y avanzadas para no cargar demasiado la interfaz.
- Mantener dinámicos, como mínimo:
  - fuente principal;
  - tamaño base del texto;
  - colores de títulos;
  - tamaños de títulos;
  - color del texto normal;
  - estilos de código;
  - estilos de tabla;
  - espaciados principales;
  - márgenes del documento.
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

## Interfaz

- Seguir puliendo el panel izquierdo con scroll y ancho mínimo calculado desde los botones Markdown.
- Valorar una ventana sin barra nativa de Windows al final del desarrollo.
  - Habría que crear botones propios para cerrar, minimizar y maximizar.
  - Habría que implementar arrastre manual de ventana.
- Revisar el comportamiento de la vista previa con PDFs largos.
- Mejorar la pestaña de diseño para que permita regenerar el PDF sin perder contexto.
- Valorar si una galería futura de plantillas debe permitir duplicar y editar plantillas.

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

## Próxima Sesión

Recomendación para empezar un chat nuevo:

```text
Continuamos en el proyecto pdf_apuntes.
Lee README.md, APP_ESCRITORIO.md y TODO.md antes de tocar código.
Quiero seguir con la parte de plantillas y opciones de diseño de Markdown PDF Designer.
Mantén intacta la versión portable: crear_pdf.bat y templates/apuntes.typ.
En Python usa indentación de dos espacios y comillas simples cuando se pueda.
```
