# Estilos individuales de tablas

Las tablas sin opciones usan los ajustes de la plantilla y de Diseno. Cada
bloque `table-style` modifica solamente la tabla que contiene.

## Tabla normal

| Concepto | Valor |
| --- | --- |
| Plantilla | La seleccionada en Diseno |
| Estilo | Valores generales del documento |

## Tabla ancha con ajustes propios

La columna Descripcion recibe cuatro partes de ancho, frente a una para ID.
La letra y el espacio de las celdas se reducen solamente en esta tabla.

::: {.table-style font-size=8pt cell-padding=2pt table-width=full columns="1,4,2,2"}

| ID | Descripcion | Responsable | Estado |
| --- | --- | --- | --- |
| 01 | Revisar los requisitos y preparar el documento de trabajo. | Equipo de analisis | En curso |
| 02 | Comprobar la conversion y la distribucion del contenido. | Equipo de pruebas | Pendiente |
| 03 | Publicar el documento cuando termine la revision. | Coordinacion | Completado |

:::

## Tabla ajustada al contenido

Este modo local se respeta aunque en Diseno se haya elegido ancho disponible.

::: {.table-style table-width=auto cell-padding=3pt}

| Codigo | Total |
| --- | ---: |
| A | 12 |
| B | 8 |

:::

## Tabla con proporciones de columnas

Las proporciones ocupan el ancho disponible. No es necesario indicar tambien
`table-width=full`. El tamano de letra sigue siendo el general de la plantilla.

::: {.table-style columns="1,3"}

| Paso | Explicacion |
| --- | --- |
| 1 | Abrir el Markdown que contiene las tablas. |
| 2 | Generar una vista previa y revisar si el texto se lee con comodidad. |

:::

## Vuelta al estilo general

Esta tabla vuelve a usar los valores de Diseno: los ajustes anteriores no se
propagan al resto del documento.

| Concepto | Valor |
| --- | --- |
| Letra | Tamano general de tablas |
| Celdas | Espacio general de tablas |

No todas las tablas caben con cualquier tamano de texto. Si una columna sigue
siendo demasiado estrecha, dale una proporcion mayor, reduce el espacio de
las celdas o divide la informacion en varias tablas. En Compacto, el ancho
disponible es el de una columna, no el de la pagina completa.
