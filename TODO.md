# TODO

## Opciones de diseno

- Revisar que opciones visuales deben estar disponibles desde la app.
- Seguir separando opciones basicas y avanzadas para no cargar demasiado la interfaz.
- Mantener dinamicos, como minimo:
  - fuente principal;
  - tamano base del texto;
  - colores de titulos;
  - tamanos de titulos;
  - color del texto normal;
  - estilos de codigo;
  - espaciados principales;
  - margenes del documento.
- Decidir si cada ajuste se guarda por documento, por plantilla o como preferencia global.

## Plantillas

- Revisar y mejorar la estructura para crear y listar plantillas de la app.
- Mantener separadas las plantillas de la app y la plantilla portable por `.bat`.
- Mejorar las plantillas base:
  - estudio;
  - compacto;
  - profesional;
  - apuntes con portada.
- Preparar una pantalla para crear nuevas plantillas desde la interfaz.
- Decidir que partes de una plantilla se editan con controles y cuales se editan como codigo Typst.

## Interfaz

- Seguir puliendo el panel izquierdo con scroll y ancho minimo calculado desde los botones Markdown.
- Valorar una ventana sin barra nativa de Windows al final del desarrollo.
  - Habria que crear botones propios para cerrar, minimizar y maximizar.
  - Habria que implementar arrastre manual de ventana.
- Revisar el comportamiento de la vista previa con PDFs largos.
- Mejorar la pestana de diseno para que permita regenerar el PDF sin perder contexto.
- Ampliar la pestana de plantillas para duplicar y editar plantillas.

## Persistencia

- Guardar la plantilla elegida.
- Guardar opciones visuales usadas recientemente.
- Revisar si conviene guardar ajustes por archivo Markdown.
- Anadir mas adelante una ruta de salida para el PDF.
  - Durante las pruebas, mantener `Generar PDF` sobrescribiendo directamente.
  - En el futuro, preguntar ubicacion la primera vez y permitir `Guardar PDF como`.

## Pruebas

- Probar la app en pantalla de 13 o 14 pulgadas.
- Probar con Markdown largo, tablas, codigo y listas.
- Comprobar que la version portable con `crear_pdf.bat` sigue funcionando tras cada cambio.
