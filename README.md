# pdf_apuntes

Prueba minima para evaluar el flujo:

```text
Markdown -> Pandoc -> Typst -> PDF
```

## Requisitos

- `pandoc` disponible en `PATH`.
- `typst` disponible en `PATH` para generar el PDF final.

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

Si `typst` no esta instalado, el script generara igualmente:

```text
ejemplos\prueba_apuntes.typ
```

Ese archivo permite comprobar la salida de Pandoc antes de instalar Typst.

## Estructura

```text
pdf_apuntes/
├── crear_pdf.bat
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
