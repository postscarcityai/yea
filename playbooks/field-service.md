# Field service: estimates and jobs

You go to the customer's place, look at the problem, quote it and do the work.

Example: **Mendell Property Group**, a property manager running repair estimates and jobs. The companies, people and numbers in these pages are made up. The patterns come from real builds. Back to [all playbooks](README.md).

## Who pays and how

- The customer pays per job, from an estimate.
- The estimate comes from a price table, not a guess, so every quote is the same for the same work.
- The estimator itself can run on the firm's own brand, which is how the marketplace sells it.

## The core loop

1. **Request.** The customer starts on your site and sends photos.
2. **Estimate.** The photos are read for scope and priced from your table.
3. **Follow up.** Half-finished requests and quiet reports get one nudge each.
4. **Job file.** The won estimate becomes a job with stages, tasks and dates.
5. **Due today.** A daily digest says what is due and what is late.

## Modules on

| Module key | Label we used | Why |
|---|---|---|
| `leads` | Requests | every estimate request with photos |
| `jobs` | Jobs | one file per job |
| `intake` | Get an estimate | the photo estimator on your site |
| `costs` | Cost per lead | what each job costs to win |
| `reviews` | Reviews | the business profile and reviews |
| `social` | Posts | a business profile post a day |
| `catalog` | Price table | the prices the estimate uses |

Core modules (Home, Inbox, People, Views, Goals, Team, Agents, Board, Log, Settings, Site, Intake, Portal) are always on as well. See `shared/modules.md`.

## Stages we actually used

- **request** (`leads`): new, contacted, connected, closed.
- **severity** (`leads`): minor, moderate, major, high_risk.
- **job task** (`jobs`): open, in_progress, done, canceled.

## The agent's first three jobs

1. Read each photo request, price it from your table and send the report.
2. Nudge every half-finished request and every quiet estimate, once.
3. Send the morning digest: jobs due today, jobs late, estimates waiting on you.

## Hero workflow: Photos to an estimate before the truck rolls

