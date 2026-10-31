# Jobs (admin, Sell)

- **Module key:** `jobs` (stable, never renamed)
- **Tier:** industry (service, case and project work)
- **Route:** `/admin/jobs`
- **Folder:** `admin/sell/jobs/`

## Job

"The work we deliver after the sale, one file per job: who is involved, what is due when, what is left to do, and every document, so nobody misses a date." A won lead becomes a job in one step. Deadlines come to the team; the client gets updates without having to call.

The number: **missed deadlines this month** (target zero), with open tasks past due next to it.

Usually relabeled: Matters, Cases, Projects or Engagements.

## Users and permissions

Start from `shared/roles.md` section 4c. What differs or needs saying:

- **Owner, Admin:** every job, every verb, plus stages, party roles and event kinds in the module Settings tab.
- **Staff:** View, Create, Edit, Send on every job. Can add parties, events, tasks and documents and draft client updates. Cannot delete a job or archive a document they did not add.
- **Contractor:** `own` scope: jobs they are assigned to as a party or task owner. View and Edit on those jobs only (update tasks, log notes, add documents). No Create, no Send to the client.
- **Customer:** only when `fields.client_view` is on: a read view of their own job (stage, next date, documents shared with them) inside the portal. Covered in `customer/portal/documents/PRD.md` and `customer/portal/bookings/PRD.md`.
- **Agent:** V C E. A status update to the client is a Send and is gated. Filing an incoming document to a job is an Edit and is not gated. Deleting an event or task is gated.
- **Sensitive fields:** `jobs.notes_internal`, any party marked `confidential`, documents marked `internal`. Hidden from Contractors unless granted, never shown in the client view, stripped from the agent's results for users without the grant.

## Pages and states

Tabs, in nav order (each a sub-route):

1. **Open** `/admin/jobs`: open jobs, sorted by the next date due. Columns: job, client, stage chip, next date and what it is, open tasks, lead person. Primary action per row: **Open**.
2. **Calendar** `/admin/jobs/calendar`: every dated event across jobs. Overdue first, then the next 14 days, then a month grid. Events also appear on Bookings > Calendar when Bookings is on.
3. **Tasks** `/admin/jobs/tasks`: every open task across jobs. Quick views Mine, Due this week, Overdue. One primary action per row: **Done**.
4. **All** `/admin/jobs/all`: every job including closed, with saved views.

**Record view:** full route `/admin/jobs/[id]`. Blocks, each saving on its own (no page-wide save): **Header** (title, client, stage, lead person, opened and closed dates, value), **Parties** (people and companies with a role from `fields.party_roles`), **Dates** (events with kind from `fields.event_kinds`, date, done), **Tasks** (title, owner, due, status), **Documents** (from Documents and Library, with share-with-client toggle), **Notes** (internal), **Activity** (timeline with agent bylines and Undo). Read-only by default with **Edit** per block.

**Quick views:** Next 7 days, Overdue, No next date, Waiting on client, Opened this month. Filters: stage, lead person, client, kind, party.

**States:**

- Empty: "No jobs yet. Win a lead in Pipeline and turn it into a job, or add one here." Button: **New job**.
- Empty for a Contractor: "No jobs assigned to you."
- Loading: list skeleton; on the record, each block loads on its own with its own skeleton.
- Error: per block ("Dates did not load. Try again."), so one failed block never blanks the job.
- No access: no nav item, deep link shows the no-access page with nothing about the job.
- Read-only: a Contractor sees Notes only if granted; otherwise the block is not rendered.
- Disabled with reason: **Close job** reads "3 open tasks" until tasks are done or moved.

**Badge:** overdue events plus events due in the next 2 days, same scope as the list.

## Data model

Owned tables (each also carries `org_id`, `created_at`, `updated_at`, `deleted_at`):

| Table | Columns |
|---|---|
| `jobs` | `id`, `number text unique per org`, `title`, `client_id → people`, `company_id → companies null`, `stage text` (key from `fields.stages`), `kind text`, `lead_user_id → users`, `owner_id`, `assignee_id`, `opened_at`, `closed_at null`, `value_cents int null`, `currency`, `source_lead_id → leads null`, `notes_internal text`, `client_view bool`, `custom jsonb` |
| `job_parties` | `id`, `job_id`, `person_id → people null`, `company_id → companies null`, `role text` (key from `fields.party_roles`), `confidential bool` |
| `job_events` | `id`, `job_id`, `kind text` (key from `fields.event_kinds`), `title`, `at timestamptz`, `all_day bool`, `done_at null`, `remind_days int[]` |
| `job_tasks` | `id`, `job_id`, `title`, `owner_user_id`, `due_on date null`, `status text` (open, done), `done_at null` |
| `job_documents` | `id`, `job_id`, `document_id → documents null`, `file_id → files null`, `shared_with_client bool`, `internal bool`, `filed_by` |

Foreign keys into shared tables: `people`, `companies`, `users`, `files`, `activities` (the timeline), `change_log`. `job_events` mirror into `calendar_events` when Bookings is on.

**Row rules for `own`:** a Contractor sees a job when they are its `assignee_id`, a `job_parties` person linked to their user, or the owner of any of its `job_tasks`. A Customer sees a job when `client_id` is their `people` row and `client_view` is true.

