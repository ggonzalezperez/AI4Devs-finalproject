# Cómo se genera el manual en PDF

El PDF que se entrega a las familias es
[`docs/Chispa-Manual-de-uso.pdf`](../Chispa-Manual-de-uso.pdf). **No se edita a mano**: se compone
desde `manual.html` y se imprime con el Chrome del sistema, así que el diseño usa exactamente la
paleta y las tipografías de la aplicación (`frontend/src/styles/theme.css` y
[`docs/design-system.md`](../design-system.md)).

## Por qué HTML y no una librería de PDF

`reportlab` y compañía obligan a colocar cada elemento por coordenadas. Aquí hacía falta tipografía
real —Fredoka, Mulish, Space Grotesk—, tablas, avisos de color y capturas encajadas con el texto. Con
CSS eso es el trabajo normal del navegador, y el resultado se puede mirar en pantalla antes de
imprimirlo.

## Requisitos

- Node y Google Chrome instalados.
- `npm i playwright` en cualquier carpeta de trabajo (no hace falta descargar navegadores: los
  guiones usan el Chrome del sistema con `channel: "chrome"`).
- Conexión a internet la primera vez: las tipografías vienen de Google Fonts.

## Los dos pasos

```bash
# 1) Recortar las capturas. Las evidencias son de 1280 px de ancho y la tarjeta
#    de la app ocupa unos 550: sin recortar, el PDF sale casi todo vacío.
node recortar.mjs "../entrega-2/evidencias;../entrega-3/evidencias" "./capturas"

# 2) Componer e imprimir.
node pdf.mjs manual.html "../Chispa-Manual-de-uso.pdf"
```

`capturas/` es material generado y **no se versiona** (está en `.gitignore`): se reconstruye con el
paso 1 a partir de las evidencias, que sí están en el repositorio.

## Detalles que costaron una vuelta, para no repetirlos

- **La portada va a sangre** con `@page :first { margin: 0 }` y los márgenes declarados en CSS, no en
  las opciones de `page.pdf()`. Si se pasan ahí, el CSS deja de mandar y la portada queda con un
  borde blanco desigual.
- **No hay pie de página.** Chrome lo pinta también sobre la primera página aunque su margen sea
  cero, y un «Manual de uso · 1» difuminado sobre el verde estropeaba la portada. El índice remite a
  los apartados por nombre, así que la numeración no hacía falta.
- **Nada de `radial-gradient` con paradas translúcidas** en elementos decorativos: al rasterizar
  salía un manchón grisáceo. Un color plano con `opacity` sobrevive al paso por PDF.
- **Hay que esperar a `document.fonts.ready`** antes de imprimir, o el PDF sale con la tipografía de
  reserva. `pdf.mjs` lo comprueba y avisa por consola de qué familias e imágenes ha cargado.
  Ojo: `document.fonts.check('12px "Fredoka"')` da `false` aunque esté bien cargada, porque el peso
  por defecto (400) no se pide; con `700` da `true`.
