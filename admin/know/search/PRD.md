# Search (admin, Know)

- **Module key:** `search` (stable, never renamed)
- **Tier:** common
- **Route:** `/admin/search`
- **Folder:** `admin/know/search/`

## Job

"Are we found when people search for what we do, on search engines and in AI answers, and what should we fix first?" Search tracks the keywords that bring customers, watches the competitors who outrank you, audits the Site every week, and tells you the three fixes worth doing this month.

The number that tells you it is working: **clicks from organic search, last 28 days vs the 28 before** (shown with the count of tracked keywords on page one next to it).

## Users and permissions

Starts from `shared/roles.md` 4e. Only what differs or needs saying:

| User type | Scope | Verbs |
|---|---|---|
| Owner | all | V C X K |
| Admin | all | V C X K |
| Staff | all | V (read only) |
| Contractor | hidden | · |
| Customer | hidden | · |
| Agent | role it runs as | V C (audit runs, keyword ideas, rank refreshes) |

- **Create** here means: add a tracked keyword, add a competitor, start an audit, promote a keyword idea. There is no Send or Publish in Search: page changes ship through Site and Content, under their own gates.
- **Gated for the agent:** none of its default actions are gated. Rank refreshes and keyword research cost money per call, so they count against the `$` flag: anything that would push the month past `fields.monthly_budget_cents` waits for a human yes and files a Board card (same rule as the spend cap in `shared/roles.md` 5.8).
- **Sensitive fields:** none. Search holds public web data about the business.

## Pages and states

Tabs, in nav order (each a sub-route):

| Tab | Route | What it shows |
|---|---|---|
| Overview | `/admin/search` | Organic clicks, impressions, average position: last 28 days vs prior 28, next to tracked-keyword movement (up, down, new on page one). Three "fix this first" cards the agent writes from Audit, Indexing and Rankings |
| Rankings | `/admin/search/rankings` | Tracked keyword watchlist with daily positions, sparkline, the ranking URL, tag, and the API quota used this month on screen |
| Keywords | `/admin/search/keywords` | Research pool: ideas harvested from real search queries plus autocomplete, related searches and "people also ask". Difficulty score, volume band, intent. Promote to Rankings or dismiss |
| Competitors | `/admin/search/competitors` | Who else ranks on our results pages, built from results already pulled (no extra API cost). Share of page one, head-to-head per keyword |
| Links | `/admin/search/links` | External links pointing in, from the search engine's inspection data, plus internal link equity from our own crawl |
| Audit | `/admin/search/audit` | Latest site audit: issues by severity (broken links, missing titles, slow pages, duplicate content, missing structured data), with the page and the fix |
| Pages | `/admin/search/pages` | Search performance per URL: clicks, impressions, position, top queries |
| Indexing | `/admin/search/indexing` | Pages the search engine has not indexed and why, plus the last IndexNow ping per page |
| AI crawlers | `/admin/search/ai-crawlers` | Hits from AI crawler user agents by bot, by day and by page, logged at the edge. Shows which pages AI answer engines read |

- **Record view:** URL modal `?keyword=<id>` with Overview (position history chart, ranking URL, difficulty), Results (latest results page snapshot with competitors), Notes. Audit issues open as `?issue=<id>`. Pages open as `?page=<path>`.
- **Empty state:** "No keywords tracked yet. Add five, or ask the agent to suggest them from your Site." One button, Suggest keywords.
- **Loading:** skeleton table rows; charts reserve their height.
- **Error:** if the webmaster connection is missing, Overview, Pages, Links and Indexing show one card, "Connect your site's search console in Settings > Integrations", and Rankings, Keywords, Competitors, Audit and AI crawlers keep working (they do not need it). Quota exhausted: Rankings shows "Daily refresh paused: monthly quota used. Resets on <date>." as a disabled reason under Refresh.
- **Permission states:** Staff see every tab read-only: no Add keyword, no Start audit, no Track competitor buttons. Hidden for Contractor and Customer with the standard no-access page.
- **Quick views:** Rankings: "Page one", "Dropped this week", "Striking distance (11 to 20)". Keywords: "New ideas", "Low difficulty". Audit: "Critical", "New since last run". Indexing: "Not indexed".
- **Badge:** none in the nav. Overview shows a count of critical audit issues on its tab label.

