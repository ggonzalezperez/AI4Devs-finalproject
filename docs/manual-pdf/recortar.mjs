// Recorta el margen uniforme de las capturas: la tarjeta de la app va centrada
// sobre el papel #e8e6e1 y ocupa ~36% del ancho, así que sin recortar el PDF
// sale casi todo vacío. Se hace con el propio Chrome (canvas) para no añadir
// dependencias de imagen al proyecto.
import { chromium } from "playwright";
import { readdirSync, mkdirSync, writeFileSync, readFileSync } from "node:fs";
import { join } from "node:path";

const [srcDirs, outDir] = [process.argv[2].split(";"), process.argv[3]];
mkdirSync(outDir, { recursive: true });

const browser = await chromium.launch({ channel: "chrome" });
const page = await browser.newPage();

for (const dir of srcDirs) {
  for (const nombre of readdirSync(dir).filter((f) => f.endsWith(".png"))) {
    // Se pasa como data URL: una página about:blank no puede leer file:// y el
    // canvas quedaría contaminado de todos modos.
    const url =
      "data:image/png;base64," + readFileSync(join(dir, nombre)).toString("base64");
    const recorte = await page.evaluate(async (src) => {
      const img = new Image();
      img.src = src;
      await img.decode();
      const c = document.createElement("canvas");
      c.width = img.width;
      c.height = img.height;
      const ctx = c.getContext("2d", { willReadFrequently: true });
      ctx.drawImage(img, 0, 0);
      const { data } = ctx.getImageData(0, 0, c.width, c.height);
      const at = (x, y) => (y * c.width + x) * 4;
      // Color de fondo: la esquina superior izquierda.
      const [br, bg, bb] = [data[0], data[1], data[2]];
      const difiere = (x, y) => {
        const i = at(x, y);
        return (
          Math.abs(data[i] - br) > 8 ||
          Math.abs(data[i + 1] - bg) > 8 ||
          Math.abs(data[i + 2] - bb) > 8
        );
      };
      let x0 = c.width, y0 = c.height, x1 = 0, y1 = 0;
      for (let y = 0; y < c.height; y++) {
        for (let x = 0; x < c.width; x++) {
          if (difiere(x, y)) {
            if (x < x0) x0 = x;
            if (x > x1) x1 = x;
            if (y < y0) y0 = y;
            if (y > y1) y1 = y;
          }
        }
      }
      if (x1 <= x0 || y1 <= y0) return null; // imagen uniforme: no tocar
      // Un respiro alrededor, sin salirse.
      const pad = 12;
      x0 = Math.max(0, x0 - pad);
      y0 = Math.max(0, y0 - pad);
      x1 = Math.min(c.width - 1, x1 + pad);
      y1 = Math.min(c.height - 1, y1 + pad);
      const w = x1 - x0 + 1, h = y1 - y0 + 1;
      const out = document.createElement("canvas");
      out.width = w;
      out.height = h;
      out.getContext("2d").drawImage(c, x0, y0, w, h, 0, 0, w, h);
      return { dataUrl: out.toDataURL("image/png"), w, h, antes: `${c.width}x${c.height}` };
    }, url);

    if (!recorte) {
      console.log(`${nombre}: uniforme, sin recortar`);
      continue;
    }
    writeFileSync(join(outDir, nombre), Buffer.from(recorte.dataUrl.split(",")[1], "base64"));
    console.log(`${nombre}: ${recorte.antes} -> ${recorte.w}x${recorte.h}`);
  }
}

await browser.close();
