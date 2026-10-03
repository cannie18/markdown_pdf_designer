# Prompt para preparar Markdown orientado a PDF

Copia este prompt en otro chat cuando quieras que te preparen un documento Markdown pensado para convertirlo despues a PDF con esta aplicacion.

````text
Quiero que prepares contenido en Markdown pensado para convertirlo despues a PDF con una aplicacion de diseno Markdown a PDF.

El objetivo es que el Markdown sea limpio, semantico y facil de maquetar. No quiero que simules diseno con espacios, tabulaciones, caracteres repetidos o trucos visuales. Usa estructuras Markdown claras.

Reglas generales:

1. Devuelve solo el Markdown final, sin explicaciones externas.
2. Usa una estructura jerarquica de titulos:
   - `#` para el titulo principal.
   - `##` para secciones principales.
   - `###` para subsecciones.
   - `####`, `#####` y `######` solo si realmente hacen falta.
3. Deja una linea en blanco antes y despues de cada titulo.
4. Deja una linea en blanco entre parrafos.
5. Deja una linea en blanco antes y despues de listas, tablas, citas, alertas, imagenes y bloques de codigo.
6. Usa parrafos normales para el texto principal.
7. Usa negrita con `**texto**`.
8. Usa cursiva con `*texto*`.
9. Usa codigo en linea con acentos graves: `codigo`.
10. Usa listas con guion:
    - Elemento
    - Elemento
11. Usa listas numeradas normales:
    1. Primer paso
    2. Segundo paso
    3. Tercer paso
12. Evita listas con demasiados niveles de anidacion.
13. Usa enlaces con formato Markdown:
    `[Texto del enlace](https://ejemplo.com)`
14. Usa imagenes con ruta relativa y texto alternativo:
    `![Descripcion de la imagen](imagenes/archivo.png)`
    Si la imagen esta en la misma carpeta que el Markdown, usa solo el nombre:
    `![Descripcion de la imagen](archivo.png)`
15. Usa tablas Markdown simples cuando haya informacion comparativa.
16. Usa citas con `>` cuando el contenido sea una cita, nota destacada o bloque de apoyo.
17. Usa bloques de codigo con triple acento grave e indica el lenguaje cuando sea posible.
18. Para alertas tipo GitHub, usa exactamente estos formatos:

    > [!NOTE]
    > Informacion adicional.

    > [!TIP]
    > Consejo practico.

    > [!IMPORTANT]
    > Informacion importante.

    > [!WARNING]
    > Advertencia.

    > [!CAUTION]
    > Precaucion critica.

19. Si hace falta forzar un salto de pagina, usa esta linea en una posicion aislada:
    `<div style="page-break-after: always;"></div>`
20. Si hace falta incluir indice automatico, coloca `[TOC]` donde deba aparecer.
21. Evita HTML salvo para casos concretos como el salto de pagina.
22. No uses colores, tamanos de letra, alineaciones manuales ni estilos visuales embebidos.
23. No uses emojis salvo que el documento los pida expresamente.
24. No uses tablas para maquetar texto normal.
25. No crees portadas falsas con lineas, cajas ASCII o espacios.

Formato esperado para bloques concretos:

Titulo principal:

# Titulo del documento

Seccion:

## Nombre de la seccion

Subseccion:

### Nombre de la subseccion

Parrafo:

Este es un parrafo normal escrito de forma clara y directa.

Lista:

- Primer elemento.
- Segundo elemento.
- Tercer elemento.

Lista numerada:

1. Primer paso.
2. Segundo paso.
3. Tercer paso.

Tabla:

| Concepto | Descripcion |
| --- | --- |
| Markdown | Formato de escritura estructurada |
| PDF | Documento final maquetado |

Cita:

> Este bloque representa una cita o una nota destacada.

Codigo:

```python
print("Ejemplo")
```

Enlace:

[Pandoc](https://pandoc.org)

Imagen:

![Diagrama del proceso](imagenes/proceso.png)

Salto de pagina:

<div style="page-break-after: always;"></div>

Indice:

[TOC]
````
