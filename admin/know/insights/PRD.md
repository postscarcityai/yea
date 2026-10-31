# Insights (admin, Know)

- **Module key:** `insights` (stable, never renamed)
- **Tier:** common
- **Route:** `/admin/insights`
- **Folder:** `admin/know/insights/`

## Job

"Where do my customers come from, and what happens to them after they show up?" Insights answers in plain sentences first ("Paid search brought 14 leads this week, 6 booked, cost per booked lead $41, up from $33"), then shows the charts behind the sentence. It ties every lead to its true source and ad click, so the owner stops paying for traffic that never turns into money.

The number that tells you it is working: **share of leads with a known source** (target 95% or better). If the business cannot say where a lead came from, nothing else on this page can be trusted.

## Users and permissions

Starts from `shared/roles.md` 4e. Only what differs or needs saying:

| User type | Scope | Verbs |
|---|---|---|
| Owner | all | V X K |
| Admin | all | V X K |
| Staff | all | V (read only; no export, no ad spend figures unless granted) |
| Contractor | hidden | · |
| Customer | hidden | · (their own tracking is governed by the opt-out page on the Site) |
| Agent | role it runs as | V, X* |

- Insights writes almost nothing. The only writes are notes on a funnel step or source, saved annotations on a chart ("Price change went live"), and config. All go to `change_log`.
- **Gated for the agent:** X (export) whenever the export carries visitor or lead personal data. Exports of aggregates (counts by source) are not gated.
- **No per-module relax** needed beyond the default; there are no sends here.
- **Sensitive fields (column-level grants):** `ad_reports.spend_cents`, `attribution.cost_cents`, and ad click ids are hidden from Staff unless the Owner grants `insights.fields.spend`. IP addresses are never shown in the UI to anyone; they are hashed at write time.

## Pages and states

Tabs, in nav order (each a sub-route, so every view is a link):

| Tab | Route | What it shows |
|---|---|---|
| Sources | `/admin/insights` | The opener. A three-sentence summary the agent writes on load, then a table of sources (paid search, paid social, organic search, AI answers, referral, direct, email, partner) with visitors, leads, booked or bought, revenue, cost, cost per outcome. Period switch (7d, 28d, 90d, custom), compare to prior period |
| Traffic | `/admin/insights/traffic` | Visitors and page views over time, top landing pages, top exits, device split, new vs returning |
| Funnel | `/admin/insights/funnel` | The business's own funnel (landing, start, step N, lead, qualified, won) with drop-off per step, by source. Steps come from `fields.funnel` |
| What worked | `/admin/insights/what-worked` | Weekly top 3 pages, posts, emails or ads by outcome, each with a short "why it worked" note the agent writes. Feeds next week's drafts in Make |
| Ads | `/admin/insights/ads` | Spend, clicks, leads and booked outcomes per ad account, campaign and ad, matched to leads by click id. "Where the ad money leaks" list at the top. Hidden when `fields.ads` is off |

- **Record view:** one visitor's timeline as a full route, `/admin/insights/visitors/[id]`, with tabs **Timeline** (every page view and touch, first touch first), **Lead** (the linked `people` row, if any, read-only summary with a link to Leads), **Attribution** (first touch, last touch, ad click, UTM set, landing page, the rule that assigned the source). Opened from any lead's Attribution panel or from a Funnel drill-down.
- **Empty state:** "No visits yet. Add the tracking snippet to your Site, or ask the agent to check it." with one button, Check tracking (runs `check_tracking`).
- **Loading:** skeleton rows and grey chart frames sized like the final chart, so nothing jumps.
- **Error:** an inline card per failed source ("Ad account not connected: reconnect in Settings > Integrations"), the rest of the page still renders. Never a blank page because one ad API is down.
- **Permission states:** Staff open every tab read-only; spend columns are not rendered without the grant. Ads tab hidden when `fields.ads` is off. Contractors and Customers never see the nav item; a deep link shows the no-access page with Request access.
- **Quick views (chips above lists):** "This week", "Paid only", "Unknown source", "Dropped at step" (Funnel), "Spend, no leads" (Ads).
- **Badge:** none. Insights is read for meaning, not worked as a queue. The one alert it raises ("Funnel step dropped 30% week over week") goes to Home > Today as a Feed item, not a badge.

## Data model

Tables owned by this module:

