"""Building blocks for a change video. A scene has spoken words, cues (the spoken word that reveals step 1, 2, ...) and HTML.
Solid lines mean running or a hard fact. Dashed lines mean planned. Every scene states its status in the footer."""
from pathlib import Path

def art(path): return f'<img class="art" src="file://{Path(path).resolve()}">'
def line(s, text, cls="ln"): return f'<p class="{cls}" data-s="{s}">{text}</p>'
def h1(text, cls=""): return f'<h1 class="sc {cls}">{text}</h1>'

def hero(image, title, lines, w=900):
    """A title over a full-bleed image, with lines that appear as they are spoken."""
    return art(image) + f'<div class="hero" style="width:{w}px">{h1(title)}' + "".join(line(s, t) for s, t in lines) + "</div>"

def rows(title, items):
    """A list. item: (step, name, description, chosen)."""
    out = f'<div class="top">{h1(title, "h2")}</div><div class="rows">'
    for s, n, d, ch in items:
        mark = '<span class="star">★</span>' if ch else '<span class="star"></span>'
        out += f'<div class="row{" on" if ch else ""}" data-s="{s}">{mark}<div class="nm{" sc" if ch else ""}">{n}</div><div class="ds">{d}</div></div>'
    return out + "</div>"

def procon(title, good_h, good, cost_h, cost):
    """Two columns. items: (step, text)."""
    def col(h, its): return f'<div class="col"><h3>{h}</h3>' + "".join(f'<p class="pc" data-s="{s}">{t}</p>' for s, t in its) + "</div>"
    return f'<div class="top">{h1(title, "h2")}</div><div class="cols">{col(good_h, good)}{col(cost_h, cost)}</div>'

def shot(image, title, caption_step=1, caption=""):
    """A screenshot of the change, with the title above it. Show the real thing wherever you can."""
    return f'<div class="top">{h1(title, "h2")}</div><img class="shot" src="file://{Path(image).resolve()}"><p class="cap2" data-s="{caption_step}">{caption}</p>'

def opens(items, built, title="Still open"):
    """The closing scene on the dark tone. items: (step, question, detail). built: (step, one honest line)."""
    out = f'<div class="top">{h1(title, "h2 op")}</div><div class="opens">'
    for s, a, b in items: out += f'<div class="opn" data-s="{s}"><div class="a">{a}</div><div class="b">{b}</div></div>'
    return out + f'</div><p class="built sc" data-s="{built[0]}">{built[1]}</p>'

def S(id, tone, vo, cues, html, state="Proposed, not built"):
    return dict(id=id, tone=tone, vo=vo, cues=cues, html=html, state=state)
