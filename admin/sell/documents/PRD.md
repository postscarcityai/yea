# Documents (admin, Sell)

- **Module key:** `documents` (stable, never renamed)
- **Tier:** common
- **Route:** `/admin/documents`
- **Folder:** `admin/sell/documents/`

## Job

"Every document we send or sign lives in one place: quotes, agreements, reports, and the signed copies with proof of who signed and when." A template fills itself from the record, goes out for signature, and the signed copy files itself to the person and the job.

Status: **not yet proven** in production (`shared/modules.md` section 1, call 8). Parts run today (generated reports with a shareable private link, reading uploaded documents and extracting fields); signing does not. Build signing to this spec.

The number: **median hours from sent to signed**, with documents out for signature longer than 7 days next to it.

## Users and permissions

Start from `shared/roles.md` section 4c. What differs or needs saying:

- **Owner, Admin:** every document and template, every verb. Template edits are Configure.
- **Staff:** View, Create, Edit, Send. Can fill a template, send for signature, file and share. Cannot edit templates, cannot void a signed document, cannot delete what they did not create.
- **Contractor:** `own` scope: documents on their records or that they created. Can create from a template and upload. Sending for signature goes to Admin as a request.
- **Customer:** portal (`/portal/documents`) and private report links: their own documents. View, sign (their Approve), download. Covered in `customer/portal/documents/PRD.md`.
- **Agent:** V C E. Sending for signature or sending a document by email is a Send and is gated. Filing a signed copy or an incoming upload is an Edit and is not gated. A document that a customer asked for (their report) is a system message and is not gated.
- **Sensitive fields:** documents marked `internal`, extracted fields marked sensitive on the template (ID numbers, policy numbers, health or case details). Column grant; stripped from the agent for users without it. Extraction never sends a sensitive document to a model the Owner has not allowed.
- **Signed is final.** Nobody edits a signed document. Void creates a new record and keeps the original with its audit trail.

## Pages and states

Tabs, in nav order (each a sub-route):

1. **All** `/admin/documents`: every document. Columns: title, kind, linked to (person, job, order), status chip, updated. Primary action per row: **Send** (draft, has the verb), **Open** (everything else).
2. **Templates** `/admin/documents/templates`: quotes, agreements, letters, reports. Each with merge fields, signer roles and a preview against a sample record.
3. **Out for signature** `/admin/documents/out`: sent and not complete, with who has signed, who has not, and days waiting. Primary action: **Remind**.
4. **Signed** `/admin/documents/signed`: completed documents with their certificate.

**Record view:** full route `/admin/documents/[id]`. Tabs: **Preview** (the rendered PDF), **Fields** (merged values and extracted values, each extracted value with its source page and a confidence), **Signers** (each signer, order, status, timestamps), **Audit** (every event: created, viewed, signed, voided, with IP and user agent), **Activity**. Read-only with **Edit** while draft; no Edit once sent.

**Quick views:** Drafts, Waiting over 7 days, Signed this week, Needs filing (uploads not linked to a record). Filters: kind, status, linked record, template.

**States:**

- Empty: "No documents yet. Start from a template or upload one." Buttons: **New from template**, **Upload**.
- Loading: list skeleton; the preview shows a page outline while the PDF renders.
- Error: "This PDF did not render. Try again." The merged data is kept; re-render does not lose fields.
- No access: no nav item; deep link shows the no-access page. A private report link with a wrong key shows not found.
- Read-only: a sent or signed document has no Edit; the actions are Remind, Void (Admin) and Download.
- Disabled with reason: **Send for signature** reads "Add an email for the second signer" or "2 merge fields are empty".

**Badge:** none on the nav. Out for signature shows a count of documents waiting over 7 days.

## Data model

Owned tables (each also carries `org_id`, `created_at`, `updated_at`, `deleted_at`):

| Table | Columns |
|---|---|
| `document_templates` | `id`, `key`, `label`, `kind text` (quote, agreement, letter, report, form), `body text` (template source), `merge_fields jsonb`, `signer_roles jsonb` (role, order, required), `sensitive_fields text[]`, `version int`, `status text` |
| `documents` | `id`, `template_id null`, `template_version int null`, `title`, `kind`, `status text` (draft, sent, partly_signed, signed, voided, uploaded), `subject_kind text`, `subject_id` (person, job, order, booking), `person_id → people null`, `job_id → jobs null`, `file_id → files` (current PDF), `signed_file_id → files null`, `data jsonb` (merged values), `extracted jsonb` (field, value, page, confidence), `internal bool`, `share_key text` (private link), `owner_id`, `custom jsonb` |
| `signatures` | `id`, `document_id`, `role text`, `order int`, `person_id → people`, `email`, `status text` (waiting, viewed, signed, declined), `signed_at null`, `signature_file_id null`, `sign_key text` (single-use link) |
| `signature_events` | `id`, `document_id`, `signature_id null`, `kind text` (created, sent, viewed, signed, declined, voided, reminded, downloaded), `ip inet`, `user_agent text`, `at` |

Foreign keys into shared tables: `people`, `files` (every PDF and upload), `messages` (send and remind emails), `approvals`, `change_log`. Signed PDFs carry a SHA-256 of the final file in `signature_events` so tampering is detectable.

**Row rules for `own`:** a Contractor sees a document when `owner_id` is them or its subject is a record they own. A Customer sees a document when they are its `person_id` or one of its signers, and it is not `internal`.

