# Two-sided lead marketplace

You bring in people who need a job done and sell or route each request to the firms who do it.

Machine-readable copy: `lib/yea-finale/playbooks/archetypes.ts` in the postscarcity-ai repo, id `lead-marketplace`. Back to [all playbooks](README.md).

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

- **Id:** `photo-to-priced-lead`
- **Modules:** `intake`, `leads`, `site`
- **Fits when you see:** photos, estimate, quote, free quote, damage, repair, inspection, assessment, how much
- **Proved in:**
  - `~/dev/waterdamageiq/app/api/photos/route.ts`: private bucket, wide, closeup, floor, source shots
  - `~/dev/waterdamageiq/lib/ai/interview.ts`: the adaptive interview
  - `~/dev/waterdamageiq/lib/ai/assess.ts`: the model reads scope only, never dollars
  - `~/dev/waterdamageiq/lib/pricing/price.ts`: dollars come from a deterministic price table
  - `~/dev/waterdamageiq/app/r/[slug]/page.tsx`: the shareable report

### Price book at 65% of buyer break-even (innovation)

<a id="price-book-65"></a>Every lead is priced at 65% of what the buyer can afford to pay for it, so buyers keep making money and keep buying.

- **Id:** `price-book-65`
- **Modules:** `marketplace`, `costs`
- **Fits when you see:** per lead, lead buyers, pay per lead, referral fee, lead generation, sell leads
- **Proved in:**
  - `~/dev/waterdamageiq/lib/marketplace/price-book.ts`: CHARGE_SHARE = 0.65, MIN_PRICE_USD = 15, market ceiling per row
  - `~/dev/waterdamageiq/lib/ads/economics.ts`: maxLeadPriceUsd: the buyer's break-even per lead
  - `~/dev/waterdamageiq/lib/marketplace/pricing.ts`: override, then schedule, then trade default; no match means no send

### Claim-invite waves (innovation)

<a id="claim-invite-waves"></a>Invite firms in small daily waves, follow up twice, stop on reply or claim, and compare waves by who opened and who claimed.

- **Id:** `claim-invite-waves`
- **Modules:** `outreach`, `prospects`
- **Fits when you see:** partners, providers, vendors, network, join our network, become a partner, for pros, list your business
- **Proved in:**
  - `~/dev/waterdamageiq/lib/directory-outreach.ts`: inviteCompany is the only send path; stages target, invited, engaged, claimed, declined
  - `~/dev/waterdamageiq/lib/outreach-sequence.ts`: FOLLOW_UP_DAYS = [4, 6], stop reasons
  - `~/dev/waterdamageiq/scripts/outreach-send.ts`: dry run by default, daily cap
  - `~/dev/waterdamageiq/lib/invite-tracking.ts`
  - `~/dev/waterdamageiq/app/admin/directory/waves/page.tsx`

### Cost per lead, every channel

<a id="cost-per-lead"></a>Ad spend and tool spend divided by real leads, per channel, so you know what a customer costs before you scale it.

- **Id:** `cost-per-lead`
- **Modules:** `costs`, `insights`
- **Fits when you see:** google ads, advertising, ads, marketing spend, cost per, paid search, facebook ads
- **Proved in:**
  - `~/dev/waterdamageiq/lib/costs.ts`
  - `~/dev/waterdamageiq/app/admin/costs/page.tsx`: nav label: Cost per lead
  - `~/dev/waterdamageiq/lib/api-spend.ts`: monthly caps on model and API spend
  - `~/dev/waterdamageiq/scripts/ads/sync-spend.ts`

### Qualify before you route

<a id="qualify-tiers"></a>Each request is graded qualified, marginal or unqualified with the reason, so buyers only pay for real work.

- **Id:** `qualify-tiers`
- **Modules:** `leads`, `marketplace`
- **Fits when you see:** qualified leads, insurance, claim, deductible, pre-qualified
- **Proved in:**
  - `~/dev/waterdamageiq/lib/marketplace/qualify.ts`: deductible headroom and claim-size floors set the tier

### Route, debit, ping

<a id="lead-routing-wallet"></a>A request splits into every trade it implies, matches a buyer, debits a prepaid balance and pings the buyer in one step.

- **Id:** `lead-routing-wallet`
- **Modules:** `marketplace`, `leads`, `money`
- **Fits when you see:** contractors, pros, partners, network, matched, connect you, near you, referral network
- **Proved in:**
  - `~/dev/waterdamageiq/lib/marketplace/derive.ts`: one lead per trade the job implies
  - `~/dev/waterdamageiq/lib/marketplace/routing.ts`: match, round robin, debit and assign, ping
  - `~/dev/waterdamageiq/supabase/migrations/0006_leads.sql`: ledger, debit_and_assign, post_ledger_entry
  - `~/dev/waterdamageiq/app/api/cron/route-leads/route.ts`: hourly catch for anything the live path missed

### A directory every firm can claim

<a id="claimed-directory"></a>Every firm in the market gets a listing; claimed ones are indexed and sort first, unclaimed ones invite a claim.

