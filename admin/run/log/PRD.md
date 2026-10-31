# Log (admin, Run)

- **Module key:** `log` (stable, never renamed)
- **Tier:** core
- **Route:** `/admin/log`
- **Folder:** `admin/run/log/`

## Job

"Every change anyone made, person or agent, with what it was before, what it is now, and a button to put it back." Log is the reason an owner can let an agent work: nothing changes silently, and almost everything can be undone. It also shows every sign-in and every export of data, so the owner can answer "who touched this, and who took data out" in one place.

The number that tells you it is working: **share of agent changes undone within 7 days** (falling over time means the agent is getting it right). A health check, not a goal: zero writes in the app without a `change_log` row.

## Users and permissions

Start from `shared/roles.md` section 4f. Log has no Delete for anyone. E on Log means Undo.

| User type | Scope | Differs from the matrix how |
|---|---|---|
| Owner | all | V E X K. Sets retention. Only type that sees Sign-ins for every user. |
| Admin | all | V E X. Sees Sign-ins for everyone except the Owner's IP details. |
| Staff | own | V E on changes they made, or the agent made on their behalf. Can undo those. Sees their own sign-ins. |
| Contractor | own | V on changes they made and changes to records in their book. Cannot undo (asks an Admin). |
| Customer | none | Hidden. Their data download and account deletion are logged here, and they see their own history on Portal Account. |
| Agent | own | V E on its own changes: it can report them and undo one on request. |

- **Undo still needs the verb on the record.** Undo on a lead change requires E on that lead. Log never grants a write the module itself does not.
- **Gated verbs for the agent:** X (export of the log) is gated. Undo of its own change is not gated, but Undo of a change that touched more than 5 records states the scope and waits for a yes.
- **Sensitive fields:** `before` and `after` are filtered through the reader's column grants. A Staff user without the cost grant sees "cost changed" with the values replaced by "hidden". Hard deletes are logged without content.

## Pages and states

| Tab | Route | Holds |
|---|---|---|
| Changes | `/admin/log` | Every `change_log` row, newest first: when, who (person, or "Agent, on behalf of Dana", or "Agent, scheduled, as Admin", or System), what record (anchor chip), field summary ("stage: New to Contacted"), Undo. |
| Sign-ins | `/admin/log?tab=signins` | Every sign-in attempt from `auth_log`: user, method (magic link, passkey), result, IP, device, time. Failed attempts highlighted. |
| Exports | `/admin/log?tab=exports` | Every export: who, module, rows, whether it held personal data, who approved it (if gated), file link while it is kept. |

- **Record view:** URL modal `?change=<id>`: full before and after side by side (changed fields highlighted), actor, on behalf of whom, the chat thread and message that caused it (linked), related changes in the same request, and Undo. For an undone change, a link to the change that undid it.
- **Undo flow:** Undo writes a new row restoring `before` and sets `undone_by` on the original. If a later change touched the same field, the modal shows both values and asks "Put back X? This also overwrites Y made later by Z." with Undo anyway and Cancel. Sends cannot be unsent: Undo on a sent email reverts the record state only and says so ("The email stays sent").
- **Empty states:** Changes: "No changes yet. Every edit, by anyone or the agent, will show here." Sign-ins: "No sign-ins yet." Exports: "No exports yet."
- **Loading:** table skeleton (15 rows). Infinite scroll in pages of 50, keyed by `id` so new rows do not shift the page.
- **Error:** load failure shows Retry. An Undo that fails leaves the original row as is and shows the reason ("The record was deleted. Restore it from Trash first.").
- **Permission states:** hidden for Customer. Contractor sees no Undo button. Undo is not rendered on rows whose record the user cannot edit.
- **Quick views:** Agent changes, My changes, Today, Undone. Collapsed filters: actor kind, actor, module, record, operation, date range.
- **Badge count:** none.

## Data model

Shared tables (defined in `shared/data-model.md`): `change_log`, `auth_log`. Log owns both views and adds `exports`.

**`change_log`** (shared, owned here): `id` bigint, `org_id`, `actor_kind` (person, agent, system), `actor_id`, `on_behalf_of`, `agent_run_id` null, `chat_message_id` null, `request_id` (groups changes from one action), `subject_kind`, `subject_id`, `module`, `op` (insert, update, delete), `before jsonb`, `after jsonb`, `fields text[]` (changed field names), `undone_by` bigint null, `undoes` bigint null, `at`.

**`auth_log`** (shared, owned here): `id`, `org_id`, `user_id` null (unknown email attempts keep the email hash), `method` (magic_link, passkey, session_refresh, sign_out), `result` (ok, failed, locked, expired_link), `ip`, `user_agent`, `at`.

