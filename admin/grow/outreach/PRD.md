# Outreach (admin, Grow)

- **Module key:** `outreach`
- **Tier:** common
- **Route:** `/admin/outreach`
- **Folder:** `admin/grow/outreach/`

## Job

"Multi-step sequences that stop the moment someone answers, with every step already drafted." Email, call, visit, text and mail steps, written for each company, sent inside business hours, and every reply read and answered in the thread.

The number: **reply rate per wave** (replies divided by delivered first steps). Second number: **steps overdue**, which should be zero at end of day.

## Users and permissions

Starts from `shared/roles.md` section 4b. Differences only:

| User type | Outreach |
|---|---|
| Owner, Admin | all. Editing a sequence's steps and turning on auto-send is K |
| Staff | V C E P. Send and skip their steps; cannot edit shared sequences or turn on auto-send |
| Contractor | own: V C E P. Their enrollments only, their own templates; shared sequences are read-only |
| Customer | hidden. They see only the unsubscribe and takedown pages on the Site |
| Agent | V C E, P* (with daily cap) |

- **Gated agent verbs:** P on every step and every reply, until the Owner relaxes Outreach.
- **Per-module relax:** "Go ahead" for steps of a sequence a person approved, with limits: `fields.daily_cap` (default 50 sends a day), business hours of the recipient's time zone, and stop on any reply. Replies to inbound threads stay gated unless relaxed separately.
- **Sensitive fields:** none beyond People's. Suppression lists are visible to Admin and Owner only.

## Pages and states

Tabs in nav order:

| Tab | Route | What it shows |
|---|---|---|
| Today | `/admin/outreach` | Steps due today in the user's scope, grouped by kind (email, call, visit, text, mail), each with the draft open and Send, Skip, Done |
| Sequences | `/admin/outreach/sequences` | Every sequence: steps, enrolled, active, replied, finished, auto-send on or off |
| Waves | `/admin/outreach/waves` | Sends grouped into waves, compared side by side: delivered, opened, engaged, replied, converted, bounced |
| Templates | `/admin/outreach/templates` | Shared and personal templates with merge fields and the share of each draft people kept |
| Replies | `/admin/outreach/replies` | Every reply to a sequence step, with the agent's drafted answer and the suggested next step (call, not now, remove) |
| Settings | `/admin/outreach/settings` | Step kinds, daily cap, auto-send, sending hours, from-addresses. Hidden without K |

**Record view:** full route `/admin/outreach/sequences/[id]` with tabs **Steps** (editor), **Enrolled** (who, where they are, stop reason), **Results** (by step). Enrollments open as a URL modal `?enrollment=<id>`.

**Quick views:** Due now, Overdue, Replied today, Bounced, Mine. Filters: sequence, step kind, owner, wave, status.

**States:**

- **Empty Today:** "No steps due. Enroll a few companies to start." Button: Enroll from Prospects or Pipeline.
- **Empty Sequences:** "Write your first sequence, or ask the agent for one." Buttons: New sequence, Ask the agent.
- **Loading:** step cards in skeleton.
- **Error:** "Outreach didn't load. Try again." A failed send shows on the step: "Bounced: mailbox does not exist" with the enrollment stopped.
- **Permission:** without `outreach.view`, hidden and no-access on deep link. Without K, the step editor opens read-only and the auto-send switch is not rendered.
- **Disabled with reason:** Send shows "Daily cap reached (50 of 50). Resumes tomorrow 9:00", "Outside sending hours for this recipient", "Add a mailing address in Settings to send".

**Badge:** steps due today plus unanswered replies, in the user's scope.

## Data model

| Table | Columns |
|---|---|
| `sequences` | `id`, `org_id`, `name`, `goal` text, `auto_send` bool, `approved_by`, `approved_at`, `status` (`draft`, `active`, `paused`, `archived`), `owner_id`, `created_at`, `updated_at`, `deleted_at` |
| `sequence_steps` | `id`, `sequence_id`, `position` int, `kind` (from `fields.step_kinds`), `wait_days` int, `template_id`, `instructions` text (what the agent tailors) |
| `enrollments` | `id`, `sequence_id`, `person_id`, `company_id`, `current_step` int, `status` (`active`, `replied`, `converted`, `bounced`, `unsubscribed`, `stopped`, `finished`), `stop_reason`, `wave_id`, `owner_id`, `assignee_id`, `enrolled_at`, `stopped_at` |
| `tasks` | `id`, `enrollment_id`, `step_id`, `due_at`, `draft_subject`, `draft_body`, `status` (`due`, `sent`, `skipped`, `done`), `done_by`, `done_at` |
| `templates` | `id`, `org_id`, `name`, `kind`, `subject`, `body`, `shared` bool, `owner_id`, `kept_ratio` numeric |
| `send_events` | `id`, `task_id`, `provider_message_id`, `event` (`delivered`, `open`, `click`, `bounce`, `spam`, `unsubscribe`, `human_click`), `at` |
| `suppressions` | `id`, `org_id`, `email` or `phone` or `domain`, `reason` (`bounce`, `spam`, `unsubscribe`, `do_not_contact`, `takedown`), `added_at` |
| `waves` | `id`, `sequence_id`, `started_at`, `ended_at`, `size` |