**Anchor kinds:** `job:<id>`, `job_task:<id>`, `job_event:<id>`, `field:job:<id>.<field>`. Each block renders as an anchored section so "add a hearing to this" works on the pinned block.

**Config knobs:**

- `label`: Jobs, Matters, Cases, Projects or Engagements.
- `fields.stages`: default Intake, Active, Waiting on client, Wrapping up, Closed.
- `fields.party_roles`: default client, contact, opposing party, vendor, referrer.
- `fields.event_kinds`: default deadline, meeting, site visit, filing, milestone.
- `fields.client_view`: on or off. Default off.
- `fields.remind_days`: default reminders at 7, 2 and 0 days before each deadline.
- `fields.custom`: extra job fields (job site address, claim number, jurisdiction).
- **Sample:** `jobs`.

## Agent actions

| Action | Tool | Verb | Gated | Writes to `change_log` | Undo |
|---|---|---|---|---|---|
| Turn a won lead into a job | `create_job_from_lead` | C | No | `jobs` insert, `job_parties` insert (client), lead linked | Deletes the job and unlinks the lead |
| Add an event or task from plain words ("hearing on the 14th at 9") | `add_job_event`, `add_job_task` | C | No; it repeats the date back before saving when the words are ambiguous | `job_events` or `job_tasks` insert | Deletes the row |
| Move a stage | `update_record` | E | No | `jobs.stage` | Restores the prior stage |
| File an incoming document to the right job | `file_document` | E | No; when the match is under 0.9 confidence it asks which job | `job_documents` insert | Unfiles it |
| Draft a status update to the client | `draft_email` | P | Gated (the approval shows recipients and full text) | `messages` insert on send | A sent email cannot be unsent; logged |
| Delete an event or task | `delete_record` | D | Gated | `deleted_at` set | Restores from Trash |
| Answer "what is due this week and who has it" | `query_db`, `highlight` | V | No | Nothing | n/a |

**Background jobs:**

- **Deadline digest** (07:00 daily): overdue and upcoming events per lead person by email; overdue items also land on Home > Today for the Owner. Writes an `agent_runs` row.
- **No next date** (weekly): lists open jobs without a future event and files one Board card.
- **Document filer** (on inbound mail with an attachment): matches by job number, party email or client name and files it, or leaves it in Inbox with a "which job?" note.

## Integrations

- **Email delivery** (default SendGrid): the deadline digest and client updates, sent from the business domain.
- **Files:** stored on the business's object storage; Documents handles templates and signing.
- **Calendar:** events mirror to Bookings > Calendar inside YEA. An `.ics` feed per user (read-only, private URL) lets staff see deadlines in any calendar app.
- **Webhooks in:** inbound email from Inbox (for the document filer).
- **Webhooks out:** `job.created`, `job.stage_changed`, `job_event.overdue`.
- **Secrets (names only):** `EMAIL_API_KEY`, `ICS_FEED_SIGNING_KEY`.

## SaaS replaced

`shared/saas.md` lists no product for this module. Practice and project management tools for service work were seen in the inventories but are not priced in the SaaS list, so they are not claimed here. Migration from any of them follows the standard steps: export jobs, parties, events and documents; import open jobs first with every future date; run both for one month so no deadline is missed; cut over; cancel.

## Acceptance criteria

1. A Contractor never sees jobs they are not on, and a deep link to another job shows the no-access page with no title, client or date.
2. Every agent write (job created from a lead, event added, document filed) appears in Log with before, after and a working Undo; Undo on a filed document removes it from the job's Documents block.
3. When the agent drafts a client status update, the user sees an approval card with the recipient, subject and full body, and one Approve button; nothing is sent before Approve.
4. Every submit button (Save on each block, Add event, Done, Close job) shows a spinner and disables while it runs.
5. Staff marks a lead Won in Pipeline and clicks **Make a job**; the job opens with the client in Parties and the lead linked in Activity.
6. A deadline is two days out; the lead person gets it in the 07:00 digest and the Jobs badge counts it.
7. A user saves the Dates block while the Tasks block fails to load; the date saves and the Tasks block shows its own retry.
8. With `fields.client_view` on, a Customer sees their job's stage, next date and documents marked shared, and no internal notes, confidential parties or internal documents.
9. An Admin relabels the module to "Matters" in Settings; the nav, page title and empty states say Matters on the next load and every saved link still opens.
10. Staff tries to close a job with open tasks; Close job is disabled with "3 open tasks".

## Open questions

1. **Does every deadline need a second person?** Recommended default: no, but the digest goes to the lead person and the Owner for anything overdue.
2. **Time tracking and billing on jobs?** Recommended default: out of v1. Money invoices a job by `job_id`; hours tracking is a later knob.
3. **Client view on by default?** Recommended default: off. Turn it on per business once documents are tagged for sharing.
4. **Court or agency date rules (counting days from an event)?** Recommended default: not computed in v1. A person enters the date; the agent can suggest one but marks it "check this" and never saves it without a yes.
5. **Job numbering?** Recommended default: year plus sequence (`2026-0042`), per org.
