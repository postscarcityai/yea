# Marketplace (admin, Sell)

- **Module key:** `marketplace` (stable, never renamed)
- **Tier:** industry (businesses that route or resell leads, bookings or work)
- **Route:** `/admin/marketplace`
- **Folder:** `admin/sell/marketplace/`

## Job

"Every request we cannot serve ourselves goes to the right partner in seconds, at the right price, paid from their prepaid balance, and nothing gets stuck." One customer request can imply several trades; each becomes its own lead, routed by the buyer's own criteria.

The number: **median seconds from a qualified request to a delivered lead**, with the count of stuck leads (qualified, not delivered) next to it.

Usually relabeled: Referrals or Lead buyers.

## Users and permissions

Start from `shared/roles.md` section 4c. What differs or needs saying:

- **Owner, Admin:** every tab and every verb. Recording a deposit, a refund or a manual adjustment is `$`; Admin can do it up to the Owner's per-entry cap.
- **Staff, Contractor:** hidden. The module carries buyer balances and prices.
- **Customer (partner kind):** portal only, own records: their purchased leads with the full file, their balance and ledger, their criteria (read), and an optional white-label intake on their own brand. Covered in `customer/portal/leads/PRD.md`.
- **Agent:** V E. Routing and debiting a lead that matches written criteria is a `$` action, gated by default. The Owner usually relaxes it with a limit (per-lead price cap, buyer must have balance), because routing has to happen in seconds. Manual sends, refunds and adjustments are always gated; refunds over the cap are never relaxable.
- **Sensitive fields:** the requester's contact details and uploaded documents on an assignment. Visible to the buyer only after delivery and only with the requester's recorded consent. `lead_prices` margin notes are Owner and Admin only.
- **Consent:** a lead is never routed without a consent record that names sharing with a partner, stored verbatim with its timestamp.

## Pages and states

Tabs, in nav order (each a sub-route):

1. **Buyers** `/admin/marketplace`: one row per buyer. Columns: name, status chip (active, paused, no funds), what they buy, balance, runway in days, last lead. Primary action per row: **Open**. Quick views: Active no funds, No criteria, Paused, Runs dry this week.
2. **Pricing** `/admin/marketplace/pricing`: the price and routing matrix. One row per lead type: price by severity or qualification band, max buyers per lead, exclusive or shared.
3. **Routing** `/admin/marketplace/routing`: the live feed of routing decisions. Each row shows the lead, the types it was split into, which buyers matched, who got it, the price and why the others did not.
4. **Ledger** `/admin/marketplace/ledger`: every deposit, debit, refund and adjustment across buyers, with running balances. Export to Money.
5. **Stuck** `/admin/marketplace/stuck`: qualified leads with no delivery. Each row says why (no matching buyer, no balance, buyer paused) with one action: **Retry** or **Send manually**.

