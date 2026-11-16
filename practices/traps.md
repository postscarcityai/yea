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

## Setup and accounts

- **Keys added mid-build don't reach `.env.example` by themselves.** A scheduled job's secret was set on the host but missing from the example file, so a fresh setup had no way to know it existed. Add the name the moment you add the key.
- **Pin the package manager version in CI.** Our checks needed the `pnpm` version pinned before installs ran the same as on the laptop. Pin it in `package.json` and in the workflow.
- **A database CLI can hang on a hidden prompt.** Listing projects with no flags waited forever on an organization picker. Pass the org or project id.
- **Piping a value into a host's env command can save it empty and still report success.** Production values are write-only, so pulling them shows blanks either way, and a `??` fallback does not catch an empty string. Pass the value as a flag, then check the app actually reads it.
- **A commit from an email the host doesn't know can block the deploy** with no build and no error, so it looks stalled. Commit as the account the host expects. On a shared branch, recover with an empty commit, not a force-push.
- **Branch protection may not exist on your plan.** On a free plan, rules on a private repo returned 403, so any token that can push can also merge. Give the agent a token that can't push to main, and open pull requests from a server route that holds an app key. A deploy key can't open pull requests.
- **Worker CLIs drift.** A token printed across lines broke as a header ("Illegal header value"), a subfolder Dockerfile built without the shared code until the root was set as the build context, and secrets copied out over SSH carried a carriage return that broke every URL. Strip whitespace, set the context, trim line endings.
- **GPU machines bill while they download.** Pulling model weights on start meant a long, paid cold start. Bake weights into the image or a volume.
- **Pin the framework preset in the host's config file.** Don't rely on the host detecting it. Ours needed it set explicitly.

---

## Next.js and Vercel

- **Tracked media is your build time.** Our app built in 32 seconds and deployed in many minutes, because the clone was 787 MB. Move media to blob storage.
- **`vercel env pull` and some blob commands overwrite `.env.local`,** and sensitive values come back empty. Back up first.
- **Preview URLs can sit behind sign-in.** A 302 to SSO isn't a broken deploy. Test on the production alias, or use a bypass.
- **A strict CSP can stop dev pages hydrating,** so nothing is clickable and it looks like your bug. Test against a production build.
- **Fonts from a remote service can crash a build.** Self-host them.
- **Previews often lack production env.** Admin allowlists and API keys may be production only, so prove it locally and test after merge.
- **An effect that returns a value can crash the page.** A chat panel died when its thread changed, because the effect returned what `scrollTo` returned, now a promise in current Chrome, and React calls a returned value as cleanup. Give effects a block body that returns nothing.
- **Two submit buttons sharing one `name` can lose their value.** The server action never saw which was clicked, so Send did what Save does. Give each button its own `formAction`.
- **A relative redirect in middleware can crash behind a proxy.** Sign-out broke on the live domain and worked locally. Build the redirect from the forwarded host as an absolute URL.
- **Dates rendered on the server and in the browser must use one timezone.** A date shown in the server's zone and re-rendered in the visitor's threw a hydration error. Format in one fixed zone on both sides.
- **A nav item with no page is a 404 in production.** A module was in the nav, its data was in the database, and nobody had built the screen. Every nav entry ships with a page, even an empty state.
- **A monorepo can build everything on every push.** A host's "affected projects" setting still rebuilt the web app for a README change. Check what each push actually builds.
- **Lazy plus `display:none` means nothing loads until it's shown.** That's a flash on swap. Stack the layers and load the hidden one at low priority.

---

## Data and forms

- **`NaN` becomes `null` in JSON.** Then `.toFixed` throws, and the catch-all shows "Network hiccup" on a working network. Don't let generic error copy hide the real error.
- **Sandboxed iframes without `allow-forms` drop submits silently.** Use keydown and click handlers.
- **Free database plans have transfer caps.** Streaming video from a bucket through your app ate most of one in a month. Check the number, and don't test video against production.
- **Dates stored in UTC render on the wrong day** for anyone west of Greenwich. Convert on display, and test near midnight.
- **An insert-only database login can't use `RETURNING` or `ON CONFLICT`.** Both need read access, so every write failed. Have the insert return nothing, and check column defaults the narrow login will now fill.
- **Roles made in a hosted database's console can read everything.** They joined the provider's superuser group without saying so. Create limited roles in SQL.
- **Production starts empty.** Fake data shipped to a live back office and had to be wiped by hand. Keep demo data in seeds that use fictional companies, can be rerun, and send nothing. Build real empty states for the first day.
- **Record every migration you apply.** Without a table of applied files, nobody could tell which changes had run on which database. Build the runner on day one.
- **Capturing a client's live funnel needs zero writes.** Allow-list the read routes and fake every write.