**Anchor kinds:** `document:<id>`, `template:<key>`, `field:document:<id>.<field>` (for example `field:document:301.deductible`), so a user can pin an extracted value and ask where it came from.

**Config knobs:**

- `fields.templates`: the starting set (quote, service agreement, report).
- `fields.signing`: on or off. Off hides Out for signature and Signed; documents are send and download only.
- `fields.remind_days`: default reminders at day 3 and day 7.
- `fields.kinds`: document kinds shown in filters.
- **Sample:** `documents`.

## Agent actions

| Action | Tool | Verb | Gated | Writes to `change_log` | Undo |
|---|---|---|---|---|---|
| Fill a template from a record | `fill_template` | C | No (lands as draft) | `documents` insert with `data` | Deletes the draft |
| Render the PDF | `render_document` | E | No | `documents.file_id` | Restores the previous file |
| Send for signature | `send_for_signature` | P | Gated (approval shows signers, order, and the PDF) | `signatures` insert, `signature_events` sent | Void before anyone signs |
| Send a document by email | `send_document` | P | Gated, except a report the recipient requested (system message) | `messages` insert | Logged; cannot unsend |
| Remind signers | `remind_signers` | P | Gated unless relaxed (limit: twice per document) | `signature_events` reminded | Logged only |
| Read an upload and extract fields | `extract_fields` | E | No; values with low confidence are left empty and flagged, never guessed | `documents.extracted` | Restores the prior extraction |
| File a document to a person and job | `file_document` | E | No | `documents.subject_*`, `job_documents` insert | Unfiles it |
| Void a sent document | `void_document` | D | Gated; never on a signed document without an Admin | `documents.status = voided` | Not undoable once voided; the original is kept |

**Background jobs:**

- **Reminders** (daily): reminds waiting signers on `fields.remind_days`.
- **Complete** (on the last signature): flattens the PDF, appends the certificate page, stores the hash, files the signed copy to the person and job, emails a copy to every signer (system message).
- **Needs filing** (on upload): tries to match the upload to a record; when unsure, it lands in Needs filing with the agent's best two guesses.

## Integrations

- **Email delivery** (default SendGrid): signing links, reminders, completed copies, report links.
- **Files:** object storage on the hosting provider; private by default, served through short-lived signed URLs.
- **PDF rendering:** server-side HTML to PDF in the app; no outside service required.
- **E-signature evidence:** signing is built in (consent to sign electronically, intent, single-use link, audit trail, final hash). The contract is the audit record in `signature_events`; keep it for the life of the document.
- **Webhooks out:** `document.signed`, `document.declined`.
- **Secrets (names only):** `EMAIL_API_KEY`, `BLOB_STORAGE_TOKEN`, `SIGN_LINK_SECRET`.

## SaaS replaced

| Product | Risk | Migration |
|---|---|---|
| DocuSign eSignature | Plan it | Export: every completed envelope as PDF with its certificate of completion. Import: each as an `uploaded` signed document linked to the person, original certificate kept as a file. Parallel run: new agreements go out from YEA while in-flight envelopes finish on the old account. Cutover: when the last in-flight envelope completes. Cancel, and keep the export archive for the retention period. |
| Dropbox Sign | Plan it | Same steps: export completed documents and audit trails, import as signed uploads, finish in-flight requests, cancel. |
| PandaDoc | Plan it | Export: templates and completed documents with audit trails. Import: rebuild templates as `document_templates`; signed documents as uploads. Parallel run until in-flight proposals close. Cutover, then cancel. |

## Acceptance criteria

1. A Contractor never sees documents outside their records, and a deep link to another document shows the no-access page with no title or signer names.
2. Every agent write (a draft filled, fields extracted, a document filed) appears in Log with before, after and a working Undo; Undo on filing removes the link from the job's Documents block.
3. When the agent sends an agreement for signature, the user sees an approval card with each signer, the signing order and a link to the exact PDF, and one Approve button; no signing email goes out before Approve.
4. Every submit button (Create, Render, Send for signature, Remind, Void) shows a spinner and disables while it runs.
5. A Customer signs from the emailed link; the document moves to Signed, the PDF gains a certificate page with names, times and IP addresses, and every signer receives the signed copy.
6. Staff opens a signed document; no Edit button renders, and the only actions are Download and Remind (disabled with "Already signed").
7. The agent extracts a deductible from an uploaded page it cannot read clearly; the field is left empty with "Could not read, page 2" and nothing is guessed.
8. A Customer opens their portal Documents; documents marked internal are not listed and a direct link to one returns not found.
9. An Admin switches `fields.signing` off; Out for signature and Signed tabs disappear and Send for signature is no longer offered.
10. A user changes a signed PDF file in storage by hand; the Audit tab shows "File does not match the signed hash".

## Open questions

1. **Build signing in, or keep a signing vendor as a rail?** Recommended default: build it in for standard agreements and quotes; keep a vendor only where a regulator names one.
2. **Template language?** Recommended default: HTML with `{{field}}` merge tags, rendered to PDF on the server; no word-processor files as templates.
3. **Retention of signed documents?** Recommended default: keep for 7 years and block delete; the Owner can set a different period per kind.
4. **Can a customer upload documents to a job?** Recommended default: yes, through the portal, landing in Needs filing until a person or the agent files them.
5. **Identity check before signing?** Recommended default: email link only; add an SMS code per template when the document is high value.
