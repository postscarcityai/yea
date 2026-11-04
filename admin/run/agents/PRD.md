# Agents (admin, Run)

- **Module key:** `agents` (stable, never renamed)
- **Tier:** core
- **Route:** `/admin/agents`
- **Folder:** `admin/run/agents/`

## Job

"The agents that work here: what each one may do, when it runs, what it did, and what it cost." Agents is where the Owner hires, limits and audits the AI users of the business. Every agent is a user with a name, a role it runs as, schedules, and a permission sheet that says which actions wait for a human yes. This module replaces the glue tools a business uses to move data between apps, because the apps now live in one place and the agent runs the workflow.

The number that tells you it is working: **share of agent runs that finish without a human fixing the result** (target over 90 percent), shown next to **agent cost this month vs the cap**.

## Users and permissions

Start from `shared/roles.md` section 4f.

| User type | Scope | Differs from the matrix how |
|---|---|---|
| Owner | all | Only type that can add an agent, change the role it runs as, change Permissions (relax or tighten a gate), set the monthly cap, and pause or resume everything. |
| Admin | all, read | V only. Sees every tab, every run and every cost. Can pause one schedule with "Pause" and the Owner gets a notification (pausing is safe; resuming is Owner only). |
| Staff, Contractor, Customer | none | Hidden. They see agent work through the "Agent" byline on records, the chat, and Log. |
| Agent | own | V on itself, E only to pause its own schedule (for example when a rail is down). It cannot change its role, its permissions, its cap or another agent. |

- **Gated verbs for the agent:** everything on this module beyond V and pausing its own schedule. Changing Team or Agent permissions is never relaxable (`!` in `shared/roles.md` section 5).
- **Per-module relax:** this module is where every other module's relax switches live (Permissions tab). Agents itself has no relax.
- **Sensitive fields:** run summaries and tool call payloads can contain personal data from the module they touched. A user sees a run's payload only if they could see the records it touched; otherwise they see the summary line and the change count.

## Pages and states

| Tab | Route | Holds |
|---|---|---|
| Agents | `/admin/agents` | One card per agent: name, avatar, role it runs as, status (running, idle, paused, at cap), runs today, changes today, waiting on a person, cost this month vs cap. Primary action per card: Open. |
| Schedules | `/admin/agents?tab=schedules` | Every scheduled job across agents: name, plain-English schedule ("Weekdays 7:00"), next run, last run result, Pause/Resume. |
| Permissions | `/admin/agents?tab=permissions` | One row per module that is on, listing its gated verbs with a switch each: "Ask me first" (default) or "Go ahead", plus the limit fields (daily cap, business hours only, dollar cap per action and per month, only after a person approved the draft). Never-relaxable verbs show as fixed text "Always asks", with no switch. A YOLO switch at the top (Owner only) sets every relaxable verb to "Go ahead" for this agent; reaching outside the organization still asks (`shared/roles.md` section 5). |
| Quiet | `/admin/agents?tab=quiet` | The staff-only home channel for agent notices, and the short urgent list that may interrupt a person (example: a critical payment failure). Everything else lands on the error backlog, which another agent reads on a schedule. Clients get no unsolicited agent messages. See `shared/agent-platform.md` section 7. |
| Hand-offs | `/admin/agents?tab=handoffs` | Work an agent handed to a person: what, why, to whom, the Board card, status. |