Signed in as the customer, approved by the owner. The agent is "Estimate desk". Shows the play [Your own photo estimator](#white-label-photo-estimator).

Steps on screen: Photos in > Ask > Priced from your table > Estimate ready > Owner approves > Logged with Undo.

- **Pinned:** Photo "Photo 1", Photo "Photo 2"
- **Ask:** "The unit is blowing warm air and dripping inside. Can you fix it this week?"
- **Agent works:** Read 2 photos; Matched the data plate: 2014, 3 ton; Priced a drain clear and a capacitor from your table; Held Thursday 8 AM for Marco.
- **Reply:** "Most likely a clogged condensate line and a weak capacitor. The estimate is $289 and Marco can be there Thursday at 8."
- **Approval:** "Send the $289 estimate and the Thursday slot to Ruth Okafor?" [Edit] [Approve], then "Approved. Estimate sent."
- **Log, with Undo:** Estimate desk sent a $289 estimate to Ruth Okafor. Approved by the owner.

Names in the script are fictional.

## What it lets them cancel

Jotform, Typeform, Calendly, Mailchimp, Trello, Wix. Prices and risk for each are in [shared/saas.md](../shared/saas.md).

## Rails kept

Vercel, Twilio SendGrid, Google Business Profile API.

## Plays

Innovation plays first: things we built that most businesses like this do not have yet.

### Your own photo estimator (innovation)

<a id="white-label-photo-estimator"></a>The photo-to-report estimator on your own brand and URL, so every visitor leaves with a price and you get the lead.

**The rule.** One funnel, stamped per run. A hidden slug on the form stamps the job with the brand and a snapshot of its mode, and every later step reads the snapshot. Preview is inert and the default for any firm with a logo.

**The data it needs**

- Firm: slug, name, logo path, listing state.
- Site row: state (preview or live), lead recipient, palette, palette's logo path, offered-at, requested-at.
- Job: brand firm id, mode snapshot.
- Price table: item key, low, high, commercial overrides, plus region multipliers.

**The steps**

1. On page load, refuse firms with no logo or a hidden listing. Create the site row on first read, so no backfill.
2. Derive the palette from the logo, recompute only when the logo path changes, and write only hex-checked values into a root CSS override.
3. The model emits scope keys and quantities. Dollars come from quantity times table range times region multiplier, rounded out to the nearest 100.
4. A preview run gets the report, records no request and sends nothing. A live run routes to a recipient that stays server-side.
5. Show the offer only to firms that claimed or clicked. They ask by email, and first mail to the dedicated address stamps requested-at when the sender matches a firm.

**What breaks**

- A page view recomputes colours during an admin switch to live. The upsert names only palette columns, so the switch survives.
- A site flips back to preview mid-run. The snapshot rules, so a request made while live still reaches the firm.
- The model invents an item key. It is logged and omitted, so the range understates.
- Link from listings only when live with a recipient. A preview link dead-ends the customer.

**Not proven by the code behind this play**

- The page lives under the platform's domain with the firm's brand. The cited code has no custom domain or embed.

- **Id:** `white-label-photo-estimator`
- **Modules:** `intake`, `site`, `leads`
- **Fits when you see:** estimate, free estimate, quote, inspection, service area, restoration, repair, install

### Nobody falls out of the funnel (innovation)

<a id="funnel-followups"></a>Half-finished requests get one resume email, and reports with no ask get one follow-up, on a clock, never twice.

**The rule.** Each nudge is a time window plus a one-shot timestamp on the job, claimed before the send. The window's upper bound means a cron that was down never emails about stale work when it returns.

**The data it needs**

- Job: status, last step, email, updated time, report-claimed time, one sent-at column per nudge.
- Help requests: job id, type, created time.
- Address suppression list.

**The steps**

1. Guard each cron with a bearer secret compared in constant time. No secret set means refuse.
2. Resume nudge: status draft, analyzing or failed, has email, updated 2 to 48 hours ago.
3. Missing-detail nudge: help request 2 to 48 hours old, question unanswered, no document uploaded.
4. Post-report nudge: status assessed, claimed 3 to 14 days ago, no help request, address not suppressed.
5. Claim: set sent-at where still null. No row back means skip.
6. Send up to 25 per run with a minted link back to where they stopped.

**What breaks**

- Two runs overlap: the conditional update lets one win. A failed send after the claim is never retried, on purpose: an unsent reminder beats a double-send.
- The query layer has no NOT EXISTS, so filter help requests in code and fetch 100 rows, above the send cap.
- These nudges carry the platform brand, so they skip every partner-branded run, preview and live.
- The marker lives on the job, so one person with two jobs gets two emails.

**Not proven by the code behind this play**

- The marker lives on each job, so never twice means per job, not per person.

- **Id:** `funnel-followups`
- **Modules:** `intake`, `campaigns`, `leads`
- **Fits when you see:** get started, free quote, request, book, schedule, estimate

### Cost per lead, every channel (innovation)

<a id="cost-per-lead"></a>Ad spend and tool spend divided by real leads, per channel, so you know what a customer costs before you scale it.

**The rule.** Keep cost in layers of unequal trust: model calls exact, ad and fixed costs allocated, each labelled. Spend on a channel-day with no leads never lands on another lead's row. It shows as its own wasted number.

**The data it needs**

- Leads: created time, channel, contact email, help requests.
- Model calls: lead id and cost, both nullable.
- Ad spend: channel, start day, end day, amount, unique external key.
- Fixed costs: monthly amount, active from, active to.
- API call log and per-provider monthly caps.

**The steps**

1. Sync platform cost per campaign-day over an overlapping 7-day window, upserting on platform:account:campaign:date.
2. Spread each spend row evenly over its days. Keep days inside the 7, 30 or 90 day report.
3. Split each channel-day across that day's leads. No leads: add it to wasted.
4. Split fixed costs, prorated to covered days, across that month's leads.
5. Report per channel: cost per lead, per contactable lead, per help request.
6. Before a billed API call, check the cap against this month's log. No cap row refuses the call.

**What breaks**

- The ad platform restates cost for up to three days. The overlap plus upsert corrects it without doubling.
- A model call can return no cost. Count it as unpriced and show the count.
- A channel with spend and no leads returns null cost per lead, not zero. Channel totals include wasted spend, so channel averages run above row shares.

**Not proven by the code behind this play**

- The monthly caps cover one map-imagery call, not model spend, and that log does not feed cost per lead.
- The base count includes unfinished requests. The contactable and help-request views are the strict ones.
- One ad platform syncs by script. Other channels are typed in.

- **Id:** `cost-per-lead`
- **Modules:** `costs`, `insights`
- **Fits when you see:** google ads, advertising, ads, marketing spend, cost per, paid search, facebook ads

### Photos to a priced lead

<a id="photo-to-priced-lead"></a>A customer sends photos and answers a short interview, and gets a written report with a price before anyone calls.

**The rule.** The model reads scope and never touches money. It returns line-item keys and quantities from a closed enum, and code multiplies them by a cost table, so every range traces to a table row.

**The data it needs**

- Job: description, customer kind, region, status, share slug.
- Photos in a private bucket, tagged by shot kind.
- Question bank: key, options, priority rank.
- Cost table: key, unit, low, high, per-kind overrides, region multipliers.

**The steps**

1. On upload, cap at 15 MB and re-encode to JPEG to strip GPS metadata.
2. One vision call plans up to 8 cards. Code forces bank options, appends missing keys by priority, and cuts non-bank cards first.
3. A new photo or significant answer replans only the unanswered tail, budget 8 minus answered.
4. A second vision call returns findings, risks, severity, confidence and scope, with the key enum built per customer kind.
5. Code prices quantity times unit low and high times region multiplier, rounding the total outward to the nearest hundred.
6. Serve the report at the slug once assessed: noindexed, generic preview metadata, one-hour signed photo URLs.

**What breaks**

- A tight token budget cuts the plan mid-JSON. Give headroom, retry once, then fall back to static questions.
- A no-photo job cannot claim high confidence: code downgrades it to medium.

**Not proven by the code behind this play**

- The output is a low and high range labelled as triage, not a binding quote.
- The cited code stops at the report. It does not show a lead being created from it.

- **Id:** `photo-to-priced-lead`
- **Modules:** `intake`, `leads`, `site`
- **Fits when you see:** photos, estimate, quote, free quote, damage, repair, inspection, assessment, how much

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

### Every inbox in one place

<a id="inbound-parse-inbox"></a>Mail to any address on your domain lands in the app's inbox, threaded, with the agent's draft reply.

**The rule.** Point the whole domain at one webhook and treat every address as a mailbox. Stamp your own Message-ID on every send, so replies thread by header first, and fall back to the same outside party plus normalised subject inside 60 days.

**The data it needs**

- Threads: subject, counterparty, mailbox, status (inbox, archived, spam), unread, count, snippet, firm id, labels.
- Messages: thread id, direction, Message-ID, In-Reply-To, References, bodies, spam score.
- Attachments: message id, file name, private storage path.

**The steps**

1. Route the whole domain to an email provider's inbound webhook. The secret rides in the query string because the provider cannot send headers.
2. Read the envelope for real recipients, including Bcc. The first address on your domain sets the mailbox.
3. Return early if the Message-ID exists. Otherwise find or create the thread and insert the message.
4. A spam score of 5 or more files a new thread as spam. A reply pulls an archived thread back.
5. Match the sender to a firm: address, then portal account, then domain, skipping free mail and requiring exactly one firm.
6. Reply through one send function that sets threading headers and turns tracking off.

**What breaks**

- The provider retries non-2xx for up to three days. Bad secret gets 401, unparseable body 200, database failure 500, and Message-ID dedupe makes retries safe.
- A franchise domain matches many firms. The exactly-one rule leaves the thread unlinked.
- A failed attachment upload is logged and skipped, since the message already exists.

**Not proven by the code behind this play**

- The cited code shows no agent draft. The inbox receives, threads and sends. A draft step would be new work.

- **Id:** `inbound-parse-inbox`
- **Modules:** `inbox`
- **Fits when you see:** email us, contact us, support, info@

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

## Not proven yet

The generator must not show these as done.

- Dispatch and crew scheduling: Bookings is not yet proven in any build.
- Taking payment on the job: Money is not yet proven end to end.
- Texting customers: no build sends SMS yet.

## Signals that point here

repair, repairs, install, installation, service call, estimate, estimates, free estimate, technician, crew, plumbing, hvac, roofing, restoration, mitigation, cleaning, landscaping, pest, electrical, service area
