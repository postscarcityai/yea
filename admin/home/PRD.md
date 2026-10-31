# Home (admin, pinned above the groups)

- **Module key:** `home` (stable, never renamed)
- **Tier:** core
- **Route:** `/admin`
- **Folder:** `admin/home/`

## Job

"Show me what needs a person right now, then how the business is doing." Home is the first screen every signed-in admin-side user lands on: a queue of things waiting on a human, the handful of numbers the owner watches, and a feed of what changed. It stores almost nothing of its own; it reads every other module.

The number that tells you it is working: **median age of items in the Now bucket at the end of each day** (target under 4 hours). A second check: share of agent approvals decided from Home within 24 hours.

## Users and permissions

Start from `shared/roles.md` section 4a. What differs or needs spelling out:

| User type | Scope | What Home shows |
|---|---|---|
| Owner | all | Approval queue first (everything waiting on a yes), then Today, Numbers, Feed. The morning summary sits at the top. Can configure tiles for every role (K). |
| Admin | all | Today across every module, then approvals the Owner delegated, then Numbers minus Owner-only tiles (spend caps, payouts to the Owner). Can configure tiles (K). |
| Staff | all, filtered by default to "assigned to me" | Their queue first, then the team queue, then the short Numbers row the Owner picked for Staff. |
| Contractor | own | Their own Today (who to call, what is due, replies waiting), their scorecard, the leaderboard if Reps is on. Every count is their book only. |
| Customer | own | Not this page. Customers land on Portal Home (`/portal`), specified in `customer/portal/home/PRD.md`. |
| Agent | as its role | V, plus E to pin a chart as a tile. It never sees a tile the person it acts for cannot see. |

- **Gated verbs for the agent:** none on Home itself. Approve buttons on Home decide gated actions owned by other modules; the agent can never press them (Approve is always human).
- **Per-module relax:** not applicable.
- **Sensitive fields:** tiles that read cost, margin, payouts or Owner-only money are tagged `sensitive: true` and render only for users whose grants include those fields. A hidden tile leaves no gap: the grid reflows.

## Pages and states

Tabs are sub-routes, in nav order:

| Tab | Route | What it holds |
|---|---|---|
| Today | `/admin` (default) | Morning summary card, then the act-now queue in four buckets: **Now** (approvals waiting, overdue, stuck, needs reply past the response target), **Today** (due today), **Soon** (next 7 days), **Whenever** (no date). One row per item, one primary action per row. |
| Numbers | `/admin?tab=numbers` | KPI tiles with a sparkline and change vs the prior period, and one funnel chart. Window chips: 7d, 30d, 90d (in the URL). |
| Feed | `/admin?tab=feed` | Latest changes across modules from `change_log`, newest first, with who made them. Agent rows carry the "Agent" byline and Undo for users with E on that record. |

- **Record view:** none. Every queue row and tile links into its module's record or list, with the filter that produced the number already applied (a "12 stuck leads" tile opens Leads with the Stuck view on).
- **Queue rows:** module icon, record label, why it is here ("Waiting on approval", "Overdue 2d", "No reply 6h"), age, and one button: Approve (approver, gated item), Reply (inbox thread), Open (everything else). Approve opens the approval preview inline (what will happen, Approve, Change); it never approves blind.
- **Empty states:**
  - Today, nothing waiting: "Nothing needs you right now." plus the next due item, if any.
  - Numbers, no data yet: one line per tile ("No orders yet") instead of a flat zero chart, and a button "Load sample data" when the org is a demo.
  - Feed, no changes: "Changes show up here as soon as anyone, or the agent, edits a record."
- **Loading:** skeleton rows (5) and skeleton tiles; the summary card shows its last version with a "refreshing" note. Data refreshes every 60 seconds while the tab is visible.
- **Error:** a failed tile shows "Couldn't load this number" with Retry inside the tile. One failing source never blanks the page.
- **Permission states:** Home is visible to every admin-side type, so there is no hidden state for the page. Tiles and queue rows the user cannot see are not rendered (hidden, never locked). Approve shows only for users with A on that module; others see the same row with Open and a "Waiting on approval" chip.
- **Quick views (Today):** All, Assigned to me (default for Staff), Approvals, Overdue. Collapsed filter: module, assignee, bucket.
- **Badge count:** Home carries no nav badge. The tab title shows the Now count ("Today 4").

## Data model

Home owns two tables. Everything else it reads.

**`home_tiles`**

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | |
| `org_id` | uuid | |
| `role_key` | text null | Tile set for a role ("staff"). Null when `user_id` is set |
| `user_id` | uuid null | A personal pin. Wins over the role set |
| `tile_key` | text | Built-in key from `fields.tiles` ("revenue", "leads_new", "cost_per_lead", "cash_owed", "median_reply") or `chart:<hash>` for a pinned chart |
| `source` | jsonb | Built-in: `{ module, metric, window }`. Pinned chart: the read-only query and chart spec from the chat |
| `position` | int | Order in the grid |
| `sensitive` | bool | Reads sensitive columns |
| `owner_id`, `created_at`, `updated_at`, `deleted_at` | | Shared columns |

**`home_summaries`**

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | |
| `org_id` | uuid | |
| `user_id` | uuid | Who it was written for (summaries are per person, scoped to what they can see) |
| `for_date` | date | |
| `body` | text | Markdown, 5 to 8 lines, every number linked to its record or view |
| `agent_run_id` | uuid | FK `agent_runs` |
| `emailed_at` | timestamptz null | |

