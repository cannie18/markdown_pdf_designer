# Navegacion del PDF al Markdown

Genera el PDF y pulsa sobre sus bloques. El editor debe mostrar el comienzo
del bloque correspondiente y resaltarlo brevemente.

## Parrafo de prueba

Este parrafo es un bloque independiente. El clic sobre cualquiera de sus
lineas debe llevar al comienzo de este parrafo en el Markdown.

## Lista

- Primer elemento de una lista.
- Segundo elemento del mismo bloque.
  - Elemento anidado.

## Tabla

::: {.table-style font-size=9pt cell-padding=3pt columns="1,3"}

| Tipo | Resultado esperado |
| --- | --- |
| Tabla | Saltar al comienzo del bloque table-style. |
| Celda | No se intenta localizar la celda exacta. |

:::

## Codigo

```python
def saludar(nombre):
    return f'Hola, {nombre}'
```

## Imagen

![Diagrama de prueba](imagenes/imagen-ejemplo.svg){width=50%}

## Alerta

> [!NOTE]
> El clic debe localizar la alerta en el Markdown original,
> aunque la conversion transforme su representacion.

## Enlaces

[Ir al parrafo de prueba](#parrafo-de-prueba).

[Consultar Pandoc](https://pandoc.org).

Los enlaces mantienen su funcion y no llevan el editor al Markdown.

<!-- pagebreak -->

## Otra pagina

Este bloque permite comprobar el clic despues de desplazar el visor.
En Compacto, el salto manual pasa a la siguiente columna.

## Markdown modificado

Si editas el Markdown despues de generar el PDF, el salto se suspende hasta
que el texto vuelva a coincidir con la vista previa o generes un PDF nuevo.
