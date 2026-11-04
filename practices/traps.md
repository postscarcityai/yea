# Traps

Specific failures from real builds. What it looked like, why, and the fix. Versions and vendor behavior change, so check before relying on any one line.

---

## Models and JSON

- **A strict schema kills a whole pass over one extra item.** A `.max(10)` on model JSON threw away a good answer because it returned 11. Trim instead of rejecting.
- **Models copy your example's shape.** Show `{label, at}` and you get `{label, at}`, whatever the schema says. Make examples match exactly.
- **Put required fields before big arrays.** A long response that truncates still leaves you what matters.
- **Thinking eats small token limits.** Some models think by default, so a small `max_tokens` comes back as thinking and empty text. Raise the limit.
- **Check your SDK against your router.** One SDK version's stream died on a router's trailing `[DONE]`. Pin a version that works.
- **Sync calls can time out and still charge you.** Use async jobs for slow generation, and check the bill before retrying.
- **Log the cost of every call.** You can't manage what you can't see. Our own usage ran far above what anyone guessed.
- **Never let a model invent facts.** Interviewers and generators get "use only the facts in your notes," and say so when they don't know.

---

## Realtime voice and video

- **Don't trust a recorder's chunking.** One browser's MP4 recorder ignored the timeslice in our setup: a 1 KB chunk, then everything at stop. A dropped call lost it all. Try WebM first, and test by killing a call midway. Another setup behaved fine, so measure yours.
- **Chunks need joining rules.** Upload as you go, assemble at the end, and mark failure honestly.
- **Long talkers get cut off.** A short silence window interrupts people mid-thought. We raised it from 700 ms to 1200 ms.
- **Budget time per topic.** A hard cap hit topic six of seven with a person who gives long answers. Resume across calls, so a cap never loses anything.
- **Interviewers shouldn't assume an answer.** No answer means none. Never fill it in.
- **Name content types carefully.** An audio file with a `.webm` extension can be inferred as video, and a strict upload rule rejects it.
- **Speech-to-text hallucinates over music** and splits hyphens. Check every transcript before burning captions.

---

## Next.js and Vercel

- **Tracked media is your build time.** Our app built in 32 seconds and deployed in many minutes, because the clone was 787 MB. Move media to blob storage.
- **`vercel env pull` and some blob commands overwrite `.env.local`,** and sensitive values come back empty. Back up first.
- **Preview URLs can sit behind sign-in.** A 302 to SSO isn't a broken deploy. Test on the production alias, or use a bypass.
- **A strict CSP can stop dev pages hydrating,** so nothing is clickable and it looks like your bug. Test against a production build.
- **Fonts from a remote service can crash a build.** Self-host them.
- **Previews often lack production env.** Admin allowlists and API keys may be production only, so prove it locally and test after merge.
- **Lazy plus `display:none` means nothing loads until it's shown.** That's a flash on swap. Stack the layers and load the hidden one at low priority.

---

## Data and forms

- **`NaN` becomes `null` in JSON.** Then `.toFixed` throws, and the catch-all shows "Network hiccup" on a working network. Don't let generic error copy hide the real error.
- **Sandboxed iframes without `allow-forms` drop submits silently.** Use keydown and click handlers.
- **Free database plans have transfer caps.** Streaming video from a bucket through your app ate most of one in a month. Check the number, and don't test video against production.
- **Dates stored in UTC render on the wrong day** for anyone west of Greenwich. Convert on display, and test near midnight.
- **Capturing a client's live funnel needs zero writes.** Allow-list the read routes and fake every write.

---

## Testing with browsers

- **Some Playwright calls have no timeout** (`evaluate`, `mouse`, `keyboard`, `close`), and a `NaN` timeout never fires. Wrap them, or a hung page hangs the run.
- **Check iPhone WebKit, not only Chromium.** Some effects only work in Chromium.
- **`--use-fake-ui-for-media-stream` returns a fake pattern for screen share,** not the tab. Don't read it as a bug in your capture.

---

## Shell and scheduling

- **A pipeline can fake a pass.** Exit codes get swallowed by pipes and command substitution. Gate on the artifact: does the file exist and is it right?
- **Resuming a paused schedule can fire the missed run late.** For a one-day hold, put a date guard in the script.
- **Never name a shell variable `HOME`.** Tools then read a stray empty database and report that your data is missing.
- **Tools' success messages can lie.** Confirm in the database when it matters.

---

## Copy and search

- **Don't invent numbers.** Every claim needs a source you can show. We checked our own "two orders of magnitude" line and it didn't hold.
- **Never publish a home unit number,** even when it's the legal mailing address.
- **Redirect old URLs** when a page moves, or lose its rank.

---

## Safety

- **`can()` means little if the app logs in as the database owner.** Our own back office checked permissions in code while connecting as the owner, who bypasses row rules and can rewrite the log. Give the app its own login. Keep the owner for migrations.
- **A half-applied migration can leave you open.** One stopped at its first revoke and left the log writable. Run each migration as one transaction, and run the conformance kit on a clean database in CI.
- **Log writes in the database, not in each action.** A trigger can't be forgotten. Ours also records scripts and direct fixes that a helper function would never see.
- **Test routes can have real side effects.** A scheduled digest route ignored the email sandbox, so a test sent a real email. Check what a route sends before you call it.
