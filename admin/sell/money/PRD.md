# Money (admin, Sell)

- **Module key:** `money` (stable, never renamed)
- **Tier:** common
- **Route:** `/admin/money`
- **Folder:** `admin/sell/money/`

## Job

"What we are owed, what we were paid, and what we owe out, without retyping anything into the books." Invoices come from orders, jobs and bookings; payments match themselves; commission and payout statements build themselves at month end; the books get a clean export.

Status: **not yet proven end to end** (`shared/modules.md` section 1, call 8). Invoices, receivables, aging, payment recording, commission statements and a books export run in production today; card collection on invoices, payouts through a payments rail and running the books inside YEA do not. Build those to this spec.

The number: **days sales outstanding** (average days from invoice to paid), with cash owed over 30 days next to it.

## Users and permissions

Start from `shared/roles.md` section 4c. What differs or needs saying:

- **Owner:** every verb, plus the payments and banking rails, payout approval, and the books setting (`fields.books`). Only the Owner approves money out unless they delegate it to Admin (A†).
- **Admin:** View, Create, Edit, Approve (invoices and recorded payments), Send (invoices, reminders), Export, and `$` up to the Owner's caps. Cannot connect or change rails.
- **Staff:** hidden by default. A named role (Bookkeeper, an Admin type trimmed to Money V E X and Costs V) is the usual way to give a person access.
- **Contractor:** `own` scope, read only: their commission statements and payouts.
- **Customer:** portal (`/portal/invoices`): their own invoices. View, pay (`$`), download. Covered in `customer/portal/invoices/PRD.md`.
- **Agent:** V, C (draft invoices), P* (reminders, gated unless relaxed with a daily cap), and `$!`: any money out (payouts, refunds, transfers) needs a person every time and can never be relaxed. Recording a payment the agent matched is a draft that a person approves.
- **Sensitive fields:** the whole module is sensitive. Bank details on payouts show the last four only to everyone, including the Owner. Commission amounts are visible to the rep they belong to and to Owner and Admin.

## Pages and states

Tabs, in nav order (each a sub-route). `fields.tabs` can hide any of them.

1. **Invoices** `/admin/money`: every invoice. Columns: number, customer, source (order, job, booking, manual), issued, due, total, paid, status chip (draft, sent, partly paid, paid, overdue, void). Primary action per row: **Send** (draft), **Remind** (overdue), **Open**.
2. **Payments** `/admin/money/payments`: money in. Each payment with method, reference, matched invoice or "unmatched". Primary action: **Match** (unmatched), **Approve** (agent-recorded, waiting).
3. **Aging** `/admin/money/aging`: receivables by customer in 0 to 30, 31 to 60, 61 to 90, over 90 day buckets. Chart on top, table below, every cell a link to the invoices behind it.
4. **Payouts** `/admin/money/payouts`: money out to reps, partners and affiliates. Monthly statements, status (draft, approved, paid). Primary action: **Approve** (Owner), **Mark paid**.
5. **Books export** `/admin/money/books`: a month at a time, the invoices, payments, refunds and payouts as files the books import, or the sync queue when a books connection is on. Shows what was sent and what failed.

**Record view:** full route `/admin/money/invoices/[number]`. Tabs: **Invoice** (rendered, as the customer sees it), **Lines**, **Payments** (applied payments and refunds), **Emails** (sent and reminders), **History** (from `change_log`, with Undo). Payments and payouts open as URL modals (`?payment=<id>`, `?payout=<id>`). Read-only with **Edit** while draft; a sent invoice is corrected with a credit note, never edited.

**Quick views:** Overdue, Due this week, Unmatched payments, Waiting on approval, Paid this month. Filters: status, customer, source, date range, amount.

**States:**

- Empty: "No invoices yet. They come from orders and jobs, or create one." Button: **New invoice**.
- Loading: table skeleton; Aging chart shows its frame.
- Error: "Money did not load. Try again." A failed books sync shows a banner with the count of failed items and **Retry**, never a silent gap.
- No access: no nav item for Staff; deep link shows the no-access page with no amounts.
- Read-only: a Contractor sees Payouts with only their statements; other tabs are not rendered.
- Disabled with reason: **Send** reads "Customer has no email". **Approve payout** reads "Bank details not verified".

**Badge:** overdue invoices plus unmatched payments plus items waiting on approval, same scope as the list.

## Data model

Owned tables (each also carries `org_id`, `created_at`, `updated_at`, `deleted_at`). All money in integer cents with `currency`.

