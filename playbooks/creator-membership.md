# Creator, community or event brand

You build an audience with content, then turn it into tickets, sponsors and members.

Example: **Talus Yard Climbing**, a climbing gym with a community, events and footage. The companies, people and numbers in these pages are made up. The patterns come from real builds. Back to [all playbooks](README.md).

## Who pays and how

- Fans join a waitlist for free, then buy tickets to the drop (ticket links were built on the card rail).
- Sponsors pay in tiers, from headline to in-kind, and grants count as a tier.
- Memberships are not built yet in any of our builds; the portal and shop modules carry them from the spec.

## The core loop

1. **Capture.** Fans join the list, with a welcome and a founder alert.
2. **Footage in.** Phone footage uploads straight to the shared drive.
3. **Make.** Clips are tagged and searchable; templates render posts and carousels.
4. **Send.** Campaigns to your own list, tracked, with suppression.
5. **Fund.** Sponsors researched, tracked by stage, goals read live.

## Modules on

| Module key | Label we used | Why |
|---|---|---|
| `people` | Waitlist | everyone on the list |
| `pipeline` | Sponsors | sponsors by tier and stage |
| `library` | Library | every clip and photo, searchable |
| `studio` | Studio | brand templates and renders |
| `content` | Series | recurring shows and skits |
| `campaigns` | Emails | campaigns to the list |
| `goals` | Goals | goals tied to live numbers |
| `social` | Social | posts for review and approval |

Core modules (Home, Inbox, People, Views, Goals, Team, Agents, Board, Log, Settings, Site, Intake, Portal) are always on as well. See `shared/modules.md`.

## Stages we actually used

- **sponsor** (`pipeline`): prospect, ready, approved, contacted, talking, committed, not_now, declined, past.
- **campaign** (`campaigns`): draft, queued, sending, sent.
- **upload session** (`library`): free, claimed, done, failed.
- **render job** (`studio`): queued, running, done, error.

## The agent's first three jobs

1. Tag every new clip and stack the duplicates, so the editor finds the shot in seconds.
2. Draft this week's posts and the list email from what was shot.
3. Research the next ten sponsors, fill only blank fields, and tee them up for a person to contact.

## Hero workflow: Find the shot, make the post

