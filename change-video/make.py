#!/usr/bin/env python3
"""make.py film.py [--out DIR] : script to finished MP4. Voice, word timings, a check that the voice said the script, frames, grain, encode.

film.py defines SLUG, TITLE, FOOT (footer text) and SCENES. Optional: THEME (css path), STAMP (logo path), PAPERS (backgrounds).
Env: ELEVENLABS_API_KEY, ELEVENLABS_VOICE. WHISPER (default mlx_whisper). PLAYWRIGHT (default "playwright"). GRAIN_DIR (optional, see README)."""
import difflib, hashlib, importlib.util, json, math, os, re, subprocess, sys, time, urllib.error, urllib.request
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool
from pathlib import Path
import numpy as np
from PIL import Image

T = Path(__file__).resolve().parent
sys.path.insert(0, str(T))
W, H, FPS = 1920, 1080, 30
LEAD, TAIL, END, ANIM = 0.35, 0.55, 2.4, 30.0
MAX_MB = 17.6  # stays under Telegram's 20 MB limit

def load(path):
    spec = importlib.util.spec_from_file_location("film", path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def norm(s):
    return re.findall(r"[a-z0-9']+", s.lower().replace("’", "'").replace("-", " "))

def tts(a):
    text, out = a; h = hashlib.sha1(text.encode()).hexdigest()[:10]; tag = out.with_suffix(".hash")
    if out.exists() and tag.exists() and tag.read_text() == h: return "cached"
    body = {"text": "[calm, steady] " + text, "model_id": os.environ.get("ELEVENLABS_MODEL", "eleven_v4"), "seed": 7,
            "voice_settings": {"stability": 0.4, "similarity_boost": 0.75, "style": 0.25, "speed": 1.0, "use_speaker_boost": True}}
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{os.environ['ELEVENLABS_VOICE']}?output_format=mp3_44100_192"
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"], "Content-Type": "application/json"})
    for i in range(5):
        try:
            with urllib.request.urlopen(req, timeout=180) as r: mp3 = r.read(); break
        except urllib.error.HTTPError as e:
            if e.code != 429 or i == 4: raise RuntimeError(f"{e.code} {e.read()[:200]}")
            time.sleep(3 * (i + 1))
    m = out.with_suffix(".mp3"); m.write_bytes(mp3)
    trim = "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(m), "-af", trim, "-ar", "48000", "-ac", "1", str(out)], check=True)
    m.unlink(); tag.write_text(h); out.with_suffix(".json").unlink(missing_ok=True); return "ok"

def prep(film, D):
    (D / "vo").mkdir(parents=True, exist_ok=True)
    papers = getattr(film, "PAPERS", ["#F3F0EC", "#f4efe6", "#F5EFE2"]); secs = ""
    for i, s in enumerate(film.SCENES):
        bg = "" if s["tone"] == "umber" else f' style="background:{papers[i % len(papers)]}"'
        secs += f'<section class="{s["tone"]}"{bg}>{s["html"]}<div class="foot"><span>{film.FOOT}</span><span>{s["state"]}</span></div></section>\n'
    stamp = getattr(film, "STAMP", None); img = f'<img src="file://{stamp}">' if stamp else ""
    secs += f'<section class="umber"><div class="endc">{img}<p>{film.TITLE}</p></div></section>\n'
    theme = getattr(film, "THEME", None); th = f'<link rel="stylesheet" href="file://{theme}">' if theme else ""
    (D / "deck.html").write_text(f'<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="file://{T}/deck.css">{th}</head><body>{secs}<script src="file://{T}/runtime.js"></script></body></html>')
    (D / "steps.json").write_text(json.dumps([len(s["cues"]) for s in film.SCENES] + [0]))
    with ThreadPoolExecutor(4) as ex: print("voice", list(ex.map(tts, [(s["vo"], D / f"vo/{s['id']}.wav") for s in film.SCENES])), flush=True)
    whisper = os.environ.get("WHISPER", "mlx_whisper")
    for s in film.SCENES:
        a = D / f"vo/{s['id']}.wav"
        if not a.with_suffix(".json").exists():
            subprocess.run([whisper, str(a), "--model", "mlx-community/whisper-large-v3-turbo", "--word-timestamps", "True", "--language", "en", "--output-format", "json", "--output-dir", str(D / "vo"), "--verbose", "False"], check=True, capture_output=True)
    timing = []; ok = True; tot = 0
    for s in film.SCENES:
        j = json.loads((D / f"vo/{s['id']}.json").read_text()); ws = [w for seg in j["segments"] for w in seg.get("words", [])]
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(D / f"vo/{s['id']}.wav")], capture_output=True, text=True).stdout); tot += dur
        heard = norm(" ".join(w["word"] for w in ws)); said = norm(s["vo"]); sm = difflib.SequenceMatcher(None, said, heard, autojunk=False)
        diffs = [(" ".join(said[a:b]), " ".join(heard[c:d])) for t, a, b, c, d in sm.get_opcodes() if t != "equal"]
        print(f"  {s['id']} {dur:5.1f}s heard {sm.ratio():.3f}", diffs or "", flush=True)
        nw = [(norm(w["word"]) or [""])[0] for w in ws]; pos = 0; times = []
        for c in s["cues"]:
            hit = next((i for i in range(pos, len(nw)) if nw[i] == norm(c)[0]), None)
            if hit is None: print("  CUE MISS", s["id"], c, flush=True); ok = False; times.append(times[-1] + 1 if times else 1.0); continue
            pos = hit + 1; times.append(ws[hit]["start"])
        timing.append(dict(id=s["id"], dur=dur, cues=times, tone=s["tone"]))
    (D / "timing.json").write_text(json.dumps(timing)); print(f"voice total {tot:.1f}s, cues ok={ok}", flush=True)
    if not ok: sys.exit("A cue word was not heard. Fix the script.")
    subprocess.run(["node", str(T / "capture.mjs"), str(D)], check=True)

