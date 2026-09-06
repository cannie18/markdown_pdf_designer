# Plantilla Accesibilidad Y Neurodivergencia

Este documento describe los estilos aplicados por la plantilla `Accesibilidad y
neurodivergencia` de Markdown PDF Designer.

La plantilla está pensada para documentos de lectura accesible, especialmente
cuando se quiere reducir carga visual y mejorar legibilidad para personas con
dislexia, TDA o TDAH.

## Archivos Relacionados

- Plantilla Typst: `app/templates/accesibilidad_neurodivergencia.typ`.
- Preset visual: `accesibilidad_neurodivergencia` en `app/pdf_builder.py`.
- Selector visible en la app: `Accesibilidad y neurodivergencia`.

## Principios De Diseño

La plantilla prioriza:

- alineación izquierda;
- aire visual amplio;
- fondo suave de bajo deslumbramiento;
- fuente sans-serif legible;
- títulos muy diferenciados;
- más espacio por encima que por debajo de los títulos;
- bloques, tablas y código con contraste moderado;
- evitar cursiva real en énfasis, usando negrita en su lugar.

## Página

Valores base:

| Parámetro | Valor |
| --- | --- |
| Papel | A4 |
| Fondo de página | `#fbf6e8` |
| Margen lateral | `32 mm` |
| Margen vertical | `28 mm` |
| Numeración | Activada |
| Posición de número | Inferior centrada |
| Modo continuo | Desactivado por defecto |

Cuando se activa `Documento continuo` en la app, la plantilla añade:

```typst
height: auto,
```

Esto hace que el PDF se genere como una página vertical de altura automática,
salvo que el Markdown incluya saltos manuales.

## Texto Base

Valores base:

| Parámetro | Valor |
| --- | --- |
| Fuente | `Verdana` |
| Tamaño | `13.5 pt` |
| Color | `#333333` |
| Idioma | Español |
| Tracking | `0.018em` |
| Justificación | Desactivada |
| Interlineado | `1.55em` |
| Espacio entre párrafos | `1.65em` |

La alineación izquierda evita ríos visuales y espacios irregulares entre
palabras. El tracking ligero mejora la separación entre caracteres.

## Títulos

Reglas generales:

- no tienen numeración automática;
- no usan justificación;
- no tienen sangría de primera línea;
- no usan guionado automático;
- eliminan el tracking del texto base;
- evitan partirse entre páginas cuando es posible.

### Título De Nivel 1

| Parámetro | Valor |
| --- | --- |
| Tamaño | `27 pt` |
| Peso | Negrita |
| Color | `#24435a` |
| Espacio antes | `1.8em` |
| Espacio después | `0.9em` |
| Línea inferior | `2.2 pt`, color `#24435a` |
| Separación texto/línea | `0.28em` |

### Título De Nivel 2

| Parámetro | Valor |
| --- | --- |
| Tamaño | `20 pt` |
| Peso | Negrita |
| Color | `#2f6f66` |
| Espacio antes | `1.5em` |
| Espacio después | `0.45em` |
| Línea inferior | `1.5 pt`, color `#2f6f66` |
| Separación texto/línea | `0.22em` |

### Título De Nivel 3

| Parámetro | Valor |
| --- | --- |
| Tamaño | `16 pt` |
| Peso | Negrita |
| Color | `#5a5f7a` |
| Espacio antes | `1.1em` |
| Espacio después | `0.32em` |
| Línea inferior | `0.9 pt`, color `#5a5f7a` |
| Separación texto/línea | `0.16em` |

### Títulos De Nivel 4 A 6

| Nivel | Tamaño | Estilo | Color | Espacio antes | Espacio después |
| --- | --- | --- | --- | --- | --- |
| 4 | `tamaño base * 1.02` | Negrita | `#5a5f7a` | `0.7em` | `0.12em` |
| 5 | `tamaño base` | Negrita | `#5a5f7a` | `0.55em` | `0.1em` |
| 6 | `tamaño base * 0.95` | Cursiva | `#5a5f7a` | `0.45em` | `0.08em` |

## Énfasis

| Markdown | Resultado |
| --- | --- |
| `**texto**` | Negrita con color `#24435a` |
| `*texto*` | Negrita con color `#24435a` |

En esta plantilla la cursiva Markdown se transforma en negrita. Esta decisión
busca mejorar legibilidad en contextos donde la cursiva puede dificultar la
lectura.

## Enlaces

Los enlaces se muestran con:

- color `#0057b8`;
- subrayado;
- hipervínculo clicable conservado.

## Listas

Listas con viñetas:

| Parámetro | Valor |
| --- | --- |
| Sangría | `1.3em` |
| Sangría del cuerpo | `0.7em` |
| Espacio entre elementos | `1.65em` |
| Espacio al terminar la lista | `1.65em` |

