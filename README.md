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

La app Python vive en `app/` y usa sus propias plantillas en `app/templates/`.
Esto evita que los cambios de la app rompan la version portable por `.bat`.

Para abrirla:

```bat
abrir_app.bat
```

Tambien puedes arrastrar un archivo Markdown sobre `abrir_app.bat`.

La app permite, de momento:

- abrir un archivo `.md`;
- arrastrar un archivo `.md`;
- generar el PDF con un boton.

## Estructura

```text
pdf_apuntes/
├── abrir_app.bat
├── app/
│   ├── main.py
│   ├── pdf_builder.py
│   └── templates/
│       └── estudio.typ
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