## Data model

Tables owned by this module:

| Table | Columns |
|---|---|
| `keywords` | `id`, `org_id`, `phrase text`, `tag text`, `location text`, `device text`, `target_path text null`, `tracked bool`, `owner_id`, `created_at`, `updated_at`, `deleted_at` |
| `rank_snapshots` | `id`, `org_id`, `keyword_id` (FK), `day date`, `position int null`, `url text null`, `features text[]` (answer box, map pack, AI answer) |
| `keyword_ideas` | `id`, `org_id`, `phrase`, `source text` (queries, autocomplete, related, paa), `volume_band text`, `difficulty int` (0 to 100), `intent text`, `status text` (new, promoted, dismissed), `harvested_at` |
| `serp_results` | `id`, `org_id`, `keyword_id`, `day`, `position`, `domain`, `url`, `title` |
| `competitors` | `id`, `org_id`, `domain`, `label`, `tracked bool`, `first_seen_at` |
| `backlinks` | `id`, `org_id`, `source_url`, `target_path`, `anchor_text`, `kind` (external, internal), `seen_at` |
| `audit_runs` | `id`, `org_id`, `started_at`, `ended_at`, `pages_crawled int`, `status`, `agent_run_id null` |
| `audit_issues` | `id`, `org_id`, `audit_run_id`, `path`, `rule text`, `severity` (critical, warn, info), `detail`, `fix text`, `status` (open, fixed, ignored) |
| `url_inspections` | `id`, `org_id`, `path`, `indexed bool`, `reason text`, `last_crawled_at`, `last_ping_at`, `inspected_at` |
| `crawler_hits` | `id`, `org_id`, `bot text`, `path`, `at`, `status int` |
| `search_api_usage` | `id`, `org_id`, `month date`, `provider text`, `calls int`, `cost_cents bigint`, `currency` |

- **Foreign keys into shared tables:** `change_log` (every add, dismiss, track and status change), `files` (exported reports), `cards` (a fix the agent hands to a person files a Board card with `source = search`). Search reads Site's `site_pages` to know which paths exist. API cost per month also lands in Costs.
- **Row rules:** no `own` scope. `org_id` filter on every table.
- **Anchor kinds for the chat:** `keyword:<id>`, `page:<path>`, `issue:<id>`, `competitor:<id>`, `field:keyword:<id>.position`.
- **Config knobs (`fields.*`):** `fields.tabs`, `fields.keywords` (seed list), `fields.competitors` (seed domains), `fields.location` (default market for ranks), `fields.audit_day` (default Monday), `fields.monthly_budget_cents` (API spend ceiling, default 5000). Sample: `keywords`.

## Agent actions

| Action | Tool | Verb | Gated | Writes to `change_log` | Undo |
|---|---|---|---|---|---|
| Write the three "fix this first" cards | `search_overview` | V | No | Nothing (cards are computed) | n/a |
| Harvest keyword ideas from real queries or a seed | `harvest_keywords` | C | Only past the monthly budget | `keyword_ideas` inserts (one row per batch, count in after) | Removes the batch |
| Score difficulty for ideas | `score_difficulty` | E | Only past the monthly budget | `keyword_ideas.difficulty` before and after | Restores old scores |
| Promote an idea to tracked | `track_keyword` | C | No | `keywords` insert | Untracks (soft delete) |
| Refresh ranks now | `refresh_ranks` | C | Only past the monthly budget | `rank_snapshots` inserts, `search_api_usage` update | Not undoable (a snapshot is a fact); harmless |
| Start a site audit | `start_audit` | C | No | `audit_runs` insert | Cancels if still running |
| Mark an issue fixed or ignored | `update_record(issue:<id>)` | E | No | `audit_issues.status` before and after | Restores status |
| Hand a fix to a person | `file_request` | C (Board) | No | `cards` insert | Closes the card |
| Write the monthly search report | `search_report` | C | No | `files` insert (PDF or markdown) | Deletes the file |
| Track a competitor | `track_competitor` | C | No | `competitors.tracked` before and after | Untracks |

