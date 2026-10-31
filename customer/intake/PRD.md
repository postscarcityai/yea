# Intake (customer, public)

- **Module key:** `intake` (stable, never renamed)
- **Tier:** core
- **Route:** `/start` and its steps, `/r/[slug]`, `/resume/[token]`, `/e/[slug]` (white label, Marketplace only)
- **Folder:** `customer/intake/`

## Job

Turn a visitor into a lead with the least typing, and give them something useful back right away: a report, an estimate, a place on the list, or a booked time. Every run lands in Leads with its answers, photos, consent and where the visitor came from.

The number that tells you it is working: **start to finish rate** (runs that reach the last step divided by runs that answered step 1, last 30 days). Secondary: median time from finish to first human or agent reply in Leads.

## Users and permissions

Starts from `shared/roles.md` section 4g (Intake row). What differs or needs saying:

- **Public visitors:** run any live intake with no login. A run is tied to an anonymous cookie until the visitor gives an email or phone.
- **Customer:** owns their runs (`own: V C D`). They resume a draft from a link, see their report at `/r/[slug]`, see every run on that email in Portal Documents, and delete their own data. Deleting is a hard delete of photos, uploaded documents and answers, logged without content (one of the two hard-delete cases in `shared/roles.md`).
- **Owner, Admin:** configure kinds, steps, questions and the price table (Settings tab on Intake, needs K), read every run, export.
- **Staff:** read runs and reports (`V`). They work the resulting lead in Leads, not here.
- **Contractor:** hidden. A Contractor sees a run only through a lead assigned to them in Leads.
- **Agent:** creates reports and sends them to the requester (`V C`). The report, the resume link and the receipt are replies to the person who asked, so they are system messages and need no approval. The agent **never writes a price**: estimates come from `fields.price_table` rules. Routing a lead to a paying buyer is a Marketplace `$*` action and is gated there.
- **Sensitive fields:** photos, uploaded documents (insurance pages, IDs, medical or case details) and free-text answers the Owner marks sensitive are column-level grants. Staff without the grant see "Photo (sensitive)" placeholders and the agent strips those fields from query results for them. Photos are stripped of location and camera data in the browser and again on the server.

## Pages and states

Public pages use the Site top nav except the steps themselves, which use a **focused header**: logo, step indicator, no other links (fewer exits on paid traffic).

Kinds (`fields.kind`), one or more per business, each with its own slug:

| Kind | Flow | Gives back |
|---|---|---|
| `form` | Short multi-step form (2 to 5 steps) | Confirmation and a time to expect a reply |
| `application` | Multi-step form plus vetting | Status page; Admin sees a vetting verdict |
| `waitlist` | Name, email, optional phone | Welcome email and their place on the list |
| `photo_report` | Describe, safety screen, details, photos, adaptive interview, analysis, result | A cited report and a rules-based estimate at `/r/[slug]`, emailed as a PDF |
| `booking` | Two questions, then hands off to Bookings | A booked time |

Routes:

| Page | Route |
|---|---|
| Start (picker or the single kind) | `/start`, `/start/[kind]` |
| Steps | `/start/[kind]/[step]` (each step a route so the back button works and analytics see each step) |
| Off-ramp | `/start/[kind]/other` (the request is out of scope; guidance, no lead charge) |
| Result | `/start/[kind]/result` |
| Report | `/r/[slug]` (unguessable slug, noindex, print-ready) |
| Resume | `/resume/[token]` |
| White label | `/e/[slug]`, `/e/[slug]/embed` (only with Marketplace on: the same flow in a partner's logo and colors) |
| Sample report | `/sample` (built from seed data, same component as a real report) |

**Admin side** has no nav item: runs land in **Leads** (a run is a tab on the lead record: Answers, Photos, Report, Consent, Source). Intake's knobs sit on Settings > Intake (`/admin/settings/intake`, tabs: Kinds, Steps, Questions, Price table, Consent text).

- **Empty state (admin):** "No intake runs yet. Share your Get started link." with a copy-link button and a preview.
- **Loading:** each step renders instantly from config. The analysis step streams real progress lines ("Reading 4 photos", "Checking the price table") and never fakes a progress bar. Interview planning falls back to the static question list after 25 seconds or when the agent is off.
- **Error:** a failed upload keeps the step and shows Retry per photo. A failed analysis keeps every answer, shows "We saved your answers. We'll email your report within the hour." and files a Board card. Rate limits return a plain "Too many tries from this network, try again in a few minutes" page (limits per IP plus email, loose enough for a crowd on one network).
- **Permission states:** a report slug that does not exist or was deleted shows a normal 404. A customer who deleted their run lands on a "Deleted" confirmation page. Staff without the sensitive grant see placeholders, not a lock.
- **Quick views (in Leads):** New from intake, Unfinished (resume link sent), Waiting on vetting, Off-ramp.
- **Badge:** counted in Leads (new runs that finished and have no reply yet).

## Data model

| Table | Columns |
|---|---|
| `intake_runs` | `id`, `org_id`, `kind`, `slug text unique` (report slug), `status` (started, in_progress, finished, abandoned, off_ramp, deleted, from `fields.stages`), `step`, `person_id null`, `lead_id null`, `customer_id null`, `anon_cookie`, `source jsonb` (utm, click ids, referrer, landing path, white-label slug), `resume_token_hash`, `vetting jsonb` (application only: verdict, score, reasons), `custom jsonb`, `created_at`, `updated_at`, `finished_at`, `deleted_at` |
| `intake_answers` | `id`, `run_id`, `question_key`, `value jsonb`, `asked_by` (config or agent plan), `answered_at` |
| `intake_photos` | `id`, `run_id`, `file_id`, `glance text`, `order int`, `requested_by_question_key null` |
| `reports` | `id`, `run_id`, `slug`, `body jsonb` (sections; each observation carries the `intake_photos.id` it cites), `estimate jsonb` (line items from the price table: rule key, qty, unit cents, total cents, currency), `pdf_file_id`, `version int`, `created_by` (agent or system), `created_at` |
| `consents` | `id`, `org_id`, `person_id`, `run_id`, `channel` (email, sms, phone, share_with_partner), `text` (verbatim, as shown), `granted bool`, `ip`, `user_agent`, `at` |

Foreign keys into shared tables: `people` (created or matched by email or phone at the first contact field; `people.consent` updated from `consents`), Leads (`leads.intake_run_id`; one lead per run, or one per trade the run implies when Marketplace splits it), `files` (photos, uploaded documents, report PDF), `threads` and `messages` (report email, resume link), `change_log`.

Row rules: public reads a run only by its anonymous cookie or resume token; a report only by its slug. A signed-in customer reads runs where `customer_id` or the matched `people.email` is theirs. Staff read all runs in the org, with sensitive columns stripped without the grant.

Anchor kinds: `report:<slug>`, `intake_run:<id>`, `intake_answer:<id>`, `intake_photo:<id>`, `field:intake_run:<id>.<field>`. The customer can pin their own report and photos in the portal chat; staff pin them from the lead record.

Config knobs: `fields.kind` (list of enabled kinds), `fields.steps` (per kind, ordered), `fields.questions` (per step: key, label, type, required, options, show-if), `fields.price_table` (photo_report only: rules keyed by observation and quantity), `fields.consent_text` (verbatim per channel), `fields.off_ramp` (what is out of scope and the guidance shown), `fields.vetting` (application only: checks to run), `fields.stages`. Sample type: `intake_runs` (20 runs across kinds, `.example` emails, 555-01xx phones, stock photos with no people).

## Agent actions

| Action | Tool | Verb | Gated | Writes to `change_log` | Undo |
|---|---|---|---|---|---|
| Classify the free-text description into a kind or the off-ramp | `classify_request` | C | No | `intake_runs.kind` and `status` before and after | Restores prior kind |
| Glance at photos while the visitor waits | `glance_photos` | C | No | `intake_photos.glance` insert | Clears the glance |
| Plan the interview from the photos (up to 8 questions, price-critical first; replans when a requested photo arrives) | `plan_interview` | C | No | plan stored on the run | Falls back to the static plan |
| Read an uploaded document (fields extracted as text, nulls instead of guesses) | `read_document` | C | No | `intake_answers` insert with `asked_by = 'agent'` | Deletes the extracted answers |
| Write the report: observations each citing a photo, hidden risks, next steps | `write_report` | C | No | `reports` insert | Previous version restored; the slug keeps working |
| Price the estimate | `price_from_table` (rules, not a model) | C | No | `reports.estimate` | Restores prior estimate |
| Send the report and resume link to the requester | `send_report` | system message | No (a reply to the person who asked) | `messages` insert | n/a (sent mail cannot be unsent); logged |
| Vet an application: domain, mail records, website, phone format, repeat match, then a verdict "Looks legit", "Check" or "Red flags" with reasons | `vet_application` | C | No | `intake_runs.vetting` | Clears the verdict |
| Create or update the lead | `update_record` on Leads | C, E | No | Leads insert | Soft-deletes the lead |
| Route the lead to a paying buyer | Marketplace `route_lead` | $ | **Yes** unless the Owner relaxed Marketplace routing with a cap | Marketplace ledger | Marketplace refund flow |
| Delete a run on the customer's request | `delete_run` | D (customer's own) | No when the customer asks in their own chat; **yes** when anyone else asks | logged without content | None (hard delete, by design) |

