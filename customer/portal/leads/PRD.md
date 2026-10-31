# Portal: Leads (customer, portal)

- **Module key:** `portal.leads` (stable, never renamed)
- **Tier:** follows Marketplace (`marketplace`, industry, businesses that route or resell leads or work). Shows only when Marketplace is enabled.
- **Route:** `/portal/leads`, record `/portal/leads/[id]`
- **Folder:** `customer/portal/leads/`

## Job

Give a partner firm that buys leads every lead it was sent, with the full file, so it can call fast and tell the business how each one went. The number that tells you it is working: **median minutes from lead delivered to lead first viewed**, and **share of delivered leads with an outcome reported** (contacted, won, lost).

## Users and permissions

- Customer kind `partner` only: View and Export (`shared/roles.md` 4g). Partners also Edit the outcome on their own leads (a status field on the assignment, not the lead).
- A partner firm can have several people; every member of the firm sees every lead delivered to the firm.
- The page shows only when the partner buys leads: a positive balance, any routing criteria, or a live white-label intake.
- Partners cannot see the price matrix, routing rules, other buyers, or leads not assigned to them. They see the price charged for each of their own leads.
- Agent (as the partner): View, summarize, set outcome, file a return request. **Gated (customer's yes):** export, and a return request (it asks for a credit, a `$` action the business approves).
- Sensitive fields: the homeowner or end customer's personal data is shown only for leads that consented to be shared with this buyer; the consent record is shown with it. Insurance policy fields show only on lead types that require them.

## Pages and states

- **List** `/portal/leads`: newest first. Columns: received, lead type, area (city, state), value signal (severity or estimated range), price or "No charge", outcome chip, NEW chip until first viewed. One primary action: Open.
- **Quick views:** New, Needs outcome (viewed over 48 hours ago, no outcome), Won, All. Filter (collapsed): lead type, date, outcome.
- **Record** `/portal/leads/[id]` (full route, linked from the new-lead email). Tabs: Overview (contact, address, consent time and the exact consent text, what they asked for), Details (answers, photos, report, interview transcript), Outcome (set Contacted, Booked, Won with value, Lost with reason, and a note). First view marks the lead viewed and stamps the time.
- **What I buy:** a panel on the list showing the firm's criteria (lead types, areas, filters) read-only, with "Ask for a change" (files a Board card).
- **Balance** strip at the top: prepaid balance and "Add funds" (links to Account > Balance).
- **States:** empty list says "No leads yet. New leads appear here and by email the moment they are routed to you." Loading skeleton rows. Error with Retry. Low balance banner: "Your balance covers about 2 more leads."
- **Badge:** count of leads delivered and not yet viewed.

## Data model

- Owns no tables. Reads `assignments`, `ledger_entries`, `buyer_criteria`, `lead_types` (Marketplace), `leads`, `lead_answers`, `lead_files`, `consents`, `reports` (Leads, Intake) through row rules: a partner reads a lead only through an `assignments` row whose `buyer_id` is their firm.
- Writes `assignments.outcome`, `assignments.outcome_value_cents`, `assignments.outcome_note`, `assignments.viewed_at`, and `cards` (Board) for return requests and criteria changes, each with `change_log`.
- A return request writes `ledger_entries` with `kind = credit_requested`; the credit itself is posted only when staff approve it in admin Marketplace.
- Anchors: `assignment:<id>`, `lead:<id>` (resolved only through the assignment), `field:assignment:<id>.outcome`, `buyer:<id>` (own firm).
- Knobs (on Marketplace): `fields.lead_types`, `fields.return_window_days` (default 7), `fields.return_reasons` (wrong area, duplicate, bad contact, not a real request). Sample: `lead_buyers`.

## Agent actions

| Action | Tool | Verb | Gated | Writes to `change_log` | Undo |
|---|---|---|---|---|---|
| What came in today | `query_db` | V | No | Nothing | n/a |
| Summarize a lead before I call | `get_record` | V | No | Nothing | n/a |
| Point at leads still needing an outcome | `highlight` | none | No | Nothing | n/a |
| Set an outcome ("mark 31 as won, $4,800") | `update_record` on `assignments` | E | No for one lead; Yes for more than 5 at once | outcome fields before and after | Yes |
| Ask for a credit on a bad lead | `request_lead_return` | C, $ | Yes | `ledger_entries` credit_requested, Board card | Yes while pending |
| Ask to change what I buy | `file_request` | C | No | Board card | Yes while New |
| Export my leads to CSV | `export_leads` | X | Yes | Log > Exports row | n/a |

Background jobs (owned by Marketplace, surfaced here): new-lead email and optional SMS to the firm the moment a lead routes, low-balance warning when the balance covers fewer than 3 leads, "needs outcome" nudge after 48 hours.

## Integrations

- **Email delivery and SMS:** new-lead alerts with a link to the record, never the personal data in the message body.
- **Payments:** deposits through Account > Balance.
- **Object storage:** lead photos and report PDFs by short-lived signed URL.
- Webhooks out: an optional per-firm webhook that posts each new lead to the firm's own system, signed with a per-firm secret (`buyer_webhook_secret`, stored per buyer).

## SaaS replaced

None from `shared/saas.md`. Lead distribution software is not priced in the explorer yet; see admin Marketplace for what the inventories saw.

## Acceptance criteria

1. A non-partner customer never sees Leads in the nav, and a deep link to `/portal/leads/31` shows the not-found page.
2. Every agent write on Leads (outcomes, return requests) appears in Log with before, after and a working Undo.
3. Asked to export all leads, the agent shows "Export 48 leads with contact details to CSV" with one Approve button and exports nothing until approved.
4. Every submit button on Leads shows a spinner and disables while it runs.
5. A partner opens a NEW lead; the NEW chip clears, the nav badge drops by one, and admin Marketplace shows the viewed time.
6. A partner firm never sees a lead routed to another firm, even by changing the id in the URL.
7. A partner sets Won with $4,800; the value shows on the lead and on admin Marketplace for that buyer.
8. A partner requests a credit for a duplicate lead within the window; the balance does not change until staff approve, then a credit line appears in the ledger.
9. The new-lead email contains the lead type, area and a link, and no name, phone or address.

## Open questions

1. **Return window for credits?** Default: 7 days from delivery.
2. **Can partners pause their own lead flow?** Default: yes, a Pause switch on What I buy that stops routing until they resume; the change is logged.
3. **Show the firm how its outcomes compare to other buyers?** Default: no names, only "your win rate vs. the average".
