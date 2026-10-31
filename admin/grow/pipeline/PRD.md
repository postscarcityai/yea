# Pipeline (admin, Grow)

- **Module key:** `pipeline`
- **Tier:** common
- **Route:** `/admin/pipeline`
- **Folder:** `admin/grow/pipeline/`

## Job

"The companies and deals we are working, by stage, with the next step on every row." Every account and deal has an owner, a stage, a next step and a date. The agent opens each one with the next email already drafted, and it says out loud when an account stops buying.

The number: **share of open deals with a next step dated in the future** (target 100 percent). Second number: accounts flagged for win-back this month and how many came back.

## Users and permissions

Starts from `shared/roles.md` section 4b. Differences only:

| User type | Pipeline |
|---|---|
| Owner, Admin | all |
| Staff | V C E P. No D, X, K |
| Contractor | own: V C E P on their book. Own = `companies.owner_id` or `deals.owner_id` is them. They never see other books, totals across books, or another rep's notes |
| Customer | hidden |
| Agent | V C E, P* |

- **Gated agent verbs:** P (any email or text to an account contact). Stage moves, notes and drafts are not gated. Bulk stage moves over 5 records ask first.
- **Per-module relax:** none recommended. A drafted email to a named buyer is a relationship; the Owner may relax only "send a sequence step already approved in Outreach".
- **Sensitive fields:** deal value and margin fields (`deals.value_cents`, `deals.margin_pct`) are visible to Contractors only on their own deals; cost and margin hidden from Staff unless granted. Tax ID uploads on an account are sensitive.

## Pages and states

Tabs in nav order:

| Tab | Route | What it shows |
|---|---|---|
| Board | `/admin/pipeline` | Deals as cards in stage columns. Drag to move (asks for a reason on Lost). Column totals in value |
| List | `/admin/pipeline/list` | Companies and deals in a table: name, stage, owner, value, last order or touch, next step, due |
| Map | `/admin/pipeline/map` | Accounts on a map, colored by recency of last order or touch |
| Follow-ups due | `/admin/pipeline/due` | Deals and accounts whose `next_step_on` is today or past |
| Hot | `/admin/pipeline/hot` | Rows marked hot by a person or by the agent, with the reason |
| Settings | `/admin/pipeline/settings` | Stages, kinds, stage mode, custom fields. Hidden without K |

**Record view:** full route `/admin/pipeline/[id]` for a company (deals open inside it as `?deal=<id>`). Header: company name, kind chip, stage chip, owner, primary action (Email, with the draft already loaded). Tabs:

1. **Conversations**: every email and text with the company's people, newest first, with the agent's next draft pinned on top.
2. **Orders or Jobs**: label follows which Sell module is on. Recency and frequency at the top ("ordered every 21 days, last 47 days ago").
3. **Timeline**: calls, visits, notes, stage moves, owner changes, agent writes with Undo.
4. **People**: contacts at the company with role and last touch.
5. **Details**: address, domain, custom fields, tax ID (sensitive), import source.

**Quick views:** Follow-up due, Mine, No next step, Stopped buying, Hot. Filters: stage, kind, owner, value band, last touch window, territory.

**States:**

- **Empty:** "Companies you are working show up here. Convert a lead or add one." Buttons: Add company (primary), Import CSV.
- **Empty for a Contractor:** "No accounts in your book yet."
- **Loading:** board columns render with three ghost cards each.
- **Error:** "Pipeline didn't load. Try again." with Retry. A drag that fails to save snaps the card back and shows a toast with the reason.
- **Permission:** without `pipeline.view` the nav item is hidden and deep links show the no-access page. Without E, cards are not draggable and the record has no Edit. Import is hidden for Contractors.
- **Disabled with reason:** Email shows "Add a contact with an email to send" when the company has no reachable contact; "On do-not-contact" when the person is suppressed.

**Badge:** count of deals and accounts in Follow-ups due in the user's scope.

## Data model

Owned tables (the shared `companies` table holds the account itself):