- **Id:** `claimed-directory`
- **Modules:** `prospects`, `site`, `portal`
- **Fits when you see:** directory, find a, listing, claim your, near you, top rated
- **Proved in:**
  - `~/dev/waterdamageiq/lib/directory.ts`: listing states, founding sort
  - `~/dev/waterdamageiq/app/directory/[state]/[company]/page.tsx`
  - `~/dev/waterdamageiq/app/portal/claim/[token]/page.tsx`

### Five-step series after the claim

<a id="firm-email-series"></a>A firm that claims gets five emails over three weeks: welcome, expert invite, a sample lead, the white-label offer, a page check.

- **Id:** `firm-email-series`
- **Modules:** `campaigns`, `outreach`
- **Fits when you see:** partners, onboarding, providers, members
- **Proved in:**
  - `~/dev/waterdamageiq/lib/email/firm-series.ts`: days 0, 2, 7, 14, 21; behind a growth flag
  - `~/dev/waterdamageiq/app/api/cron/firm-series/route.ts`

### Nobody falls out of the funnel

<a id="funnel-followups"></a>Half-finished requests get one resume email, and reports with no ask get one follow-up, on a clock, never twice.

- **Id:** `funnel-followups`
- **Modules:** `intake`, `campaigns`, `leads`
- **Fits when you see:** get started, free quote, request, book, schedule, estimate
- **Proved in:**
  - `~/dev/waterdamageiq/app/api/cron/abandoned/route.ts`: stalled 2 to 48 hours ago
  - `~/dev/waterdamageiq/app/api/cron/insurance-followup/route.ts`
  - `~/dev/waterdamageiq/app/api/cron/lead-followup/route.ts`: 3 to 14 days after the report

### Your own photo estimator

<a id="white-label-photo-estimator"></a>The photo-to-report estimator on your own brand and URL, so every visitor leaves with a price and you get the lead.

- **Id:** `white-label-photo-estimator`
- **Modules:** `intake`, `site`, `leads`
- **Fits when you see:** estimate, free estimate, quote, inspection, service area, restoration, repair, install
- **Proved in:**
  - `~/dev/waterdamageiq/app/e/[slug]/page.tsx`
  - `~/dev/waterdamageiq/lib/white-label.ts`
  - `~/dev/waterdamageiq/lib/white-label-offer.ts`
  - `~/dev/waterdamageiq/lib/pricing/price.ts`

### Who is running ads

<a id="competitor-ad-intel"></a>Scan every competitor's site tags and public ad libraries, and see who is spending where.

- **Id:** `competitor-ad-intel`
- **Modules:** `prospects`, `insights`
- **Fits when you see:** competitors, market, ads, compete
- **Proved in:**
  - `~/dev/waterdamageiq/scripts/intel-scan.ts`: site tags, Google Ads Transparency, Meta Ad Library
  - `~/dev/waterdamageiq/scripts/intel-report.ts`
  - `~/dev/waterdamageiq/supabase/migrations/0024_directory_intel.sql`

### Licence check on every firm

<a id="licence-check"></a>Match each firm to its state licence record and flag the ones that do not match.

- **Id:** `licence-check`
- **Modules:** `prospects`
- **Fits when you see:** licensed, licence, license, certified, insured
- **Proved in:**
  - `~/dev/waterdamageiq/lib/dbpr.ts`
  - `~/dev/waterdamageiq/supabase/migrations/0028_licences.sql`

### One-click unsubscribe and takedown

<a id="unsub-takedown"></a>Every outbound email carries one-click unsubscribe, and any listed firm can remove itself in one click.

- **Id:** `unsub-takedown`
- **Modules:** `outreach`, `campaigns`, `settings`
- **Fits when you see:** outreach, cold email, newsletter, email list
- **Proved in:**
  - `~/dev/waterdamageiq/lib/unsubscribe.ts`: RFC 8058 one-click
  - `~/dev/waterdamageiq/app/unsubscribe/[token]/actions.ts`: takeDownListing hides the listing
  - `~/dev/waterdamageiq/supabase/migrations/0019_followup.sql`: email_suppressions

### Every inbox in one place

<a id="inbound-parse-inbox"></a>Mail to any address on your domain lands in the app's inbox, threaded, with the agent's draft reply.

- **Id:** `inbound-parse-inbox`
- **Modules:** `inbox`
- **Fits when you see:** email us, contact us, support, info@
- **Proved in:**
  - `~/dev/waterdamageiq/app/api/inbound-email/route.ts`: inbound parse webhook
  - `~/dev/waterdamageiq/lib/mail.ts`
  - `~/dev/waterdamageiq/app/admin/inbox/page.tsx`

### Sequences the agent drafts, a person sends

<a id="drafted-sequences"></a>Every step of a sequence is drafted for that account; it waits for a person to press Send unless auto-send is on, and stops on a reply.

- **Id:** `drafted-sequences`
- **Modules:** `outreach`
- **Fits when you see:** outreach, follow up, sales, prospects, b2b
- **Proved in:**
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