Listas numeradas:

| Parámetro | Valor |
| --- | --- |
| Sangría | `1.3em` |
| Sangría del cuerpo | `0.8em` |
| Espacio entre elementos | `1.65em` |
| Espacio al terminar la lista | `1.65em` |

El espacio entre elementos y el espacio inferior al terminar el bloque de lista
usan el mismo valor que el espacio entre párrafos de la plantilla.

## Bloques Destacados Y Citas

Valores base:

| Parámetro | Valor |
| --- | --- |
| Espacio antes | `0.9em` |
| Espacio después | `0.9em` |
| Espacio interno | `0.95em` |
| Radio | `3 pt` |
| Borde lateral | `4 pt`, color `#6aa38f` |
| Fondo | `#e8f4ec` |
| Texto | `13.5 pt`, color `#333333` |

Las citas Markdown normales y los bloques destacados se convierten en bloques
con fondo suave y borde lateral.

## Alertas Tipo GitHub

La app reconoce esta sintaxis:

```markdown
> [!NOTE]
> Texto de la alerta.
```

Tipos reconocidos:

- `NOTE`;
- `TIP`;
- `IMPORTANT`;
- `WARNING`;
- `CAUTION`.

Las alertas se procesan en `app/pdf_builder.py`, no directamente en la plantilla
Typst. El resultado visual usa:

- icono SVG desde `assets/icons/`;
- etiqueta en negrita;
- borde lateral coloreado;
- color propio por tipo.

Paleta usada:

| Tipo | Color | Icono |
| --- | --- | --- |
| `NOTE` | `#2f6feb` | `note.svg` |
| `TIP` | `#2da44e` | `tip.svg` |
| `IMPORTANT` | `#8957e5` | `important.svg` |
| `WARNING` | `#bf8700` | `warning.svg` |
| `CAUTION` | `#cf222e` | `caution.svg` |

## Código

Bloques de código:

| Parámetro | Valor |
| --- | --- |
| Espacio antes | `1em` |
| Espacio después | `1em` |
| Espacio interno | `0.95em` |
| Radio | `4 pt` |
| Fuente | `Cascadia Mono` |
| Tamaño | `10.5 pt` |
| Fondo | `#e7f3f2` |
| Texto | `#263638` |

El código inline queda gestionado por la conversión de Pandoc/Typst.

## Tablas

Valores base:

| Parámetro | Valor |
| --- | --- |
| Espacio interno de celdas | `9 pt` |
| Borde | `#b8cbc6` |
| Texto de celda | `13 pt`, color `#333333` |
| Fondo de cabecera | `#e8f4ec` |
| Texto de cabecera | Negrita, color `#24435a` |
| Modo de ancho | Ajustar al contenido |

Desde la app puede cambiarse el modo de ancho:

- `Ajustar al contenido`;
- `Usar ancho disponible`.

## Sintaxis Especial Compatible

La plantilla funciona con las extensiones especiales de la app.

### Índice

```markdown
[TOC]
```

Genera un índice Typst con separación vertical antes y después.

### Salto De Página

```markdown
<!-- pagebreak -->
```

Genera un salto manual de página. En plantillas con columnas se convierte en
salto de columna.

## Opciones Modificables Desde La App

El usuario puede modificar desde `Diseño`:

- fuente principal;
- tamaño base;
- color del texto;
- fondo de página;
- modo continuo;
- interlineado;
- espacio entre párrafos;
- márgenes laterales;
- márgenes verticales;
- tamaños de títulos 1, 2 y 3;
- colores de títulos 1, 2 y 3;
- color de negrita;
- color de cursiva;
- fuente de código;
- tamaño de código;
- fondo de código;
- espacio interno de bloques;
- tamaño de texto de bloques;
- color de texto de bloques;
- color de borde de bloques;
- fondo de bloques;
- espacio de celdas de tabla;
- modo de ancho de tabla;
- tamaño de texto de tabla;
- color de texto de tabla;
- color de bordes de tabla;
- fondo de cabecera;
- color de texto de cabecera.

Si se guarda como plantilla personalizada, estos valores quedan almacenados en
la carpeta de datos de usuario:

```text
%APPDATA%\pdf_apuntes\templates
```

## Resumen Visual

La plantilla `Accesibilidad y neurodivergencia` se caracteriza por:

- fondo crema claro;
- texto grande;
- interlineado amplio;
- párrafos separados;
- títulos con líneas inferiores;
- énfasis sin cursiva real;
- bloques y tablas con tonos verdes suaves;
- código con fondo azul verdoso claro;
- alineación izquierda;
- baja densidad visual.
