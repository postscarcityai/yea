# Leads (admin, Grow)

- **Module key:** `leads`
- **Tier:** core
- **Route:** `/admin/leads`
- **Folder:** `admin/grow/leads/`

## Job

"Everyone who raised a hand, in one queue, scored and answered fast." A form fill, an application, a consult request, a waitlist signup, a business card photo: each becomes one lead with its answers, files, source and consent, and nobody waits on a reply.

The number: **median time to first reply on a new lead**, shown on the Queue header and on Home. Second number: share of leads older than 24 hours with no reply (target 0).

## Users and permissions

Starts from `shared/roles.md` section 4b. Only the differences and specifics:

| User type | Leads |
|---|---|
| Owner, Admin | all |
| Staff | V C E P (all leads). No D, X, K |
| Contractor | own: V C E P. Own = `assignee_id` or `owner_id` is them. Applications in their territory show in Applied only if routing assigns them |
| Customer | own: V of their own submission and its report, in the portal. Never the admin record |
| Agent | V C E, P* (first reply, routed alert to a buyer), D* (spam, duplicates) |

- **Gated agent verbs:** P (any reply that is not a system confirmation of the person's own submission) and D. Approve is never the agent's: approving or declining an application is human every time.
- **Per-module relax:** the Owner can set "first reply: Go ahead" with a limit of business hours only and a daily cap (default 25). The relaxed reply must use an approved template; anything freer stays gated.
- **System messages, not sends:** the "we got it" confirmation and the requested report go out without approval (roles.md rule 6).
- **Sensitive fields (column grants):** `lead_answers` marked sensitive by the intake (health, legal, insurance details), `lead_files` of kind `id_document` or `insurance`, consent IP and user agent. Hidden from Staff without the grant, from Contractors always unless the lead is theirs and the Owner granted it, and stripped from agent query results for that user.

## Pages and states

Tabs in nav order (each a sub-route):

| Tab | Route | What it shows |
|---|---|---|
| Queue | `/admin/leads` | Every open lead, newest first. Table on desktop, cards on mobile. Columns: name, kind, source, score with reason, stage, owner, age, last touch |
| Applied | `/admin/leads/applied` | Leads of kind `application` waiting on Approve or Decline, each with the agent's vetting verdict |
| Map | `/admin/leads/map` | Leads with an address on a map, pin color by stage |
| Sources | `/admin/leads/sources` | Leads by source, campaign and landing page for 7, 30 and 90 days, with reply time and win rate per source |
| Settings | `/admin/leads/settings` | Stages, kinds, custom fields, routing rules, reply templates. Hidden without K |

**Record view:** full route `/admin/leads/[id]` (the record has tabs). Header: name, kind chip, stage chip, owner, score, primary action (Reply, or Approve on an application). Tabs:

1. **Overview**: answers in the order asked, key facts in the right column (contact, address, source, age, routed to).
2. **Files**: photos and documents, thumbnails, open in a lightbox.
3. **Attribution**: source, campaign, click id, landing page, referrer, first and last touch.
4. **Consent**: the verbatim consent text shown at submit, timestamp, channel (email, SMS, call), IP and user agent (sensitive).
5. **Activity**: timeline of replies, calls, notes, stage moves and agent writes with the Agent byline and Undo.

A light URL modal (`/admin/leads?lead=<id>`) opens from the Queue for a quick look; "Open full record" goes to the route.

**Quick views (chips above the Queue):** Needs reply, Assigned to me, Stuck (no touch in 48 hours), Applied waiting, Hot (score 80 and up). Filters behind the Filter button: stage, kind, source, owner, score band, date window. All in the URL.

**States:**

- **Empty:** "New inquiries land here the moment someone fills a form." One button: Add a lead. A second line links to Intake settings for the Owner and Admin.
- **Empty for a Contractor:** "No open leads in your book."
- **Loading:** table skeleton, 8 rows. Map shows tiles first, pins after.
- **Error:** "Leads didn't load. Try again." with a Retry button. Record route 404s show "This lead was deleted or never existed" with a link back to the Queue.
- **Permission:** without `leads.view` the nav item is hidden and a deep link shows the no-access page with Request access. Without E the record opens read-only with no Edit button. Approve on Applied is hidden for anyone without A. Sensitive answers are not rendered at all without the grant.
- **Disabled with reason:** Reply shows "Add an email or phone to reply" when the lead has neither; "Consent missing for SMS" on the Text action when no SMS consent is on file.

**Badge:** count of leads in Needs reply (new, no outbound touch yet) in the user's scope.

## Data model

Owned tables:

| Table | Columns |
|---|---|
| `leads` | `id`, `org_id`, `person_id` (fk `people`), `company_id` (fk `companies`, null), `kind` text (from `fields.kinds`), `stage` text (from `fields.stages`), `score` int 0 to 100 null, `score_reasons` jsonb, `vetting` text (`legit`, `check`, `red_flags`, null), `vetting_reasons` jsonb, `source` text, `intake_run_id` (fk Intake, null), `routed_to` jsonb (people or buyer ids), `first_reply_at` timestamptz, `last_touch_at` timestamptz, `next_step` text, `follow_up_on` date, `lost_reason` text, `converted_to` jsonb (`{ kind: "deal"|"job"|"customer", id }`), `custom` jsonb, `owner_id`, `assignee_id`, `customer_id`, `created_at`, `updated_at`, `deleted_at` |
| `lead_answers` | `id`, `lead_id`, `question_key`, `question_label`, `answer` jsonb, `sensitive` bool, `position` int |
| `lead_files` | `id`, `lead_id`, `file_id` (fk `files`), `kind` (`photo`, `document`, `id_document`, `insurance`, `card_scan`) |
| `consents` | `id`, `org_id`, `person_id`, `lead_id`, `channel` (`email`, `sms`, `call`), `text` (verbatim), `granted_at`, `ip`, `user_agent`, `revoked_at` |
| `attribution` | `id`, `lead_id`, `source`, `medium`, `campaign`, `click_id`, `landing_page`, `referrer`, `first_touch_at`, `last_touch_at` |

- **Shared:** `people` (every lead is a person; converting changes `people.kind`, never a new row), `companies`, `activities` (timeline, `subject_kind = 'lead'`), `files`, `threads` and `messages` (replies), `approvals`, `change_log`.
- **Row rules for `own`:** a Contractor reads and writes a `leads` row only where `assignee_id` or `owner_id` = their user id. A Customer reads only where `customer_id` = their user id, and only the columns the portal renders (no score, vetting, notes).
- **Anchor kinds:** `lead:<id>`, `field:lead:<id>.<field>` (for example `field:lead:12.email`, `field:lead:12.score`). Answer rows anchor as `field:lead:<id>.answer.<question_key>`.
- **Config knobs:** `fields.stages` (default New, Contacted, Qualified, Won, Lost), `fields.kinds` (default inquiry, application, consult, waitlist), `fields.custom`, `fields.routing` (`owner`, `round_robin`, `marketplace`), `fields.first_reply_template`, `fields.stuck_hours` (default 48).
- **Sample type:** `inbound_leads`. Seeds 40 leads across all kinds and stages, 6 applications in Applied, `.example` emails, 555-01xx phones, three sources, two with photos.

## Agent actions

| Action | Tool | Verb | Gated | Writes to `change_log` | Undo |
|---|---|---|---|---|---|
| Score a lead with plain reasons | `score_lead` | E | No | `leads.score`, `score_reasons` before and after | Restores the prior score |
| Vet an application (domain, phone, website, repeat match) | `vet_application` | E | No | `vetting`, `vetting_reasons` | Restores prior verdict |
| Draft the first reply | `draft_email` / `draft_sms` | C | No (draft only) | New draft message on the thread | Deletes the draft |
| Send the first reply | `send_message` | P | Yes (relaxable to business hours plus cap) | Message row, `first_reply_at`, `last_touch_at` | Not undoable once delivered; Log says so and offers a follow-up correction draft |
| Route to a person or a buyer | `route_lead` | E (P when it alerts an outside buyer) | Buyer alerts gated | `assignee_id` or `routed_to` | Unroutes and re-queues; buyer debits are reversed through Marketplace |
| Create a lead from a business card or badge photo | `create_lead_from_image` | C | No | New `leads` and `people` rows, the photo in `lead_files` | Soft deletes both rows |
| Move stage with a reason | `update_record` | E | No (bulk over 5 asks) | `stage`, reason in an activity | Restores stage |
| Convert to a deal, job or customer | `convert_lead` | C + E | Asks first | New target row, `converted_to`, `people.kind` | Removes the new row and restores kind |
| Mark spam or merge a duplicate | `update_record` / `merge_people` | D | Yes | `deleted_at` or merge map | Restores from Trash or unmerges |
| Log a call, visit or note | `log_activity` | C | No | Activity row | Removes the activity |

**Background jobs:**

- **On new lead (trigger):** score, vet if an application, draft the first reply, route by `fields.routing`, notify the owner. Produces a scored row and a draft in Needs reply within one minute.
- **Stale nudge (hourly):** leads past `fields.stuck_hours` with no touch get a nudge draft and a Home row "6 leads waiting over 48 hours".
- **Morning summary input (daily):** new leads, reply time, source mix, fed to the Home summary.

## Integrations

- **Email delivery** (default SendGrid; contract: send with a from-address on the business domain, signed event webhook for delivered, bounced, spam report, unsubscribe). Replies thread into Inbox.
- **SMS** (default Twilio; contract: send and receive on a registered number, delivery status callback, STOP handling writes `consents.revoked_at`).
- **Database** (default Neon Postgres) with row rules for `own` scope.
- **Platform APIs (optional):** an ad platform's offline conversion endpoint, fired when a lead with a click id reaches Qualified or Won. A maps tile source for the Map tab.
- **Webhooks in:** Intake submit (internal), inbound form posts from an external site (`POST /api/leads/inbound`, signed with `LEADS_INBOUND_SECRET`).
- **Webhooks out:** optional `lead.created` and `lead.won` to a URL the Owner sets.
- **Secrets by name:** `SENDGRID_API_KEY`, `SENDGRID_WEBHOOK_KEY`, `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `LEADS_INBOUND_SECRET`, `ADS_CONVERSION_TOKEN` (optional).

## SaaS replaced

Leads is not priced as its own line in `shared/saas.md`. CRM intake is part of the CRM entries, which re-key to Pipeline and People; forms re-key to Intake. Leads carries the intake half of those moves:

| Product | Risk | Migration step for Leads |
|---|---|---|
| Close | Easy | Export open leads and activity to CSV, import to `leads` and `activities` with source kept, run both for one week, cut over new form posts, cancel |
| Pipedrive | Easy | Export leads (not deals) to CSV, import, point web forms at Intake, cancel after one week of zero new leads in the old tool |
| Zoho CRM | Easy | Export leads with custom fields, map each to `fields.custom` first, import, parallel run one week, cutover, cancel |
| HubSpot Sales Hub Starter | Plan it | Export contacts with lifecycle stage and original source, import open leads only (history goes to People), keep forms on both for two weeks, compare counts daily, cut over, cancel |

## Acceptance criteria

1. A Staff user whose role lacks `leads.view` never sees Leads in the nav, and opening `/admin/leads/12` shows the no-access page with Request access and no lead name.
2. Every agent write on a lead (score, stage, route, draft) appears in Log with before, after and an Undo that restores the prior value.
3. When the agent wants to send a first reply and the module is not relaxed, the Owner sees an approval card in chat and on Home > Today that shows the recipient, channel and full text, with one Approve button; nothing sends until Approve.
4. Every submit button on Leads (Reply, Approve, Decline, Save, Convert) shows a spinner and disables while it runs, then re-enables with an inline result.
5. A visitor submits the Intake form; within 60 seconds an Admin sees the lead at the top of Needs reply with a score, at least one plain-language reason, and a drafted reply.
6. A Contractor opens the Queue and sees only leads assigned to them; the nav badge equals the count of their own Needs reply rows.
7. An Admin opens a lead record and sees the verbatim consent text, the timestamp and the channel on the Consent tab.
8. A Staff user without the sensitive grant opens a lead with a sensitive answer and the answer row is not rendered; the agent, asked in that user's chat, says it cannot see that field.
9. The Owner drops a business card photo into chat; a new lead appears with name, email and phone filled, and the photo on the Files tab.
10. An Admin clicks Convert to deal; a Pipeline record opens with the same person, and the lead shows Won with a link to the deal.
11. A lead untouched for 48 hours appears in the Stuck quick view and on Home with a nudge draft.
12. A Customer signed into the portal sees their own submission and report, and never sees score, vetting or notes.

## Open questions

1. **Default routing for a business with one person?** Recommended: `owner`. Switch to `round_robin` when a second Staff or Contractor joins.
2. **Relax first reply out of the box?** Recommended: no. Ship gated; suggest relaxing after the Owner approves 20 first replies with no edits.
3. **Stuck threshold?** Recommended: 48 hours for consumer leads, 24 hours for businesses selling an urgent service. Set by industry during the interview.
4. **Score model inputs?** Recommended: start from the answers plus source plus repeat match, and let the Owner override with a note; notes feed the next scoring pass.
5. **Keep a lead row after conversion?** Recommended: yes, read-only with stage Won and a link, so source reporting never loses the first touch.
6. **Map tab for businesses with no addresses?** Recommended: hide Map through `fields.tabs` when fewer than 10 percent of leads carry an address.
