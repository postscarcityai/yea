# Two-sided lead marketplace

You bring in people who need a job done and sell or route each request to the firms who do it.

Machine-readable copy: `lib/yea-finale/playbooks/archetypes.ts` in the postscarcity-ai repo, id `lead-marketplace`. Back to [all playbooks](README.md).

Paths starting with `~/` are internal proof: they point into private repos, so you cannot open them from outside. Every play's recipe stands alone without them.

## Who pays and how

- The person asking is free. They get a report and a price for nothing.
- Firms list and claim for free, and pay per lead they opt into, from a prepaid balance.
- Each lead is priced at 65% of what that buyer can pay for it and still make money, with a $15 floor.
- Founding firms sort first in the directory until a cutoff date.

## The core loop

1. **Start.** The customer starts a request on the site, safety and address first. `~/dev/waterdamageiq/app/start/actions.ts`
2. **Photos and interview.** Photos in, then a short interview that adapts to what the photos show. `~/dev/waterdamageiq/lib/ai/interview.ts`
3. **Priced report.** Scope from the model, dollars from the price table, a report they can share. `~/dev/waterdamageiq/lib/pricing/price.ts`
4. **Ask for help.** They ask for help; one lead is made per trade the job needs. `~/dev/waterdamageiq/lib/marketplace/create.ts`
5. **Qualify and route.** Graded, matched to a buyer, debited and delivered with a ping. `~/dev/waterdamageiq/lib/marketplace/routing.ts`
6. **Grow the supply.** Every firm in the market is listed, invited in waves and onboarded with a five-step series. `~/dev/waterdamageiq/lib/directory-outreach.ts`

## Modules on

| Module key | Label we used | Why |
|---|---|---|
| `leads` | Leads | every homeowner request, with its report |
| `costs` | Cost per lead | spend divided by real requests, per channel |
| `pipeline` | Pipeline | firms you are working, invited to buying |
| `prospects` | All firms | the whole market, listed and scored |
| `outreach` | Outreach | claim-invite waves |
| `marketplace` | Lead buyers | buyers, balances, routing |
| `catalog` | Pricing | the price book per lead type |
| `playbook` | Flows | every automated flow, drawn and explained |
| `intake` | Start | the photo funnel |
| `portal` | Pro portal | claimed firms see their listing, leads and balance |

Core modules (Home, Inbox, People, Views, Goals, Team, Agents, Board, Log, Settings, Site, Intake, Portal) are always on as well. See `shared/modules.md`.

## Stages we actually used

- **lead route** (`leads`): pending, assigned, unrouted, closed. `~/dev/waterdamageiq/supabase/migrations/0006_leads.sql`
- **qualification** (`leads`): qualified, marginal, unqualified. `~/dev/waterdamageiq/lib/marketplace/qualify.ts`
- **firm outreach** (`outreach`): target, invited, engaged, claimed, declined. `~/dev/waterdamageiq/lib/directory-outreach.ts`
- **firm** (`pipeline`): invited, engaged, claimed, in_talks, white_label, buying, not_now. `~/dev/waterdamageiq/lib/pipeline.ts`
- **buyer** (`marketplace`): invited, active, paused, archived. `~/dev/waterdamageiq/supabase/migrations/0006_leads.sql`

## The agent's first three jobs

1. Turn every photo request into a priced report and a qualified lead, and route it to the buyer who matches.
2. Send today's claim-invite wave inside the daily cap, read replies, and stop anyone who answered or claimed.
3. Warn when a buyer's balance will run dry and catch any lead the live path did not route.

## Hero workflow: Photos in, priced lead out, routed in one step

