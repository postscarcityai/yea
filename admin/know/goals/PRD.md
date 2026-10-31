# Goals (admin, Know)

- **Module key:** `goals` (stable, never renamed)
- **Tier:** core
- **Route:** `/admin/goals`
- **Folder:** `admin/know/goals/`

## Job

"What are we working toward, how close are we, and what is left to do?" Each goal has a due date, a checklist, and an optional live number with a target ("200 on the waitlist by March 1"). The number moves by itself from real data, the checklist moves when someone (or the agent) does the work, and the ring shows both.

The number that tells you it is working: **share of open goals on pace** (progress at or above the share of time elapsed). Shown at the top of the Goals tab.

## Users and permissions

Starts from `shared/roles.md` 4e. Only what differs or needs saying:

| User type | Scope | Verbs |
|---|---|---|
| Owner | all | V C E A D X K |
| Admin | all | V C E A D X K |
| Staff | all | V C E (create goals and steps, tick steps). No delete: they ask an Owner or Admin |
| Contractor | own | V E on goals assigned to them (tick steps, add notes). They cannot change a goal's target or due date |
| Customer | hidden | · |
| Agent | role it runs as | V C E |

- **No Send, no Spend.** Goals never leave the app. Nothing is gated for the agent by default except the shared rules: changing more than 5 steps at once, or changing a goal's target or due date, states the change and waits for a yes (a target change is a money-like change to what the team is held to).
- **Approve** applies to one thing: a Staff-created goal can be marked "Company goal" (shown on Home) only by Owner or Admin.
- **Sensitive fields:** a goal whose live number reads a sensitive column (revenue, margin, payouts) shows its progress percent to users without that grant, never the raw number.

## Pages and states

Tabs, in nav order:

| Tab | Route | What it shows |
|---|---|---|
| Goals | `/admin/goals` | Open goals as cards: title, owner, progress ring (checklist and live number blended), live number vs target, countdown chip (days left, or past due in the bad status color), on-pace chip. Company goals first, then by due date |
| Done | `/admin/goals/done` | Goals marked done or past due and closed, with the final number and the date it closed |