| Table | Columns |
|---|---|
| `invoices` | `id`, `number text unique per org`, `customer_id → people`, `company_id → companies null`, `source_kind text` (order, job, booking, manual), `source_id null`, `issued_on date`, `due_on date`, `terms text`, `subtotal_cents`, `tax_cents`, `total_cents`, `paid_cents`, `currency`, `status text`, `pay_key text` (private pay link), `owner_id`, `custom jsonb` |
| `invoice_lines` | `id`, `invoice_id`, `description`, `qty numeric(10,2)`, `unit_cents int`, `tax_rate_id null`, `line_total_cents int` |
| `credit_notes` | `id`, `invoice_id`, `amount_cents`, `reason text`, `approval_id` |
| `payments` | `id`, `customer_id`, `amount_cents`, `currency`, `method text` (card, bank, check, wire, cash, other), `reference text`, `rail_ref text null`, `received_on date`, `status text` (recorded, waiting_approval, matched, refunded), `recorded_by` |
| `payment_applications` | `id`, `payment_id`, `invoice_id`, `amount_cents` (one payment can pay several invoices) |
| `payouts` | `id`, `payee_user_id null`, `payee_company_id null`, `period text` (YYYY-MM), `amount_cents`, `status text` (draft, approved, paid), `approval_id`, `rail_ref text null`, `paid_on null`, `bank_last4 text` |
| `commission_statements` | `id`, `user_id`, `period text`, `basis jsonb` (orders and payments counted, rate), `amount_cents`, `payout_id null` |
| `tax_rates` | `id`, `region text`, `rate_bp int` (basis points), `label`, `active bool` |
| `books_sync` | `id`, `period text`, `kind text` (invoice, payment, refund, payout), `subject_id`, `status text` (queued, sent, failed), `error text null`, `external_ref text null` |

Foreign keys into shared tables: `people`, `companies`, `users`, `messages` (invoice and reminder emails), `approvals`, `change_log`. Orders, Jobs and Bookings write invoices through one function, `issue_invoice(source_kind, source_id)`, so totals are computed in one place.

**Row rules for `own`:** a Contractor sees `commission_statements` and `payouts` where they are the payee. A Customer sees `invoices` and their `payments` where `customer_id` is their `people` row or a company they belong to.

**Anchor kinds:** `invoice:<number>`, `payment:<id>`, `payout:<id>`, `statement:<id>`, `field:invoice:<number>.<field>`. Aging cells render a `query:` anchor ("Customer X, 31 to 60 days, 4 invoices").

**Config knobs:**

- `label`: Money, Billing or Finance.
- `fields.tabs`: which tabs show and in what order.
- `fields.books`: `keep` (default: export to the current books) or `run_in_yea` (YEA is the ledger; only after a full parallel close).
- `fields.terms`: default due on receipt; net 15 and net 30 available.
- `fields.reminder_days`: default 3 days before due, on due, 7 and 14 days after.
- `fields.commission`: off, or a rate rule (percent of paid revenue per rep).
- `fields.money_out_cap_cents`: per-action and monthly caps for Admin.
- **Sample:** `invoices`.

## Agent actions

| Action | Tool | Verb | Gated | Writes to `change_log` | Undo |
|---|---|---|---|---|---|
| Answer "who owes us and how much" | `query_db`, `show_chart`, `highlight` | V | No | Nothing | n/a |
| Draft an invoice from an order, job or booking | `draft_invoice` | C | No (draft, not sent) | `invoices`, `invoice_lines` insert | Deletes the draft |
| Send an invoice | `send_invoice` | P | Gated | `invoices.status = sent`, `messages` insert | Void plus a note to the customer; the email itself stays sent |
| Send reminders on overdue invoices | `send_reminder` | P | Gated unless relaxed (daily cap, business hours) | `messages` insert | Logged only |
| Match a payment to invoices | `match_payment` | E, `$` | Gated: lands as waiting_approval | `payment_applications` insert, `invoices.paid_cents` | Unmatch, restoring the invoice balances |
| Build monthly commission and payout statements | `build_statements` | C | No (drafts) | `commission_statements`, `payouts` insert as draft | Deletes the drafts |
| Pay out, refund, transfer | `send_payout`, `refund_payment` | `$!` | Always gated, never relaxable, Owner or delegated Admin | `payouts.status`, rail call | Not undoable once the rail confirms; a reversal is a new entry |
| Export a month to the books | `export_books` | X | Gated (it takes data out) | `books_sync` rows | Re-export replaces the file; the books side is fixed there |

**Background jobs:**