Background jobs:

- **Resume nudge** (hourly): a run with an email and no finish for 2 hours gets one resume email. Once only.
- **Post-report follow-up** (daily): one email 2 days after the report if no reply in Leads. Once only.
- **Abandoned close** (daily): runs idle for 30 days move to abandoned; their photos stay until the retention window in Settings > Data, then purge.
- **Weekly funnel note** (Mondays): drop-off per step with the worst step named and a suggested question change, ready to approve on Settings > Intake.

## Integrations

- **Rails:** email delivery (default SendGrid; contract: report, receipt and resume link from the business's own domain, one-click unsubscribe header on every follow-up), SMS (default Twilio; only with a `consents` row for SMS), payments (default Stripe; deposits on the `booking` kind only), database, hosting, file storage for photos (private bucket, signed URLs that expire).
- **Platform APIs:** an ad platform's conversion API when the business runs paid ads (finish fires a conversion with the stored click id); a bot check on the first step.
- **Webhooks in:** email events (delivered, bounced, spam report) to suppress future follow-ups. **Webhooks out:** `intake.finished` with run id and lead id, for any outside system.
- **Secrets (names only):** `EMAIL_API_KEY`, `SMS_ACCOUNT_SID`, `SMS_AUTH_TOKEN`, `PAYMENTS_SECRET_KEY`, `STORAGE_BUCKET_KEY`, `BOT_CHECK_SECRET`, `ADS_CONVERSION_TOKEN` (optional).

## SaaS replaced

| Product | Risk | Migration |
|---|---|---|
| Typeform | No brainer | Rebuild each form as an intake kind, export old responses to CSV and import as runs on the matching people, swap embeds and links to `/start/[kind]`, cancel |
| Tally | No brainer | Same as Typeform |
| SurveyMonkey | No brainer | Rebuild surveys as `form` kinds, export results, let the agent write the analysis, cancel |
| Jotform | Easy | Check first for forms that take payments or collect health data; rebuild those with the payments rail and the sensitive-field grants, import old submissions, swap links, cancel |

## Acceptance criteria

1. A Contractor never sees Settings > Intake, and opening `/admin/settings/intake` shows the no-access page with Request access; a Contractor sees a run only inside a lead assigned to them.
2. Every agent write (classification, report, vetting verdict, lead created) appears in Log with before, after and a working Undo.
3. When the agent would route a lead to a paying buyer, an approval card shows the buyer, the price and the balance after debit, and no money moves until a human approves (unless the Owner relaxed routing with a cap).
4. Every submit button (Next, Upload, Send me my report, Join the list, Delete my data) shows a spinner and disables while it runs.
5. A visitor finishing a `photo_report` run sees a report where every observation links to the photo it came from, and every dollar figure comes from a `price_table` rule shown in the estimate lines.
6. A visitor who gives an email on step 2 and leaves receives exactly one resume email, and the link reopens the run at the step they left.
7. A finished run creates exactly one lead in Leads (or one per trade with Marketplace splitting on), with source, consent and answers on the lead record.
8. The consent text a visitor agreed to is stored verbatim in `consents` and shown on the lead's Consent tab exactly as the visitor saw it.
9. A signed-in customer taps Delete my data on a run; photos, documents and answers are gone, `/r/[slug]` returns 404, and Log shows a hard-delete row with no content.
10. With the agent off or slow past 25 seconds, the interview falls back to the static questions and the visitor can still finish.
11. A Staff user without the sensitive grant opens a lead from intake and sees "Photo (sensitive)" placeholders, and the agent's answers to that user never quote those fields.
12. An `application` run shows Admin a verdict chip (Looks legit, Check, Red flags) with the reasons listed, and nothing is approved without a person.

## Open questions

1. **Which kinds ship on day one?** Default: `form` for every business; add `photo_report` when the business prices from what it sees, `application` for B2B or partner programs, `waitlist` before launch.
2. **Ask for email early or late?** Default: optional on step 2 with "Email me a link to finish later", required only at the result step.
3. **Show the estimate on screen or only in the email?** Default: on screen and in the PDF, as a range with the rule lines visible.
4. **Report link public or sign-in only?** Default: public by unguessable link, noindex, with a sign-in link to keep it in Portal Documents.
5. **Photo retention?** Default: 365 days after the run finishes, then purge; delete on request any time.
6. **Bot check on step 1?** Default: an invisible check plus a honeypot field; a visible challenge only after rate limits trip.
