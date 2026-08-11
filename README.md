# pdf_apuntes

Prueba minima para evaluar el flujo:

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
que cualquier instalacion del sistema.

Los binarios locales no se suben a GitHub porque estan ignorados en
`.gitignore`. Esto mantiene el repositorio ligero, pero permite copiar la
carpeta local completa a otro equipo para trabajar sin instalar dependencias.

En esta primera prueba no se usa Python. La idea es comprobar si Pandoc y Typst
pueden hacerse cargo de la conversion y la maquetacion basica sin un
preprocesador lleno de expresiones regulares.

## Probar en Windows

Desde PowerShell o `cmd.exe`:

```bat
cd ruta\a\pdf_apuntes
crear_pdf.bat ejemplos\prueba_apuntes.md
```

Resultado esperado:

```text
ejemplos\prueba_apuntes.pdf
```

Si `typst` no esta disponible, el script generara igualmente:

```text
ejemplos\prueba_apuntes.typ
```

Ese archivo permite comprobar la salida de Pandoc antes de anadir Typst al
modo instalado o al modo portable.

## App de escritorio

La app Python se llama Markdown PDF Designer. Vive en `app/` y usa sus propias
plantillas en `app/templates/`. Esto evita que los cambios de la app rompan la
version portable por `.bat`.

Para abrirla:

```bat
abrir_app.bat
```

Tambien puedes arrastrar un archivo Markdown sobre `abrir_app.bat`.

La app permite, de momento:

- crear un archivo Markdown nuevo;
- abrir un archivo `.md`;
- arrastrar un archivo `.md`;
- elegir entre los ultimos Markdown usados desde el desplegable de ruta;
- cargar el Markdown directamente en el editor al abrirlo;
- guardar o guardar como el Markdown;
- generar el PDF con un boton;
- ver el PDF generado dentro de la propia app;
- abrir el PDF generado en el visor predeterminado de Windows;
- elegir fuente, tamano base, margenes, tamanos de titulos y colores antes de generar;
- definir colores independientes para titulos, negrita y cursiva;
- ajustar interlineado, espaciado entre parrafos y estilos de codigo;
- elegir una plantilla visual predefinida;
- recordar posicion, monitor y tamano de ventana;
- mantener un ancho minimo usable para controles y dejar que la vista previa use el espacio restante.

Las opciones visuales de la app se aplican generando una plantilla Typst
temporal a partir de la plantilla elegida en `app/templates/`. La plantilla
portable `templates/apuntes.typ` no se modifica.

## Estructura

```text
pdf_apuntes/
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
│       └── profesional.typ
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

## Siguiente paso

Cuando esta prueba compile correctamente, podemos iterar sobre la plantilla
`templates\apuntes.typ`: portada, colores, cabecera, pie, tablas, codigo,
bloques destacados y tratamiento de ecuaciones.

## Plantillas de la app

Las plantillas disponibles en la app son:

- `Estudio`: equilibrada para apuntes claros.
- `LaTeX clasico`: academica, monocromatica y con margenes amplios.
- `Ensayo APA / MLA`: pensada para trabajos universitarios.
- `Informe ejecutivo`: estilo corporativo con titulos destacados.
- `Manual tecnico`: pensada para documentacion y bloques de codigo.
- `Manuscrito / novela`: formato A5 para lectura prolongada.
- `Profesional`: informe sobrio de uso general.
- `Compacto`: dos columnas y menor consumo de paginas.
