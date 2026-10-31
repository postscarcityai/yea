# Portal: Documents (customer, portal)

- **Module key:** `portal.documents` (stable, never renamed)
- **Tier:** follows Documents (`documents`, common, not yet proven) or Content reports. Shows only when one of them is enabled.
- **Route:** `/portal/documents`
- **Folder:** `customer/portal/documents/`

Documents is not yet proven end to end: generated report PDFs and document requests run today, in-app signing does not. The signing flow below starts from the spec.

## Job

Every document between the customer and the business in one place: reports to download, agreements to sign, and files the business asked them to upload. The number that tells you it is working: **median time from "sent for signature" to "signed"**, and **share of requested uploads received without a follow-up**.

## Users and permissions

- Customer kinds and verbs (`shared/roles.md` 4g): `buyer` View; `partner` View and Approve (sign); `client` View, Approve (sign) and Export (download all). Shoppers and members do not see Documents.
- Sign is the customer's Approve verb on their own document. Only the named signer can sign; another store member sees it read-only with "Waiting on Pat Lee to sign".
- Uploads requested by the business create files in Library tagged to the request (Library grants customers own: Create).
- Agent (as the customer): View, find, summarize, upload a file the customer attached in chat to an open request. **Never signs.** Signing always happens by the customer's own hand on the signing screen; the agent can only open it.
- Sensitive fields: internal drafts, template internals, staff comments, other parties' contact details on a multi-party document unless the template marks them visible.

## Pages and states

- **Tabs:** To do (`/portal/documents`: waiting for my signature or upload), All (`/portal/documents/all`), Signed (`/portal/documents/signed`).
- **List row:** title, kind chip (Report, Agreement, Quote, Request), date, status chip, one primary action: Sign, Upload, or Download.
- **Record:** full route `/portal/documents/[id]` with an inline PDF viewer, details (sent by, sent on, related order, booking or job), and history (sent, viewed, signed, with time).
- **Sign** `/portal/documents/[id]/sign`: consent to sign electronically (one checkbox with the exact text stored), scroll through the document, place each required signature and initial by typing a name (drawn signature optional), Finish. On finish: a signed PDF with a certificate page (signer, email, time, IP, document hash) is filed and both parties get a copy by email.
- **Upload request:** the record shows what is asked ("Photo ID, front and back"), accepted file types, and an upload area; phones can take a photo directly.
- **States:** empty To do says "Nothing needs you right now." Loading skeletons. Error with Retry. A voided document shows "This document was withdrawn by the business" and no Sign button.
- **Disabled with reason:** Sign disabled with "Open every page to sign" until the viewer has reached the end; Finish disabled until every required field is filled.
- Badge: none in the nav (the map gives badges to Invoices and Leads only). Home lists every To do item.

## Data model

- Owns no tables. Reads `documents`, `signatures`, `signature_events` (Documents), `reports` (Intake), `job_documents` (Jobs), `files` (Library), through row rules on `customer_id` or the signer's person id.
- Writes `signatures` (fields placed, typed name, drawn image file id), `signature_events` (viewed, consented, signed, with time, IP and user agent), and `files` for uploads, each with `change_log`.
- The signed PDF is stored as a new `files` row; the original is never overwritten. Document hash (sha256) of the original and the signed copy are stored on `signature_events`.
- Anchors: `document:<id>`, `report:<slug>`, `doc_request:<id>`, `file:<id>`.
- Knobs (on Documents): `fields.signing` (on or off), `fields.templates`. Portal knob: `fields.documents.draw_signature` (default off). Sample: `documents`.

## Agent actions

| Action | Tool | Verb | Gated | Writes to `change_log` | Undo |
|---|---|---|---|---|---|
| Find a document ("my agreement from March") | `query_db` | V | No | Nothing | n/a |
| Summarize a document or point at a clause | `get_record`, `highlight` | V | No | Nothing | n/a |
| Open the signing screen | `navigate` | none | No | Nothing | n/a |
| Attach a photo or file from chat to an open upload request | `upload_to_request` | C | No | `files` insert linked to the request | Yes until staff accept it |
| Ask for a change to a document | `file_request` | C | No | Board card linked to the document | Yes while New |
| Download all my documents | `export_documents` | X | Yes | Log > Exports row | n/a |
| Sign | none | A | Never available to the agent | n/a | n/a |

Background jobs (owned by Documents, surfaced here): reminder to sign after 3 and 7 days, reminder for open upload requests, notice to the business when a document is signed or a file is uploaded.

## Integrations

- **Email delivery:** "Document ready to sign" and "Signed copy" emails, each with a link to the record.
- **Database / object storage:** originals, signed copies and uploads, served by short-lived signed URLs only.
- E-signature records follow the ESIGN Act and UETA basics: consent to sign electronically, the signer's ability to download a copy, and an audit trail tied to the document hash.
- Webhooks: none. Secrets: storage signing key (shared).

## SaaS replaced

| Product | Risk | Migration |
|---|---|---|
| DocuSign eSignature | Plan it | Export the completed archive with certificates of completion first, and import as signed documents (read-only, original certificates kept). Rebuild templates in Documents. Parallel run: send new agreements from YEA while old envelopes finish in the old tool. Cut over when no envelopes are open. Cancel, keeping the exported archive. |
| Dropbox Sign | Plan it | Same steps as DocuSign. |
| PandaDoc | Plan it | Export signed documents and audit trails; rebuild quote and proposal templates in Documents; parallel run until open documents close; cancel. |
| Dropbox (client file sharing folders) | Easy | Copy client folders into Library by person; replace shared links sent to clients with portal links; cancel the shared folders after one month. |

## Acceptance criteria

1. A shopper never sees Documents in the nav, and a deep link to `/portal/documents/55` shows the not-found page.
2. Every agent write on Documents (an upload to a request, a filed change request) appears in Log with before, after and a working Undo.
3. Asked to export all documents, the agent shows "Download 14 documents as a zip" with one Approve button and starts nothing until approved.
4. Every submit button on Documents, including Finish on the signing screen, shows a spinner and disables while it runs.
5. A client opens an agreement, consents, types their name in every required field, presses Finish, and the document moves to Signed with a downloadable PDF that has a certificate page.
6. Asked "sign it for me", the agent replies that only the customer can sign and opens the signing screen.
7. A partner store member who is not the named signer sees the agreement read-only with "Waiting on Pat Lee to sign".
8. A client uploads two photos to an ID request from a phone; the request shows Received and the files appear on the client's record in admin.
9. A document voided by the business shows as withdrawn, and its old signing link returns the record page with no Sign button.

## Open questions

1. **Allow drawn signatures?** Default: typed name only; drawn is a per-business option.
2. **Identity check before signing (SMS code)?** Default: off; on for documents whose template sets `requires_identity = true`.
3. **Multi-party signing order?** Default: sequential in the order the template lists signers.
4. **Keep reports from Intake here or only by private link?** Default: both. A signed-in customer sees every report tied to their email under All.
