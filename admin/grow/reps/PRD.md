# Reps (admin, Grow)

- **Module key:** `reps`
- **Tier:** industry (field sales teams)
- **Route:** `/admin/reps`
- **Folder:** `admin/grow/reps/`

## Job

"A scorecard for every rep: their goal, their book, and who to call next." Owners see the whole team ranked; each rep sees their own number, their leaderboard spot and a short list of accounts to call with what to offer.

The number: **share of reps at or above goal pace** for the period. Second number: cold accounts in each book (no order or touch past cadence).

## Users and permissions

Starts from `shared/roles.md` section 4b. Differences only:

| User type | Reps |
|---|---|
| Owner, Admin | all. Setting goals and territories is E; changing the goal metric is K |
| Staff | V. Read the leaderboard and scorecards; no edits |
| Contractor (a rep) | own: V. Their own scorecard and the leaderboard. Their commission lives in Money (own: V) |
| Customer | hidden |
| Agent | V C E (notes). Writes scorecard notes and call lists; never sets goals or territories |

- **Gated agent verbs:** none in Reps (no sends, no money). Messages to a rep's accounts go through Pipeline and Outreach and are gated there.
- **Leaderboard visibility:** on by default, a knob (`fields.leaderboard`). When on, reps see other reps' names, rank and the ranked metric only; never their books, accounts or commission.
- **Sensitive fields:** commission rates and amounts (`reps.commission_pct`, statements in Money) visible to the Owner, Admin and the rep themself.

## Pages and states

Tabs in nav order:

| Tab | Route | What it shows |
|---|---|---|
| Leaderboard | `/admin/reps` | Reps ranked by `fields.goal_metric` for the period, with goal ring, change versus last period, badges |
| Goals | `/admin/reps/goals` | Each rep's goal by month or quarter, pace, set or change goal |
| Activity | `/admin/reps/activity` | Visits, calls, texts, emails and notes logged by reps, filterable, with a quick log form |
| Territories | `/admin/reps/territories` | Territories on a map and as a list: rep, accounts, open applications, coverage gaps |
| Settings | `/admin/reps/settings` | Goal metric, period, leaderboard on or off, territories mode. Hidden without K |

**Record view:** full route `/admin/reps/[id]`. Header: rep name, territory, goal ring, primary action (Set goal, Admin only). Tabs: **Scorecard** (6 month trend, goal, milestones, weekly note from the agent), **Book** (their accounts with last order and cadence, cold ones on top), **Call list** (who to call this week and what to offer, with the reason), **Activity**.

A rep (Contractor) landing on `/admin/reps` sees the Leaderboard with their own row highlighted, and their own record at `/admin/reps/me`.

**Quick views:** Behind pace, Ahead of pace, Cold accounts over 5, No activity this week. Filters: territory, period.

**States:**

- **Empty:** "Add your reps on Team as Contractors and they show up here." Button (Owner): Invite a rep.
- **Empty for a rep:** "No accounts in your book yet. New accounts you add show here."
- **Loading:** leaderboard rows in skeleton.
- **Error:** "Reps didn't load. Try again." with Retry.
- **Permission:** hidden for Customer. Staff see no Set goal. A rep opening another rep's record gets the no-access page. Settings hidden without K.
- **Disabled with reason:** Set goal shows "Pick a period first"; Log activity shows "Pick an account".

**Badge:** none on the nav. Home shows "3 reps behind pace" for Owner and Admin.

## Data model

| Table | Columns |
|---|---|
| `reps` | `id`, `org_id`, `user_id` (fk `users`), `territory_id`, `commission_pct` numeric (sensitive), `started_on`, `status` (`active`, `paused`, `left`), `created_at`, `updated_at`, `deleted_at` |
| `rep_goals` | `id`, `rep_id`, `period_start`, `period_end`, `metric` (from `fields.goal_metric`), `target` numeric, `set_by`, `set_at` |
| `territories` | `id`, `org_id`, `name`, `geo` jsonb (states, ZIPs, polygons), `rep_id` |
| `rep_notes` | `id`, `rep_id`, `week_of`, `body`, `call_list` jsonb (`[{ company_id, reason, offer }]`), `author_kind`, `created_at` |

