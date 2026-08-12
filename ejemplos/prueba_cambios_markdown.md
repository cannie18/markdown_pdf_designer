---
title: "Prueba De Cambios Markdown"
subtitle: "Casos recientes de conversión a PDF"
author: "Markdown PDF Designer"
date: "2026-08-12"
lang: "es"
toc: true
---

# Prueba De Cambios Markdown

Este documento resume los cambios recientes aplicados al flujo Markdown -> PDF.
Está pensado para abrirlo desde la app, generar el PDF y comprobar visualmente
si cada caso queda como se espera.

[TOC]

---

## 1. Títulos De Nivel 4 A 6 {#titulos-secundarios-prueba}

Los títulos de nivel 4, 5 y 6 ya no deberían verse todos iguales.

#### Título De Nivel 4

Texto de prueba debajo del título de nivel 4.

##### Título De Nivel 5

Texto de prueba debajo del título de nivel 5.

###### Título De Nivel 6

Texto de prueba debajo del título de nivel 6.

## 2. Enlaces Clicables

Estos enlaces deben verse diferentes al texto normal y conservar el hipervínculo
clicable dentro del PDF:

- Enlace con texto descriptivo: [Pandoc](https://pandoc.org).
- Enlace automático: <https://typst.app>.
- Correo automático: <contacto@example.com>.
- Referencia reutilizable: [documentación de Markdown][markdown-docs].

[markdown-docs]: https://www.markdownguide.org/basic-syntax/

## 3. HTML Inline Básico

La conversión normaliza algunos elementos HTML frecuentes antes de llamar a
Pandoc:

Texto con <mark>resaltado HTML</mark>.

Texto antes del salto manual <br> texto después del salto manual.

Texto con <strong>negrita HTML</strong> y texto con <em>cursiva HTML</em>.

<div>
  <strong>Bloque HTML:</strong> el contenido básico en negrita debe conservarse,
  aunque la app no intenta reproducir todo el comportamiento de HTML.
</div>

## 4. Alertas Tipo GitHub

Las alertas tipo GitHub se convierten en citas con una etiqueta visible.

> [!NOTE]
> Esta nota debería aparecer como una cita etiquetada como Nota.

> [!WARNING]
> Esta advertencia debería aparecer como una cita etiquetada como Advertencia.

> [!TIP]
> Este consejo debería aparecer como una cita etiquetada como Consejo.

> [!IMPORTANT]
> Este bloque debería aparecer como una cita etiquetada como Importante.

> [!CAUTION]
> Esta precaución debería aparecer como una cita etiquetada como Precaución.

## 5. Enlaces Internos {#enlaces-internos-prueba}

Este enlace debe saltar a la sección de [títulos de nivel 4 a 6](#titulos-secundarios-prueba).

Este enlace debe saltar a esta misma sección mediante un identificador
personalizado: [enlaces internos de prueba](#enlaces-internos-prueba).

## 6. Salto De Página

El siguiente comentario debe convertirse en un salto de página real.

<!-- pagebreak -->

Este texto debería empezar en una página nueva.

## 7. Texto Preformateado Por Sangría

Este caso sigue siendo útil para decidir si el aspecto actual del bloque
preformateado nos vale o si queremos darle un estilo específico.

    bloque_preformateado = true
    origen = "cuatro espacios iniciales"

## 8. Tabla Y Unicode

| Caso | Resultado esperado |
| --- | --- |
| Enlace visual | Azul, subrayado y clicable |
| HTML inline | Resaltado, salto manual, negrita y cursiva |
| Alertas | Citas con etiqueta |
| Unicode | ✓ correcto, ✗ error, ≤ límite, ≥ mínimo |

## 9. Cierre

Si este PDF se genera sin errores, los cambios recientes están integrados en el
flujo principal. Los detalles visuales que no convenzan se pueden convertir en
tareas concretas de diseño.
