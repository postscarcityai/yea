# Views (admin, Know)

- **Module key:** `views` (stable, never renamed)
- **Tier:** core
- **Route:** `/admin/views`
- **Folder:** `admin/know/views/`

## Job

"Let me save the answers I keep asking for." Ask the chat a question, get a chart, click Pin, and that chart becomes a live tile on a view you can open any morning. No report builder, no dashboard tool: the question is the query.

The number that tells you it is working: **views opened per active user per week** (a dashboard nobody opens is dead; target at least two opens a week for each Owner and Admin).

## Users and permissions

Starts from `shared/roles.md` 4e. Only what differs or needs saying:

| User type | Scope | Verbs |
|---|---|---|
| Owner | all | V C E D P X K |
| Admin | all | V C E D P X K |
| Staff | all to view shared; own to edit | V C E, D and P on views they own (share to the team) |
| Contractor | own | V C E D on their own views. Every tile runs under their `own` scope, so a shared view shows them only their numbers |
| Customer | hidden | · |
| Agent | role it runs as | V C E |

- **A tile runs as the person looking at it, not the person who made it.** The stored query is executed under the viewer's role with row rules and column grants applied. Sharing a view never shares data the viewer could not already see.
- **Publish (P)** here means "share with the team": the view moves from My views to Shared. It is internal and not gated for humans. For the agent it is not in its verbs (V C E only), so the agent can build and edit a view but a person shares it.
- **Delete** is soft (Trash, 30 days, Undo).
- **Sensitive fields:** a tile whose query touches a column the viewer lacks (cost, margin, payouts) renders "This tile uses data you don't have access to" instead of a chart, with no numbers. Owners see which tiles are affected on the view's Settings tab.

## Pages and states

Tabs, in nav order:

| Tab | Route | What it shows |
|---|---|---|
| My views | `/admin/views` | Views the user owns, as cards with a thumbnail of the first four tiles, last opened, tile count |
| Shared | `/admin/views/shared` | Views shared with the team, with the owner's name. Default views from `fields.default_views` live here |

- **Record view:** full route `/admin/views/[id]`. The view is a grid of tiles (1, 2 or 3 columns, drag to reorder in Edit). Each tile: title, the chart or number, the question it came from, "updated 2 min ago", and a menu (Explain, Open in chat, Edit query, Remove). Tabs on the record: **Tiles** (default), **Activity** (edits with Agent bylines and Undo), **Settings** (name, share, refresh, owner-visible only).
- **Tile modal:** `?tile=<id>` opens one tile full size with its data table under the chart and the read-only query behind a "Show query" toggle.
- **Records open read-only.** Edit switches on drag handles, rename and remove.
- **Empty state (My views):** "Ask the chat a question and pin the chart. It shows up here." One button, Ask the agent, which opens chat with the composer focused.
- **Empty view:** "No tiles yet. Ask a question in chat and tap Pin."
- **Loading:** each tile loads independently with a skeleton the size of its last render. One slow tile never blocks the others.
- **Error per tile:** "This tile's query failed: column `stage` no longer exists. Ask the agent to fix it." with one button, Fix with agent. The rest of the view renders.
- **Permission states:** Staff see Shared read-only unless they own the view. Contractors see their own views and shared views, every tile already scoped to their book; the empty state says "No data in your book for this tile yet". Customers never see the nav item.
- **Quick views:** My views: "Recently opened", "Pinned to Home". Shared: "Default", "By owner".
- **Badge:** none.

## Data model

Tables owned by this module:

| Table | Columns |
|---|---|
| `views` | `id`, `org_id`, `name text`, `owner_id`, `shared bool`, `is_default bool`, `pinned_to_home bool`, `layout jsonb` (tile order and widths, keyed by tile id), `last_opened_at`, `created_at`, `updated_at`, `deleted_at` |
| `view_tiles` | `id`, `org_id`, `view_id` (FK), `title text`, `question text` (the words the user asked), `query text` (read-only SQL or a named module summary), `query_kind` (`sql`, `summary`), `chart jsonb` (type, x, y, series, number format), `modules text[]` (which modules the query reads, for permission checks), `refresh` (`on_open`, `hourly`, `daily`), `last_result jsonb`, `last_run_at`, `last_error text null`, `created_by`, `created_at`, `updated_at`, `deleted_at` |
| `view_opens` | `id`, `org_id`, `view_id`, `user_id`, `at` (feeds the "is it working" number) |

- **Foreign keys into shared tables:** `users` (owner, created_by), `chat_messages` (the tile remembers the message it was pinned from, so Open in chat jumps to it), `change_log`.
- **Query safety:** tiles run through the same read-only database role the agent's `query_db` uses. Only `SELECT`, a statement timeout (5 seconds), a row cap (5,000), and the viewer's row rules and column grants applied at run time. `modules` is checked against `can(viewer, module, "view")` before running; any miss shows the access message instead of running.
- **Row rules for `own` scope:** a user sees views they own plus views with `shared = true`. Tiles inherit the view's visibility; the data inside follows the viewer's scope.
- **Anchor kinds for the chat:** `view:<id>`, `tile:<id>`, `field:tile:<id>.query`. A pinned tile chip gives the agent the question, the query and the last result.
- **Config knobs (`fields.*`):** `fields.default_views` (list of `{ name, tiles: [{ title, question, query_kind, query, chart }] }` seeded into Shared), `fields.max_tiles` (default 24 per view), `fields.refresh_floor` (fastest allowed refresh, default `hourly`). Sample: `chart_tiles`.