Signed in as the customer, approved by the owner. The agent is "Intake desk". Shows the play [Photos to a priced lead](#photo-to-priced-lead).

Steps on screen: Photos in > Ask > Priced report > Lead routes itself > Owner approves > Logged with Undo.

- **Pinned:** Photo "Photo 1", Photo "Photo 2", Photo "Photo 3"
- **Ask:** "Water came through the kitchen ceiling last night. How bad is it and what will it cost?"
- **Agent works:** Read 3 photos; Asked 4 questions about the source; Priced drying and drywall from the price table; Graded it qualified: claim clears the deductible.
- **Reply:** "Category 1 water, about 120 square feet of ceiling and wall. The report and a $4,180 estimate are on the left. A local firm can be there today."
- **Approval:** "Routed to Brightwater Drying, Cedar County, $62 at 65% of their break-even. Send it?" [Change route] [Approve], then "Approved. Lead delivered and debited."
- **Log, with Undo:** Intake desk routed the request to Brightwater Drying and debited $62. Approved by the owner.

Names in the script are fictional.

## What it lets them cancel

Typeform, HubSpot Sales Hub Starter, Mailchimp, Help Scout, Zapier, Webflow. Prices and risk for each are in [shared/saas.md](../shared/saas.md).

## Rails kept

Vercel, Twilio SendGrid, Supabase (Postgres), Google Ads API, OpenRouter.

## Plays

Innovation plays first: things we built that most businesses like this do not have yet.

### Photos to a priced lead (innovation)

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
- **Internal proof (private repos, not reachable from outside):**
  - `~/dev/waterdamageiq/app/api/photos/route.ts`: private bucket, wide, closeup, floor, source shots
  - `~/dev/waterdamageiq/lib/ai/interview.ts`: the adaptive interview
  - `~/dev/waterdamageiq/lib/ai/assess.ts`: the model reads scope only, never dollars
  - `~/dev/waterdamageiq/lib/pricing/price.ts`: dollars come from a deterministic price table
  - `~/dev/waterdamageiq/app/r/[slug]/page.tsx`: the shareable report

### Price book at 65% of buyer break-even (innovation)

<a id="price-book-65"></a>Every lead is priced at 65% of what the buyer can afford to pay for it, so buyers keep making money and keep buying.

**The rule.** Derive each price from the buyer's economics instead of choosing it. Break-even is revenue per won job times win rate times marketing share of revenue. Charge 65% of that, capped by what the market already pays.

**The data it needs**

- Buyer model per row: revenue per won job, win rate, marketing share, written basis.
- Price book row: lead type, severity, tier, market ceiling.
- Per-buyer negotiated override.

**The steps**

1. Take the lower of 65% of break-even and the market ceiling, round to a quotable number, then raise it to a fixed minimum.
2. Seed the results into a schedule table. Database rows win at runtime.
3. Resolve most-specific first: override, severity plus tier, tier, severity, type default.
4. No price makes that buyer ineligible, so a lead never goes out free by accident.
5. Set the top click bid at price times click-to-sold-lead rate, then cut it for margin.

**What breaks**

- Underpricing lowers the affordable bid and prices you out of the auction. It reads as "ads do not work" when the cause is a table row.
- A generous buyer model yields an unsellable price, so the ceiling wins and an explain output flags where it binds.
- Check whether your trade allows paid referrals before you charge. A hard constant gates every money path.

**Not proven by the code behind this play**

- Charging is switched off in the build behind this play. The price book is kept as inactive code and no buyer pays these prices today.

- **Id:** `price-book-65`
- **Modules:** `marketplace`, `costs`
- **Fits when you see:** per lead, lead buyers, pay per lead, referral fee, lead generation, sell leads
- **Internal proof (private repos, not reachable from outside):**
  - `~/dev/waterdamageiq/lib/marketplace/price-book.ts`: CHARGE_SHARE = 0.65, a minimum price, market ceiling per row
  - `~/dev/waterdamageiq/lib/ads/economics.ts`: maxLeadPriceUsd: the buyer's break-even per lead
  - `~/dev/waterdamageiq/lib/marketplace/pricing.ts`: override, then schedule, then trade default; no match means no send

### Claim-invite waves (innovation)

<a id="claim-invite-waves"></a>Invite firms in small daily waves, follow up twice, stop on reply or claim, and compare waves by who opened and who claimed.

**The rule.** A wave is not a stored object. Derive it from send timestamps: a run with no gap over 45 minutes is a wave, and under 5 sends is a test. Judge waves by human signals, because pixel opens are rough.

**The data it needs**

- Company: listing state, public email, invited_at, invite_email, invite_clicked_at.
- Tracking row per firm: fixed ref, sent_at, delivery, opens, click times, bounce, spam report.
- Global suppression list: email, reason.

**The steps**

1. Derive stage: claimed, declined (hidden or suppressed), engaged (clicked), invited, else target.
2. The bulk sender dry-runs without an execute flag and takes target firms up to a daily cap (default 20) minus today's invites.
3. One invite function refuses claimed, hidden, suppressed or cross-linked addresses and creates an account with no buying criteria.
4. Each invite carries claim, tracked listing and unsubscribe links, a postal address and RFC 8058 headers.
5. Follow up after 4 days, then 6 more, on a weekday, with a fresh claim link. Stop on claim, reply, unsubscribe, bounce or spam report.
6. Rank waves by claim rate, then engaged rate, out of delivered. Chase firms that pressed claim, viewed the listing, or opened 3 times.

**What breaks**

- Mail scanners open the claim page after delivery, so only a real listing interaction or button press counts.
- A new sending domain burns fast, so the cap counts invites from every path.

**Not proven by the code behind this play**

- The stop rules appear in a code comment. The sender that enforces them sits outside the cited code.
- Follow-ups do not count toward the daily cap.

- **Id:** `claim-invite-waves`
- **Modules:** `outreach`, `prospects`
- **Fits when you see:** partners, providers, vendors, network, join our network, become a partner, for pros, list your business
- **Internal proof (private repos, not reachable from outside):**
  - `~/dev/waterdamageiq/lib/directory-outreach.ts`: inviteCompany is the only send path; stages target, invited, engaged, claimed, declined
  - `~/dev/waterdamageiq/lib/outreach-sequence.ts`: FOLLOW_UP_DAYS = [4, 6], stop reasons
  - `~/dev/waterdamageiq/scripts/outreach-send.ts`: dry run by default, daily cap
  - `~/dev/waterdamageiq/lib/invite-tracking.ts`
  - `~/dev/waterdamageiq/app/admin/directory/waves/page.tsx`

### Cost per lead, every channel

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
- **Internal proof (private repos, not reachable from outside):**
  - `~/dev/waterdamageiq/lib/costs.ts`
  - `~/dev/waterdamageiq/app/admin/costs/page.tsx`: nav label: Cost per lead
  - `~/dev/waterdamageiq/lib/api-spend.ts`: monthly caps on model and API spend
  - `~/dev/waterdamageiq/scripts/ads/sync-spend.ts`

### Qualify before you route

<a id="qualify-tiers"></a>Each request is graded qualified, marginal or unqualified with the reason, so buyers only pay for real work.

**The rule.** Grade with a fixed table, never a model, because lead quality is a pricing decision. Only arithmetic disqualifies: a known deductible at or above the top of the estimate. Every other doubt lands in marginal, which stays routable.

**The data it needs**

- Insurance answer: yes, no, unsure or null.
- Severity, top of the priced estimate, customer kind.
- Deductible: policy document first, then self-reported, null when only a percentage exists.

**The steps**

1. Grade only the lead type whose buyer earns a share of the eventual payout.
2. If deductible and estimate top are both known and the deductible reaches the top, return unqualified with that reason.
3. Collect a reason per failure: answered no insurance, severity below moderate or missing, coverage often excluded, no estimate.
4. A known deductible needs an estimate top of 2x. An unknown one needs a per-kind floor where the deductible's size stops mattering.
5. No failures returns qualified. Any failure returns marginal with all reasons.
6. Stamp the tier on the lead for buyer filters and price rows.

**What breaks**

- Customers tap no insurance when they cannot find the policy, so no is a downgrade and never an exit.
- Selling unqualified files under a permissive any filter churns buyers, so that tier reaches only buyers who opt in.
- Telling a customer the job is too small oversteps, so reasons stay operator-facing.

**Not proven by the code behind this play**

- The grade covers one lead type. Other types carry no tier.
- Buyers do not pay in the build behind this play today, so the grade filters routing, not billing.

- **Id:** `qualify-tiers`
- **Modules:** `leads`, `marketplace`
- **Fits when you see:** qualified leads, insurance, claim, deductible, pre-qualified
- **Internal proof (private repos, not reachable from outside):**
  - `~/dev/waterdamageiq/lib/marketplace/qualify.ts`: deductible headroom and claim-size floors set the tier

### Route, debit, ping

<a id="lead-routing-wallet"></a>A request splits into every trade it implies, matches a buyer, debits a prepaid balance and pings the buyer in one step.

**The rule.** Money moves only inside one database function that debits, assigns and writes the ledger in a single transaction, so a crash cannot charge a buyer without recording the lead. The ping sits outside it and can be re-sent.

**The data it needs**

- Lead: type, job id, tier, status, routed_at, outcome.
- Lead type: enabled, max_buyers (1 means exclusive).
- Buyer: status, integer-cent balance, last_assigned_at, firm id.
- Buyer criteria per type: null-means-any filter lists, price override.
- Assignment unique on lead and buyer, append-only signed ledger.

**The steps**

1. Split: map scope categories to trades through a table, collapse duplicates, always add the base type.
2. Claim: update routed_at where null. Only the caller that gets a row back continues.
3. Match criteria, drop firms already on this job unless opted in, drop buyers with no price or short balance.
4. Sort least recently assigned first and call the function per candidate up to max_buyers.
5. The function debits only if active and funded, inserts the assignment, and raises on a duplicate. Then ping with no customer details.
6. An hourly sweep routes up to 25 unclaimed pending leads older than 15 minutes.

**What breaks**

- One firm with several accounts gets billed repeatedly, so the guard keys on firm id.
- A crash after the claim leaves routed_at set, so the sweep skips it and it waits for a manual retry.
- Check whether your trade allows paid referrals. A hard constant reroutes every lead to free delivery when it does not.

**Not proven by the code behind this play**

- The debit path is coded but switched off. Requests route free in the build behind this play today.
- Splitting a request into trades is a separate function. The cited code handles one lead at a time.

- **Id:** `lead-routing-wallet`
- **Modules:** `marketplace`, `leads`, `money`
- **Fits when you see:** contractors, pros, partners, network, matched, connect you, near you, referral network
- **Internal proof (private repos, not reachable from outside):**
  - `~/dev/waterdamageiq/lib/marketplace/derive.ts`: one lead per trade the job implies
  - `~/dev/waterdamageiq/lib/marketplace/routing.ts`: match, round robin, debit and assign, ping
  - `~/dev/waterdamageiq/supabase/migrations/0006_leads.sql`: ledger, debit_and_assign, post_ledger_entry
  - `~/dev/waterdamageiq/app/api/cron/route-leads/route.ts`: hourly catch for anything the live path missed

### A directory every firm can claim

<a id="claimed-directory"></a>Every firm in the market gets a listing; claimed ones are indexed and sort first, unclaimed ones invite a claim.

**The rule.** Publishing and indexing are separate decisions. Every published listing renders, but only a claim earns search indexing, followed links and full colour. Search visibility is the reason to claim.

**The data it needs**

- Company: unique slug, region, listing state (draft, listed, claimed, hidden), claimed_at, contact fields, licence number.
- Separate account table for logins and balances, never joined into a public query.
- Hashed claim token, 7 days, reusable until claimed.

**The steps**

1. Assemble listings from public sources as draft. Draft and hidden stay off every public surface.
2. Render listed pages with a grey logo, nofollow links and noindex robots.
3. Index pages sort founding, then claimed, then unclaimed, alphabetical inside each tier.
4. Compute founding from the claim date against a fixed cutoff, so nobody can grant or buy it.
5. The claim link's GET only renders. The button's POST records a human click, signs the firm in and opens its profile.
6. A claimed page gets index robots, followed links, a badge and a sitemap entry.

**What breaks**

- Thin pages at scale risk a penalty on the whole domain, so noindex holds until claim and the sitemap lists claimed only.
- Mail scanners open links after delivery, so a GET never signs anyone in.

**Not proven by the code behind this play**

- The claim token flow is reached from an emailed invite. An unclaimed page offers a contact link, not a self-serve claim.
- The write that flips a listing to claimed sits outside the cited code.

- **Id:** `claimed-directory`
- **Modules:** `prospects`, `site`, `portal`
- **Fits when you see:** directory, find a, listing, claim your, near you, top rated
- **Internal proof (private repos, not reachable from outside):**
  - `~/dev/waterdamageiq/lib/directory.ts`: listing states, founding sort
  - `~/dev/waterdamageiq/app/directory/[state]/[company]/page.tsx`
  - `~/dev/waterdamageiq/app/portal/claim/[token]/page.tsx`

### Five-step series after the claim

<a id="firm-email-series"></a>A firm that claims gets five emails over three weeks: welcome, expert invite, a sample lead, the white-label offer, a page check.

**The rule.** One pure planner decides every step from facts about the firm, so the cron and the admin preview agree. Skip a step when the firm already did what it asks, and never send a step late.

**The data it needs**

- Firm: claimed_at, listing state, profile fields, invite email.
- Send log unique on company and step.
- Facts: expert answers submitted, white-label requested or live, address suppressed.
- A growth flag that gates real sending.

**The steps**

1. A daily job loads firms claimed in the last 29 days and counts calendar days in one timezone.
2. Steps sit at days 0, 2, 7, 14, 21: welcome, expert invite, sample lead, white-label offer, page check.
3. Give each step a verdict: sent, skip, not_yet, stale (over 6 days past its day) or due.
4. Send only the first due step, none within 36 hours of the last, capped at 50 per run.
5. With the flag off, return the would-send list and send nothing.
6. With the flag on, insert the log row first, so a duplicate is a no-op. Then send with a fresh unsubscribe token.

**What breaks**

- A downed job would send a welcome a month late, so stale steps never go out.
- A crash mid-send could double-mail, so the row stays and the step is never retried.
- A step can outlive its offer. The planner holds the skip, so one rule retires it everywhere.

**Not proven by the code behind this play**

- Four emails at most: the sample lead step is retired and always skips.
- The job is written but not on a schedule, and it sends nothing until the growth flag is on.

- **Id:** `firm-email-series`
- **Modules:** `campaigns`, `outreach`
- **Fits when you see:** partners, onboarding, providers, members
- **Internal proof (private repos, not reachable from outside):**
  - `~/dev/waterdamageiq/lib/email/firm-series.ts`: days 0, 2, 7, 14, 21; behind a growth flag
  - `~/dev/waterdamageiq/app/api/cron/firm-series/route.ts`

### Nobody falls out of the funnel

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
- **Internal proof (private repos, not reachable from outside):**
  - `~/dev/waterdamageiq/app/api/cron/abandoned/route.ts`: stalled 2 to 48 hours ago
  - `~/dev/waterdamageiq/app/api/cron/insurance-followup/route.ts`
  - `~/dev/waterdamageiq/app/api/cron/lead-followup/route.ts`: 3 to 14 days after the report

### Your own photo estimator

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
- **Internal proof (private repos, not reachable from outside):**
  - `~/dev/waterdamageiq/app/e/[slug]/page.tsx`
  - `~/dev/waterdamageiq/lib/white-label.ts`
  - `~/dev/waterdamageiq/lib/white-label-offer.ts`
  - `~/dev/waterdamageiq/lib/pricing/price.ts`

### Who is running ads

<a id="competitor-ad-intel"></a>Scan every competitor's site tags and public ad libraries, and see who is spending where.

**The rule.** Judge ads per business, not per domain or phrase. A franchise domain shows every office's ads and keyword search finds namesakes, so those hits count only when they match the listing's name or domain. Keep raw evidence so a flag can be re-derived without rescanning.

**The data it needs**

- Businesses: name, website, trade categories.
- Private intel table, apart from public columns: per-source scanned-at, tools by category, lead channels, ad-active flags, raw results.

**The steps**

1. Skip sources already scanned, so an interrupted run resumes. A refresh flag overrides.
2. Site: fetch the homepage with a 12-second timeout and run per-tool regexes for pixels, call tracking, chat, forms, booking, reviews.
3. Public ads transparency library: search by domain, one worker, 1.5 seconds apart. Active means shown in the last 30 days.
4. Public social ad library: search the short name in a headless browser, 3 workers, and match each ad card.
5. Report active rates per trade, tool tallies, payers on more than one listing, and a CSV with active rows first.

**What breaks**

- More than 5 payers on one domain means a franchise: only a name-matched advertiser counts.
- A website on a social or directory domain returns someone else's ads. A denylist marks it never active.
- The library rate-limits. Back off from 5 seconds, doubling over 5 tries, and leave failures unstamped so they retry.
- A rule change would force a rescan. Rescope mode re-applies the decision to stored results with no network.

**Not proven by the code behind this play**

- No spend figures exist. The scan records active flags, creative counts, last-shown dates and sample ad text.
- It scans listed firms from your own directory, not a whole market.

- **Id:** `competitor-ad-intel`
- **Modules:** `prospects`, `insights`
- **Fits when you see:** competitors, market, ads, compete
- **Internal proof (private repos, not reachable from outside):**
  - `~/dev/waterdamageiq/scripts/intel-scan.ts`: site tags, Google Ads Transparency, Meta Ad Library
  - `~/dev/waterdamageiq/scripts/intel-report.ts`
  - `~/dev/waterdamageiq/supabase/migrations/0024_directory_intel.sql`

### Licence check on every firm

<a id="licence-check"></a>Match each firm to its state licence record and flag the ones that do not match.

**The rule.** A wrong licence on a listing is worse than none, so an uncertain match goes to a human queue and is never attached automatically. The verified mark keys off a date that only a current and active licence can set.

**The data it needs**

- The state's free public licence file, imported weekly.
- On each firm: licence type, status label, last-checked, last-verified (null means not verified).
- Review queue: source record, firm, reason, status (open, attached, rejected), unique per pair.
- Licence-type table: label, trade, whether an unmatched business becomes a prospect.

**The steps**

1. Normalise numbers: strip punctuation, uppercase, drop zeros after the prefix, so ABC000123 and ABC 123 match.
2. Reduce names to distinctive words: 3 letters or more, minus a stoplist of trade and place words.
3. Status: expiry first, then codes. Current plus active counts as active, as does current with a blank secondary on firm licences. Report other codes raw.
4. Stamp last-checked on every lookup, last-verified only when active.
5. Queue doubts with a reason: number_name_differs, number_prefix_differs, name_city_only, licence_conflict.

**What breaks**

- A name of only generic words identifies nobody, so an exact-name match on it is never confident.
- Resolving a review links the source record or marks it rejected, and the next run reads that decision, so it never asks twice.
- A record past its expiry reads Expired, whatever the status code says.
- Unmatched businesses become prospect rows: never public, never invited to claim.

**Not proven by the code behind this play**

- One state's register. The matcher itself sits outside the cited code, so match behaviour here comes from its helpers and schema.

- **Id:** `licence-check`
- **Modules:** `prospects`
- **Fits when you see:** licensed, licence, license, certified, insured
- **Internal proof (private repos, not reachable from outside):**
  - `~/dev/waterdamageiq/lib/dbpr.ts`
  - `~/dev/waterdamageiq/supabase/migrations/0028_licences.sql`

### One-click unsubscribe and takedown

<a id="unsub-takedown"></a>Every outbound email carries one-click unsubscribe, and any listed firm can remove itself in one click.

**The rule.** Mint an opaque token per send and resolve it to an address, so a click needs no login and no crypto. The button and the RFC 8058 POST call one function so they cannot drift. Suppress the person, not the record, and hide a listing rather than delete it.

**The data it needs**

- Tokens: token, email, purpose, used-at.
- Suppressions: lowercase email as primary key, reason.
- Listings and their people: invite email, state.

**The steps**

1. At send, insert a token row with purpose unsub and link it in the email.
2. The button and the one-click POST look up the token, upsert the address into suppressions, and stamp used-at.
3. Check suppressions in a batch query before a send.
4. Takedown suppresses first, then finds unclaimed listings (draft, listed, hidden) whose invite email equals the address.
5. Set those listings and their people to hidden, then clear the directory cache.
6. Importers skip hidden rows, so the page stays down.

**What breaks**

- A repeat click hits the upsert, so it is a no-op.
- This build's other nudges carry no token and skip the check. To honour every email, gate all sends in one function.
- A claimed listing is its owner's to manage in a portal, so the state filter leaves it out.
- The takedown update has no error check and the redirect always says removed. Check the result if you copy this.

**Not proven by the code behind this play**

- Not every email: in the cited crons only one follow-up mints a token, and two others neither mint one nor check suppressions.
- Takedown works for the holder of a token whose address matches an unclaimed listing, not for any firm.

- **Id:** `unsub-takedown`
- **Modules:** `outreach`, `campaigns`, `settings`
- **Fits when you see:** outreach, cold email, newsletter, email list
- **Internal proof (private repos, not reachable from outside):**
  - `~/dev/waterdamageiq/lib/unsubscribe.ts`: RFC 8058 one-click
  - `~/dev/waterdamageiq/app/unsubscribe/[token]/actions.ts`: takeDownListing hides the listing
  - `~/dev/waterdamageiq/supabase/migrations/0019_followup.sql`: email_suppressions

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
- **Internal proof (private repos, not reachable from outside):**
  - `~/dev/waterdamageiq/app/api/inbound-email/route.ts`: inbound parse webhook
  - `~/dev/waterdamageiq/lib/mail.ts`
  - `~/dev/waterdamageiq/app/admin/inbox/page.tsx`

### Sequences the agent drafts, a person sends

<a id="drafted-sequences"></a>Every step of a sequence is drafted for that account; it waits for a person to press Send unless auto-send is on, and stops on a reply.

**The rule.** Advancing a sequence only creates a task, and an email task carries a finished draft. The model rewrites a merged template, and a reply that fails the checks leaves the template in place. One open task per enrollment holds the next step back.

**The data it needs**

- Sequence: auto_send off by default. Step: position, kind, wait days, subject, body.
- Enrollment: account, owner, status, step position, next due, started at. One active per company.
- Task: position, recipients, draft, status, sending_at, unique on enrollment and position.

**The steps**

1. Hourly and after each task, find active enrollments that are due with no open task.
2. Stop on a reply or application since the start, any order, a closed stage or do-not-contact.
3. For email steps, ask the model for the same ask, same length or shorter, one or two facts, nothing invented. Other kinds queue a task with a note.
4. Finishing a task sets next due to now plus the next wait: 0, 3, 4, 7, 7 days.
5. With auto_send on, send on weekdays from 9 to 17 in the recipient's time zone, under 25 per owner per day, after re-checking stop rules.

**What breaks**

- Two runs could send twice. Each send claims sending_at with a 10 minute timeout.
- A failed send clears the claim, logs a note and waits for a person.
- A reply during an open draft is not caught, because advance skips enrollments with an open task. Only auto-send re-checks.

**Not proven by the code behind this play**

- Only email steps get a draft. Other kinds queue a task with a note.
- A reply during an open draft does not stop the sequence.
- Live auto-send is hard-coded off. Auto-send runs in test mode only.

- **Id:** `drafted-sequences`
- **Modules:** `outreach`
- **Fits when you see:** outreach, follow up, sales, prospects, b2b
- **Internal proof (private repos, not reachable from outside):**
  - `~/dev/peels/lib/sequences.ts`
  - `~/dev/peels/db/082_sequence_auto_send.sql`
  - `~/dev/peels/app/api/cron/outreach/route.ts`
  - `~/dev/waterdamageiq/lib/outreach-sequence.ts`

## Not proven yet

The generator must not show these as done.

- Card checkout for buyer deposits: deposits are recorded by hand today.
- A founding first look at requests is promised, not yet a routing rule.

## Built from

- `~/dev/waterdamageiq`: the whole marketplace: funnel, pricing, routing, directory, outreach

## Signals that point here

marketplace, lead generation, per lead, lead buyers, directory, contractors, pros, homeowner, homeowners, matched with, connect you, referral network, find a pro, near you, list your business
