# TODO

## Opciones de diseno

- Revisar que opciones visuales deben estar disponibles desde la app.
- Separar opciones basicas y avanzadas para no cargar demasiado la interfaz.
- Mantener dinamicos, como minimo:
  - fuente principal;
  - tamano base del texto;
  - colores de titulos;
  - tamanos de titulos;
  - espaciados principales;
  - margenes del documento.
- Decidir si cada ajuste se guarda por documento, por plantilla o como preferencia global.

## Plantillas

- Definir una estructura para crear y listar plantillas de la app.
- Mantener separadas las plantillas de la app y la plantilla portable por `.bat`.
- Crear varias plantillas base cuando el diseno este mas claro:
  - estudio;
  - compacto;
  - profesional;
  - apuntes con portada.
- Preparar una pantalla para crear nuevas plantillas desde la interfaz.
- Decidir que partes de una plantilla se editan con controles y cuales se editan como codigo Typst.

## Interfaz

- Seguir puliendo el panel izquierdo con scroll y ancho minimo calculado desde los botones Markdown.
- Revisar el comportamiento de la vista previa con PDFs largos.
- Mejorar la pestana de diseno para que permita regenerar el PDF sin perder contexto.
- Dejar la pestana de plantillas preparada para seleccionar, duplicar y editar plantillas.

## Persistencia

- Guardar la plantilla elegida.
- Guardar opciones visuales usadas recientemente.
- Revisar si conviene guardar ajustes por archivo Markdown.

## Pruebas

- Probar la app en pantalla de 13 o 14 pulgadas.
- Probar con Markdown largo, tablas, codigo y listas.
- Comprobar que la version portable con `crear_pdf.bat` sigue funcionando tras cada cambio.
