# Professional practice, intake first

Clients come to you with a problem, you decide fast whether to take it, and the work runs on deadlines and documents.

Machine-readable copy: `lib/yea-finale/playbooks/archetypes.ts` in the postscarcity-ai repo, id `professional-practice`. Back to [all playbooks](README.md).

## Who pays and how

- Clients pay the practice directly under a signed agreement, by whatever method the practice takes.
- New clients come from paid search, organic search and referrals; spend is judged by who signs, not by who fills a form.

## The core loop

1. **Intake.** A spam-proof consult form that keeps the ad click. `~/dev/amc/app/api/consultation/create/route.ts` (at `origin/main`)
2. **Alert.** The team gets the inquiry in seconds, deadline first. `~/dev/amc/lib/email.ts` (at `origin/main`)
3. **Consult.** The inquiry moves through contacted and qualified to retained or closed. `~/dev/amc/app/admin/leads/actions.ts` (at `origin/main`)
4. **Agreement.** The client asks for the agreement and it is tracked to signed. `~/dev/amc/app/api/agreement-request/route.ts` (at `origin/main`)
5. **Job file.** The retained client becomes a file with stages, tasks and dates. `~/dev/amc/supabase/migrations/0102_convert_lead_to_matter.sql` (at `origin/main`)
6. **Read back.** Every source read against who signed. `~/dev/amc/lib/leads/insights.ts` (at `origin/main`)

## Modules on

| Module key | Label we used | Why |
|---|---|---|
| `leads` | Leads | every inquiry, deadline first |
| `insights` | Insights | source against outcome |
| `jobs` | Matters | one file per client matter |
| `documents` | Agreements | agreement requests to signed |
| `content` | Blog | posts published without a CMS |
| `search` | SEO | rankings, keywords, audits |
| `costs` | Ads | paid search spend and results |
| `social` | Social | videos and posts for review |

Core modules (Home, Inbox, People, Views, Goals, Team, Agents, Board, Log, Settings, Site, Intake, Portal) are always on as well. See `shared/modules.md`.

## Stages we actually used

- **lead** (`leads`): new, contacted, qualified, retained, closed. `~/dev/amc/lib/admin/types.ts` (at `origin/main`)
- **agreement request** (`documents`): pending, contacted, agreement_sent, signed, declined. `~/dev/amc/lib/admin/types.ts` (at `origin/main`)
- **matter status** (`jobs`): open, on_hold, closed, declined. `~/dev/amc/supabase/migrations/0100_docket_core.sql` (at `origin/main`)
- **video** (`social`): draft, in_review, changes_requested, approved, posted. `~/dev/amc/supabase/migrations/0114_social.sql` (at `origin/main`)
- **claim check** (`documents`): confirmed, contradicted, partial, unverifiable, ambiguous, pending. `~/dev/dili/supabase/migrations/0001_init.sql`

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
- **Reply:** "The estate planning campaign brought 18 inquiries and 7 signed, at $310 a client. The general campaign brought 64 inquiries and 3 signed, at $2,140 a client. Moving $1,500 a month from general to estate planning should add about 4 clients."
- **Approval:** "Move $1,500 a month from General to Estate planning starting Monday?" [Not yet] [Approve], then "Approved. Budget change queued for Monday."
- **Log, with Undo:** Front desk queued a $1,500 budget move to Estate planning. Approved by Helen Vance.

Names in the script are fictional.

## What it lets them cancel

HubSpot Sales Hub Starter, Mailchimp, Typeform, WordPress.com, Hootsuite, Calendly. Prices and risk for each are in [shared/saas.md](../shared/saas.md).

## Rails kept

Vercel, Twilio SendGrid, Supabase (Postgres), Google Ads API, Search Console API, Meeting recorder API, Social posting API.

## Plays

Innovation plays first: things we built that most businesses like this do not have yet.

### Which source brings clients who sign (innovation)

<a id="source-outcome-insights"></a>Every lead's source read against its outcome, down to the ad campaign, so spend follows retained clients, not form fills.

- **Id:** `source-outcome-insights`
- **Modules:** `insights`, `leads`, `costs`
- **Fits when you see:** google ads, clients, consultation, retained, marketing
- **Proved in:**
  - `~/dev/amc/lib/leads/insights.ts` (at `origin/main`): sources by outcomes, computed at read time
  - `~/dev/amc/lib/ads/click-lookup.ts` (at `origin/main`): click id to campaign
  - `~/dev/amc/app/admin/insights/page.tsx` (at `origin/main`)

### Claims checked live on the call (innovation)

<a id="live-claim-check"></a>During a meeting the agent checks what is said against the documents on file and flags what does not match.