- **Shared:** `activities` (reps log into the shared timeline with `actor_id` = rep's user), `companies` (book = `owner_id`), `owners` history (Pipeline), Orders for revenue, Money for commission, `change_log`.
- **Row rules for `own`:** a Contractor reads their own `reps`, `rep_goals`, `rep_notes` rows; the leaderboard is served by a view exposing only `rep name`, `rank`, `metric value`, `goal pct` for all reps.
- **Anchor kinds:** `rep:<id>`, `territory:<id>`, `field:rep:<id>.goal`, `calllist:<rep_id>.<company_id>`.
- **Config knobs:** `label` (Reps, Agents, Ambassadors), `fields.goal_metric` (revenue, orders, new accounts, visits), `fields.period` (month, quarter), `fields.leaderboard` (on), `fields.territories` (`geo` or `named_accounts`).
- **Sample type:** `reps`. Seeds 6 reps, 3 territories, 6 months of goals and orders, 2 reps behind pace, fictional names and 555-01xx phones.

## Agent actions

| Action | Tool | Verb | Gated | Writes to `change_log` | Undo |
|---|---|---|---|---|---|
| Build each rep's weekly call list with what to offer and why | `build_call_list` | C | No | `rep_notes.call_list` | Restores prior list |
| Flag cold accounts in a book | `flag_signal` (Pipeline) | C | No | `account_signals` rows | Resolves |
| Write the weekly scorecard note | `write_rep_note` | C | No | `rep_notes` row | Deletes |
| Log a visit or call a rep dictates in chat | `log_activity` | C | No | Activity row | Removes |
| Answer "how am I doing" for a rep in chat | read tools | read | No | Nothing | n/a |
| Suggest a goal from history | `suggest_goal` | read | Setting it is a human E | Nothing until a person sets it | n/a |

**Background jobs:**

- **Monday 7:00 local:** call lists and scorecard notes for every active rep; each rep gets an email digest and a Home row.
- **Nightly pace:** recompute progress against goal for the period.
- **Month end:** freeze the period's scorecard so later edits to orders do not change a closed month's rank.

## Integrations

- **Database** (default Neon Postgres) with the leaderboard view.
- **Email delivery** (default SendGrid) for the Monday digest to reps, a system message.
- **Platform APIs (optional):** map tiles for Territories.
- **Webhooks:** none.
- **Secrets by name:** `SENDGRID_API_KEY`, `MAP_TILES_KEY` (optional).
- No rails beyond these. Commission payouts live in Money.

## SaaS replaced

None priced in `shared/saas.md`. Sales performance and commission tools are not in the explorer yet, so no product is listed here. When the explorer adds them, expected risk is Plan it (commission owed is money and must reconcile).

Migration pattern: export goals and the last closed period's commission per rep, import goals into `rep_goals`, run one period with both computing commission and reconcile line by line in Money, cancel after the match.

## Acceptance criteria

1. A Customer never sees Reps in the nav, and a deep link shows a not found page; a rep opening `/admin/reps/<another rep id>` sees the no-access page.
2. Every agent write (call list, note, logged activity, signal) appears in Log with before, after and a working Undo.
3. If the agent proposes a goal, the Admin sees the proposed number and the history behind it with one Set goal button; the agent cannot set it.
4. Every submit button (Set goal, Log activity, Save territory) shows a spinner and disables while it runs.
5. A rep signs in and sees the Leaderboard with their row highlighted and other reps' names, rank and metric only; clicking another rep's row does nothing.
6. A rep opens their scorecard and sees goal, progress, 6 month trend and this week's call list with a reason and an offer for each account.
7. A rep dictates "visited the shop on 5th street, they want the new size" in chat; an activity lands on that account's timeline with the rep as actor.
8. Reassigning an account to another rep mid-month keeps the first rep's closed months unchanged.
9. With `fields.leaderboard` off, reps see only their own scorecard and the Leaderboard tab is hidden for them.
10. On Monday at 7:00 local each active rep has a new note and call list, and the Owner's Home shows reps behind pace.

## Open questions

1. **Leaderboard on by default?** Recommended: on, ranked by the goal metric only. Turn off for teams under 3 reps.
2. **Goal metric?** Recommended: revenue for wholesale and distribution, new accounts for teams opening territory.
3. **Can reps see each other's revenue numbers?** Recommended: yes on the leaderboard metric only; books and commission stay private.
4. **Period?** Recommended: monthly goals with a quarterly roll-up.
5. **Are reps Contractors or Staff?** Recommended: Contractors (own book only). Employees who sell from the office are Staff with the Sales, no personal data preset when needed.
