# Field service: estimates and jobs

You go to the customer's place, look at the problem, quote it and do the work.

Machine-readable copy: `lib/yea-finale/playbooks/archetypes.ts` in the postscarcity-ai repo, id `field-service`. Back to [all playbooks](README.md).

## Who pays and how

- The customer pays per job, from an estimate.
- The estimate comes from a price table, not a guess, so every quote is the same for the same work.
- The estimator itself can run on the firm's own brand, which is how the marketplace sells it.

## The core loop

1. **Request.** The customer starts on your site and sends photos. `~/dev/waterdamageiq/app/e/[slug]/page.tsx`
2. **Estimate.** The photos are read for scope and priced from your table. `~/dev/waterdamageiq/lib/ai/assess.ts`
3. **Follow up.** Half-finished requests and quiet reports get one nudge each. `~/dev/waterdamageiq/app/api/cron/abandoned/route.ts`
4. **Job file.** The won estimate becomes a job with stages, tasks and dates. `~/dev/amc/supabase/migrations/0100_docket_core.sql` (at `origin/main`)
5. **Due today.** A daily digest says what is due and what is late. `~/dev/amc/app/api/cron/matter-reminders/route.ts` (at `origin/main`)

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

- **request** (`leads`): new, contacted, connected, closed. `~/dev/waterdamageiq/supabase/migrations/0001_init.sql`
- **severity** (`leads`): minor, moderate, major, high_risk. `~/dev/waterdamageiq/supabase/migrations/0001_init.sql`
- **job task** (`jobs`): open, in_progress, done, canceled. `~/dev/amc/supabase/migrations/0100_docket_core.sql` (at `origin/main`)

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

- **Id:** `white-label-photo-estimator`
- **Modules:** `intake`, `site`, `leads`
- **Fits when you see:** estimate, free estimate, quote, inspection, service area, restoration, repair, install
- **Proved in:**
  - `~/dev/waterdamageiq/app/e/[slug]/page.tsx`
  - `~/dev/waterdamageiq/lib/white-label.ts`
  - `~/dev/waterdamageiq/lib/white-label-offer.ts`
  - `~/dev/waterdamageiq/lib/pricing/price.ts`

### Nobody falls out of the funnel (innovation)

<a id="funnel-followups"></a>Half-finished requests get one resume email, and reports with no ask get one follow-up, on a clock, never twice.

- **Id:** `funnel-followups`
- **Modules:** `intake`, `campaigns`, `leads`
- **Fits when you see:** get started, free quote, request, book, schedule, estimate
- **Proved in:**
  - `~/dev/waterdamageiq/app/api/cron/abandoned/route.ts`: stalled 2 to 48 hours ago
  - `~/dev/waterdamageiq/app/api/cron/insurance-followup/route.ts`
  - `~/dev/waterdamageiq/app/api/cron/lead-followup/route.ts`: 3 to 14 days after the report

### Cost per lead, every channel (innovation)

<a id="cost-per-lead"></a>Ad spend and tool spend divided by real leads, per channel, so you know what a customer costs before you scale it.

- **Id:** `cost-per-lead`
- **Modules:** `costs`, `insights`
- **Fits when you see:** google ads, advertising, ads, marketing spend, cost per, paid search, facebook ads
- **Proved in:**
  - `~/dev/waterdamageiq/lib/costs.ts`
  - `~/dev/waterdamageiq/app/admin/costs/page.tsx`: nav label: Cost per lead
  - `~/dev/waterdamageiq/lib/api-spend.ts`: monthly caps on model and API spend
  - `~/dev/waterdamageiq/scripts/ads/sync-spend.ts`

### Photos to a priced lead

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

### One file per job, with a reminder digest

<a id="job-file-deadline-digest"></a>A won lead becomes a job file with stages, tasks and dates, and a daily digest says what is due.

- **Id:** `job-file-deadline-digest`
- **Modules:** `jobs`, `board`
- **Fits when you see:** cases, matters, projects, engagements, jobs, clients
- **Proved in:**
  - `~/dev/amc/supabase/migrations/0100_docket_core.sql` (at `origin/main`): matter stages, statuses, tasks
  - `~/dev/amc/supabase/migrations/0102_convert_lead_to_matter.sql` (at `origin/main`)
  - `~/dev/amc/app/api/cron/matter-reminders/route.ts` (at `origin/main`)

### A business profile post every day

<a id="gbp-daily-post"></a>The agent drafts and posts to the Google business profile on a schedule, from what the business already published.

- **Id:** `gbp-daily-post`
- **Modules:** `social`, `reviews`
- **Fits when you see:** google reviews, local, near me, service area, locations, office
- **Proved in:**
  - `~/dev/amc/scripts/post-gbp-update.mjs` (at `origin/main`)
  - `~/dev/amc/scripts/gbp-pending.mjs` (at `origin/main`)
  - `~/dev/amc/docs/google-business-profile-automation.md` (at `origin/main`)

### Every inbox in one place

<a id="inbound-parse-inbox"></a>Mail to any address on your domain lands in the app's inbox, threaded, with the agent's draft reply.

- **Id:** `inbound-parse-inbox`
- **Modules:** `inbox`
- **Fits when you see:** email us, contact us, support, info@
- **Proved in:**
  - `~/dev/waterdamageiq/app/api/inbound-email/route.ts`: inbound parse webhook
  - `~/dev/waterdamageiq/lib/mail.ts`
  - `~/dev/waterdamageiq/app/admin/inbox/page.tsx`

### Every agent edit, logged with Undo

<a id="agent-change-log"></a>The agent edits records from chat, and every change lands in a log a person can undo.

- **Id:** `agent-change-log`
- **Modules:** `agents`, `log`
- **Fits when you see:** team, office, staff, admin
- **Proved in:**
  - `~/dev/dili/apps/worker/src/chat/changes.ts`
  - `~/dev/dili/apps/worker/src/chat/tools/edit.ts`
  - `~/dev/peels/lib/agent/tools.ts`

## Not proven yet

The generator must not show these as done.

- Dispatch and crew scheduling: Bookings is not yet proven in any build.
- Taking payment on the job: Money is not yet proven end to end.
- Texting customers: no build sends SMS yet.

## Built from

- `~/dev/waterdamageiq`: the photo estimator, price table, follow-up crons and white-label estimator
- `~/dev/amc`: job files with stages and a daily reminder digest

## Signals that point here

repair, repairs, install, installation, service call, estimate, estimates, free estimate, technician, crew, plumbing, hvac, roofing, restoration, mitigation, cleaning, landscaping, pest, electrical, service area
