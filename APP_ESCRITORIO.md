# Markdown PDF Designer

## Que es

Markdown PDF Designer es una app de escritorio local para generar PDF de
apuntes a partir de archivos Markdown, ajustando el resultado a necesidades de
diseno concretas.

Su objetivo no es sustituir al Markdown ni convertir la herramienta en un
editor complejo. La idea principal es facilitar este flujo:

```text
abrir o arrastrar Markdown
revisar opcionalmente el contenido
elegir estilo visual
generar PDF
ver el resultado dentro de la app
```

La app esta creada con Python y PySide6.

## Estructura visual deseada

La app se organiza con una vista previa PDF permanente a la derecha y un panel
de trabajo cambiante a la izquierda.

```text
panel izquierdo cambiante | vista previa PDF
```

El panel izquierdo tiene tres secciones:

- `Archivo`: abrir o arrastrar Markdown, revisar contenido y generar PDF.
- `Diseno`: ajustar fuente, tamano y colores antes de volver a generar.
- `Plantillas`: preparar seleccion y creacion de plantillas visuales.

La vista previa no es una pestana separada: debe estar siempre disponible para
comprobar el PDF real generado.

## Principio de diseno

La herramienta mantiene separado:

```text
contenido != presentacion
```

El Markdown debe describir la estructura del apunte:

```markdown
# Titulo

## Seccion

Texto, listas, tablas, codigo y bloques destacados.
```

La apariencia del PDF se controla desde plantillas Typst y desde opciones de la
app, no desde marcas visuales incrustadas en el Markdown.

## Estado actual

La app permite:

- abrir un archivo `.md`;
- arrastrar un archivo `.md`;
- ver y editar opcionalmente el contenido;
- preguntar antes de generar si hay cambios sin guardar;
- elegir tipo de fuente;
- elegir tamano base del texto;
- elegir color del texto normal;
- ajustar interlineado y espacio entre parrafos;
- elegir margenes laterales y verticales;
- elegir tamano de titulos de nivel 1, 2 y 3;
- elegir colores para titulos de nivel 1, 2 y 3;
- elegir colores independientes para negrita y cursiva;
- elegir fuente, tamano y fondo de los bloques de codigo;
- generar el PDF;
- mostrar el PDF generado dentro de la propia app;
- abrir el PDF en el visor externo de Windows.
- cambiar entre secciones `Archivo`, `Diseno` y `Plantillas` en el panel
  izquierdo.

## Relacion con la version portable

La app Python y la version portable por `.bat` deben evolucionar de forma
separada.

```text
crear_pdf.bat
templates/apuntes.typ
```

pertenecen a la version portable basica.

```text
app/main.py
app/pdf_builder.py
app/templates/estudio.typ
```

pertenecen a la app de escritorio.

Esto permite mejorar la app sin romper el flujo simple:

```powershell
.\crear_pdf.bat .\ejemplos\archivo.md
```

## Como genera el PDF la app

La app no transforma manualmente el Markdown con expresiones regulares.

El flujo es:

```text
Markdown
  -> Pandoc
  -> Typst
  -> PDF
```

Cuando el usuario cambia fuente, tamano, margenes, titulos o colores, Python genera una plantilla
Typst temporal a partir de:

```text
app/templates/estudio.typ
```

Esa plantilla temporal se usa solo durante la conversion y se elimina al
terminar.

## Pretensiones

La app quiere convertirse progresivamente en una herramienta sencilla para
crear PDF de estudio con buena maquetacion.

Objetivos previstos:

- selector de plantillas visuales;
- ajustes dinamicos por plantilla;
- estilos para tablas;
- estilos para bloques destacados;
- estilos para codigo;
- portada opcional;
- cabecera y pie de pagina configurables;
- numero de pagina y total de paginas;
- salida a una carpeta elegida por el usuario;
- modo debug para conservar `.typ` intermedios;
- mensajes de error mas comprensibles;
- empaquetado como `.exe` para usar sin abrir terminal;
- version portable completa distribuible como `.zip`.

## Cosas que no queremos hacer de momento

- crear un editor Markdown avanzado;
- mezclar la plantilla portable con las plantillas dinamicas de la app;
- volver a convertir Markdown a mano mediante muchas expresiones regulares;
- subir binarios pesados como `pandoc.exe` o `typst.exe` al repositorio Git.

## Criterio de avance

Cada mejora debe ser pequena y comprobable.

Antes de ampliar la app conviene verificar siempre:

- que la app genera PDF;
- que la vista previa carga el PDF;
- que la version `crear_pdf.bat` sigue funcionando;
- que las plantillas de la app no rompen las plantillas portables.
