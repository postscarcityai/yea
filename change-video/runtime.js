// Deterministic stage: __set(scene, step, u). Text prints instantly; .sc runs the site's star scramble; .draw strokes in.
const G = "*∗⁎✱✲✳✴✵✶✷✸✹✺✻✼✽✾❃❋★☆✦✧⋆";
const scenes = [...document.querySelectorAll("section")];
function wrap(el) {
  const walk = (n) => { for (const c of [...n.childNodes]) {
    if (c.nodeType === 3) { const f = document.createDocumentFragment();
      c.textContent.split(/(\s+)/).forEach((p) => { if (!p) return; if (/^\s+$/.test(p)) { f.append(p); return; }
        const w = document.createElement("span"); w.className = "w";
        for (const ch of p) { const s = document.createElement("span"); s.className = "c"; s.textContent = ch; w.append(s); } f.append(w); });
      c.replaceWith(f);
    } else if (c.nodeType === 1) walk(c); } };
  walk(el);
  el._c = [...el.querySelectorAll(".c")];
  el._c.forEach((s, i) => { s.dataset.g = G[(i * 7 + 3) % G.length]; });
}
document.querySelectorAll(".sc").forEach(wrap);
const lvl = (el) => { const p = el.closest("[data-s]"); return p ? +p.dataset.s : 0; };
const ease = (u) => (u < .5 ? 4*u*u*u : 1 - Math.pow(-2*u+2, 3)/2);
function scr(el, u) { const n = el._c.length;
  el._c.forEach((s, i) => { const a = (i / n) * .62, l = (u - a) / .38; s.classList.remove("st", "hid"); s.style.removeProperty("--z");
    if (u >= 1 || l >= 1) return; if (l <= 0) { s.classList.add("hid"); return; }
    s.classList.add("st"); s.style.setProperty("--z", String(.45 + .75 * Math.sin(l * Math.PI))); }); }
window.__set = (si, step, u) => { scenes.forEach((s, i) => { s.style.display = i === si ? "block" : "none"; });
  const sc = scenes[si];
  sc.querySelectorAll("[data-s]").forEach((el) => { el.style.visibility = +el.dataset.s <= step ? "visible" : "hidden"; });
  sc.querySelectorAll(".sc").forEach((el) => { const k = lvl(el); scr(el, k === step ? u : k < step ? 1 : 0); });
  sc.querySelectorAll(".draw").forEach((p) => { const L = p.getTotalLength(), k = lvl(p), v = k < step ? 1 : k === step ? ease(u) : 0;
    p.style.strokeDasharray = `${L} ${L}`; p.style.strokeDashoffset = String(L * (1 - v)); }); };
window.__meta = () => scenes.map((sc) => { const out = {}; const mark = (el, key) => { const k = lvl(el); out[k] = out[k] || { anim: false, f: null }; if (key) out[k].anim = true; };
  sc.querySelectorAll(".sc").forEach((e) => mark(e, 1)); sc.querySelectorAll(".draw").forEach((e) => mark(e, 1));
  return out; });
window.__focus = (si, step) => { const els = [...scenes[si].querySelectorAll("[data-f]")].filter((e) => lvl(e) === step); if (!els.length) return null;
  let a = 1e9, b = 1e9, c = -1e9, d = -1e9; for (const e of els) { const r = e.getBoundingClientRect(); a = Math.min(a, r.left); b = Math.min(b, r.top); c = Math.max(c, r.right); d = Math.max(d, r.bottom); } return [a, b, c - a, d - b]; };
