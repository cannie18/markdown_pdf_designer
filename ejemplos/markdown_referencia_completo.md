---
title: "Documento De Referencia Markdown"
subtitle: "Banco de pruebas para Markdown PDF Designer"
author: "Equipo Markdown PDF Designer"
date: "2026-08-12"
lang: "es"
keywords:
  - markdown
  - pdf
  - typst
---

# Documento De Referencia Markdown

Este archivo sirve como banco de pruebas para comprobar que la app interpreta y
convierte correctamente los elementos habituales de Markdown al generar un PDF.
Debe poder abrirse desde la app, generar un PDF y mostrar diferencias claras
cuando alguna parte del flujo no esté soportada todavía.

[TOC]

---

## 1. Párrafos Y Saltos

Este es un párrafo normal. Incluye texto suficiente para comprobar el ancho de
línea, el interlineado, la separación entre párrafos y la justificación aplicada
por cada plantilla visual.

Este es otro párrafo. Markdown separa párrafos con una línea en blanco.

Esta línea termina con dos espacios para forzar un salto de línea.  
Esta línea debería aparecer justo debajo, dentro del mismo bloque de texto.

## 2. Títulos

# Título Nivel 1

## Título Nivel 2

### Título Nivel 3

#### Título Nivel 4

##### Título Nivel 5

###### Título Nivel 6

## 3. Énfasis En Línea

Texto con **negrita**, *cursiva*, ***negrita y cursiva***, ~~tachado~~,
`código inline`, texto con <sub>subíndice</sub> y texto con <sup>superíndice</sup>.

También conviene probar caracteres frecuentes en español: á, é, í, ó, ú, ñ,
ü, signos de apertura ¿? y ¡!, comillas “tipográficas” y guiones largos.

## 4. Enlaces

Enlace con texto descriptivo: [Pandoc](https://pandoc.org).

Enlace automático: <https://typst.app>.

Correo automático: <contacto@example.com>.

Referencia reutilizable: consulta la [documentación de Markdown][markdown-docs].

[markdown-docs]: https://www.markdownguide.org/basic-syntax/

## 5. Listas No Ordenadas

- Elemento principal.
- Elemento con texto largo para revisar sangrías y saltos de línea dentro de la
  misma viñeta cuando el contenido ocupa más de una línea.
  - Subnivel uno.
    - Subnivel dos.
      - Subnivel tres.
- Último elemento de la lista.

## 6. Listas Ordenadas

1. Primer paso.
2. Segundo paso.
   1. Subpaso A.
   2. Subpaso B.
3. Tercer paso con un párrafo asociado.

   Este párrafo pertenece al tercer paso y debe conservar la sangría visual.

## 7. Listas De Tareas

- [x] Abrir un archivo Markdown.
- [x] Ajustar una plantilla visual.
- [ ] Generar soporte completo para imágenes.
- [ ] Revisar notas al pie y enlaces internos.

## 8. Citas

> Una cita simple debe diferenciarse visualmente del texto normal.

> Una cita puede tener varios párrafos.
>
> El segundo párrafo sigue perteneciendo al mismo bloque citado.

> Cita de primer nivel.
>
> > Cita anidada de segundo nivel.

## 9. Bloques De Código

Código sin lenguaje:

```
linea_uno = "valor"
linea_dos = linea_uno.upper()
```

Código Python:

```python
def generar_titulo(texto: str) -> str:
  return texto.strip().title()

print(generar_titulo('markdown pdf designer'))
```

Código JSON:

```json
{
  "documento": "referencia",
  "formatos": ["markdown", "typst", "pdf"],
  "activo": true
}
```

## 10. Tablas Básicas

| Elemento | Estado | Prioridad |
| --- | --- | --- |
| Títulos | Soportado | Alta |
| Listas | Soportado | Alta |
| Imágenes | Pendiente de revisión | Media |
| Notas al pie | Pendiente de revisión | Media |

## 11. Tablas Con Alineación

| Izquierda | Centro | Derecha |
| :--- | :---: | ---: |
| Texto | Texto | 12 |
| Más texto | Valor centrado | 345 |
| Celda larga para probar ajuste de línea | Otro valor | 6789 |

## 12. Tabla Compleja

+----------------------+----------------------+----------------------+
| Columna A            | Columna B            | Columna C            |
+======================+======================+======================+
| Contenido largo que  | Lista dentro de una  | Código inline:       |
| debería partir línea | celda:               | `valor = 42`         |
| sin romper la tabla. |                      |                      |
|                      | - uno                |                      |
|                      | - dos                |                      |
+----------------------+----------------------+----------------------+
| Segunda fila         | Texto normal         | Resultado esperado   |
+----------------------+----------------------+----------------------+

## 13. Imágenes

Imagen local con ruta relativa desde este archivo:

![Diagrama local usado como imagen de prueba](imagenes/imagen-ejemplo.svg)

La app debería resolver la ruta relativa respecto a la carpeta del Markdown, no
respecto al directorio desde el que se ejecuta la aplicación.

## 14. Notas Al Pie

Este párrafo incluye una nota al pie breve.[^nota-breve]

También incluye una nota con más contenido.[^nota-larga]

[^nota-breve]: Esta es una nota al pie sencilla.

[^nota-larga]: Esta nota al pie tiene más texto para comprobar el ancho, el
  salto de línea y la separación respecto al cuerpo principal del documento.

## 15. Definiciones

Markdown
: Lenguaje de marcado ligero pensado para escribir texto estructurado de forma
  legible.

PDF
: Formato final de salida que debe conservar composición, tipografía y
  paginación.

Typst
: Motor de maquetación usado para convertir el contenido intermedio en PDF.

## 16. Separadores

Texto antes del separador.

---

Texto después del separador.

## 17. Matemáticas

Fórmula inline: $E = mc^2$.

Fórmula en bloque:

$$
\int_0^1 x^2\,dx = \frac{1}{3}
$$

## 18. HTML Inline Y Bloques HTML

Markdown admite HTML en muchos procesadores. La app debe decidir si lo soporta,
si lo ignora o si muestra una advertencia clara.

Texto con <mark>resaltado HTML</mark> y un salto manual <br> dentro de la línea.

<div>
  <strong>Bloque HTML:</strong> contenido que puede no tener equivalencia directa
  en Typst.
</div>

## 19. Comentarios

El siguiente comentario HTML no debería verse en el PDF final si el conversor lo
trata como comentario.

<!-- Comentario interno que no debería renderizarse. -->

## 20. Bloques Especiales Tipo Alerta

> [!NOTE]
> Este patrón se usa en GitHub para notas destacadas.

> [!WARNING]
> Este patrón no es Markdown básico. La app debe decidir si lo transforma, lo
> deja como cita normal o lo documenta como no soportado.

## 21. Enlaces Internos

Este enlace apunta a la sección [Tablas Básicas](#tablas-básicas).

## 22. Caracteres Y Escapes

Caracteres escapados: \*no cursiva\*, \`no código\`, \[no enlace\].

Símbolos frecuentes: %, €, $, &, #, _, *, |, \, /, @.

## 23. Texto Preformateado Por Sangría

    Este bloque usa cuatro espacios iniciales.
    Debe tratarse como código o texto preformateado.

## 24. Párrafo Final

Si este documento genera un PDF sin errores, la app tiene una base sólida para
Markdown común. Las secciones que no se rendericen bien deben convertirse en
tareas concretas del proyecto.
