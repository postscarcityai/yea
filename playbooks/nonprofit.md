# Nonprofit, donor funded

You run programs for people who cannot pay, funded by donors, sponsors and grants.

Machine-readable copy: `lib/yea-finale/playbooks/archetypes.ts` in the postscarcity-ai repo, id `nonprofit`. Back to [all playbooks](README.md).

Paths starting with `~/` are internal proof: they point into private repos, so you cannot open them from outside. Every play's recipe stands alone without them.

## Who pays and how

- Donors give through a giving rail, from one giving page with tiers, the tax status and the EIN.
- Sponsors and funders give in tiers; grants and in-kind count.
- Raffles and giveaways need rules and a recorded draw.

## The core loop

1. **Tell the mission.** The home page shows the gap the programs fill. `~/dev/healing-alliance/src/app/page.tsx`
2. **Give.** Every button goes to one giving page, then out to the giving rail. `~/dev/healing-alliance/src/app/donate/page.tsx`
3. **Show impact.** Real figures, or a plain note that they are coming. `~/dev/healing-alliance/src/app/donate/page.tsx`
4. **Fund.** Sponsors and funders tracked by tier and stage. `~/dev/bootyverse/fn/sponsors.ts`
5. **Keep in touch.** Updates to donors from your own list. `~/dev/bootyverse/fn/campaigns.ts`

## Modules on

| Module key | Label we used | Why |
|---|---|---|
| `site` | Site | mission, team, resources, giving page |
| `shop` | Donate | giving tiers |
| `pipeline` | Funders | sponsors, funders and grants by stage |
| `people` | Donors | everyone who gave or signed up |
| `campaigns` | Updates | donor updates |
| `goals` | Goals | the raise and program goals, live |
| `programs` | Raffles | raffles with rules and a draw |
| `playbook` | Approved copy | the words the board signed off |

Core modules (Home, Inbox, People, Views, Goals, Team, Agents, Board, Log, Settings, Site, Intake, Portal) are always on as well. See `shared/modules.md`.

## Stages we actually used

- **funder** (`pipeline`): prospect, ready, approved, contacted, talking, committed, not_now, declined, past. `~/dev/bootyverse/fn/sponsors.ts`
- **raffle** (`programs`): draft, scheduled, live, closed, drawn, fulfilled. `~/dev/peels/lib/giveaways.ts`
- **update** (`campaigns`): draft, queued, sending, sent. `~/dev/bootyverse/fn/campaigns.ts`

## The agent's first three jobs

1. Thank every donor the day they give, in the board's approved words.
2. Research funders and grants that match the mission and tee them up by stage.
3. Keep the impact panel honest: update it when real numbers come in, never invent one.

## Hero workflow: Ten funders that fit, ready for Monday