**Record view:** full route `/admin/marketplace/buyers/[id]`. Tabs: **Criteria** (per lead type: regions, bands, sub-types, schedule, daily cap), **Ledger** (this buyer's entries and balance), **Delivered** (leads sent, viewed or not, disputes), **People** (logins for the portal), **White label** (when on: their intake page, preview or live, embed snippet), **Activity**. Read-only with **Edit**.

**States:**

- Empty: "No buyers yet. Add your first partner and what they buy." Button: **Add buyer**.
- Loading: table skeleton.
- Error: "Routing feed did not load. Try again." Routing itself runs server-side and never depends on this page.
- No access: no nav item for Staff or Contractor; deep link shows the no-access page.
- Disabled with reason: **Send manually** reads "No consent to share on this request" or "Buyer balance is $12, lead price is $45".

**Badge:** stuck leads plus buyers at zero balance with active criteria.

## Data model

Owned tables (each also carries `org_id`, `created_at`, `updated_at`, `deleted_at`):

| Table | Columns |
|---|---|
| `buyers` | `id`, `company_id → companies`, `status text` (active, paused, closed), `owner_id`, `notify_emails text[]`, `notify_sms text null`, `daily_cap int null`, `custom jsonb` |
| `buyer_criteria` | `id`, `buyer_id`, `lead_type_key text`, `regions text[]`, `bands text[]`, `subtypes text[]`, `schedule jsonb`, `active bool` |
| `lead_types` | `id`, `key text`, `label`, `derive_rules jsonb` (which requests imply this type), `max_buyers int`, `exclusive bool` |
| `lead_prices` | `id`, `lead_type_key`, `band text`, `price_cents int`, `currency`, `notes_internal text` |
| `assignments` | `id`, `lead_id → leads`, `lead_type_key`, `buyer_id`, `price_cents`, `status text` (delivered, viewed, disputed, refunded, failed), `consent_snapshot jsonb`, `delivered_at`, `viewed_at null`, `reason text` (why this buyer) |
| `routing_attempts` | `id`, `lead_id`, `lead_type_key`, `matched_buyer_ids uuid[]`, `outcome text`, `detail jsonb`, `at` |
| `ledger_entries` | `id`, `buyer_id`, `kind text` (deposit, debit, refund, adjustment), `amount_cents int` (signed), `balance_after_cents int`, `assignment_id null`, `reference text` (check, invoice, payment id), `approval_id null`, `entered_by` |
| `white_label_sites` | `id`, `buyer_id`, `slug`, `mode text` (preview, live), `brand jsonb` (logo file, palette), `embed_key text` |

Foreign keys into shared tables: `companies`, `people`, `leads` (from Grow > Leads), `files`, `approvals`, `change_log`. Debits and the balance update happen in one transaction with a row lock on the buyer, so a balance never goes negative.

**Row rules for `own`:** a partner Customer sees `assignments`, `ledger_entries` and `white_label_sites` where `buyer_id` belongs to a company they are a member of.

**Anchor kinds:** `buyer:<id>`, `assignment:<id>`, `lead_type:<key>`, `ledger:<id>`, `field:buyer:<id>.<field>`.

**Config knobs:**

- `label`: Marketplace, Referrals or Lead buyers.
- `fields.lead_types`: the starting list with derive rules.
- `fields.price_matrix`: price per lead type and band.
- `fields.white_label`: on or off. Default off.
- `fields.routing`: round robin among matching buyers (default) or highest bid.
- `fields.low_balance_days`: warn a buyer when runway drops under this. Default 7.
- **Sample:** `lead_buyers`.

## Agent actions

| Action | Tool | Verb | Gated | Writes to `change_log` | Undo |
|---|---|---|---|---|---|
| Split a request into every lead type it implies | `derive_lead_types` | C | No (rule-based, shows its reasons) | `routing_attempts` insert | n/a, a record of a decision |
| Score whether a request qualifies for a type | `qualify_lead` | E | No; rules first, a model may explain, never sets the price | `leads.custom.qualification` | Restores the prior score |
| Route and debit | `route_lead` | E, `$` | Gated by default. Usually relaxed with a limit (price under the per-lead cap, consent present, balance covers it) | `assignments` insert, `ledger_entries` debit | Refund entry plus `assignments.status = refunded`; the buyer is told |
| Retry stuck leads | `retry_routing` | E, `$` | Same gate as Route | as Route | as Route |
| Send a lead manually to a named buyer | `send_lead_manual` | E, `$` | Always gated; consent must be present | as Route | as Route |
| Record a deposit | `record_deposit` | C, `$` | Always gated | `ledger_entries` deposit | Reverse entry |
| Refund or adjust | `adjust_balance` | `$` | Always gated; over cap never relaxable | `ledger_entries` | Reverse entry |
| Warn a buyer who will run dry | `draft_email` | P | Gated unless relaxed | `messages` insert | Logged only |

**Background jobs:**

- **Route on qualify** (triggered when a lead is qualified with consent): derive, match criteria, check balance, debit, deliver, ping the buyer. Target under 10 seconds end to end.
- **Stuck sweep** (hourly): retries every stuck lead; anything older than 24 hours files a Board card for the Owner.
- **Runway** (daily): computes days of balance left per buyer from the last 30 days of debits; lists buyers under `fields.low_balance_days`.
- **Dispute window** (daily): closes disputes older than `fields.dispute_days` (default 7) as accepted.

## Integrations

- **Payments rail** (default Stripe) for buyer deposits by card or bank debit; checks and wires are recorded by hand with a reference. YEA holds a balance record, never money.
- **Banking rail** (default the business bank) for matching wire deposits by reference.
- **Email delivery** (default SendGrid): new lead pings, low balance warnings, portal sign-in links.
- **SMS rail** (optional, default Twilio): new lead pings to buyers who opt in.
- **Webhooks in:** payment succeeded (deposit), qualified lead (from Leads and Intake).
- **Webhooks out:** `lead.delivered` to a buyer's own system, signed, retried with backoff.
- **Secrets (names only):** `PAYMENTS_SECRET_KEY`, `PAYMENTS_WEBHOOK_SECRET`, `EMAIL_API_KEY`, `SMS_AUTH_TOKEN`, `BUYER_WEBHOOK_SIGNING_KEY`.

## SaaS replaced

`shared/saas.md` lists no product for this module. Lead distribution software was seen in the inventories but is not priced in the SaaS list, so nothing is claimed here. A business moving off one follows the standard steps: export buyers, criteria and balances; import balances as opening `ledger_entries` signed off by the Owner; run both for one week with routing live only in YEA; cut over the intake webhooks; cancel.

## Acceptance criteria

1. Staff and Contractors never see the Marketplace nav item, and a deep link to `/admin/marketplace/buyers/7` shows the no-access page with no buyer name or balance.
2. Every agent write (a routed lead, a deposit, a refund) appears in Log with before, after and a working Undo; Undo on a routed lead writes a refund entry and the buyer's balance goes back up by the price.
3. With routing not relaxed, a qualified lead creates an approval card naming the buyer, lead type, price and balance after, with one Approve button; no debit and no ping happen before Approve.
4. Every submit button (Add buyer, Save criteria, Record deposit, Retry, Send manually) shows a spinner and disables while it runs.
5. With routing relaxed under a $60 per-lead cap, a qualified lead priced at $45 with consent is delivered to a matching buyer within 10 seconds, the buyer's balance drops by $45, and the Routing tab shows why that buyer got it.
6. A buyer with $12 balance matches a $45 lead; the lead goes to the next matching buyer, and if none, lands in Stuck with "No balance" and the badge counts it.
7. A request has no consent to share; it never appears in Routing, and Send manually is disabled with "No consent to share on this request".
8. Two leads route to the same buyer at the same moment; the ledger shows two debits in order and the balance never goes below zero.
9. A partner Customer signs in to the portal and sees only their delivered leads and ledger, never another buyer's.
10. An Admin pauses a buyer; no new leads route to them and the Buyers list shows Paused.

## Open questions

1. **Exclusive or shared leads by default?** Recommended default: exclusive (max buyers 1) for every type; raise per type in Pricing.
2. **Does the agent route on its own from day one?** Recommended default: no. Gated for the first 20 routed leads so the Owner sees the decisions, then the Owner relaxes with a per-lead price cap.
3. **Refund policy for disputed leads?** Recommended default: one free dispute per 10 delivered leads within 7 days, reviewed by Admin; the agent drafts, a person approves.
4. **Do buyers bid?** Recommended default: no. Fixed prices from the matrix in v1; `fields.routing = highest_bid` is a later knob.
5. **White-label leads: charged or free?** Recommended default: free to the buyer whose page captured them, never routed to anyone else.
