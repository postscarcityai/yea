# Professional practice, intake first

Clients come to you with a problem, you decide fast whether to take it, and the work runs on deadlines and documents.

Example: **Kettle Creek Veterinary**, a three-location veterinary practice. The companies, people and numbers in these pages are made up. The patterns come from real builds. Back to [all playbooks](README.md).

## Who pays and how

- Clients pay the practice directly under a signed agreement, by whatever method the practice takes.
- New clients come from paid search, organic search and referrals; spend is judged by who signs, not by who fills a form.

## The core loop

1. **Intake.** A spam-proof consult form that keeps the ad click.
2. **Alert.** The team gets the inquiry in seconds, deadline first.
3. **Consult.** The inquiry moves through contacted and qualified to retained or closed.
4. **Agreement.** The client asks for the agreement and it is tracked to signed.
5. **Job file.** The retained client becomes a file with stages, tasks and dates.
6. **Read back.** Every source read against who signed.

## Modules on

| Module key | Label we used | Why |
|---|---|---|
| `leads` | Leads | every inquiry, deadline first |
| `insights` | Insights | source against outcome |
| `jobs` | Matters | one file per client matter |
| `documents` | Agreements | agreement requests to signed |
| `calls` | Calls | the agent in client meetings, what is said checked live |
| `content` | Blog | posts published without a CMS |
| `search` | SEO | rankings, keywords, audits |
| `costs` | Ads | paid search spend and results |
| `social` | Social | videos and posts for review |

Core modules (Home, Inbox, People, Views, Goals, Team, Agents, Board, Log, Settings, Site, Intake, Portal) are on by default as well. Nothing is required: switch off any the business will not use. See `shared/modules.md`.

## Stages we actually used

- **lead** (`leads`): new, contacted, qualified, retained, closed.
- **agreement request** (`documents`): pending, contacted, agreement_sent, signed, declined.
- **matter status** (`jobs`): open, on_hold, closed, declined.
- **video** (`social`): draft, in_review, changes_requested, approved, posted.
- **claim check** (`documents`): confirmed, contradicted, partial, unverifiable, ambiguous, pending.

## The agent's first three jobs

1. Answer every new inquiry with a drafted reply and put the nearest deadline at the top.
2. Every Monday, show which sources brought clients who signed and what each one cost.
3. Turn a signed client into a file and send the digest of what is due this week.

## Hero workflow: Which ads bring clients who sign

