# Costs (admin, Know)

- **Module key:** `costs` (stable, never renamed)
- **Tier:** common
- **Route:** `/admin/costs`
- **Folder:** `admin/know/costs/`

## Job

"What did each lead, order or job really cost me, including every agent call?" Costs shows unit economics in three honest layers: the exact cost of every model call the agent made, ad spend allocated by real attribution, and fixed costs allocated across the period. Spend that cannot be tied to a unit sits on its own line, never averaged away. It also holds the caps that stop the agent from overspending.

The number that tells you it is working: **cost per unit** (`fields.unit`: lead, order or job) for the period, with the unattributed share next to it. The unattributed share should trend toward zero.

## Users and permissions

Starts from `shared/roles.md` 4e. Only what differs or needs saying:

| User type | Scope | Verbs |
|---|---|---|
| Owner | all | V C E D X K (set caps, budgets, fixed costs) |
| Admin | all | V X (read and export only; named roles trim verbs, never add, so fixed costs, budgets and caps stay with the Owner) |
| Staff | hidden | · |
| Contractor | hidden | · |
| Customer | hidden | · |
| Agent | role it runs as | V (read only) |

- **Caps are Owner-only.** Raising or lowering a cap is Configure on Costs and is never relaxable for the agent (`shared/roles.md` 5.7 and 5.8). The agent can file a Board card asking for more; only the Owner changes the number.
- **The agent never writes Costs records directly.** Its model-call costs are logged by the system layer on every call (actor kind `system`), not by an agent tool, so the agent cannot under-report itself.
- **Sensitive fields:** every money column here is sensitive by definition. Cost per unit tiles that other modules show (Home, Views) render only for users with `costs.view`. The Bookkeeper preset (`shared/roles.md` 7) gets Costs V.

## Pages and states

Tabs, in nav order:

| Tab | Route | What it shows |
|---|---|---|
| Per lead (label follows `fields.unit`: Per lead, Per order, Per job) | `/admin/costs` | The opener. Cost per unit for the period in three stacked layers (agent, ads, fixed), the unattributed line below it, the trend by week, and a table of units with their cost. Period switch and compare to prior |
| Agent spend | `/admin/costs/agent` | Every model call: when, which agent, on behalf of whom, which chat or run, tokens in and out, real cost. Grouped by agent and by module, month to date vs cap |
| Ad spend | `/admin/costs/ads` | Spend per platform, campaign and ad from Insights' `ad_reports`, allocated to units by attribution. Spend with no unit sits on "Unattributed ad spend" |
| Fixed costs | `/admin/costs/fixed` | Monthly fixed costs (software, rent, salaries if the Owner chooses, rails like hosting and email delivery) with amount, start, end, allocation rule |
| Caps | `/admin/costs/caps` | Monthly caps: agent spend overall, per agent, per module, and API budgets (Search, Studio renders). Month to date bar per cap, what happens at the cap |
| Budget | `/admin/costs/budget` | Planned spend by category per month vs actual, with variance. Replaces the separate budget spreadsheet |

- **Record view:** none. Lines open as a URL modal `?line=<id>` showing the source (the model call with its chat message link, the ad report row, the fixed cost entry) and how it was allocated.
- **Empty state:** "No costs yet. Connect your bank feed or add a fixed cost; agent spend appears as soon as the agent runs." Buttons: Add fixed cost (Owner), Connect bank (Owner).
- **Loading:** skeleton bars sized like the stacked chart.
- **Error:** bank feed down: "Bank import failed on <date>. Fixed and agent costs are current; ad and bank lines stop at <date>." Other tabs keep working.
- **Permission states:** Admin sees every tab read-only (no Add, no Edit, no cap controls). Staff, Contractor and Customer never see the nav item and get the no-access page on a deep link.
- **Quick views:** Agent spend: "Today", "By agent", "Over $1 per call". Ad spend: "Unattributed". Caps: "Over 80%".
- **Badge:** none in the nav. A cap at 80% posts to Home > Today; a cap at 100% files a Board card.