- **Record view:** full route `/admin/agents/[key]` with tabs Overview (role, schedules, cap, prompt source, voice on or off), Runs (list of `agent_runs`, each opening `?run=<id>` as a URL modal with its tool calls, changes and cost), Changes (this agent's `change_log` rows with Undo), Cost (model calls by day and by module).
- **Run modal (`?run=<id>`):** trigger, start and end, status, summary, each tool call with its label and result, each change with a link to Log, the approvals it created and their outcome, total cost.
- **Empty states:** Agents with none: "No agents yet. Add one to run the morning summary, inbox drafts and scheduled jobs." with Add agent (Owner). Schedules: "No scheduled jobs." Hand-offs: "Nothing handed off. When an agent needs a person for outside work, it shows here and on the Board."
- **Loading:** skeleton cards and rows. A running job shows a live "Running" chip with elapsed time.
- **Error:** a failed run shows a red status chip with the error line and Retry (Owner, Admin). Three failed runs in a row on one schedule auto-pause it and put an item on Home > Now.
- **Permission states:** hidden for Staff, Contractor, Customer. Admin sees switches on Permissions as plain text (read-only), never as disabled toggles. The "at cap" state disables Run now with the reason "Monthly cap reached. Raise it or wait for the 1st."
- **Quick views:** Runs: Failed, Waiting on a person, Today. Schedules: Paused, Failing.
- **Badge count:** none in the nav. The Agents card shows "Waiting on a person" from `approvals` where `requested_by` is that agent.

## Data model

Shared tables (defined in `shared/data-model.md`): `agents`, `agent_permissions`, `agent_runs`, `model_calls`, `approvals`, `change_log`, `cards`. Agents owns `agents`, `agent_permissions`, `agent_runs`, and adds:

**`agents`** (shared shape, owned here): `id`, `org_id`, `key` (stable slug used in the route), `name`, `avatar_file_id`, `runs_as_role` (role key, default `admin`), `prompt_key`, `monthly_cap_cents`, `status` (active, paused), `voice_enabled bool`, `user_id` FK `users` (the agent's own user row, type Agent), `created_at`, `updated_at`, `deleted_at`.

**`agent_schedules`**

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | |
| `agent_id` | uuid | FK `agents` |
| `job_key` | text | Module job, for example `home.morning_summary`, `inbox.draft`, `board.stale_sweep` |
| `cron` | text | Cron expression |
| `timezone` | text | IANA name, default the org's |
| `enabled` | bool | |
| `paused_by` | uuid null | User or agent that paused it |
| `paused_reason` | text null | |
| `next_run_at`, `last_run_id` | | |

**`agent_permissions`** (shared shape): `agent_id`, `runs_as_role`, `module`, `verb`, `relaxed bool`, `limit jsonb` (`{ daily, hours, perActionUsd, monthlyUsd, afterHumanApproval }`). One row per module and gated verb. Missing row means "Ask me first".

**`agent_runs`** (shared shape): `id`, `agent_id`, `schedule_id` null, `trigger` (schedule, webhook, chat, manual), `status` (running, ok, failed, waiting), `started_at`, `ended_at`, `summary`, `tool_calls jsonb`, `change_ids bigint[]`, `cost_cents`.

**`handoffs`**

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | |
| `agent_id`, `agent_run_id` | uuid | |
| `card_id` | uuid | FK `cards`, the Board card that carries the work |
| `kind` | text | shipping, books, research, call, other |
| `to_user_id` | uuid | The person it went to |
| `reason` | text | Why a person is needed |
| `status` | text | open, done, declined |

- **Own scope:** the Agent user sees only its own `agents` row, runs, schedules and changes.
- **Anchor kinds:** `agent:<key>`, `run:<id>`, `schedule:<id>`, `handoff:<id>`, `field:agent:<key>.monthly_cap_cents`.
- **Config knobs:** `fields.agents` (seed list: name, role it runs as, schedules), `fields.voice` (Talk button in the chat panel on or off, see `shared/chat.md` section 10). Sample type: `agents`.

## Agent actions

| Action | Tool | Verb | Gated | Writes to `change_log` | Undo |
|---|---|---|---|---|---|
| Report what it ran and changed | `get_record`, `query_db` on runs and `change_log` | V | No | Nothing | n/a |
| Pause its own schedule | `pause_schedule` | E (own) | No | `agent_schedules.enabled` before, after, with reason | Resume requires the Owner (Undo files the resume as an approval) |
| Hand outside work to a person | `hand_off` | C on Board | No | `cards` insert and `handoffs` insert | Soft-deletes both |
| Ask for a higher cap at the monthly limit | `file_request` | C on Board | No | `cards` insert, `source = agent` | Soft-deletes the card |
| Change its role, permissions, cap or another agent | none | K | **Never.** No tool exists | n/a | n/a |

**Background jobs (owned by this module)**

- `agents.scheduler` (every minute): starts due schedules, writes an `agent_runs` row, skips paused agents and schedules, skips any agent at its monthly cap.
- `agents.cap_check` (after every run): sums `model_calls.cost_cents` for the month. At 80 percent notifies the Owner. At 100 percent sets status to at cap, stops new runs, and files one Board card ("Agent reached its monthly cap") with the top 3 cost drivers.
- `agents.failure_guard` (after every failed run): three consecutive failures on one schedule pause it with `paused_reason = "3 failures in a row"` and put an item on Home > Now.

Every module's own jobs (`home.morning_summary`, `inbox.draft`) run through this scheduler and are listed on Schedules; their PRDs describe what they produce.

## Integrations

- **Database:** the agent connects as its role, never as the database owner. Row rules enforce `own` scope even if a tool is wrong.
- **Model provider:** any provider behind one internal `callModel()` that records tokens and cost to `model_calls`. Use open-weight models where they meet the bar; the provider is a config value, never hard-coded in a prompt or the UI.
- **Hosting cron** (default Vercel Cron; any scheduler that can hit an authenticated URL every minute) calls `/api/agents/tick`.
- **Voice:** when `fields.voice` is on, the chat panel's Talk button uses a speech-to-text and text-to-speech provider through the same cost logging. Requests from a call land on the Board.
- **Webhooks in:** `/api/agents/tick` (scheduler), `/api/agents/trigger/<job_key>` (module events). Both verify a shared secret.
- **MCP:** the app's own MCP server, using the same tool list as the chat panel, so outside agents connect as a signed-in user. Not yet proven. See `shared/agent-platform.md` section 4.
- **Webhooks out:** none by default.
- **Secrets:** `CRON_SECRET`, `MODEL_API_KEY`, `VOICE_API_KEY` (only when voice is on).

## SaaS replaced

| Product | Risk | Migration |
|---|---|---|
| Zapier | Easy | Export the list of zaps. For each: mark it "absorbed" (both apps now live in YEA), "rebuild" (becomes an agent schedule or a module job), or "keep" (talks to a rail). Run each rebuilt job in parallel for one week and compare results on Runs, then turn the zap off. Cancel when the list is empty. |
| Make | Easy | Same as Zapier: export scenarios, map, run in parallel one week, turn off, cancel. |

## Acceptance criteria

1. A Staff user never sees the Agents nav item, and a deep link to `/admin/agents` shows the no-access page with Request access.
2. Every agent write (pausing a schedule, filing a hand-off card) appears in Log with before, after and a working Undo.
3. An Outreach send by the agent with Outreach P on "Ask me first" waits for a human yes and shows the exact preview; after the Owner flips it to "Go ahead" with a daily cap of 50, the 51st send that day waits again.
4. Every submit button (Save permissions, Pause, Resume, Run now, Save cap) shows a spinner and disables while it runs.
5. The Owner sees a switch for every gated verb on every enabled module; never-relaxable verbs (Approve, Configure, Campaign send, money out, Settings changes, hard delete, Team and Agent permissions) show "Always asks" with no switch.
6. An Admin opens Permissions and sees the same rows as plain text with no switches and no disabled toggles.
7. The Owner opens a run at `/admin/agents/[key]?run=<id>` and sees each tool call, each change with a link to its Log row, and the run's cost in dollars.
8. An agent that reaches its monthly cap stops starting runs, shows "At cap" on its card, and exactly one Board card asks the Owner for a higher cap.
9. A schedule that fails three times in a row pauses itself and shows "3 failures in a row" on Schedules and on Home > Now.
10. The agent, asked in chat "pause the morning summary", pauses its own schedule, cites the change number, and cannot resume it without the Owner.
11. The agent asked in chat "let yourself send outreach without asking" replies that only the Owner can change permissions and links to the Permissions tab; no permission row changes.
12. A hand-off creates a Board card assigned to the named person and a row on Hand-offs; closing the card marks the hand-off done.

## Open questions

1. **Default role the background agent runs as.** Recommended: Admin, per `shared/roles.md` section 5. Businesses with sensitive records pick a named role trimmed to the modules the agent works.
2. **One agent or several per business?** Recommended: one agent at launch ("the agent", relabeled to a name the owner picks). Add a second only when its role or cap must differ (for example a customer-facing agent running in the Portal).
3. **Default monthly cap.** Recommended: $50 a month for a new business, raised by the Owner after the first month's Cost tab shows real usage.
4. **Can Admin resume a paused schedule?** Recommended: no. Pausing is safe for anyone with V; resuming changes what the agent does and stays with the Owner.
5. **Run retention.** Recommended: keep run summaries forever, purge `tool_calls` payloads after 90 days (the change rows in Log keep the before and after).