| Table | Columns |
|---|---|
| `deals` | `id`, `org_id`, `company_id` (fk `companies`), `title`, `kind` (from `fields.kinds`), `stage` (from `fields.stages`), `value_cents` int, `currency`, `margin_pct` numeric null, `probability` int null, `expected_close_on` date, `lost_reason` text, `hot` bool, `hot_reason` text, `source_lead_id` (fk `leads`, null), `custom` jsonb, `owner_id`, `assignee_id`, `created_at`, `updated_at`, `deleted_at` |
| `deal_stage_history` | `id`, `deal_id`, `from_stage`, `to_stage`, `reason`, `actor_kind`, `actor_id`, `at` |
| `next_steps` | `id`, `subject_kind` (`company`, `deal`), `subject_id`, `text`, `due_on` date, `done_at`, `owner_id` |
| `owners` | `id`, `company_id`, `owner_id`, `from_at`, `to_at` (book ownership history, so commission and reporting survive a reassignment) |
| `account_signals` | `id`, `company_id`, `kind` (`stopped_buying`, `cadence_slip`, `new_product_interest`), `reason`, `detected_at`, `resolved_at` |

- **Shared:** `companies` (add columns via `custom` only; `stage` on `companies` holds the account stage when `fields.stage_mode = behaviour`), `people` and `company_people`, `activities`, `threads`, `messages`, `change_log`.
- **Row rules for `own`:** Contractor reads and writes `companies` and `deals` where `owner_id` = them; `activities` only on those subjects; `owners` history only for their own rows.
- **Anchor kinds:** `company:<id>`, `deal:<id>`, `field:deal:<id>.<field>`, `field:company:<id>.<field>`. Signals anchor as `signal:<id>` inside the record header.
- **Config knobs:** `label` (Pipeline, Accounts, Sponsors, Partners, Deals), `fields.stages` (default Target, Contacted, Talking, Proposal, Won, Lost), `fields.kinds` (customer, partner, sponsor, vendor, press), `fields.stage_mode` (`manual` or `behaviour`), `fields.cadence_days` (expected reorder gap, default learned from orders), `fields.custom`.
- **Sample type:** `deals`. Seeds 30 companies, 45 deals across stages, 3 accounts that stopped buying, `.example` domains, 555-01xx phones.

## Agent actions

| Action | Tool | Verb | Gated | Writes to `change_log` | Undo |
|---|---|---|---|---|---|
| Draft the next email on every open record | `draft_email` | C | No | Draft on the thread | Deletes the draft |
| Send that email | `send_message` | P | Yes | Message row, `last_touch_at` | Not undoable once delivered; Log says so |
| Log a call, visit or note (from text, voice or a photo of notes) | `log_activity` | C | No | Activity row | Removes it |
| Move stage with a reason | `move_card` | E | No (over 5 asks) | `stage`, `deal_stage_history` row | Restores stage, removes the history row |
| Set or complete a next step | `update_record` | E | No | `next_steps` row | Restores prior |
| Start a sequence for selected contacts | `enroll_in_sequence` (Outreach) | C | No; the steps are gated in Outreach | `enrollments` rows | Unenrolls |
| Flag an account that stopped buying, with why | `flag_signal` | C | No | `account_signals` row | Resolves the signal |
| Start a win-back: query, chart, draft, plan | `start_winback` | C | Sends inside it are gated | Draft, next step, signal link | Removes drafts and next step |
| Compute stage from behaviour | background | E | No | `stage` per company | Restores prior stage |
| Reassign a book | `update_record` | E | Asks first (bulk) | `owner_id`, `owners` row | Restores owner |

**Background jobs:**

- **Nightly behaviour stages** (when `stage_mode = behaviour`): recompute stage from orders, replies, claims and visits. Produces a summary row in Log: "12 accounts moved, 2 into Stopped buying".
- **Cadence watch (daily):** compare each account's gap since last order to its usual cadence; past 1.5x creates a `stopped_buying` signal and a win-back draft.
- **Follow-up digest (weekday 8:00 local):** each owner's due list to Home and, for Contractors, by email.