# render
TL = []; TOTAL = 0; D_ = None; META = None; OV = SC = None; _c = {}
def layout(D):
    global TL, TOTAL, D_, META
    D_ = D; tm = json.loads((D / "timing.json").read_text()); META = json.loads((D / "meta.json").read_text()); t = 0; TL = []
    for i, s in enumerate(tm):
        L = LEAD + s["dur"] + TAIL; steps = [0.0] + [LEAD + c - 0.04 for c in s["cues"]]; cam = [(0.0, 960, 540, 1.0)]
        for k in range(1, len(steps)):
            fo = META[str(i)][str(k)]["focus"]
            if fo:
                x, y, w, h = fo; z = min(1.2, max(1.0, min(W / (w * 1.5), H / (h * 1.5))))
                cam += [(steps[k], *cam[-1][1:]), (steps[k] + .9, x + w/2, y + h/2, z)]
        TL.append(dict(i=i, t0=t, L=L, steps=steps, cam=cam, tone=s["tone"], id=s["id"])); t += L
    TL.append(dict(i=len(tm), t0=t, L=END, steps=[0.0], cam=[(0.0, 960, 540, 1.0)], tone="umber", id="end")); TOTAL = t + END
def ease(u): u = max(0, min(1, u)); return 4*u*u*u if u < .5 else 1 - (-2*u+2)**3/2
def grain():
    global OV, SC
    g = os.environ.get("GRAIN_DIR")
    if g and OV is None:
        OV = [np.asarray(Image.open(f"{g}/over{i}.png"), dtype=np.float32).T[..., None] / 255 for i in range(8)]
        SC = [np.asarray(Image.open(f"{g}/screen{i}.png"), dtype=np.float32).T[..., None] / 255 for i in range(8)]
def state(i, st, f):
    k = f"{i}_{st}_{f}"
    if k not in _c:
        if len(_c) > 3: _c.clear()
        _c[k] = Image.open(D_ / f"fr/s{k}.jpg").convert("RGB")
    return _c[k]