**`exports`**

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | |
| `org_id` | uuid | |
| `actor_kind`, `actor_id`, `on_behalf_of` | | Who exported |
| `module` | text | |
| `query` | jsonb | The filter that produced it |
| `row_count` | int | |
| `personal_data` | bool | Any people, consent or sensitive column in it |
| `approval_id` | uuid null | FK `approvals`, when gated |
| `file_id` | uuid null | FK `files`, kept 7 days then purged |
| `at` | timestamptz | |

- **Write rule:** every insert, update and delete through the app writes `change_log` in the same transaction (`shared/data-model.md` rule 5). Build it once as a database helper used by every server action and agent tool, not per module.
- **Immutability:** `change_log`, `auth_log` and `exports` accept insert only. No update except setting `undone_by`, no delete except the retention job.
- **Own scope:** Staff rows where `actor_id` or `on_behalf_of` is them. Contractor rows where they are the actor or the subject is in their book. Agent rows where `actor_id` is the agent.
- **Anchor kinds:** `change:<id>`, `signin:<id>`, `export:<id>`.
- **Config knobs:** `fields.retention_days` (default 365). Sample type: `changes`.

## Agent actions

| Action | Tool | Verb | Gated | Writes to `change_log` | Undo |
|---|---|---|---|---|---|
| Report changes with their numbers | `query_db` on `change_log`, `get_record` | V | No | Nothing | n/a |
| Show where a change came from | `navigate` to `?change=<id>`, `highlight` | UI | No | Nothing | n/a |
| Undo a change on request | `undo_change` | E | No for one record. States the scope and waits for a yes when more than 5 records | New row with `undoes`, sets `undone_by` | Redo by undoing the undo |
| Export the log | `export` | X | **Yes**, never relaxed (personal data) | `exports` row | n/a |

**Background jobs**

- `log.retention` (daily): deletes `change_log` and `auth_log` rows older than `fields.retention_days`, except rows tied to an open legal hold flag on Settings > Data. Writes one summary row ("Purged 1,204 rows older than 365 days") as System.
- `log.export_purge` (daily): deletes export files older than 7 days. The `exports` row stays.
- `log.signin_watch` (triggered on `auth_log` insert): 5 failed attempts for one email in 15 minutes locks magic links for that email for 15 minutes and notifies the Owner.

## Integrations

- **Database:** Postgres (default Neon) with insert-only grants on the log tables for the app role. Point-in-time restore is the database vendor's job; Log is not a backup.
- **Email delivery:** none (sign-in notifications are sent by Team).
- **Platform APIs:** none. **Webhooks:** none.
- **Secrets:** none beyond `DATABASE_URL`.

## SaaS replaced

No product in `shared/saas.md` maps to Log. Audit logs are usually sold as an enterprise tier inside other tools; those tools are replaced by their own modules. Migration: when a business leaves a tool, export its audit history as CSV and attach it to the tool's migration card on the Board; it does not import into `change_log`.

## Acceptance criteria

1. A user on a named role trimmed to no `log.view` never sees the Log nav item, and a deep link to `/admin/log` shows the no-access page; a Customer gets the normal not found page; a Contractor sees Log with only their own rows.
2. Every agent write anywhere in the app appears on Changes within 2 seconds with before, after and a working Undo for users with E on that record.
3. An agent request to undo 12 changes at once lists the 12 and waits for a human yes before writing anything.
4. Every submit button on Log (Undo, Undo anyway, Export) shows a spinner and disables while it runs.
5. An Owner opens `?change=<id>` for an agent edit and sees the before and after side by side, "Agent, on behalf of Dana", and a link to the chat message that caused it.
6. Undo restores the before value on the record, writes a new row that references the original, and the original shows "Undone".
7. Undo on a field that was changed again later shows both values and asks before overwriting.
8. A Staff user without the cost grant sees a cost change as "hidden" in both before and after.
9. Running a SQL update through the app role on `change_log` fails; only insert and setting `undone_by` succeed.
10. Five failed sign-in attempts for one email in 15 minutes lock that email for 15 minutes and show "locked" on Sign-ins.
11. Every export of people data appears on Exports with row count, `personal_data = true`, and the approver when the agent requested it.
12. With `fields.retention_days = 365`, rows older than 365 days are gone the day after and one System summary row records the purge.

## Open questions

1. **Retention default.** Recommended: 365 days, matching what the proven apps kept. Regulated businesses set a longer value on Settings > Data.
2. **Should Contractors be able to undo their own changes?** Recommended: no in the first build (matrix says V only). Add it if Contractors ask more than twice a month.
3. **Log reads (who viewed a record)?** Recommended: not logged by default. Turn on for records the Owner marks sensitive, written to a separate `read_log` table.
4. **IP addresses on Sign-ins.** Recommended: store full IP for 90 days, then truncate to /24, to cut personal data kept.
5. **Undo window.** Recommended: no time limit while the row is retained; Undo always checks for later conflicting changes.
