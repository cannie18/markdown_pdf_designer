---
title: "Prueba de apuntes con Typst"
author: "Codex"
---

# Microsoft Fabric

Este documento pequeno sirve para comprobar el flujo tecnico
**Markdown -> Pandoc -> Typst -> PDF** sin reproducir todavia toda la
plantilla LaTeX anterior.

## OneLake

**Definicion**

OneLake es una capa de almacenamiento unificada. El objetivo de esta prueba es
comprobar parrafos, *cursivas*, **negritas** y jerarquia visual.

### Ideas principales

- Separar contenido y presentacion.
- Mantener Markdown lo mas estandar posible.
- Delegar la maquetacion en una plantilla.

1. Escribir el contenido en Markdown.
2. Convertir a Typst con Pandoc.
3. Compilar el PDF con Typst.

> Este bloque debe verse como una caja destacada, no como texto ordinario.

| Elemento | Responsabilidad |
| --- | --- |
| Markdown | Contenido semantico |
| Pandoc | Conversion de formato |
| Typst | Maquetacion y PDF |

Codigo en linea: `print("hola")`.

```python
def saludar(nombre):
    return f"Hola, {nombre}"
```

Ecuacion en linea: $a^2 + b^2 = c^2$.