- **Id:** `live-claim-check`
- **Modules:** `jobs`, `documents`
- **Fits when you see:** diligence, due diligence, investors, advisory, audit, review, meetings
- **Proved in:**
  - `~/dev/dili/apps/worker/src/live/pipeline.ts`: triage then verification against the brief
  - `~/dev/dili/apps/worker/src/live/brief.ts`
  - `~/dev/dili/apps/worker/src/jobs/post-call.ts`: the post-call report

### Search ranks without the subscription (innovation)

<a id="seo-in-house"></a>Rankings, keywords, competitors, links, site audit and index checks in your own app, refreshed on a schedule.

- **Id:** `seo-in-house`
- **Modules:** `insights`, `site`
- **Fits when you see:** seo, rankings, google, search, blog
- **Proved in:**
  - `~/dev/amc/lib/seo/rank-tracker.ts` (at `origin/main`)
  - `~/dev/amc/app/admin/seo/layout.tsx` (at `origin/main`): Overview, Rankings, Keywords, Competitors, Links, Site Audit, Pages, Indexing, AI Crawlers
  - `~/dev/amc/app/api/cron/seo-ranks/route.ts` (at `origin/main`)

### Intake that remembers the click

<a id="intake-with-click-ids"></a>A spam-proof consult form that keeps the ad click id for 90 days, logs phone and chat taps, and alerts the team in seconds.

- **Id:** `intake-with-click-ids`
- **Modules:** `intake`, `leads`, `insights`
- **Fits when you see:** free consultation, consultation, call now, schedule a call, case review, contact us
- **Proved in:**
  - `~/dev/amc/app/api/consultation/create/route.ts` (at `origin/main`): honeypot, Turnstile, click id fallback
  - `~/dev/amc/middleware.ts` (at `origin/main`): 90-day click cookie
  - `~/dev/amc/app/api/track-contact/route.ts` (at `origin/main`): phone and WhatsApp taps
  - `~/dev/amc/lib/email.ts` (at `origin/main`): new lead and completed form alerts

### Deadlines decide the queue

<a id="deadline-urgency"></a>Each inquiry carries its next deadline, and anything inside seven days turns red at the top of the queue.

- **Id:** `deadline-urgency`
- **Modules:** `leads`
- **Fits when you see:** deadline, court, urgent, arrested, filing, time sensitive
- **Proved in:**
  - `~/dev/amc/supabase/migrations/0101_leads_inbox.sql` (at `origin/main`): urgency_level, next_deadline

### One file per job, with a reminder digest

<a id="job-file-deadline-digest"></a>A won lead becomes a job file with stages, tasks and dates, and a daily digest says what is due.

- **Id:** `job-file-deadline-digest`
- **Modules:** `jobs`, `board`
- **Fits when you see:** cases, matters, projects, engagements, jobs, clients
- **Proved in:**
  - `~/dev/amc/supabase/migrations/0100_docket_core.sql` (at `origin/main`): matter stages, statuses, tasks
  - `~/dev/amc/supabase/migrations/0102_convert_lead_to_matter.sql` (at `origin/main`)
  - `~/dev/amc/app/api/cron/matter-reminders/route.ts` (at `origin/main`)

### Agreement requests in the inbox

<a id="agreement-request-inbox"></a>A client asks for the agreement online and the request lands in the app with its status, from pending to signed.

- **Id:** `agreement-request-inbox`
- **Modules:** `documents`, `leads`
- **Fits when you see:** retainer, engagement letter, agreement, contract, sign
- **Proved in:**
  - `~/dev/amc/app/api/agreement-request/route.ts` (at `origin/main`)
  - `~/dev/amc/supabase/migrations/0106_agreement_requests_inbox.sql` (at `origin/main`)

### See which AI read your site

<a id="ai-crawler-log"></a>Log every AI crawler that reads your pages, so you know which answers engines are learning from you.

- **Id:** `ai-crawler-log`
- **Modules:** `insights`
- **Fits when you see:** seo, content, blog, articles, ai search
- **Proved in:**
  - `~/dev/amc/lib/crawlers/log.ts` (at `origin/main`)
  - `~/dev/amc/lib/crawlers/registry.ts` (at `origin/main`)
  - `~/dev/amc/supabase/migrations/0113_ai_crawler_hits.sql` (at `origin/main`)

### Earned media pipeline

<a id="press-pipeline"></a>Press targets with stages from not contacted to placed, pitches drafted in a plain voice, every touch logged.