| Table | Columns |
|---|---|
| `visitors` | `id`, `org_id`, `anon_key text` (first-party cookie value, hashed), `person_id uuid null` (FK `people`), `first_seen_at`, `last_seen_at`, `first_touch_id`, `device text`, `country text`, `opted_out bool`, `created_at`, `updated_at`, `deleted_at` |
| `page_views` | `id`, `org_id`, `visitor_id` (FK), `path text`, `referrer text`, `utm jsonb`, `click_ids jsonb`, `at timestamptz`, `duration_ms int` |
| `touches` | `id`, `org_id`, `visitor_id`, `person_id null`, `channel text` (key from `fields.sources`), `source text`, `campaign text`, `ad_id text null`, `kind text` (visit, form_start, call_tap, email_click, dm), `at` |
| `attribution` | `id`, `org_id`, `person_id` (FK `people`), `subject_kind` (lead, order, booking, job), `subject_id`, `first_touch_id`, `last_touch_id`, `source_key text`, `rule text` (which rule decided), `ad_click_id text null`, `cost_cents bigint null`, `currency`, `computed_at` |
| `funnel_snapshots` | `id`, `org_id`, `day date`, `source_key`, `step_key`, `count int` (nightly rollup so long ranges load fast) |
| `ad_reports` | `id`, `org_id`, `platform text`, `account_id text`, `campaign_id`, `ad_id`, `day date`, `impressions`, `clicks`, `spend_cents`, `currency`, `conversions int`, `pulled_at` |
| `insight_notes` | `id`, `org_id`, `subject_kind` (source, funnel_step, chart), `subject_key`, `body`, `at`, `owner_id` |

- **Foreign keys into shared tables:** `people` (a visitor becomes a person when they leave a lead), `change_log` (notes and config), `files` (exported CSVs). Leads, Orders, Bookings and Jobs read `attribution` to show the Attribution panel on their records; Costs reads `attribution` and `ad_reports` to allocate spend.
- **Compute at read time, no backfill.** Source assignment runs from raw `touches` with a versioned rule set, so a rule change re-scores history without a migration. `funnel_snapshots` is a cache, never the source of truth.
- **Row rules:** Insights has no `own` scope (Contractors do not see it). `org_id` filter on every table. Visitors with `opted_out = true` get no new rows; existing rows are deleted on opt-out.
- **Anchor kinds for the chat:** `source:<key>`, `visitor:<id>`, `funnel_step:<key>`, `ad:<platform>:<ad_id>`, `field:visitor:<id>.<field>`. Every chart renders `data-anchor` on its series and bars so a user can pin "the paid social bar" and ask about it.
- **Config knobs (`fields.*`):** `fields.tabs` (subset and order), `fields.ads` (bool), `fields.sources` (ordered channel keys and labels), `fields.funnel` (ordered step keys, each mapped to an event or a table status), `fields.outcome` (what counts as the win: lead, booking, order, job), `fields.attribution_rule` (`first_touch`, `last_touch`, `last_paid`; default `last_paid`). Sample: `traffic`.

## Agent actions

| Action | Tool | Verb | Gated | Writes to `change_log` | Undo |
|---|---|---|---|---|---|
| Answer "is this working" in sentences with a chart | `insights_summary`, `query_db`, `show_chart` | V | No | Nothing | n/a |
| Explain one lead's true source and ad click | `get_record(lead:<id>)`, `get_attribution` | V | No | Nothing | n/a |
| Find where ad money leaks (spend with no outcome) | `ads_leaks` | V | No | Nothing | n/a |
| Flag a funnel step that dropped | `funnel_check` | V | No | Feed item only (a notification, not a record write) | n/a |
| Add a note to a source, step or chart | `add_note` | C | No | `insight_notes` insert, after = note | Deletes the note |
| Pin a chart to Views | `add_to_view` | C (on Views) | No | `view_tiles` insert (logged under Views) | Removes the tile |
| Export source or funnel data | `export_csv` | X | Yes when rows carry personal data, else no | `files` insert, Log > Exports row | Not undoable (data has left); the file link can be revoked |
| Check the tracking snippet on the Site | `check_tracking` | V | No | Nothing | n/a |

Background jobs:

- **Ad pull, nightly:** pulls yesterday's spend, clicks and conversions per ad from each connected ad account into `ad_reports`. Logged as an `agent_runs` row with counts.
- **Click match, hourly:** matches new leads' click ids to ad clicks and writes `attribution`. Each write is a `change_log` row with actor kind `system`.
- **Funnel rollup, nightly:** writes `funnel_snapshots`.
- **Weekly "What worked", Monday 7am local:** writes the top 3 with notes, posts a one-paragraph summary to Home > Today.
- **Drop alert, daily:** if any funnel step or source falls more than `fields.drop_alert_pct` (default 30%) week over week, a Feed item with the sentence and a link to the filtered Funnel tab.