## Integrations

- **Email delivery** (default SendGrid; contract: send from the owner's address on the business domain, reply-to that owner, event webhook for opens and bounces). Replies land in Inbox and thread onto the company.
- **SMS** (default Twilio) for text touches, consent checked against `consents`.
- **Database** (default Neon Postgres) with row rules.
- **Platform APIs (optional):** a places or maps API to fill address and photo on a new company (budget capped in Costs); map tiles for the Map tab.
- **Webhooks:** none in. Optional `deal.won` out.
- **Secrets by name:** `SENDGRID_API_KEY`, `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `PLACES_API_KEY` (optional), `MAP_TILES_KEY` (optional).

## SaaS replaced

| Product | Risk | Migration step |
|---|---|---|
| Close | Easy | Export companies, contacts, opportunities and activity; import to `companies`, `people`, `deals`, `activities`; parallel run one week; cut over; cancel |
| Pipedrive | Easy | Export deals and organizations; map pipelines and stages one to one into `fields.stages`; import; parallel run one week; cancel |
| Zoho CRM | Easy | Export accounts, deals, contacts with custom fields; create matching `fields.custom` first; import; parallel run; cancel |
| ActiveCampaign (CRM half) | Easy | Export deals and contacts with deal stage; import; move automations through Outreach and Campaigns; cancel when both halves are live |
| HubSpot Sales Hub Starter | Plan it | Export companies, deals, contacts and the engagement history; import history into `activities` so nothing is lost; run both for two weeks with reps logging only in YEA; compare open deal counts and values; cut over; cancel |
| Salesforce Starter Suite | Plan it | Map custom objects to `fields.custom` and kinds before export; export with IDs kept in `custom.legacy_id`; import; two week parallel run; rebuild the three reports the team uses as Views; cut over; cancel |

## Acceptance criteria

1. A Customer never sees Pipeline, and a Staff user without `pipeline.view` sees no nav item; a deep link to `/admin/pipeline/7` shows the no-access page with no company name.
2. Every agent write (stage move, next step, signal, draft) appears in Log with before, after and a working Undo.
3. When the agent wants to email an account contact, the user sees an approval card with recipient, subject and full body and one Approve button; nothing sends before Approve.
4. Every submit button (Send, Save, Move, Import) shows a spinner and disables while it runs.
5. An Admin opens any open company record and the Conversations tab shows a drafted next email at the top, written for that company.
6. A Contractor sees only their own book on Board, List and Map; column totals equal the sum of their own deals.
7. A Staff user drags a deal to Lost and is asked for a reason; the reason appears on the Timeline and in `deal_stage_history`.
8. The Owner pins an account in chat and asks "why did they stop ordering, start a win-back"; the agent replies with a chart of order history, a plain reason, a drafted email and a next step, and the email waits for Approve.
9. An account past 1.5 times its usual reorder gap appears under Stopped buying with the reason the agent gives.
10. With `stage_mode = behaviour`, an account whose contact replies moves to Talking overnight and the move shows the Agent byline and Undo.
11. An Admin imports a CSV of 200 companies; a preview shows new versus matched rows before import, and duplicates by domain are not created.
12. Reassigning an account to another rep keeps the earlier owner in `owners` history, and the old owner's past numbers on Reps stay the same.

## Open questions

1. **Manual or behaviour stages by default?** Recommended: manual for service and B2B deals, behaviour for wholesale accounts that reorder. Set during the interview.
2. **Deals or accounts as the board unit?** Recommended: deals for businesses that sell discrete projects, companies for businesses with repeat buyers (relabel to Accounts and hide deal value).
3. **Win-back threshold?** Recommended: 1.5 times the account's own median reorder gap, minimum 30 days.
4. **Can Staff reassign books?** Recommended: no. Admin and Owner only, since book ownership drives commission.
5. **Keep legacy CRM ids?** Recommended: yes, in `custom.legacy_id`, for one year after cutover.
