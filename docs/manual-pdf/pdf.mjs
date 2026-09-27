import { chromium } from "playwright";
import { pathToFileURL } from "node:url";
import { resolve } from "node:path";

const [src, out] = [process.argv[2], process.argv[3]];
const browser = await chromium.launch({ channel: "chrome" });
const page = await browser.newPage();

const fallos = [];
page.on("requestfailed", (r) => fallos.push(`${r.failure()?.errorText} ${r.url().slice(0, 90)}`));

await page.goto(pathToFileURL(resolve(src)).href, { waitUntil: "networkidle" });
// Las tipografías vienen de Google Fonts: sin esperarlas, el PDF sale con la
// fuente de reserva y el diseño no es el de la app.
await page.evaluate(() => document.fonts.ready);
const cargadas = await page.evaluate(() =>
  ["Fredoka", "Mulish", "Space Grotesk"].map((f) => `${f}:${document.fonts.check(`12px "${f}"`)}`),
);
console.log("tipografías ->", cargadas.join("  "));

const imgs = await page.evaluate(() =>
  [...document.images].map((i) => ({ src: i.getAttribute("src"), ok: i.naturalWidth > 0 })),
);
const rotas = imgs.filter((i) => !i.ok);
console.log(`imágenes: ${imgs.length} total, ${rotas.length} rotas`);
rotas.forEach((i) => console.log("  ROTA:", i.src));

await page.pdf({
  path: out,
  format: "A4",
  printBackground: true,
  // Sin pie de página. `@page :first { margin:0 }` deja la portada a sangre pero
  // Chrome sigue pintando el pie encima, y un «Manual de uso · 1» difuminado
  // sobre el verde estropea la portada. El índice remite a los apartados por
  // nombre, no por número de página, así que la numeración no hacía falta.
  displayHeaderFooter: false,
  // Sin `margin` a propósito: manda el CSS, que es quien sabe que la portada
  // va a sangre.
  preferCSSPageSize: true,
});

if (fallos.length) console.log("peticiones fallidas:", fallos);
await browser.close();
console.log("PDF escrito en", out);