def frame(fi):
    t = fi / FPS; sc = next(s for s in reversed(TL) if s["t0"] <= t + 1e-9); tl = t - sc["t0"]
    st = max(k for k, v in enumerate(sc["steps"]) if v <= tl + 1e-9); frames = META[str(sc["i"])][str(st)]["frames"]
    f = min(frames - 1, int((tl - sc["steps"][st]) * ANIM)) if frames > 1 else 0
    keys = sc["cam"]; cx, cy, z = keys[-1][1:]
    for a, b in zip(keys, keys[1:]):
        if tl <= b[0]:
            u = ease((tl - a[0]) / max(1e-6, b[0] - a[0])); cx, cy = a[1] + (b[1]-a[1])*u, a[2] + (b[2]-a[2])*u; z = math.exp(math.log(a[3]) + (math.log(b[3])-math.log(a[3]))*u); break
    vw, vh = W / z, H / z; x0 = min(max(cx - vw/2, 0), W - vw); y0 = min(max(cy - vh/2, 0), H - vh)
    im = state(sc["i"], st, f).resize((W, H), Image.LANCZOS, box=(x0*2, y0*2, (x0+vw)*2, (y0+vh)*2)); grain()
    if OV is None: return im.tobytes()
    a = np.asarray(im, dtype=np.float32) / 255; g = int(t * 5) % 8
    if sc["tone"] == "umber": s = SC[g]; b = 1 - (1 - a) * (1 - s); o = .22
    else: s = OV[g]; b = np.where(a < .5, 2*a*s, 1 - 2*(1-a)*(1-s)); o = .13
    return (np.clip(a*(1-o) + b*o, 0, 1)*255 + .5).astype(np.uint8).tobytes()
def render(slug, D, out):
    layout(D); total = int(TOTAL * FPS); vid = D / "video.mp4"; print(f"render {TOTAL:.1f}s, {total} frames", flush=True)
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", str(vid)], stdin=subprocess.PIPE)
    with Pool(6, initializer=layout, initargs=(D,)) as p:
        for i, b in enumerate(p.imap(frame, range(total), chunksize=10)):
            ff.stdin.write(b)
            if i % 600 == 0: print(f"  frame {i}", flush=True)
    ff.stdin.close(); ff.wait()
    ins, fl = [], []; scs = [s for s in TL if s["id"] != "end"]
    for j, s in enumerate(scs):
        ins += ["-i", str(D / f"vo/{s['id']}.wav")]; ms = int((s["t0"] + LEAD) * 1000); fl.append(f"[{j}:a]adelay={ms}|{ms}[a{j}]")
    fl.append("".join(f"[a{j}]" for j in range(len(scs))) + f"amix=inputs={len(scs)}:normalize=0:duration=longest,apad,atrim=0:{TOTAL:.3f},loudnorm=I=-16:TP=-1.5:LRA=11[vo]")
    aud = D / "vo.m4a"; subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(fl), "-map", "[vo]", "-ar", "48000", "-c:a", "aac", "-b:a", "128k", str(aud)], check=True)
    final = out / f"{slug}.mp4"; kbps = int((MAX_MB * 1e6 * 8 / TOTAL - 128e3) / 1e3); enc = D / "enc.mp4"; log = str(D / "x264")
    for ps in (1, 2):
        tail = ["-f", "null", "/dev/null"] if ps == 1 else [str(enc)]
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(vid), "-c:v", "libx264", "-preset", "slower", "-tune", "grain", "-b:v", f"{kbps}k", "-pass", str(ps), "-passlogfile", log, "-pix_fmt", "yuv420p", "-an", *tail], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(enc), "-i", str(aud), "-c", "copy", "-shortest", "-movflags", "+faststart", str(final)], check=True)
    ts = []
    for s in TL:
        for k, v in enumerate(s["steps"]):
            nx = s["steps"][k+1] if k+1 < len(s["steps"]) else s["L"]; ts.append(s["t0"] + nx - 0.12)
    cols = 5; tw, th = 480, 270; sheet = Image.new("RGB", (cols*tw, math.ceil(len(ts)/cols)*th), "white")
    for i, tt in enumerate(ts):
        o = D / "cs.jpg"; subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{tt:.2f}", "-i", str(final), "-frames:v", "1", "-q:v", "3", str(o)], check=True)
        sheet.paste(Image.open(o).resize((tw, th)), ((i % cols)*tw, (i//cols)*th))
    sheet.save(out / f"{slug}-contact-sheet.jpg", quality=86); print("wrote", final, f"{os.path.getsize(final)/1e6:.1f} MB", flush=True)

if __name__ == "__main__":
    path = Path(sys.argv[1]).resolve(); film = load(path)
    out = Path(sys.argv[sys.argv.index("--out") + 1]).resolve() if "--out" in sys.argv else path.parent
    D = out / "work" / film.SLUG; D.mkdir(parents=True, exist_ok=True)
    prep(film, D); render(film.SLUG, D, out)