- **The queue is a view, not a table.** `home_queue` unions each enabled module's "needs a person" query (pending `approvals`, overdue `cards`, unreplied `threads`, stuck leads, due bookings). Each module PRD names its queue query; Home renders whatever modules return in the shape `{ module, kind, id, label, reason, due_at, bucket, assignee_id, owner_id }`.
- **Foreign keys:** `approvals`, `change_log`, `agent_runs`, `users`, `notifications`.
- **Own scope:** the queue and every tile apply the reader's row rules (`owner_id`, `assignee_id`). A Contractor's tile counts only their book. Tile queries run through `can()` per module and with the reader's database role, never as superuser.
- **Anchor kinds:** `tile:<key>`, `queue_item:<module>:<id>`, plus `change:<id>` on Feed rows.
- **Config knobs:** `fields.tiles` (which KPI tiles ship, per role), `fields.summary_hour` (local hour the summary is written and emailed, default 7). Sample type: `chart_tiles`.

## Agent actions

| Action | Tool | Verb | Gated | Writes to `change_log` | Undo |
|---|---|---|---|---|---|
| Explain a tile ("why is this red") | `get_record`, `query_db` | V | No | Nothing | n/a |
| Open the record behind a queue item | `navigate` | none (UI) | No | Nothing | n/a |
| Highlight what a number is made of | `highlight` | none (UI) | No | Nothing | n/a |
| Pin a chat chart to Home | `pin_tile` | E | No | `home_tiles` insert, after = tile row | Removes the tile |
| Reorder or remove a personal tile | `update_record` on `home_tiles` | E | No | before, after | Restores the order or the tile |
| Write the morning summary | background job `home.morning_summary` | V | No | `home_summaries` insert (system actor) | Not needed; summaries are read-only records |
| Email the morning summary | part of the same job | system message | No (a report the user subscribed to, see `shared/roles.md` rule 6) | `notifications` row | n/a |

**Background jobs**

- `home.morning_summary`: runs at `fields.summary_hour` in the org's time zone, once per opted-in user. Reads that user's queue and tiles with their permissions, writes 5 to 8 lines (what changed overnight, what needs them first, one number that moved), stores it, emails it. Skips a user with nothing in Now or Today and no tile change over 10 percent ("silent on a quiet day").
- `home.queue_refresh`: no job. The queue is live from the view; the page polls every 60 seconds.

## Integrations

- **Email delivery** (default SendGrid; any provider with a send API and event webhooks): one transactional send per summary. Contract: `send({ to, subject, html, text, category: "home_summary" })`, bounces mark the user's summary email off.
- **Database:** reads every module through the reader's role. Tile queries are read-only and capped at 5 seconds; a slow tile shows its last cached value with a timestamp.
- **Platform APIs:** none.
- **Webhooks:** none in or out.
- **Secrets:** `SENDGRID_API_KEY` (or the chosen email provider's key), `CRON_SECRET` for the summary job.

## SaaS replaced

No product in `shared/saas.md` maps to Home on its own. Businesses usually pay for dashboard tools and reporting automations that are not priced there. The reporting zaps that run on Zapier or Make are absorbed by Agents (see `admin/run/agents/PRD.md`).

Migration step when a business has a dashboard tool today: export the list of KPIs it shows, map each to a `fields.tiles` key or a pinned chart, run both for two weeks, then cancel.

## Acceptance criteria

1. A user without `home.view` never sees the Home nav item, and a deep link to `/admin` sends them to the no-access page. (Every admin-side type has V by default; test with a named role trimmed to no V.)
2. Every agent write on Home (a pinned tile, a reordered tile) appears in Log with before, after and a working Undo that removes or restores the tile.
3. A gated agent action from any module (for example an Outreach send) appears as a Now row on the Owner's Today with the exact preview the agent wrote ("Send to 38 people. 2 dropped as unsubscribed."), and nothing happens until a human presses Approve.
4. Every submit button on Home (Approve, Retry on a tile, Save tile order) shows a spinner and disables while it runs.
5. An Owner opening `/admin` sees the approval rows above every other Now row, and the summary card dated today.
6. A Staff user lands on Today with the Assigned to me view on, and the Numbers tab shows only the tiles set for the Staff role.
7. A Contractor with 3 open leads in their book and 40 in the business sees "3" on the Leads tile and only their 3 rows in the queue.
8. A user without the cost grant never sees the cost per lead tile, and the grid has no empty slot where it would be.
9. Clicking a tile opens its module list with the matching filter in the URL, and the list count equals the tile number.
10. An Admin asks the chat "pin this chart to Home"; the chart appears as a tile on their Numbers tab and a `change_log` row names the agent on behalf of that Admin.
11. With `fields.summary_hour` set to 7, a user with items in Now receives the summary email at 7:00 local time, and a user with nothing in Now or Today receives none.
12. A tile whose query fails shows "Couldn't load this number" and Retry, and every other tile still renders.

## Open questions

1. **Who gets the morning summary email by default?** Recommended: Owner and Admin on, Staff and Contractor off with a one-click opt in from the summary card.
2. **Should Approve on Home allow bulk approve?** Recommended: no. One Approve per row, so every yes is read. Revisit if an Owner regularly faces more than 20 approvals a day.
3. **Response target for "needs reply" in the Now bucket.** Recommended: 4 business hours, set per org on Settings > Business, read by Home and Inbox.
4. **Live refresh: polling or push?** Recommended: poll every 60 seconds while visible. Add server push only if a business runs Home on a wall screen.
5. **Can Staff pin personal tiles?** Recommended: yes, personal pins only (`user_id` set), never edits to the role set.