Signed in as the admin, approved by the owner. The agent is "Development desk". Shows the play [Sponsors, researched and tracked](#sponsor-crm).

Steps on screen: Pin the mission > Ask > Research > Shortlist > Director approves > Logged with Undo.

- **Pinned:** Doc "Mission and programs"
- **Ask:** "Find funders who back peer support for veterans in our county and line them up."
- **Agent works:** Read the mission and the three programs; Found 14 funders with matching giving history; Filled only blank fields, kept what we had; Ranked 10 by fit and gift size.
- **Reply:** "Ten funders are on the left, ranked by fit. Three gave to peer support in the county last year. Nothing has been sent; each one has a drafted first note."
- **Approval:** "Move these ten to Ready for Monday's outreach?" [Not yet] [Approve], then "Approved. Ten funders moved to Ready."
- **Log, with Undo:** Development desk moved 10 funders to Ready. Approved by the director.

Names in the script are fictional.

## What it lets them cancel

Wix, Mailchimp, Typeform, Airtable. Prices and risk for each are in [shared/saas.md](../shared/saas.md).

## Rails kept

Vercel, Twilio SendGrid, Giving rail (hosted donation form).

## Plays

Innovation plays first: things we built that most businesses like this do not have yet.

### Impact without made-up numbers (innovation)

<a id="honest-impact"></a>The impact panel shows real figures or says they are coming, with the program-spend goal, never invented stats.

**The rule.** Ship the empty state on purpose. The panel names the exact categories you will report, with a dash in each and a coming-soon badge, so a visitor sees what will be counted and no fake figure. The only numbers on it are goals, labelled as goals.

**The data it needs**

- Category list: a short array of countable services.
- Two program-spend goal percentages from the approved copy: now and as the organization grows.
- No totals. The panel has no data source.

**The steps**

1. State the spend goal in one plain line under the heading.
2. Render the two percentages as stat tiles whose labels contain the word goal.
3. Below them, draw a dashed-border panel with the badge and a note: verified totals publish by category.
4. Map the category array to the same stat tile with a dash as the value.
5. When verified totals exist, replace the dashes in code and remove the badge.

**What breaks**

- A stat tile reads as an achievement by default, so every percentage label says goal.
- One blended total hides what was delivered, so each category gets its own tile.
- The panel is static markup, so nothing prompts the swap and it stays coming soon until someone edits the page.

**Not proven by the code behind this play**

- The panel is static markup with no data source. Real figures take a code edit.

- **Id:** `honest-impact`
- **Modules:** `site`, `goals`
- **Fits when you see:** impact, mission, programs, served, nonprofit
- **Internal proof (private repos, not reachable from outside):**
  - `~/dev/healing-alliance/src/app/donate/page.tsx`: coming-soon stats panel and direct-services goals

### Sponsors, researched and tracked (innovation)

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
- **Internal proof (private repos, not reachable from outside):**
  - `~/dev/bootyverse/fn/sponsors.ts`: tiers headline to grant, stages prospect to committed, no send endpoint

### Giveaways with an audit trail (innovation)

<a id="giveaway-audit"></a>Official rules drafted for approval, a recorded draw, winner claims with deadlines, and an audit PDF at the end.

**The rule.** Commit before you pick: log the hash of the seed and of the eligible list, then reveal the seed and draw. Anyone holding the export can rerun the draw and get the same winners. Rules approval is a hash of the rendered text, so any text change voids it.

**The data it needs**

- Giveaway: status, dates, winner and alternate counts, claim days, eligibility lists, rules text, approved hash.
- Entry: email, region, age confirmed, status. Unique on giveaway and lowercased email.
- Log: seq, kind, actor, payload, prev hash, hash.

**The steps**

1. Scheduling requires approved rules with no blanks. A text-changing edit returns it to draft.
2. Every read syncs status by date. The entry insert rechecks dates in SQL.
3. Screen entries with a reason each: flagged, age, region, outside dates, team email, already picked.
4. Commit sha256 of a 32-byte seed plus sha256 of the sorted eligible ids.
5. Draw by partial Fisher-Yates. Each index comes from HMAC-SHA256(seed, snapshot:counter), first 48 bits, with rejection sampling. First picks win, the rest are ordered alternates.
6. Chain each entry: sha256(prev hash + canonical JSON).
7. The PDF prints verification result, chain head, algorithm and every entry.

**What breaks**

- JSON columns reorder keys, so hash canonical JSON with sorted keys.
- A redraw commits with winner count 0 and skips earlier picks.
- Standard PDF fonts cannot draw every character, so swap them first.

**Not proven by the code behind this play**

- The cited code defines log kinds for notify, claim, forfeit and promote. The claim flow and its deadline enforcement sit outside it.
- Rules drafting sits outside the cited code. Approval by hash is in it.

- **Id:** `giveaway-audit`
- **Modules:** `programs`, `social`
- **Fits when you see:** giveaway, contest, sweepstakes, raffle, win
- **Internal proof (private repos, not reachable from outside):**
  - `~/dev/peels/lib/giveaways.ts`: draft, scheduled, live, closed, drawn, fulfilled
  - `~/dev/peels/lib/giveaway-draw-core.mjs`
  - `~/dev/peels/lib/giveaway-audit-pdf.mjs`

### One path to give

<a id="one-donate-path"></a>Every button on the site goes to one giving page with tiers, the tax status and the EIN, then out to the giving rail.

**The rule.** Use two URL constants, not one. Site-wide buttons use the internal giving page constant, and only that page uses the external checkout constant. The page does the selling before anyone leaves the site.

**The data it needs**

- Site config constants: giving page path, external checkout URL, tax ID, tax status line.
- Tier array: amount label, one line on what that level funds, optional featured flag.
- The approved disclosure line about the external checkout and its fees.

**The steps**

1. Define both URLs in one module, with a comment on who uses each.
2. Point every site-wide donate button at the internal constant.
3. On the giving page, set the hero button to checkout with the disclosure under it.
4. Map the tier array to cards. Each card button goes to checkout and takes its label from the amount.
5. Add a block with the tax status and the tax ID read from the constant, then a closing band to checkout.

**What breaks**

- A button straight to checkout skips the tiers and tax status, so a comment on the constant forbids it.
- The internal constant would just reload the giving page, so that page imports only the checkout constant.
- All tier buttons share one checkout URL with no amount parameter, so the donor picks the amount again on the rail.
- The page markup puts the disclosure under the hero button only, so add it to the cards too.

**Not proven by the code behind this play**

- The cited files hold the constants and the giving page. The buttons on other pages were not read.

- **Id:** `one-donate-path`
- **Modules:** `site`, `shop`
- **Fits when you see:** donate, give, donation, support our, 501 c 3, tax deductible
- **Internal proof (private repos, not reachable from outside):**
  - `~/dev/healing-alliance/src/lib/site.ts`: DONATE_URL, DONATE_CHECKOUT_URL, ORG_EIN
  - `~/dev/healing-alliance/src/app/donate/page.tsx`: TIERS

### One source of approved copy

<a id="approved-copy-source"></a>Copy the board approved lives in one file, and the site renders from it word for word.

**The rule.** Keep one markdown file in the repo with everything the client approved, and open it with the edit rule: reorder, split and add microcopy, never change substance or claims. Builders copy from it by hand into pages. No code reads it.

**The data it needs**

- Per-page sections: hero, body, lists, button labels, disclosures, in approved wording.
- Organization facts: name, contact, legal status, brand tokens, asset list.
- Provenance: source, capture date, later transcription dates, and flags on placeholders such as coming soon or no destination.

**The steps**

1. Capture every page of the existing site or approved draft, section by section, and date the pass.
2. Put the do-not-rewrite rule at the top, and name what is allowed: order, grouping, connective labels, alt text, meta descriptions.
3. Record gaps literally: empty cards, placeholder sections, buttons with no destination.
4. Build pages by copying strings into page code and config constants, adding only allowed microcopy.
5. Where approved text does not exist yet, as with legal pages, ship the route with a pending placeholder and invent nothing.

**What breaks**

- A first pass recorded a button but not the page behind it, so the button shipped pointing at the contact page. Capture destinations on pass one.
- Strings live twice, in the file and in page code, and nothing checks them against each other. Diff by hand before launch.
- A page can add a sentence with a real claim the file never held, as one panel note did. Treat any added claim as unapproved.

**Not proven by the code behind this play**

- The site does not render from the file. Pages hardcode their strings, copied by hand.

- **Id:** `approved-copy-source`
- **Modules:** `playbook`, `site`
- **Fits when you see:** board, mission, foundation, approved
- **Internal proof (private repos, not reachable from outside):**
  - `~/dev/healing-alliance/content/SOURCE-COPY.md`

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
- **Internal proof (private repos, not reachable from outside):**
  - `~/dev/bootyverse/fn/campaigns.ts`
  - `~/dev/bootyverse/fn/sendgrid.ts`
  - `~/dev/bootyverse/fn/audit.ts`
  - `~/dev/amc/lib/email/campaign-sender.ts` (at `origin/main`)

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
- **Internal proof (private repos, not reachable from outside):**
  - `~/dev/bootyverse/fn/goals.ts`
  - `~/dev/bootyverse/admin/engine/goals.js`

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
- **Internal proof (private repos, not reachable from outside):**
  - `~/dev/bootyverse/fn/waitlist.ts`
  - `~/dev/bootyverse/fn/ratelimit.ts`
  - `~/dev/bootyverse/fn/autoemails.ts`
  - `~/dev/bootyverse/fn/alerts.ts`

## Not proven yet

The generator must not show these as done.

- Donor records inside the app: gifts live with the giving rail today.
- Recurring gift management.
- Volunteer scheduling.

## Built from

- `~/dev/healing-alliance`: the giving page, honest impact, approved copy
- `~/dev/bootyverse`: sponsor tracking, own email, live goals
- `~/dev/peels`: giveaways with rules, draw and audit

## Signals that point here

nonprofit, non profit, 501 c 3, donate, donation, donors, foundation, charity, mission, volunteers, grant, fundraiser, tax deductible