## Agent actions

| Action | Tool | Verb | Gated | Writes to `change_log` | Undo |
|---|---|---|---|---|---|
| Turn a chat chart into a tile | `add_to_view` | C | No | `view_tiles` insert (and `views` insert if new) | Removes the tile (soft) |
| Build a view from a sentence ("a Monday view for sales") | `create_view` | C | No; more than 5 tiles at once states the list and waits for a yes | `views` + `view_tiles` inserts | Removes the view and tiles |
| Re-run a tile | `run_tile` | V | No | Nothing (result cache only) | n/a |
| Explain a tile | `explain_tile` | V | No | Nothing | n/a |
| Fix a broken tile query | `update_record(tile:<id>)` | E | No | `view_tiles.query` before and after | Restores the old query |
| Rename, reorder, resize | `update_record(view:<id>)` | E | No | `views.name` or `layout` before and after | Restores |
| Remove a tile | `update_record(tile:<id>)` with `deleted_at` | E (on own view) | No | soft delete | Restores from Trash |

The agent cannot share a view (P) or delete a whole view (D). It suggests ("Share this with the team?") and the person taps Share.

Background jobs:

- **Tile refresh:** tiles with `hourly` or `daily` refresh run on schedule as the view owner's role and cache `last_result`; on open, every viewer's tiles still re-run under the viewer's own scope (cached results are shown only to the owner).
- **Broken tile sweep, nightly:** re-runs every tile once; failures set `last_error` and add one Feed item per view owner ("2 tiles on Monday Sales broke after Pipeline stages changed").

## Integrations

- **Rails:** database only (read-only role with statement timeout). Nothing leaves the app.
- **Platform APIs:** none.
- **Webhooks:** none in or out.
- **Secrets (names only):** `DATABASE_URL_READONLY`.

## SaaS replaced

| Product | Risk | Migration step |
|---|---|---|
| Airtable | Easy | Export each base to CSV. Tables that hold real business records import into the module that owns them (Leads, Orders, People); tables that were only reports become views: ask the agent each report's question and pin the answers. Run both for two weeks, confirm the numbers match, archive the base read-only, cancel |

## Acceptance criteria

1. A user without `views.view` (Customer) never sees Views in the nav, and a deep link to `/admin/views/<id>` shows a not-found page with no view name.
2. Every agent write in Views (new tile, new view, query fix, layout change, tile removal) appears in Log with before, after and a working Undo.
3. When the agent is asked to build a view with more than 5 tiles, it lists every tile title and its question, with Approve and Change, and creates nothing until a person approves.
4. Every submit button (Pin, Save, Share, Fix with agent) shows a spinner and disables while it runs.
5. Owner asks "revenue by week for the last 12 weeks" in chat, gets a chart, taps Pin, picks "Monday": the tile appears on that view with the same numbers, and the Activity tab shows it with an Agent byline.
6. Owner shares a view that has a cost-per-lead tile. Staff open it: the cost tile shows "This tile uses data you don't have access to" with no numbers, and every other tile renders.
7. Contractor opens a shared "Leads this month" view: the tile counts only leads in their book, and the number matches their Leads list count.
8. A tile whose query references a renamed column shows the error line and Fix with agent; tapping it updates the query, the tile renders, and the change is in Log with the old query in before.
9. A tile query that tries to write (`UPDATE`, `DELETE`) is refused before running, and the user sees "Tiles can only read data".
10. A tile that runs longer than 5 seconds stops, shows "This tile took too long. Ask the agent to narrow it.", and the rest of the view renders.
11. Owner pins a tile as a chip and asks "why did this jump in week 38": the agent answers in sentences citing the rows behind the jump, and Open in chat from the tile jumps back to the original message.
12. Owner removes a view: it moves to Trash, a toast offers Undo for 4 seconds, and Undo from Log restores it with every tile.

## Open questions

1. **Can a tile query another module the viewer cannot see?** Recommended default: no. The tile renders the access message. Never run the query as the creator for another viewer.
2. **Ship default views?** Recommended default: yes, two in Shared: "This week" (leads, revenue, top source, open approvals) for Owner and Admin, and "My book" (own leads, own tasks due) that renders correctly for Staff and Contractors.
3. **Email a view on a schedule?** Recommended default: not in v1. The morning summary on Home already covers it; add a "send this view Monday 8am" option only if an owner asks.
4. **Allow hand-written SQL tiles?** Recommended default: Owner and Admin only, through Edit query, same read-only role and limits. Everyone else changes a tile by asking the agent.
5. **Pin a view to Home?** Recommended default: yes, one view per user, shown under Numbers on Home > Today.