Signed in as the owner, approved by the owner. The agent is "Front desk". Shows the play [Which source brings clients who sign](#source-outcome-insights).

Steps on screen: Pin the report > Ask > Source by outcome > Recommendation > Owner approves > Logged with Undo.

- **Pinned:** View "Sources, last 90 days"
- **Ask:** "Which campaign actually brings us clients who sign?"
- **Agent works:** Read 212 inquiries from the last 90 days; Matched 141 ad clicks to their campaigns; Counted who signed, per campaign; Divided spend by signed clients.
- **Reply:** "The wellness plan campaign brought 18 inquiries and 7 signed, at $310 a client. The general campaign brought 64 inquiries and 3 signed, at $2,140 a client. Moving $1,500 a month from general to wellness plans should add about 4 clients."
- **Approval:** "Move $1,500 a month from General to Wellness plans starting Monday?" [Not yet] [Approve], then "Approved. Budget change queued for Monday."
- **Log, with Undo:** Front desk queued a $1,500 budget move to Wellness plans. Approved by Helen Vance.

Names in the script are fictional.

## What it lets them cancel

HubSpot Sales Hub Starter, Mailchimp, Typeform, WordPress.com, Hootsuite, Calendly. Prices and risk for each are in [shared/saas.md](../shared/saas.md).

## Rails kept

Vercel, Twilio SendGrid, Supabase (Postgres), Google Ads API, Search Console API, Meeting recorder API, Social posting API.

## Plays

Innovation plays first: things we built that most businesses like this do not have yet.

### Which source brings clients who sign (innovation)

<a id="source-outcome-insights"></a>Every lead's source read against its outcome, down to the ad campaign, so spend follows retained clients, not form fills.

**The rule.** Store nothing. Derive source and outcome at read time from the attribution columns intake already saves, so old leads backfill the moment the classifier ships. Labels admit what the data cannot prove.

**The data it needs**

- Lead fields: click ids, referrers, landing page, UTM source and medium, status, closed reason, created time.
- The date click-id capture began.
- A hand-kept spam id list and test rules.
- Ad platform click report, account cost, conversion counts.

**The steps**

1. Classify source by first match: click id or ad parameter, paid UTM medium, AI assistant, social, search, other search, referral, unknown.
2. A search referrer before the capture date reads 'ad or search'. After it, organic.
3. Classify outcome: signed is won, not closed is open. Closed splits by regex on the reason: blank, declined to sign, no response, other.
4. Report over 30, 90 or all days, with Monday weeks in practice time and started, finished, signed per source.
5. For each gclid, walk back 14 days from the lead in batches of 7, one query per day, because the click report takes a single date. Cache 6 hours.
6. Show ad cost through yesterday divided by all leads.

**What breaks**

- gbraid and wbraid clicks cannot be looked up, so they get a 'campaign hidden' label, never a guess.
- A click older than 14 days reads 'not recorded', even with a 90-day cookie.
- An ad platform error shows a dash, and the lead report still renders.

**Not proven by the code behind this play**

- Outcome is crossed with source. Campaigns get lead counts only, with no outcome column.
- Spend is total ad cost over all leads. The cited code has no cost per retained client or per campaign.
- The campaign lookup reaches back 14 days, against a 90-day cookie.

- **Id:** `source-outcome-insights`
- **Modules:** `insights`, `leads`, `costs`
- **Fits when you see:** google ads, clients, consultation, retained, marketing

### Your agent on the call (innovation)

<a id="live-claim-check"></a>Send the agent into the meeting. It checks what is said against your own records, tells you what to ask next, and writes up the follow-ups after.

**The rule.** Two model stages. A fast gate reads every speaking turn and only pulls out claims, then a separate verify call checks each claim against one prebuilt brief. Verify returns a verdict and ledger row IDs, and the app renders those rows as the evidence.

**The data it needs**

- Meeting: join URL, start time, opted-in flag, bot ID, status.
- Fact ledger: metric, period, basis, value, unit, source reference.
- Claim: text, metric, value, verdict, evidence, rationale, suggested question, status.

**The steps**

1. Join job: stop if not opted in or a bot ID exists. Over 2 minutes out, schedule the bot for 60 seconds before start.
2. Build the brief from ledger, notes, research and checklist. Send it as a cached prefix, rebuilt only when a fact or note changes.
3. Gate each turn with recent lines and the last 30 checked claims: one claim per metric per turn.
4. Verify numbers automatically. Named facts and evasions become chips a person taps.
5. After the call, write the report, insert follow-up requests as drafts, skipping stored item text, and email the team.

**What breaks**

- Transcripts drop decimal points. Verify gets alternate readings, and a matching reading returns ambiguous with a confirming question.
- A failed check renders as Failed, never as "Not in data".
- The bot never gets admitted: the report records why and no email goes out.

**Not proven by the code behind this play**

- The pipeline produces next questions, but the live screen hides them. The next question on screen is the one inside an opened claim card.
- Follow-ups are stored as drafts. Nothing goes to the other party.

- **Id:** `live-claim-check`
- **Modules:** `calls`, `documents`
- **Fits when you see:** diligence, due diligence, investors, advisory, audit, review, meetings, consultation, consultations, discovery call, client calls, sales calls

### Search ranks without the subscription (innovation)

<a id="seo-in-house"></a>Rankings, keywords, competitors, links, site audit and index checks in your own app, refreshed on a schedule.

**The rule.** A rank tracker is a series, and a data vendor sells today's results, never last Tuesday's. So one write path serves the button, the cron and the bulk refresh, and all of them upsert on keyword and day.

**The data it needs**

- Keyword: text, device, location, is_active, created_at.
- Snapshot: keyword, UTC date, nullable position, URL. Unique on keyword and day.
- Result rows: top 20 per keyword and day with domain, URL, title. Unique on keyword, day, position.

**The steps**

1. A cron runs at 08:10 UTC behind a bearer secret, answering 503 when it is unset.
2. Load active keywords by created date, capped at 40.
3. Check them one at a time, because the daily quota counter is read-then-write and parallel calls walk past the cap.
4. Fetch results, take your best position by filtering your domains and sorting, and upsert the snapshot, null position included.
5. Return counts for checked, ranked, from cache, failed. Log only the first error, which keeps query strings out of logs.
6. Show one tab per tool: rankings, keywords, competitors, links, audit, pages, indexing, crawlers.

**What breaks**

- Once the daily cap hits, the run stops, because each remaining call fails and burns a request.
- Local-time dates let the button and cron write two rows for one day, so capture dates use UTC.
- Past 40 keywords, created-date order re-checks the same 40 and starves the rest, so order by last capture if you outgrow the cap.

**Not proven by the code behind this play**

- The cited cron refreshes rankings and top-20 results only. Links, audit and indexing appear as tabs, and their refresh is not in the cited code.

- **Id:** `seo-in-house`
- **Modules:** `insights`, `site`
- **Fits when you see:** seo, rankings, google, search, blog

### Intake that remembers the click

<a id="intake-with-click-ids"></a>A spam-proof consult form that keeps the ad click id for 90 days, logs phone and chat taps, and alerts the team in seconds.

**The rule.** Keep ad click ids in a server-set first-party cookie, not only in browser storage. Safari wipes script-written storage after 7 days, while a response-header cookie lasts the 90 days the ad platform accepts a click.

**The data it needs**

- Click cookie: gclid, gbraid, wbraid, click time. 90 days, httpOnly, secure.
- First-touch cookie: landing path, external referrer, UTMs.
- Lead row: contact fields, consent time and IP, click ids, first-touch fields, alert-sent time.
- Tap row: phone or chat, page, click ids, first-touch fields.

**The steps**

1. Edge middleware tests URL click ids against ^[A-Za-z0-9_-]{10,255}$ and sets the cookie on a match.
2. Write first touch on the first page view. Reset it only on a new click or UTM visit.
3. The form POST runs: 5 per 15 minutes per IP, honeypot, server-verified bot challenge, validation, consent check.
4. Save the lead when contact fields arrive. Posted click ids beat the cookie. Click time survives only when both match.
5. Email the team inside that request and stamp alert-sent.
6. Taps post by sendBeacon to a route that always answers 204 and drops bot user agents.

**What breaks**

- A tripped honeypot gets the normal success shape with a decoy id, no row, no email, so the bot learns nothing.
- A failed challenge answers 403 honestly, because a real person needs to reload.
- The rate limit lives in process memory and resets per serverless instance, so the other two filters do the real work.

**Not proven by the code behind this play**

- Taps are stored, but the insights report does not read them.

- **Id:** `intake-with-click-ids`
- **Modules:** `intake`, `leads`, `insights`
- **Fits when you see:** free consultation, consultation, call now, schedule a call, case review, contact us

### Deadlines decide the queue

<a id="deadline-urgency"></a>Each inquiry carries its next deadline, and anything inside seven days turns red at the top of the queue.

**The rule.** Give each inquiry its own hard date and a separate status-moved time, because neither can be derived later. Index only open records with a pending deadline, since the queue never asks about the closed backlog.

**The data it needs**

- next_deadline timestamp on both intake tables.
- status_changed_at, because updated_at moves on any edit, notes included.

**The steps**

1. Add nullable columns only: no drops, renames or backfills on a live table.
2. Write the visitor's stated deadline from the last form step into next_deadline.
3. Create a partial index on next_deadline where it is set and closed_at is null.
4. Define urgent as inside 7 days and give it red treatment in the inbox.
5. The completed-form alert uses its own tiers: inside 72 hours gets a red header and urgent subject, inside about 2 weeks gets a time-sensitive prefix.
6. On conversion, copy the deadline onto the job file calendar as an all-day event.

**What breaks**

- A write fallback hid missing columns: the completion route caught the database error, saved a partial update, and dropped every visitor's deadline.
- A check constraint on status could reject a public intake insert, so status stays free text and server actions enforce the pipeline.
- A date-only value parsed at midnight shifts a day across time zones, so the alert anchors it to noon UTC.

**Not proven by the code behind this play**

- The cited code adds the columns and index. The red treatment appears as a schema comment, and top-of-queue sorting is not in it.

- **Id:** `deadline-urgency`
- **Modules:** `leads`
- **Fits when you see:** deadline, court, urgent, arrested, filing, time sensitive

### One file per job, with a reminder digest

<a id="job-file-deadline-digest"></a>A won lead becomes a job file with stages, tasks and dates, and a daily digest says what is due.

**The rule.** Keep identity, work and intake apart: a person row is the root, a job file is the work, and intake tables point at both. Conversion runs in one database function, so a failure cannot leave a half-built file.

**The data it needs**

- Person: email (unique among live rows), name, phone, kind.
- Job file: number, caption, stage, status (open, on_hold, closed, declined), owner.
- Event: kind, occurs_at, completed_at, remind_days_before, remind_email, reminder_sent_at.
- Task: status, due_at, assignee.

**The steps**

1. The owner triggers conversion. SELECT FOR UPDATE locks the lead, and an existing file returns with created=false.
2. Match the person by email and fill blanks only.
3. Insert the file at stage prospect, numbered PREFIX-YYYY-NNN under a per-year advisory lock, with a client party, opening note and any deadline event.
4. Link the lead and leave its status alone: opening a file is not winning the work.
5. A daily cron behind a bearer secret loads up to 500 pending dated events and compares practice-local days to remind_days_before.
6. Stamp reminder_sent_at where null, then send one email. Cap 50 per run. A failed send clears the stamp.

**What breaks**

- A crash after the stamp loses a reminder rather than doubling it, and the event stays red on the calendar.
- Events over 14 days past retire unmailed, so a backfill cannot flood an inbox.
- A missing recipient logs an error and retires the row, so a config gap consumes reminders.

**Not proven by the code behind this play**

- No digest: the cron sends one email per event, and tasks are not included.
- A person triggers conversion, and it opens at prospect. Winning the lead does not trigger it.

- **Id:** `job-file-deadline-digest`
- **Modules:** `jobs`, `board`
- **Fits when you see:** cases, matters, projects, engagements, jobs, clients

### Agreement requests in the inbox

<a id="agreement-request-inbox"></a>A client asks for the agreement online and the request lands in the app with its status, from pending to signed.

**The rule.** Treat an agreement request as a second intake stream, not a document feature. It carries the same bridge columns as the main lead table, and both streams meet on one person row by email.

**The data it needs**

- Request row: name, email, optional phone, IP, user agent, text status starting at pending, email_sent, email_sent_at.
- Bridge columns: person link, job file link, closed_at, closed_reason, assignee, next_deadline, status_changed_at.
- Index on status and created_at descending.

**The steps**

1. The POST runs: 3 per 15 minutes per IP, honeypot, server-verified bot challenge, name and email validation.
2. Insert the row as pending with email_sent false.
3. Email the owner, then write the result to email_sent. A failed alert does not fail the request.
4. Convert with a twin of the lead function, not a shared one with a table-name argument, because requests will grow signature columns.
5. Lock the row with SELECT FOR UPDATE, so a double-click returns the existing file.
6. Leave request status untouched on conversion: signing is the owner's call.

**What breaks**

- A tripped honeypot gets the normal success shape, no row, no alert.
- Saving before alerting means a mail outage cannot lose a request, and email_sent false shows which alerts failed.
- One person using both streams would split in two, so conversion dedupes on email and fills blanks only.

**Not proven by the code behind this play**

- The cited code writes pending and nothing else. A signed transition is not in it.
- The email it sends is an alert to the owner. It does not email the agreement to the client.

- **Id:** `agreement-request-inbox`
- **Modules:** `documents`, `leads`
- **Fits when you see:** retainer, engagement letter, agreement, contract, sign

### See which AI read your site

<a id="ai-crawler-log"></a>Log every AI crawler that reads your pages, so you know which answers engines are learning from you.

**The rule.** Split hits by purpose and never report one total. A live retrieval fetch stands in for one citation, an index fetch leads it, and a training fetch says little about being cited.

**The data it needs**

- Registry entry: lowercase user-agent token, canonical bot, operator, purpose (retrieval, search, training). Build it from operators' published lists and map retired tokens onto the current name.
- Hit row: time, bot, operator, purpose, path, full user agent, referer, IP, country.
- Views: per bot, per path with retrieval broken out, daily per purpose.

**The steps**

1. Run edge middleware on public paths, excluding admin, API routes and static assets. Keep robots.txt and sitemap.xml in.
2. Count only GET and HEAD. Scan the lowercased user agent by substring, first match wins.
3. On a match, hand a plain REST insert to waitUntil, so it runs after the response. Truncate user agent and referer to 512, path to 1024.
4. Leave major web search crawlers out: their consoles report that crawl.
5. Fill known bots with no rows from the registry, so 'never fetched' shows as a real zero.

**What breaks**

- A token that is a substring of another must come first, or training fetches file as indexing.
- Write failures are swallowed so a page never breaks, which makes loss silent. The last-hit time is the tell.
- Unknown crawlers stay invisible until someone adds a line, so re-read the operators' lists twice a year.
- User agents are spoofable, so the IP is stored for a reverse DNS check.

**Not proven by the code behind this play**

- Only crawlers in a fixed list are logged, not every one.
- It records fetches by purpose. It cannot see answers or citations.

- **Id:** `ai-crawler-log`
- **Modules:** `insights`
- **Fits when you see:** seo, content, blog, articles, ai search

### Earned media pipeline

<a id="press-pipeline"></a>Press targets with stages from not contacted to placed, pitches drafted in a plain voice, every touch logged.

**The rule.** Store one row per researched target, not per person, because many targets share a desk inbox. Status is a cache of an event log. Pitches render as what a person would type, with every template artifact removed.

**The data it needs**

- Target: stable key from lane, outlet and name, person link, research snapshot, email with confidence (verified, pattern, desk, form), follow_up_at.
- Status: not_contacted, queued, pitched, followed_up, replied, declined, placed, bounced.
- Touch event: kind (pitch, follow_up, reply, decline, placement, bounce, note), snapshotted recipient, subject and body, provider message ID.

**The steps**

1. Import research on the stable key, so a regenerated file adds no duplicates.
2. Render plain text: drop the headline, wrap at 72 columns without splitting long tokens, print the link as a bare URL, sign after a -- line.
3. Add a one-line reply opt-out by default. The send carries a List-Unsubscribe header.
4. Send through the campaign sender, record the touch event, refresh the cached status.
5. Build the follow-up queue from follow_up_at, skipping archived targets.

**What breaks**

- A desk gets mailed twice in one push: a unique campaign and email pair stops it.
- A guessed address reads as confirmed: show the confidence in the UI.
- A template edit rewrites history: snapshot subject and body on each event.

**Not proven by the code behind this play**

- The cited helper renders supplied text. Drafting the pitch and writing the touch events sit outside the cited code, and no trigger enforces append-only.

- **Id:** `press-pipeline`
- **Modules:** `pipeline`, `outreach`, `people`
- **Fits when you see:** press, media, featured in, as seen on, expert, commentary

### Publish without a CMS

<a id="blog-without-cms"></a>The team edits a post in the app and it commits to the site's repo, so the site redeploys with no CMS bill.

**The rule.** The runtime filesystem is read-only, so the editor commits through the GitHub Contents API and the host's git integration redeploys. The blob sha is the concurrency token: a rejected write sends the user to reload, and never retries with a fresh sha, because that is a force overwrite.

**The data it needs**

- A fine-grained token with contents:write, repo and branch.
- Per edit: path, decoded text, loaded blob sha, commit message, author name and email.
- A kill switch: the editor stays off unless a variable equals 1.

**The steps**

1. GET the file at the tracked branch. Return null on 404, throw if it is not a file, decode the base64, keep the sha.
2. Hold the sha beside the text during the edit.
3. PUT base64 text with the loaded sha, branch and message. Set the committer to the signed-in user, so git log reads as editorial history.
4. On 409 or 422, raise a conflict error: reload, your text was not saved.
5. On success, return the new sha and commit URL. The host redeploys from the commit.

**What breaks**

- Cached reads return a stale sha and create phantom conflicts: every request sends no-store.
- An unused editor still holds a write token: the kill switch shuts the path when a pipeline authors posts, and the UI shows a read-only banner.
- A preview deploy could commit to the live branch: explicit repo and branch variables override the host's values.

**Not proven by the code behind this play**

- The editor is off by default in the build behind this play, because a pipeline authors the posts now.
- The helper edits existing files. It needs a sha, so it does not create posts.

- **Id:** `blog-without-cms`
- **Modules:** `content`, `site`
- **Fits when you see:** blog, articles, insights, news

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

### A business profile post every day

<a id="gbp-daily-post"></a>The agent drafts and posts to the Google business profile on a schedule, from what the business already published.

**The rule.** Each post mirrors the article that went live today in the business's timezone. No article means no post, and a missed article is never carried forward, because a backlog only builds a stale queue. An agent writes the summary outside the script, and the script validates it.

**The data it needs**

- Articles with frontmatter: slug, status, offset date, share image path.
- Append-only ledger: timestamp, slug, post resource name.
- Refresh token with business.manage scope, account ID, location ID.

**The steps**

1. Run a daily job after the morning publish job.
2. Select articles published, not future-dated, with an image, absent from the ledger, dated today in the business timezone.
3. Validate the summary: first sentence 80 characters at most, 400 minimum, fail past 1450, reject em dashes, bullet markers and stock openers.
4. POST to the v4 localPosts endpoint with summary, absolute image URL and an action button to the article.
5. Try 4 times on 5xx and 429, waiting 5, 10, then 15 seconds. Stop on other 4xx.
6. On success, append to the ledger.

**What breaks**

- The endpoint is allowlist-only: unapproved projects get 403, or 429 with zero quota, so apply a week or more ahead.
- Tokens minted while the consent screen is in Testing expire after 7 days: publish the screen, then mint.
- Server-time date math picks the wrong day: compare calendar days in the business timezone.

**Not proven by the code behind this play**

- Not every day: a day with no article gets no post.
- The scripts post a finished summary and hold no scheduler. An outside agent and an outside job do the drafting and timing.

- **Id:** `gbp-daily-post`
- **Modules:** `social`, `reviews`
- **Fits when you see:** google reviews, local, near me, service area, locations, office

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

### Documents read on arrival

<a id="document-extraction"></a>Every file in the data room is parsed and its facts extracted, so the agent can cite page and line.

**The rule.** Key every fact on metric, period and basis, with a source reference a person can follow to the page or cell. Re-extraction replaces only machine rows, and a human-touched key blocks its fresh copy, so corrections and deletions stay put.

**The data it needs**

- Document: filename, mime type, parse status, parse error, extracted text, summary.
- Fact: metric, period, basis, value in base units, unit, source reference, note, confidence, source kind, edited-by-user flag.

**The steps**

1. Route by type. Send a PDF whole to the model and store page-tagged text separately for search and quoting.
2. Flatten spreadsheets to rows of ADDRESS=value so references point at cells. Cap sheets and text at 180,000 characters.
3. Fail other types with a message to export to PDF.
4. Request one row per key, raw base units, no derived metrics, confidence below 0.6 for ambiguous cells.
5. Delete the document's unedited facts, drop new facts matching an edited key, insert the rest, set status done.
6. Research in two passes: web search writes a brief (12 searches, 10 fetches), then a structured pass pulls numbers with URLs.

**What breaks**

- A long file loses its tail. Status still reads done, and the parse error field says the tail was not read.
- PDF text failure is logged and swallowed: extraction still runs, but search has no text for that file.
- Web numbers are secondhand, so research confidence caps at 0.7, and a new run soft-deletes earlier research facts unless a person edited them.

**Not proven by the code behind this play**

- PDF, spreadsheet and plain text types only. Word and deck files fail with a message to export to PDF.
- References point at page and table or sheet and cell, not lines.

- **Id:** `document-extraction`
- **Modules:** `documents`, `library`
- **Fits when you see:** documents, data room, files, contracts, records

### Every agent edit, logged with Undo

<a id="agent-change-log"></a>The agent edits records from chat, and every change lands in a log a person can undo.

**The rule.** Every edit tool must quote the words in the person's latest message that ask for the change, and code checks the quote is there. Text in documents, transcripts or web pages can never trigger an edit. Writes run through the person's own database client, so row-level policy decides what they may change.

**The data it needs**

- Change row: actor, entity type and ID, path, item key, op, payload, before, after, one-line summary, undone-at, undone-by.
- Generated reports: a stored base plus a current version with an updated-at stamp.

**The steps**

1. Normalize case, quotes and whitespace, then require the quote in the latest message: 12 characters minimum, or the whole message if shorter.
2. Apply the change and log before and after. Store as after what the database returned, so undo compares like with like.
3. For generated reports, store the edit as a payload and rebuild from base plus active edits, guarded on updated-at, 3 attempts.
4. Undo: if a later active change hits the same entity, path and item key, or the current value differs from after, refuse and name the conflict. A forced retry overrides.
5. Otherwise write before back, remove added rows, stamp undone-at.

**What breaks**

- A forced undo can wipe newer work, so the agent must ask the person first.
- A report rebuild fails after the log write: the edit is withdrawn, so a retry stacks no duplicate.
- Timestamps return as Z or +00:00. Equality treats them as one instant, so undo raises no false conflict.

**Not proven by the code behind this play**

- Most edit tools write the record first and the log row second, with no rollback. A failed log write leaves an unlogged edit.
- In the second build, a contact insert skips the log and undo has no later-change check.

- **Id:** `agent-change-log`
- **Modules:** `agents`, `log`
- **Fits when you see:** team, office, staff, admin

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

## Not proven yet

The generator must not show these as done.

- E-signature inside the app: agreements are tracked, signing happens outside.
- Taking payment: the practice lists its methods, there is no checkout.
- A numeric lead score: urgency comes from the deadline.

## Signals that point here

law firm, attorney, lawyer, legal, consultation, free consultation, practice, cpa, accounting firm, advisory, consulting, due diligence, clients, case, matter, retainer, clinic, patients