- **Shared:** `people`, `companies`, `threads` and `messages` (replies thread there), `do_not_contact`, `approvals`, `change_log`.
- **Row rules for `own`:** Contractor reads and writes `enrollments` and `tasks` where `owner_id` or `assignee_id` is them; reads shared `sequences` and `templates`; writes only templates they own.
- **Anchor kinds:** `sequence:<id>`, `step:<id>`, `enrollment:<id>`, `task:<id>`, `wave:<id>`, `field:task:<id>.draft_body`.
- **Config knobs:** `fields.step_kinds` (email, call, visit, text, dm, mail), `fields.daily_cap` (default 50), `fields.auto_send` (default off), `fields.sending_hours` (default 9:00 to 17:00 recipient local, weekdays), `fields.stop_on` (reply, order, application, bounce, do-not-contact, claim).
- **Sample type:** `sequences`. Seeds 3 sequences, 90 enrollments, 2 waves, 12 replies, `.example` addresses.

## Agent actions

| Action | Tool | Verb | Gated | Writes to `change_log` | Undo |
|---|---|---|---|---|---|
| Draft each step for the specific company | `draft_step` | C | No | `tasks.draft_*` | Restores prior draft |
| Send a step | `send_step` | P | Yes (relaxable: approved sequence, cap, hours) | `tasks.status = sent`, message row | Not undoable once delivered |
| Stop an enrollment on reply, order, application, bounce or do-not-contact | `stop_enrollment` | E | No | `status`, `stop_reason` | Re-activates at the same step |
| Read a reply and draft the answer in-thread | `draft_reply` | C | No | Draft on the thread | Deletes draft |
| Send that answer | `send_message` | P | Yes | Message row | Not undoable once delivered |
| Mark next step from a reply (call, not now, remove) | `update_record` | E | No | Enrollment and Pipeline next step | Restores |
| Write a sequence from a goal | `draft_sequence` | C | No; activating needs a person (K) | New `sequences` draft | Deletes draft |
| Compare waves | `compare_waves` | read | No | Nothing | n/a |
| Enroll companies | `enroll_in_sequence` | C | Over 5 asks | `enrollments` rows | Unenrolls |

**Background jobs:**

- **Hourly queue:** creates `tasks` for steps whose wait has passed, drafts them, and for auto-send sequences sends inside sending hours up to the daily cap.
- **Reply desk (twice on weekdays, default 11:00 and 16:00):** reads every unhandled reply with the company's context, drafts the answer, sets the next step.
- **Event sync (on webhook and hourly):** delivery, bounce, spam and unsubscribe events update `send_events` and `suppressions`, and stop enrollments. A human-click signal filters out link scanners.

## Integrations

- **Email delivery** (default SendGrid; contract: send from a person's address on the business domain or a dedicated sending subdomain, SPF, DKIM and DMARC aligned, List-Unsubscribe and one-click unsubscribe headers, signed event webhook, email activity API for sync).
- **SMS** (default Twilio) for text steps, only to people with SMS consent on file.
- **Database** (default Neon Postgres).
- **Platform APIs (optional):** a social network's messaging API for `dm` steps where the platform allows it; otherwise dm steps are tasks a person does by hand.
- **Webhooks in:** email events, inbound replies (through Inbox inbound parse).
- **Secrets by name:** `SENDGRID_API_KEY`, `SENDGRID_WEBHOOK_KEY`, `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`.

## SaaS replaced

None priced in `shared/saas.md`. Sales engagement tools are not in the explorer yet, so no product is listed here. The CRM tools that carry sequences (Close, Pipedrive, HubSpot Sales Hub Starter) are migrated under Pipeline; when their sequences move, follow this step order: export active enrollments with current step, rebuild the sequence in Outreach, pause the old sequence, enroll at the same step, cancel with the CRM.

## Acceptance criteria

1. A user without `outreach.view` (Customer, or a trimmed Staff role) never sees Outreach, and a deep link shows the no-access page.
2. Every agent write (draft, stop, enroll, next step) appears in Log with before, after and a working Undo.
3. A gated send shows the recipient, subject, full body and send time on an approval card with one Approve button; nothing leaves before Approve.
4. Every submit button (Send, Skip, Done, Save sequence, Enroll) shows a spinner and disables while it runs.
5. A prospect replies to step 1; within the next reply desk run their enrollment shows Replied, no further steps are created, and a drafted answer waits in Replies.
6. With auto-send on and a cap of 50, the 51st step of the day does not send and the Send button shows "Daily cap reached" with the resume time.
7. A step due at 7:00 recipient local time does not send until 9:00 their time.
8. A bounce marks the address suppressed and stops every active enrollment for it across all sequences.
9. A recipient clicks one-click unsubscribe; the next scheduled step for them never sends and Waves counts them as unsubscribed.
10. A Contractor sees only their own enrollments on Today; their badge equals their due steps plus unanswered replies.
11. On Waves, an Admin sees two waves side by side with delivered, opened, replied and converted counts that match the event rows.
12. Only Owner and Admin see the auto-send switch; a Staff user opening sequence settings sees the steps read-only.

## Open questions

1. **Auto-send default?** Recommended: off. Suggest turning on after the Owner approves 30 steps of one sequence with no edits.
2. **Daily cap?** Recommended: 50 per sending address, raised by 25 a week while the bounce rate stays under 2 percent.
3. **Sending domain?** Recommended: a dedicated subdomain for cold outreach so the main domain's reputation is protected.
4. **Do dm steps send through a platform API?** Recommended: no. Make them tasks a person sends by hand; platform rules change often.
5. **Reply desk cadence?** Recommended: twice on weekdays; hourly only for businesses where a reply is worth money the same day.