## Data model

Tables owned by this module:

| Table | Columns |
|---|---|
| `cost_lines` | `id`, `org_id`, `kind` (agent, ad, fixed, bank, api), `source_kind` (model_call, ad_report, fixed_cost, bank_txn, api_usage), `source_id`, `amount_cents bigint`, `currency`, `incurred_on date`, `category text`, `unit_kind text null` (lead, order, job), `unit_id null`, `allocation_rule text`, `created_at`, `updated_at`, `deleted_at` |
| `fixed_costs` | `id`, `org_id`, `label`, `amount_cents`, `currency`, `period` (monthly, yearly), `starts_on`, `ends_on null`, `category`, `allocate` (bool, include in cost per unit), `owner_id`, `created_at`, `updated_at`, `deleted_at` |
| `cost_caps` | `id`, `org_id`, `key text` (`agent.total`, `agent.<agent_id>`, `module.<key>`, `api.search`), `monthly_cents`, `currency`, `at_cap` (`stop`, `ask`), `warn_pct int` (default 80), `updated_by`, `updated_at` |
| `budgets` | `id`, `org_id`, `month date`, `category`, `planned_cents`, `currency`, `note` |
| `bank_txns` | `id`, `org_id`, `account_ref text`, `posted_on`, `amount_cents`, `currency`, `merchant`, `category`, `matched_fixed_cost_id null`, `imported_at` |

- **Shared tables it reads:** `model_calls` (the shared table in `shared/data-model.md` holding every model call with its real `cost_cents`; `shared/modules.md` calls it `agent_calls`, same thing), `agent_runs`, `chat_messages`, `agents`. From Insights: `ad_reports`, `attribution`. From Search and Studio: their API usage rows. Writes go to `change_log` like everywhere else.
- **Allocation rules:** agent cost goes to the unit the call worked on (the lead it scored, the order it answered about) when the call carries a subject anchor; otherwise to "Unattributed agent spend". Ad cost follows `attribution`. Fixed cost with `allocate = true` divides evenly across units in its month. Each `cost_lines` row stores the rule it used.
- **Row rules:** no `own` scope. `org_id` filter first.
- **Anchor kinds for the chat:** `cost_line:<id>`, `cap:<key>`, `fixed_cost:<id>`, `field:cap:<key>.monthly_cents`.
- **Config knobs (`fields.*`):** `fields.unit` (lead, order, job; sets the first tab label), `fields.caps` (seed caps, default `agent.total` at $100 a month with `at_cap: stop`), `fields.categories` (budget categories), `fields.bank` (on or off). Sample: `costs`.

## Agent actions

| Action | Tool | Verb | Gated | Writes to `change_log` | Undo |
|---|---|---|---|---|---|
| Answer "what did a lead cost last month, and why did it go up" | `costs_summary`, `query_db`, `show_chart` | V | No | Nothing | n/a |
| Explain one unit's cost | `get_record(lead:<id>)`, `unit_cost` | V | No | Nothing | n/a |
| Show unattributed spend and what would fix it | `unattributed_report` | V | No | Nothing | n/a |
| Ask for a cap raise at the cap | `file_request` (Board) | C on Board | No (it is a request, the Owner decides) | `cards` insert | Closes the card |
| Draft a budget line for the Owner to accept | chat reply only | V | n/a | Nothing until the Owner saves it | n/a |

System writes (not agent tools, logged with actor kind `system`):

- **Every model call:** the model layer writes `model_calls` with real cost from the provider's response, then a `cost_lines` row. If the provider gives no cost, the call is priced from a rate table and flagged "estimated".
- **Cap check, on every call:** before a model call, the layer checks month to date against each matching cap. At `warn_pct`: one Feed item to the Owner. At 100% with `at_cap: stop`: the call is refused, the agent says "I've hit this month's cap" in chat, and one Board card asks the Owner to raise it. Customer-facing replies (portal chat, intake reports) fall back to a short "a person will follow up" message and an Inbox thread, never silence.

Background jobs:

- **Allocation, nightly:** allocates yesterday's ad and fixed cost to units, writes `cost_lines`.
- **Bank import, nightly (if `fields.bank`):** reads yesterday's transactions, matches recurring ones to `fixed_costs`, flags unmatched recurring charges for the Owner.
- **Month close, 1st of the month:** writes last month's cost per unit, budget variance, and top three cost movers into the Owner's morning summary.

## Integrations

- **Rails:** database; banking (read-only transaction and balance feed from the bank or a bank-data aggregator; YEA never moves money from Costs).
- **Platform APIs:** the model provider's usage and cost fields on each response (no separate API); ad platform spend comes through Insights.
- **Webhooks in:** none required; a bank that pushes transactions can post to `/api/costs/bank` instead of the nightly pull. **Out:** none.
- **Secrets (names only):** `BANK_FEED_TOKEN`, `MODEL_PROVIDER_API_KEY` (read for usage only, owned by the agent layer).

## SaaS replaced

None of the products in `shared/saas.md` map to Costs, so there is no priced replacement to list. What it does replace in practice is the budget spreadsheet and the BI dashboard built to compute cost per lead. Migration: export the spreadsheet's categories and monthly plan, import into `budgets` and `fixed_costs`, run the spreadsheet and Costs side by side for one month close, compare cost per unit, then archive the spreadsheet. The keep-list rails it reads from (Mercury for banking, Gusto or Rippling for payroll) stay.

## Acceptance criteria

1. A user without `costs.view` (Staff, Contractor, Customer) never sees Costs in the nav, and a deep link to `/admin/costs/agent` shows the no-access page with no figures.
2. Every write in Costs (fixed cost added, cap changed, budget line saved, system allocation) appears in Log with before, after and a working Undo; system rows show actor kind system.
3. When the agent hits a cap with `at_cap: stop`, it shows "Monthly agent cap reached ($100.00). I filed card #N asking to raise it." and makes no further model calls until the Owner raises the cap; the cap itself can only be changed by the Owner.
4. Every submit button (Add fixed cost, Save cap, Save budget, Connect bank, Export) shows a spinner and disables while it runs.
5. Owner opens Per lead with seed `costs` data: the stacked bar shows agent, ad and fixed layers, the unattributed line sits below it, and the three layers plus unattributed sum to total spend for the period to the cent.
6. Owner opens one lead's cost line: the modal shows each model call with a link to its chat message or run, the ad click it was attributed to, and its share of fixed cost.
7. Admin opens Caps: bars render, and there is no Edit, no Save and no slider.
8. A chat turn's `done` event cost equals the sum of that turn's `model_calls.cost_cents`, and the same amount appears on Agent spend within one minute.
9. At 80% of a cap, the Owner sees one Feed item on Home > Today; a second call that stays above 80% does not post another.
10. With the bank feed failing, Owner opens Costs: a single line states the last good import date, and agent and fixed lines are still current.
11. A portal customer chatting when the agent cap is reached gets "Thanks, a person will follow up shortly", and a new Inbox thread appears with their message.
12. Owner changes `fields.unit` to order: the first tab label becomes Per order, and costs allocate to orders from the next nightly run.

## Open questions

1. **Table name: `model_calls` or `agent_calls`?** Recommended default: `model_calls`, as in `shared/data-model.md`. `shared/modules.md` should be updated to match (flagged to the coordinator).
2. **Include salaries in fixed costs?** Recommended default: off. Most owners want cost per lead for marketing and agent spend, not fully loaded payroll. A toggle on Fixed costs turns it on.
3. **What happens at the cap: stop or ask?** Recommended default: `stop` for the overall agent cap, `ask` for per-module and API caps, so one heavy module asks before it eats the month.
4. **Default overall agent cap?** Recommended default: $100 a month, warn at 80%. The Owner sets the real number in the onboarding interview.
5. **Bank feed now or later?** Recommended default: later. Ship with manual fixed costs and agent and ad spend; add the bank feed once the Owner asks for budget vs actual on every line.