- **Overdue** (daily 06:00): marks invoices overdue, queues reminders on `fields.reminder_days`, adds overdue totals to the Owner's morning summary.
- **Payment intake** (webhook): a rail payment creates a `payments` row and tries to match it by pay link or amount and customer; unsure matches wait in Unmatched.
- **Month end** (1st of the month): drafts commission statements and payouts for last month, and queues the books export.
- **Books sync** (when a books connection is on, hourly): pushes queued items, records failures with the error, never retries a duplicate.

## Integrations

- **Payments rail** (default Stripe; Square or PayPal fit): invoice pay links, card and bank payments, refunds, and payouts where the rail supports them. YEA never sees a card or full account number.
- **Banking rail** (default the business bank, read-only): balances and incoming transfers for matching checks and wires by reference. YEA never holds money.
- **Payroll tax rail** (default Gusto or Rippling): commission that runs through payroll is exported to the payroll provider as earnings, not paid by YEA.
- **Books** (default keep the current accounting product): monthly export files, or a sync through its API. Contract: one row per invoice, payment, refund and payout with the same ids, idempotent on re-send.
- **Email delivery** (default SendGrid): invoices, receipts, reminders.
- **Webhooks in:** payment succeeded, refunded, payout paid (payments rail); bank transaction (banking rail).
- **Secrets (names only):** `PAYMENTS_SECRET_KEY`, `PAYMENTS_WEBHOOK_SECRET`, `BANK_READ_TOKEN`, `BOOKS_OAUTH_CLIENT_SECRET`, `PAYROLL_API_KEY`, `EMAIL_API_KEY`.

## SaaS replaced

All four move last. Run the books where they are until YEA has matched them through one full month-end close.

| Product | Risk | Migration |
|---|---|---|
| QuickBooks Online | Careful | Export: customers, open invoices, payments, and the chart of accounts. Import: open invoices as live invoices, paid history as read-only. Parallel run: one complete month-end close with every invoice and payment in both, reconciled to the bank by the bookkeeper. Cutover: YEA issues invoices and sends the monthly export to the books (`fields.books = keep`). Cancel only if the CPA signs off on `run_in_yea`; most businesses keep the books product as the ledger. |
| Xero | Careful | Same steps as QuickBooks Online: export, import open invoices, one full parallel close, cut over invoicing, cancel only with CPA sign-off. |
| FreshBooks | Careful | Export: clients, open invoices, payment history. Import open invoices first so no reminder is missed. Parallel run through one close. Cutover: send new invoices from YEA. Cancel after the last old invoice is paid or moved. |
| Wave | Careful | Same steps as FreshBooks. |

## Acceptance criteria

1. Staff without a Money grant never sees the nav item, and a deep link to `/admin/money/invoices/1001` shows the no-access page with no customer or amount.
2. Every agent write (an invoice drafted, a payment matched, statements built) appears in Log with before, after and a working Undo; Undo on a match restores the invoice's open balance.
3. When the agent prepares a payout, the Owner sees an approval card with payee, period, amount, bank last four and the statement behind it, and one Approve button; Agents > Permissions shows no "Go ahead" switch for payouts.
4. Every submit button (Send, Record payment, Match, Approve, Mark paid, Export) shows a spinner and disables while it runs.
5. A Customer pays an invoice from the pay link; within one minute the invoice shows Paid, the payment shows matched, and the customer gets a receipt.
6. An Admin tries to edit a sent invoice; Edit is not rendered and the action offered is **Credit note**.
7. A Contractor opens Money; only Payouts renders, showing only their own statements.
8. A bank transfer arrives without a reference; it lands in Unmatched and the badge counts it, and the agent suggests the two most likely invoices without applying either.
9. The books export for a month runs twice; the books receive no duplicate rows, and the Books export tab shows the second run as "no changes".
10. An Admin opens Aging and clicks the 61 to 90 cell for one customer; the Invoices tab opens filtered to exactly those invoices.

## Open questions

1. **Run the books in YEA or keep the books product?** Recommended default: keep the books product (`fields.books = keep`) and export monthly. Revisit only after three clean parallel closes and CPA sign-off.
2. **Sales tax: compute or look up?** Recommended default: a rate table per region the Owner maintains, plus a warning when an invoice ships to a region with no rate.
3. **Partial payments?** Recommended default: yes; the invoice shows Partly paid and reminders state the remaining balance.
4. **Card surcharge or convenience fee?** Recommended default: off. Owner can turn it on per region where it is allowed.
5. **Who approves money out when the Owner is away?** Recommended default: nobody. Payouts wait; the Owner can delegate approval to one named Admin with a monthly cap.