- **Id:** `press-pipeline`
- **Modules:** `pipeline`, `outreach`, `people`
- **Fits when you see:** press, media, featured in, as seen on, expert, commentary
- **Proved in:**
  - `~/dev/amc/supabase/migrations/0110_press_outreach.sql` (at `origin/main`)
  - `~/dev/amc/lib/email/plain-pitch.ts` (at `origin/main`)
  - `~/dev/amc/app/press-strategy/targets.ts` (at `origin/main`)

### Publish without a CMS

<a id="blog-without-cms"></a>The team edits a post in the app and it commits to the site's repo, so the site redeploys with no CMS bill.

- **Id:** `blog-without-cms`
- **Modules:** `content`, `site`
- **Fits when you see:** blog, articles, insights, news
- **Proved in:**
  - `~/dev/amc/lib/admin/github.ts` (at `origin/main`): GitHub Contents API commit

### Explainer videos from a script

<a id="explainer-video-pipeline"></a>Stills, voice, music and captions assembled into short explainers from a written script, on a repeatable recipe.

- **Id:** `explainer-video-pipeline`
- **Modules:** `studio`, `social`
- **Fits when you see:** video, youtube, reels, explainer, tiktok
- **Proved in:**
  - `~/dev/amc/scripts/video/noir/build.mjs` (at `origin/main`)
  - `~/dev/amc/docs/COMIC-NOIR-VIDEO-PLAYBOOK.md` (at `origin/main`)

### A business profile post every day

<a id="gbp-daily-post"></a>The agent drafts and posts to the Google business profile on a schedule, from what the business already published.

- **Id:** `gbp-daily-post`
- **Modules:** `social`, `reviews`
- **Fits when you see:** google reviews, local, near me, service area, locations, office
- **Proved in:**
  - `~/dev/amc/scripts/post-gbp-update.mjs` (at `origin/main`)
  - `~/dev/amc/scripts/gbp-pending.mjs` (at `origin/main`)
  - `~/dev/amc/docs/google-business-profile-automation.md` (at `origin/main`)

### Approve posts from your phone

<a id="social-review-hub"></a>Drafted posts and videos wait in one review queue; comment, request changes or approve, and it posts to each channel.

- **Id:** `social-review-hub`
- **Modules:** `social`
- **Fits when you see:** instagram, social, facebook, linkedin, tiktok, posts
- **Proved in:**
  - `~/dev/amc/app/admin/social/[id]/page.tsx` (at `origin/main`)
  - `~/dev/amc/lib/admin/social.ts` (at `origin/main`): statuses and channels
  - `~/dev/amc/app/api/webhooks/zernio/route.ts` (at `origin/main`)

### Documents read on arrival

<a id="document-extraction"></a>Every file in the data room is parsed and its facts extracted, so the agent can cite page and line.

- **Id:** `document-extraction`
- **Modules:** `documents`, `library`
- **Fits when you see:** documents, data room, files, contracts, records
- **Proved in:**
  - `~/dev/dili/apps/worker/src/jobs/extract-document.ts`
  - `~/dev/dili/apps/worker/src/jobs/research.ts`

### Every agent edit, logged with Undo

<a id="agent-change-log"></a>The agent edits records from chat, and every change lands in a log a person can undo.

- **Id:** `agent-change-log`
- **Modules:** `agents`, `log`
- **Fits when you see:** team, office, staff, admin
- **Proved in:**
  - `~/dev/dili/apps/worker/src/chat/changes.ts`
  - `~/dev/dili/apps/worker/src/chat/tools/edit.ts`
  - `~/dev/peels/lib/agent/tools.ts`

### Your own email engine

<a id="own-email-engine"></a>Campaigns to your own list with open and click tracking, a signed delivery webhook, suppression and an audit log.

- **Id:** `own-email-engine`
- **Modules:** `campaigns`
- **Fits when you see:** newsletter, email list, subscribers, mailing list, updates
- **Proved in:**
  - `~/dev/bootyverse/fn/campaigns.ts`
  - `~/dev/bootyverse/fn/sendgrid.ts`
  - `~/dev/bootyverse/fn/audit.ts`
  - `~/dev/amc/lib/email/campaign-sender.ts` (at `origin/main`)

## Not proven yet

The generator must not show these as done.

- E-signature inside the app: agreements are tracked, signing happens outside.
- Taking payment: the practice lists its methods, there is no checkout.
- A numeric lead score: urgency comes from the deadline.

## Built from

- `~/dev/amc`: intake, attribution, insights, matters, SEO, social review, press
- `~/dev/dili`: documents read on arrival, claims checked live, change log with Undo

## Signals that point here

law firm, attorney, lawyer, legal, consultation, free consultation, practice, cpa, accounting firm, advisory, consulting, due diligence, clients, case, matter, retainer, clinic, patients