Background jobs:

- **Daily rank refresh, 5am local:** one call per tracked keyword, quota shown on Rankings.
- **Weekly audit, `fields.audit_day`:** crawls the Site, writes `audit_runs` and `audit_issues`, posts new critical issues to Home > Today.
- **Weekly query harvest:** pulls the last 7 days of real search queries from the webmaster API into `keyword_ideas`.
- **Daily URL inspection:** checks up to 50 pages per day for index status.
- **IndexNow ping, every 3 hours:** pings search engines for pages changed since the last run (reads `site_pages.updated_at`). Logged in `url_inspections.last_ping_at`.
- **Monthly report, 1st of the month:** writes the report and links it on Overview and in the Owner's morning summary.
- **AI crawler logging:** not a job. Edge middleware writes `crawler_hits` on every matching request.

## Integrations

- **Rails:** hosting (edge middleware for `crawler_hits` and the IndexNow key file), database.
- **Platform APIs:** the search engine's webmaster API (queries, pages, URL inspection); a results-page data API (ranks, autocomplete, related searches), billed per call; the IndexNow protocol endpoint. These are the channels, not SaaS being replaced.
- **Webhooks in:** Site publishes post `page_changed` so the next ping includes it. **Out:** IndexNow pings.
- **Secrets (names only):** `WEBMASTER_SERVICE_ACCOUNT_JSON`, `SERP_API_KEY`, `INDEXNOW_KEY`.

## SaaS replaced

None of the products in `shared/saas.md` map to Search, so there is no priced replacement or migration step to list here. Businesses commonly pay for a keyword and rank-tracking seat outside that list; the onboarding interview asks, and if one exists the migration is: export tracked keywords and competitor domains to CSV, import into `keywords` and `competitors`, run both for one month of daily ranks, compare page-one counts, then cancel.

## Acceptance criteria

1. A user without `search.view` (Contractor, Customer) never sees Search in the nav, and a deep link to `/admin/search/rankings` shows the no-access page with Request access.
2. Every agent write in Search (tracked keyword, idea batch, issue status, competitor tracked) appears in Log with before, after and a working Undo.
3. When a rank refresh or harvest would take the month past `fields.monthly_budget_cents`, the agent shows "Refresh 40 keywords, about $0.80, takes the month to $51.20 of $50.00" with Approve and Change, and makes no API call until a person approves.
4. Every submit button (Add keyword, Start audit, Refresh ranks, Track competitor, Export) shows a spinner and disables while it runs.
5. Owner adds a keyword: it appears in Rankings with "Checking..." and shows a position or "Not in top 100" after the next refresh, with the ranking URL.
6. Owner opens Overview with seed `keywords` data: 28-day vs prior 28-day clicks render with the delta, and three fix cards each link to the issue, page or keyword they name.
7. Staff open Audit: issues render, but Start audit and the status menu are not there.
8. With the webmaster connection missing, Owner opens Overview: one card names the missing connection, and Rankings, Keywords, Competitors, Audit and AI crawlers still load.
9. Owner pins an audit issue as a chip and asks "fix this": the agent files a Board card with the page, the rule and the fix text, and replies with the card number.
10. A request from an AI crawler user agent to any Site page appears in AI crawlers within one minute, under the right bot and path.
11. After a Site page is published, the next IndexNow run lists that path with a ping time on Indexing.
12. On the 1st of the month, Owner sees the search report linked in the morning summary, and every number in it matches Overview for the same period.

## Open questions

1. **Which results-page data provider?** Recommended default: any provider with per-call billing and a published price; start with one location and desktop only, add mobile ranks only if the business is mobile-heavy.
2. **How many tracked keywords at launch?** Recommended default: 25, picked by the agent from real queries and the Site's service pages. Owners who track 500 keywords stop reading the page.
3. **Audit depth?** Recommended default: crawl up to 500 pages per run, same host only, respect robots.txt. Bigger sites raise it in config.
4. **Block AI crawlers?** Recommended default: no. Log them and let the owner decide from the data. Blocking is a Site setting with its own confirm.
5. **Monthly API budget?** Recommended default: $50, shown on Rankings and in Costs. The agent asks before crossing it.
