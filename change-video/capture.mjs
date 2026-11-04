// node capture.mjs <work dir>: renders deck.html to JPEG states at 2x, plus meta.json. Deterministic, so a re-render matches.
const { chromium } = await import(process.env.PLAYWRIGHT || "playwright");
import { writeFileSync, mkdirSync, rmSync, readFileSync } from "node:fs";
const D = process.argv[2].replace(/\/?$/, "/"), F = 14;
const spec = JSON.parse(readFileSync(`${D}steps.json`)); rmSync(`${D}fr`, { recursive: true, force: true }); mkdirSync(`${D}fr`, { recursive: true });
const b = await chromium.launch(); const jobs = [];
const open = async () => { const p = await b.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 2 }); await p.goto(`file://${D}deck.html`, { waitUntil: "networkidle" }); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(300); return p; };
const p0 = await open(); const meta = await p0.evaluate(() => __meta()); const res = {};
for (let si = 0; si < spec.length; si++) for (let st = 0; st <= spec[si]; st++) { const anim = !!(meta[si][st] && meta[si][st].anim); jobs.push({ si, st, frames: anim ? F : 1 }); }
const pages = [p0, await open(), await open(), await open()]; let idx = 0;
await Promise.all(pages.map(async (p) => { while (idx < jobs.length) { const j = jobs[idx++];
  const fo = await p.evaluate(([a, c]) => { __set(a, c, 1); return __focus(a, c); }, [j.si, j.st]);
  (res[j.si] ??= {})[j.st] = { frames: j.frames, focus: fo };
  for (let f = 0; f < j.frames; f++) { const u = j.frames === 1 ? 1 : (f + 1) / j.frames; await p.evaluate(([a, c, v]) => __set(a, c, v), [j.si, j.st, u]);
    await p.screenshot({ path: `${D}fr/s${j.si}_${j.st}_${f}.jpg`, type: "jpeg", quality: 93 }); } } }));
await b.close(); writeFileSync(`${D}meta.json`, JSON.stringify(res)); console.log("captured", jobs.length, "states");