- **Record view:** URL modal `?goal=<id>`. Header: title, status chip, owner, due date, primary action (Mark done, shown at 100%). Tabs: **Overview** (ring, live number chart over time, checklist), **Activity** (every tick, edit and agent write with byline and Undo), **Settings** (metric, target, due date, company goal toggle; hidden without E on the goal's target).
- **Checklist behavior:** tapping a step ticks it instantly and the bar moves; if the save fails, it rolls back with an inline "Couldn't save, try again". Steps can be renamed inline, reordered by drag in Edit, and assigned to a person.
- **Progress math:** with a live number and a checklist, progress = 50% checklist share + 50% min(number / target, 1). With only one, it is that one. Shown as a percent on the ring, with the formula in a tooltip.
- **Empty state:** "No goals yet. Type one sentence, like '200 on the waitlist by March 1', and the agent sets it up." One button, Set a goal with the agent.
- **Loading:** card skeletons with grey rings.
- **Error:** a goal whose live number query fails shows the ring from the checklist only and a line "Live number unavailable" with Fix with agent.
- **Permission states:** Contractors see only goals assigned to them; the empty state says "No goals assigned to you". Staff see all goals read-only except their own and steps assigned to them. Customers never see the nav item.
- **Quick views:** "Company goals", "Mine", "Behind pace", "Due this month".
- **Badge:** none in the nav. Goals that fall behind pace post to Home > Today instead.

## Data model

Tables owned by this module:

| Table | Columns |
|---|---|
| `goals` | `id`, `org_id`, `title text`, `owner_id`, `assignee_id null`, `due_on date`, `status` (key from `fields.stages`: open, done, closed), `is_company bool`, `metric_key text null` (from `fields.metrics`), `target numeric null`, `unit text` (count, cents, percent), `started_on date`, `done_at null`, `custom jsonb`, `created_at`, `updated_at`, `deleted_at` |
| `goal_steps` | `id`, `org_id`, `goal_id` (FK), `title`, `position int`, `assignee_id null`, `done_at null`, `done_by null`, `created_at`, `updated_at`, `deleted_at` |
| `goal_metrics` | `id`, `org_id`, `goal_id` (FK), `day date`, `value numeric` (one row per day, so the chart and pace math need no recompute) |

- **Foreign keys into shared tables:** `users` (owner, assignee, done_by), `change_log`, `notifications` (behind-pace alerts). `metric_key` resolves to a named read-only query in another module (for example `leads.count`, `money.revenue`, `campaigns.list_size`) through the same read-only role Views uses.
- **Row rules for `own` scope:** Contractors read goals where `assignee_id` or `owner_id` is theirs, and steps on those goals. A Contractor goal's live number runs under the Contractor's scope (their leads, their revenue).
- **Anchor kinds for the chat:** `goal:<id>`, `goal_step:<id>`, `field:goal:<id>.target`, `field:goal:<id>.due_on`.
- **Config knobs (`fields.*`):** `fields.metrics` (list of `{ key, label, module, query, unit }` that can drive a goal; seeded per business from the modules that are on), `fields.stages` (default open, done, closed), `fields.custom`, `fields.pace_alert` (on or off, default on). Sample: `goals`.

## Agent actions

| Action | Tool | Verb | Gated | Writes to `change_log` | Undo |
|---|---|---|---|---|---|
| Set up a goal from a sentence (title, target, due date, metric, 3 to 7 steps) | `create_goal` | C | No (shows the parsed goal in chat before saving) | `goals` + `goal_steps` inserts | Removes the goal and steps |
| Wire the live number to a query | `set_goal_metric` | E | Yes, states the metric and today's value first | `goals.metric_key` before and after | Restores the old metric |
| Tick a step it completed (for example "sent the sponsor email" after an Outreach send) | `update_record(goal_step:<id>)` | E | No | `goal_steps.done_at` before and after, with the proof link in after | Unticks |
| Add, rename or reorder steps | `update_record` | E | Over 5 at once: yes | `goal_steps` before and after | Restores |
| Change target or due date | `update_record(goal:<id>)` | E | Yes, always states old and new | `goals.target` / `due_on` before and after | Restores |
| Warn when a goal is behind | `goal_pace_check` | V | No | Nothing (Feed item) | n/a |
| Answer "are we on track" | `query_db`, `show_chart` | V | No | Nothing | n/a |

Background jobs:

- **Live number snapshot, nightly:** runs each goal's metric query and writes one `goal_metrics` row per goal per day.
- **Pace check, daily 7am local:** for each open goal, compares progress to the share of time elapsed. Behind by more than 10 points: one Feed item on Home > Today for the goal's owner with the gap and the next unticked step. One alert per goal per week, never daily nagging.
- **Due date sweep, daily:** goals past due flip their countdown chip to past due; goals at 100% prompt the owner to Mark done.

## Integrations

- **Rails:** database only (read-only role for metric queries).
- **Platform APIs:** none.
- **Webhooks:** none in or out. Other modules feed goals through `fields.metrics` queries, not webhooks.
- **Secrets (names only):** `DATABASE_URL_READONLY`.

## SaaS replaced

| Product | Risk | Migration step |
|---|---|---|
| Asana (goals) | No brainer | Export goals and their linked tasks to CSV. Import goals into `goals`, subtasks into `goal_steps`; tasks that are not part of a goal go to Board. Cancel only after Board's cutover, since the seat also covers tasks |
| monday.com (goals views) | No brainer | Export the goals board to CSV, map columns (target, due date, owner) to `goals`, pick a live metric for each with the agent. Cancel with Board's cutover |
| ClickUp (goals) | No brainer | Export goals and targets, import as above. Docs move to Playbook and tasks to Board; cancel when all three are moved |

## Acceptance criteria

1. A user without `goals.view` (Customer) never sees Goals in the nav, and a deep link with `?goal=<id>` shows the no-access page and no goal title.
2. Every agent write in Goals (new goal, step tick, metric wiring, target change) appears in Log with before, after and a working Undo.
3. When the agent is asked to move a goal's target from 200 to 150, it shows "Change target on 'Waitlist' from 200 to 150. Progress moves from 41% to 55%." with Approve and Change, and nothing changes until a person approves.
4. Every submit button (Save goal, Mark done, Set a goal with the agent, Fix with agent) shows a spinner and disables while it runs.
5. Owner types "200 on the waitlist by March 1" in chat: the agent shows the parsed goal with a waitlist metric and today's value, and after Approve the card appears on Goals with the ring at the right percent.
6. Staff tick a step: the bar moves before the save returns; with the network cut, the tick rolls back and shows "Couldn't save, try again".
7. Contractor opens Goals: only goals assigned to them render, the live number counts only their book, and the target and due date are plain text with no Edit.
8. A goal 60% through its time at 30% progress shows the "Behind pace" chip, and the owner sees one Feed item on Home > Today that names the next unticked step.
9. Staff open a revenue goal without the revenue grant: the ring shows a percent and the raw revenue number is not rendered.
10. Owner pins a goal as a chip and asks "what's left": the agent lists the unticked steps with assignees and offers to file Board cards for unassigned ones.
11. When a goal's metric query breaks, the card shows the checklist-only ring and "Live number unavailable" with Fix with agent, and other goals render normally.
12. Owner taps Mark done at 100%: the goal moves to Done with its final number and date, and Undo from the toast returns it to Goals.

## Open questions

1. **Blend the checklist and the number, or pick one?** Recommended default: blend 50/50 when both exist. Show the formula in a tooltip so nobody is surprised.
2. **Contractor goals: set by whom?** Recommended default: Owner or Admin sets the target and due date; the Contractor ticks steps and adds notes. Monthly targets for reps can be created in bulk from Reps if that module is on.
3. **Recurring goals (monthly targets)?** Recommended default: a "Repeat monthly" toggle that closes the goal at month end with its final number and opens next month's copy with the same steps unticked.
4. **Where do company goals show?** Recommended default: on Home > Today under Numbers, at most three, as small rings.
5. **Pace alert threshold?** Recommended default: 10 points behind, at most one alert per goal per week.
