# Change videos

The script-to-video kit behind the step in `shared/change-video.md`. Words on screen appear on the spoken word, the voice is checked against the script, and the result is one MP4 under 20 MB plus a contact sheet.

## Run it

```bash
pip install numpy pillow        # plus ffmpeg, node with playwright, and a whisper command
export ELEVENLABS_API_KEY=... ELEVENLABS_VOICE=...
python3 make.py example.py --out out
```

Any text-to-speech works if you replace `tts()` in `make.py`. `WHISPER` names the transcriber, and it must accept the `mlx_whisper` arguments. Set `GRAIN_DIR` to a folder of `over0-7.png` and `screen0-7.png` to add film grain. Leave it unset for none.

## Write one

A film is one Python file: `SLUG`, `TITLE`, `FOOT` and `SCENES`. Optional: `THEME` (a CSS file with your brand's fonts and colors), `STAMP` (your logo), `PAPERS` (backgrounds). `example.py` is a complete one.

```python
S("a", "paper", "The words the voice says, with a word that reveals each step.",
  ["reveals"],                                  # one spoken word per step
  rows("Title", [(1, "Name", "Detail", False)]),
  "Running")                                    # the status in the footer
```

Blocks in `deck.py`: `hero`, `rows`, `procon`, `shot` (a screenshot) and `opens` (the closing scene). Or write your own HTML: anything with `data-s="2"` appears at step 2, `.sc` prints with the star scramble, and `.draw` strokes in. Use the `umber` tone for the closing scene.

If a cue word isn't heard, the build stops. Pick a nearby word: transcribers misspell names.