## Integrations

- **Rails:** database (Postgres default, read-only role for the agent's `query_db`); hosting (an edge middleware writes `page_views` and `touches` so tracking works with ad blockers and without a third-party script).
- **Platform APIs:** each ad platform's reporting API (search ads, social ads) for spend and click lookup; the search engine's webmaster API for organic query data shared with Search. These are the channels, not SaaS being replaced.
- **Webhooks in:** form starts and call taps from Site and Intake post a `touch`. **Out:** none.
- **Secrets (names only):** `ADS_SEARCH_DEVELOPER_TOKEN`, `ADS_SEARCH_OAUTH_REFRESH`, `ADS_SOCIAL_ACCESS_TOKEN`, `WEBMASTER_SERVICE_ACCOUNT_JSON`, `VISITOR_HASH_SALT`.

## SaaS replaced

| Product | Risk | Migration step |
|---|---|---|
| Hotjar (Contentsquare) | No brainer | Export nothing (recordings are disposable). Ship the YEA tracking middleware, run both for one week to compare visitor counts within 10%, remove the snippet, cancel |
| Plausible Analytics | No brainer | Export the last 12 months of pageviews by day as CSV, import into `page_views` rollups as a baseline series, parallel run one week, remove the snippet, cancel |
| Mixpanel | Easy | Export events for the funnel steps only, backfill `touches` for the trend lines you care about, map event names to `fields.funnel` steps, parallel run two weeks, cancel |
| Sprout Social (analytics half) | Easy | Export post performance history to CSV for What worked's baseline. Cancel together with the Social module's cutover, not before |

## Acceptance criteria

1. A user without `insights.view` (Contractor, Customer) never sees Insights in the nav, and a deep link to `/admin/insights/funnel` shows the no-access page with Request access and leaks no counts.
2. Every agent write in Insights (a note, an attribution row from the agent, a tile pinned to Views) appears in Log with before, after and a working Undo that removes it.
3. When the agent is asked to export visitors with emails, it shows "Export 1,204 visitors with email and source to CSV" with Approve and Change, and nothing leaves until a person with `insights.export` taps Approve.
4. Every submit button (Save note, Reconnect ad account, Export, Check tracking) shows a spinner and disables while it runs, then re-enables with an inline result.
5. Owner opens Sources: a three-sentence summary renders above the table within 3 seconds for 90 days of seed `traffic` data, and every number in the sentences matches a cell in the table below it.
6. Owner opens a lead in Leads that came from an ad: the Attribution panel shows source, campaign, ad and click id, and the same lead appears in the Ads tab under that ad.
7. Staff opens Ads: the tab renders with clicks and leads but the spend and cost per outcome columns are not rendered at all (no empty column, no lock icon).
8. With one ad platform's API returning an error, Owner opens Sources: every other source renders, and the failed one shows one inline card naming the account and a Reconnect link.
9. Owner pins the "Paid social" bar in a Funnel chart as a chip and asks "why did this drop": the agent answers in sentences, cites the step and the two periods compared, and offers to pin the chart to Views.
10. A visitor who uses the Site's opt-out page gets no new `page_views` rows, and their earlier rows are gone on the next check.
11. Owner turns `fields.ads` off in Settings tab: the Ads tab disappears from the tab bar and its URL shows the module's not-found state.
12. Monday morning, Owner sees the What worked summary in Home > Today, and each of the three items links to its source record.

## Open questions

1. **Attribution rule default?** Recommended default: `last_paid` (the last paid touch wins; if none, the last touch). It matches how owners think about ad spend. Show the rule name on every attribution so nobody argues about invisible math.
2. **Keep the site's old analytics tag during the parallel run?** Recommended default: yes, for two weeks, then remove it. Comparing counts is the only way to trust the new numbers.
3. **Store IP addresses?** Recommended default: no. Hash with `VISITOR_HASH_SALT` at the edge and store only country. Nothing in this module needs a raw IP.
4. **Cookie consent banner?** Recommended default: first-party, no cross-site cookies, opt-out page linked in the footer. Add a consent banner only when the business sells into a region that requires one; it is a Site setting, not an Insights setting.
5. **How long to keep raw `page_views`?** Recommended default: 13 months raw, rollups forever. Enough for a year over year compare.