---

## Testing with browsers

- **Some Playwright calls have no timeout** (`evaluate`, `mouse`, `keyboard`, `close`), and a `NaN` timeout never fires. Wrap them, or a hung page hangs the run.
- **Check iPhone WebKit, not only Chromium.** Some effects only work in Chromium.
- **`--use-fake-ui-for-media-stream` returns a fake pattern for screen share,** not the tab. Don't read it as a bug in your capture.

---

## Sign-in and email

- **The magic link has to carry where the person was going.** Without it, a link to a record lands on the home page after sign-in. Pass `?next=` through the email link and check it is a path on your own site.
- **Send sign-in links as plain transactional mail.** Our first sign-in email was a heavy branded layout with open and subscription tracking on. Send one line, one button and a link to paste, with tracking off for that message.
- **Plain-text email needs real links.** A sign-in email with a bare token was unusable on a phone. Send a button and a full, tappable URL.

---

## Agents and tools

- **A tool that lists things must return the total.** A partial list gave the agent a confident wrong count. Every list tool returns the total and the counts, not just the first page.
- **Adding a tool can break an old answer.** A new tool with a broad description started catching questions another tool used to answer. Write each description to say what it is not for, and rerun the full question set after any tool change.
- **Strip figures and contact details from what tools return.** A free-text field leaked a private fee to the model. Filter tool output, not only tool input.
- **An agent gateway can resume an old session.** It matched sessions on the system prompt plus the first message, so asking the same question twice continued the old chat. Put a chat id in the system message.
- **Agent answers can outlast a serverless function.** More than half of a set of real questions ran past the limit and would have shown no answer. Set the wait just inside the limit, and tell the person a broad question can take a minute or two.
- **A tool call with no result can lock a chat thread.** After a crash or a token cutoff, every later turn failed. Before the next turn, add an error result for any call that never got one.
- **MCP tools connect in the background.** The first question after a restart ran with no tools. Warm up before you test.
- **Models add markdown that breaks text matching.** Bold words broke a check that looked for a phrase. Strip markdown before you match.
- **A voice agent must not hang up by itself.** Calls ended on a model's guess or a brief network blip. Only the person ends the call: require their words as well as the model's end call, and let talking over the goodbye cancel it.
- **A worker agent's summary is not proof of what it changed.** A pull request carried an edit from an old branch while the worker said nothing else was touched. Read every diff.
- **The agent drafts, a person sends.** One path out of the app, and it needs a signed-in person. An agent route that can send will one day send the wrong thing.

---

## Shell and scheduling

- **A pipeline can fake a pass.** Exit codes get swallowed by pipes and command substitution. Gate on the artifact: does the file exist and is it right?
- **Resuming a paused schedule can fire the missed run late.** For a one-day hold, put a date guard in the script.
- **One failed `git add` in a chain skips only that commit.** A pull request merged without its core files and the build broke. Check `git status` is clean before you push.
- **A local worker pointed at production starts the whole job system:** the queue, a reconciler that sends email, the monthly digest. Test with an in-process simulator, never the full worker against production.
- **Never name a shell variable `HOME`.** Tools then read a stray empty database and report that your data is missing.
- **Tools' success messages can lie.** Confirm in the database when it matters.

---

## Workers and hosting

- **New worker apps can be public by default.** A deployed endpoint answered anyone with the URL. Turn on auth for every endpoint before it holds anything real.
- **Old versions keep serving.** A redeploy left the previous version live at its own URL. Delete old versions, or make sure they hold no secrets.
- **Deleting a disk may not delete its data.** Snapshots stayed after the disk was gone. Wipe real data before you delete a volume, or don't attach one for tests.
- **An agent with a terminal reads your setup.** A test meant to run with no access found the setup scripts on the machine. Keep configs off the box for control runs.

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