Signed in as the staff, approved by the owner. The agent is "Studio desk". Shows the play [Search footage by what is in it](#library-search-by-picture).

Steps on screen: Footage lands > Ask > Search by what is in it > Draft post > Owner approves > Logged with Undo.

- **Pinned:** Folder "Comp night, Oct 28"
- **Ask:** "Find the clip where the whole team tops the final wall, and make a post for Friday."
- **Agent works:** Searched 1,240 clips for the final wall; Found 3 takes, stacked 2 duplicates; Framed the best take on the team; Rendered the post from the Friday template.
- **Reply:** "Take 2 from Oct 28 has all six at the top together. The Friday post is drafted on the left with the clip framed on the team."
- **Approval:** "Schedule it for Friday at 6 PM?" [Change] [Approve], then "Approved. Scheduled for Friday 6 PM."
- **Log, with Undo:** Studio desk scheduled the Friday post from take 2. Approved by Juno Reyes.

Names in the script are fictional.

## What it lets them cancel

Linktree, Mailchimp, Typeform, Canva, Later, Dropbox. Prices and risk for each are in [shared/saas.md](../shared/saas.md).

## Rails kept

Vercel, Neon, Twilio SendGrid, Square, Google Drive, Voice API.

## Plays

Innovation plays first: things we built that most businesses like this do not have yet.

### Phone footage straight to the drive (innovation)

<a id="phone-upload-to-drive"></a>Shoot on a phone, upload from a link, and full-size footage lands in the shared drive, resuming after a dropped signal.

**The rule.** The server never holds the storage credential or touches a byte. An always-on machine pre-mints Google Drive resumable sessions into a table, and the browser claims one per file and PUTs straight to Drive.

**The data it needs**

- Session: unique URI, status free, claimed, done or failed, mime, created_at, file name, size, note, drive_file_id, finalized_at.
- Pool targets per content type, because Drive fixes the type at mint.

**The steps**

1. Every 2 minutes the machine deletes free sessions older than 5 days, since Drive keeps them a week, and tops up the pool. Each mint sends the app Origin header so browser PUTs pass CORS.
2. A signed-in claim takes the oldest free session of that type with SKIP LOCKED, falls back to generic, and returns 503 when empty.
3. The browser sends 2 files at a time in 16 MB chunks over XHR. A 308 with a Range header gives the next offset.
4. On a drop, retry with backoff capped at 60 seconds, first asking Drive with bytes */size where it got to.
5. On 200 or 201, report done. The machine renames the file, stores the note and messages the owner.

**What breaks**

- A 404 or 410 means a dead session, so the job drops the URI and Try again restarts on a new one.
- The queue lives in page memory, so a reload loses it. A beforeunload warning and a wake lock guard this.
- New rows sit free with a placeholder URI until the mint returns, and the claim does not filter them. Use a separate minting status.

**Not proven by the code behind this play**

- The link opens a modal in the signed-in app. It is not a public upload link.
- Resume works while the page stays open.

- **Id:** `phone-upload-to-drive`
- **Modules:** `library`, `studio`
- **Fits when you see:** video, footage, shoot, filming, content, creator, events

### Search footage by what is in it (innovation)

<a id="library-search-by-picture"></a>Find any clip by typing what is in it, with auto-tags, duplicate stacks and crops centred on people.

**The rule.** One local embedding model does all of it. Pictures and words share one 512-dimension space, so search, tags and duplicates are vector math on one column, at no per-call cost. Model tags get their own column, so the owner tags stay untouched.

**The data it needs**

- Media row: kind, vector(512), auto_tags, owner tags, dup_group, crops JSON, tagged_at.
- A tag vocabulary you write: a few prompt phrasings per tag, plus neutral prompts.
- A browser word vector file: about 6,000 words embedded as "a photo of {word}", stored as int8.

**The steps**

1. Embed rows with no vector. A video gives 3 frames at 15, 50 and 85 percent, averaged and renormalized.
2. For exclusive families, softmax the prompts and keep a winner above 0.55 to 0.6. Keep an independent tag when it beats the neutral prompts by a margin, default 0.04, calibrated per tag.
3. Stack duplicates at cosine 0.93 or above, same kind, with union-find, and rebuild all stacks in one transaction.
4. For stills, detect faces and people, weight heads above bodies, and slide a window for 4:5, 9:16 and 1:1 that keeps the heaviest boxes whole.
5. In the browser, turn typed words into a vector from the file and post it to a similarity search.

**What breaks**

- Similarity chains collapse a library into one stack, so a join also needs the group roots at 0.90.
- People facing away have no face, so the top of each person box stands in as a head.
- A row with no local picture gets no vector, so search misses it until a run finds a picture.

**Not proven by the code behind this play**

- The cited code covers the write side and the word vector file. The query itself sits outside it.
- Crops are computed for stills only, and the vocabulary is fixed at build time.

- **Id:** `library-search-by-picture`
- **Modules:** `library`
- **Fits when you see:** photos, videos, footage, library, content, media

### Call your back office (innovation)

<a id="voice-persona"></a>Talk to the business's agent by voice inside the app; it answers from the real records and files what you ask.

**The rule.** The voice agent holds thin tools, not the business. For a real answer, one tool relays the question to the live back-office agent, polls and reads the reply aloud. Every other tool draws on screen and reports an ordered event, so a dropped call keeps what was said.

**The data it needs**

- Conversation: kind interview or open line, link token, topics, checklist, saved progress.
- Events: transcript, set_topic, capture_point, complete_topic, log_request, save_summary, ended.
- Relay URL and shared secret, server side only.

**The steps**

1. Request the microphone inside the click, so the browser prompt belongs to it.
2. Start through your signed-in server, which checks the link belongs to this client and returns a short-lived token. The vendor key stays server side.
3. Open a WebRTC session with tools registered on the client.
4. Each tool updates the screen and queues an event. One batch flies at a time, and a failed batch retries after 1.5 seconds.
5. The ask tool posts to a signed-in route, which forwards with the secret and returns an ID. The browser polls every 1.5 seconds for 55 seconds.
6. The log_request tool files a typed request that lists in the app with its status.

**What breaks**

- Past 55 seconds, the tool tells the voice to say the back office will message them.
- With the relay down, the tool tells the voice to pass it along and log the request, not invent an answer.
- A tab closing mid-call reports ended early from pagehide, with keepalive on the request.

**Not proven by the code behind this play**

- The cited code relays the question and reads back the text. Record access belongs to the back-office agent and is not shown.
- Filed requests list in the voice tab. A board write is not in the cited code.

- **Id:** `voice-persona`
- **Modules:** `agents`, `board`
- **Fits when you see:** voice, phone, podcast, talk, calls

### Waitlist with a welcome

<a id="waitlist-welcome"></a>Sign-ups land in your own list, rate-limited, with a welcome email and a founder alert on every one.

**The rule.** Save the row first, then send in the background. The welcome and the alert fire only on a true insert, so a re-signup sends nothing. The limit lives in the database and keys on IP plus email, so a crowd on one network gets through.

**The data it needs**

- Signup: unique email, names, phone, source, confirmation_sent_at, confirmation_error, alerted_at.
- Rate limit: key, window_start, hits.
- Welcome template: draft and published subject and body.

**The steps**

1. Upsert a hit per 10-minute window. Block past 200 per IP, then past 5 per IP plus email.
2. Insert on conflict of email, updating the names. In Postgres, xmax = 0 on the returned row means new.
3. If new, send the published welcome, or a hardcoded original, and stamp the result on the row.
4. Count the last 24 hours. At 10 or fewer, alert the founder and stamp alerted_at.
5. An hourly cron sends one digest of unalerted rows once the oldest is 60 minutes old.

**What breaks**

- A database blip at the limit check must not block signups, so the check fails open.
- A per-process counter barely limits under load, so the count lives in one table.
- A failed alert leaves alerted_at empty, so the next digest covers it. A 1-minute guard keeps in-flight alerts out.

**Not proven by the code behind this play**

- The founder alert is per signup only up to 10 in 24 hours. Past that, an hourly digest covers them. The digest's caller sits outside the cited code.

- **Id:** `waitlist-welcome`
- **Modules:** `intake`, `people`, `campaigns`
- **Fits when you see:** waitlist, join the list, coming soon, early access, sign up, launch

### Your own email engine

<a id="own-email-engine"></a>Campaigns to your own list with open and click tracking, a signed delivery webhook, suppression and an audit log.

**The rule.** Freeze the campaign at Send: final HTML with per-recipient tokens, plus one row per recipient. Sending then means draining a resumable queue. Tracking runs on your own domain with the provider tracking off, so opens, clicks and unsubscribes are your rows.

**The data it needs**

- Campaign: status draft, sending or sent, frozen HTML, text and subject, ordered link list.
- Send row: email, random token, status, claimed_at, open and click stamps.
- Suppression: unique email, reason. Provider event: unique event ID. Audit: who, IP, path, status, capped body.

**The steps**

1. Send requires a mailing address and a confirmed count matching the suppression-filtered audience, else 409.
2. In one transaction, flip draft to sending with a status guard and insert send rows.
3. Claim 400 queued rows with SKIP LOCKED and send batches of 100 with RFC 8058 headers. An hourly cron requeues claims older than 15 minutes.
4. Serve a pixel for opens and a redirect by link index for clicks. A click also stamps the open.
5. Verify the webhook ECDSA P-256 signature over timestamp plus raw body, dedupe on event ID, then suppress hard bounces, spam reports and unsubscribes.
6. Write an audit row in the background after each non-GET admin call. Keep 365 days.
7. A second build sends per recipient with a worker pool of 8, honouring Retry-After on 429 with 3 retries.

**What breaks**

- Mail scanners prefetch links, so an unsubscribe GET only shows a button and POST does the work.
- A dead function strands claimed rows, so the cron requeues them. A rare duplicate beats a lost email.
- A dev machine holding the key would blast the list, so the second build needs a separate live-mode flag and simulates sends otherwise.

**Not proven by the code behind this play**

- The two builds differ: the second turns provider tracking on and sends one request per recipient. The first is the pattern above.

- **Id:** `own-email-engine`
- **Modules:** `campaigns`
- **Fits when you see:** newsletter, email list, subscribers, mailing list, updates

### Brand templates the agent fills

<a id="studio-templates"></a>Carousels and cards render from brand templates with framed photos, queued to a render worker.

**The rule.** One runtime file builds the template in the editor preview and in the headless renderer, so the preview is the export. Motion is a paused timeline seeked by time, so frames are deterministic. The worker wakes on a marker file in object storage, so the database can sleep.

**The data it needs**

- Template doc: kind, duration, fields, values, CSS, pages, with {{key}} tokens.
- Image value: media ID, x and y from 0 to 100, zoom from 1.
- Job: type, payload, status, worker, progress, result.

**The steps**

1. Frame a photo with object-position at x% y%, transform-origin at the same point, then scale by zoom, so the chosen spot stays pinned.
2. Attach animations through the Web Animations API, pause them, and drive them with seek(t).
3. Before capture, await fonts, decode images, and wait 2 animation frames.
4. The API inserts a job and drops a marker. The worker lists markers every 8 seconds, connects only when one exists, and claims with SKIP LOCKED.
5. Render each page in headless Chromium, upload, add a library row per output, zip carousels, delete the marker.

**What breaks**

- A worker restart strands a running job, so startup requeues running rows from that host.
- A render that throws sets status error and still clears the marker, so it never loops.
- Renders fill storage, so the worker errors the job past a 3 GB cap.
- Re-seeding starter templates would wipe edits, so the upsert skips rows with an edited flag.

**Not proven by the code behind this play**

- The worker renders a saved template by ID. No agent code appears in the cited files, so who fills the values is not shown.

- **Id:** `studio-templates`
- **Modules:** `studio`, `social`
- **Fits when you see:** instagram, carousel, brand, design, canva, graphics

### Sponsors, researched and tracked

<a id="sponsor-crm"></a>Sponsors and funders in tiers with stages; the agent researches and fills only blank fields, and nothing sends without a person.

**The rule.** Research columns and pipeline columns are separate, and import writes research only. Re-import fills blanks, so an agent restocks without overwriting the work of a person. No route mails a lead: a person sends by hand, then sets the status.

**The data it needs**

- Lead research: unique normalized brand key, website, fit, angle, tier, risks, contacts JSON, sources JSON.
- Lead pipeline: status, notes, next step, amount, draft subject and body, draft status.
- Tiers: headline, gold, community, in_kind, vendor, media_partner, grant. Stages: prospect, ready, approved, contacted, followed_up, talking, committed, not_now, declined, past, skip.
- Activity log: lead, kind, note, who.

**The steps**

1. The agent POSTs up to 500 leads. Upsert on the brand key.
2. On conflict, scalars take COALESCE(existing, incoming). JSON arrays take the incoming value only when the existing one is empty.
3. A refresh flag overwrites research on purpose. Pipeline fields stay out of the update in both modes.
4. Each status or draft status change logs before and after.

**What breaks**

- A stray test send reaches a real lead, so the test route blocks the contact emails and website domains of all leads, and caps at 20 an hour.
- COALESCE treats an empty JSON array as filled, so arrays check for empty explicitly.
- The blank-only rule lives on import alone. A direct edit overwrites anything.

**Not proven by the code behind this play**

- A refresh flag overwrites research on purpose, and a direct edit has no blank guard.
- The file holds an admin-session import route. The agent that researches sits outside it.

- **Id:** `sponsor-crm`
- **Modules:** `pipeline`, `people`
- **Fits when you see:** sponsors, sponsorship, partners, grant, underwriting, donors, funders

### Goals tied to live numbers

<a id="goals-live-numbers"></a>Goals read their number straight from the data, so the goal board is never a spreadsheet someone forgot to update.

**The rule.** A goal stores a metric key and a target, never the number. The server runs a fixed query for that key on every read, so the number cannot go stale. Keys come from a list in code, so no user input becomes SQL.

**The data it needs**

- Metric registry in code: key, label, SQL returning one integer.
- Goal: title, target date, metric key, metric target.
- Step, its own row: goal ID, title, done, done_at, done_by.

**The steps**

1. On save, null any metric key not in the registry and clamp the target to 1 through 100000.
2. On read, run each distinct metric once and attach the value to its goals.
3. The metric share is value over target, capped at 1. The goal percent averages it evenly with done steps over total steps.
4. A tick patches one step row and stamps who and when. The bar moves at once and rolls back on failure.

**What breaks**

- Two editors would overwrite each other, so a tick touches only its own step row.
- A metric goal with no steps caps at 50 percent, because an empty checklist counts as 0. Give it a step.
- A metric with no target falls back to steps alone, so the form blocks it.
- The number refreshes on load, so an open screen shows the last read.

**Not proven by the code behind this play**

- Four fixed metrics. The goal percent averages the live number with a hand-ticked checklist.

- **Id:** `goals-live-numbers`
- **Modules:** `goals`
- **Fits when you see:** goal, target, raise, launch

### Approve posts from your phone

<a id="social-review-hub"></a>Drafted posts and videos wait in one review queue; comment, request changes or approve, and it posts to each channel.

**The rule.** One row per video or carousel holds review status, and one child row per channel holds its copy, settings and outcome. Posted is the one hard gate: only an approved item reaches it, and nothing leaves it.

**The data it needs**

- Item: kind, title, private object keys, status (draft, in_review, changes_requested, approved, posted), approver.
- Status event: from, to, note, actor kind (user, agent).
- Comment: parent, author kind, body, timecode, resolved, soft delete.
- Channel post: selected, body, hashtags, settings, status (draft, ready, posted, failed), posted URL.

**The steps**

1. Build the page phone-first: player, status bar, comments, details. Media plays from a signed URL good for 1 hour.
2. Allow moves from a table: any earlier status reaches in_review, changes_requested or approved, never back to draft, and only approved reaches posted. Disable other buttons.
3. Request changes takes an optional reason, stored on the status event.
4. Sort threads: whole-item notes first, then by timecode. Give the agent plain text with full IDs.
5. Validate each channel's hard limits on save. Soft targets only move a counter.
6. Mark a channel connected from the publisher's live account list, not a stored flag.

**What breaks**

- Publisher API changes break posting: a changelog webhook verifies an HMAC of the raw body, fails closed, and alerts the owner when a change touches your calls.
- A 50 MB global storage cap overrides the bucket limit: the form refuses larger files up front.
- A failed read could look like 0 comments: the loader throws instead.

**Not proven by the code behind this play**

- Approving moves status only. Posted is a separate action, and the poster sits outside the cited code.
- The cited webhook watches the publisher's API changelog. It does not track posts.

- **Id:** `social-review-hub`
- **Modules:** `social`
- **Fits when you see:** instagram, social, facebook, linkedin, tiktok, posts

### Explainer videos from a script

<a id="explainer-video-pipeline"></a>Stills, voice, music and captions assembled into short explainers from a written script, on a repeatable recipe.

**The rule.** Narration sets the clock: a shot's default length is its voice-over length plus a 1.3 second pad, so editing a line re-times the cut. The only file authored per video is a project file, and one ffmpeg build turns it into an MP4.

**The data it needs**

- Project file: frames with prompts and references, voice lines, effects, music prompt, type cards, shots.
- Shot: ID, optional duration, motion preset, incoming transition, voice and effect cue offsets.
- Cached word timestamps per line from a speech-to-text model.

**The steps**

1. Write one story: one fictional customer, one event, one hard truth, one unresolved action, 12 to 15 short lines.
2. Generate one audio file per line, then effects, music and stills. Stills reuse style references and an establishing shot.
3. Scale each still 2x and animate it with zoompan into a 30 fps clip.
4. Chain clips with xfade, add grain and vignette, fade out over 1 second.
5. Delay each stem to its cue. Duck music with sidechain compression keyed by a narration-only bus. Limit at 0.92.
6. Burn captions in script spelling with model timing: one transparent PNG per phrase state, one overlay above the grain.

**What breaks**

- A looped 22 second bed clicks at the seam: crossfade four copies at 2.5 seconds.
- The speech-to-text model invents words over silence: drop words absent from the script, warn when under half a line matches.
- A first transition longer than the opening shot breaks the timeline: the build refuses, and it throws on any missing asset.

**Not proven by the code behind this play**

- The build assembles existing assets. The generators for stills, voice and music are separate scripts outside the cited code.
- The log says 4 parallel, but clips render one after another.

- **Id:** `explainer-video-pipeline`
- **Modules:** `studio`, `social`
- **Fits when you see:** video, youtube, reels, explainer, tiktok

### Which post sold

<a id="post-to-order-attribution"></a>Every order is tied back to the post or email that brought it, and the agent drafts next week from what worked.

**The rule.** Label every credit by how sure it is: code and link are confirmed, page-view guesses and checkout answers are estimated. Report rows must sum to the sales summary, so unclaimed orders show as Unattributed. The draft writer learns from an engagement score, not revenue.

**The data it needs**

- Order: visitor cookie, session, post id. Attribution: order, post, method (code, utm, estimated, survey), revenue.
- Post metric snapshots, daily visits, follower snapshots.
- Real assets: media library, approved customer posts.

**The steps**

1. At checkout, set the post from a code, else the browser's last post-link touch inside 30 days. A daily job fills the rest as estimated.
2. Weekly report: rank by revenue, orders, visits, engagement, reach. Show top 3 and change against last week.
3. Score posts older than 3 days: (likes + 2 comments + 4 saves + 4 shares) per 1,000 reached, times (reach / followers)^0.25 clamped 0.5 to 1.5.
4. Shrink group averages with 2 prior posts. Patterns need lift of 1.15 or more, or 0.87 or less.
5. Weekly, if no batch exists, pick 3 to 5 assets unused for 42 days. The model writes text only, shaped by those patterns.
6. Save as proposed. Approval moves posts to draft. Nothing publishes.

**What breaks**

- Under 4 scored posts: no patterns, formats rotate.
- Bad model JSON: template text fills in.
- A fetch guard blocks image and video hosts, and a draft without a real asset throws.
- Demo posts carry fake numbers and never teach the writer.

**Not proven by the code behind this play**

- Attribution covers posts, not emails, and some orders stay Unattributed.
- The draft writer learns from engagement, not orders or revenue.
- Weekly drafts default to off.

- **Id:** `post-to-order-attribution`
- **Modules:** `social`, `insights`, `orders`
- **Fits when you see:** instagram, tiktok, social, influencers, content, posts

## Not proven yet

The generator must not show these as done.

- Paid memberships and member logins.
- Ticket checkout inside the app: tickets used hosted card-rail links.

## Signals that point here

creator, community, members, membership, event, events, tickets, festival, waitlist, videos, podcast, youtube, followers, sponsors, fans, show, dance, fitness class
