# Portal: Invoices (customer, portal)

- **Module key:** `portal.invoices` (stable, never renamed)
- **Tier:** follows Money (`money`, common, not yet proven end to end). Shows only when Money is enabled.
- **Route:** `/portal/invoices`
- **Folder:** `customer/portal/invoices/`

Money is not proven end to end: invoices, aging and recorded payments run today; online payment through the rail does not. The pay flow below starts from the spec.

## Job

Show the customer what they owe and let them pay it in two taps, so the business gets paid faster and stops chasing. The number that tells you it is working: **days sales outstanding for portal customers** versus customers paying the old way.

## Users and permissions

- Customer kinds `buyer`, `member`, `partner`, `client`: View and Pay (`$`). Shoppers do not see Invoices; their receipts live on Orders.
- Buyers see invoices for the store chosen in the switcher. Store managers can pay; store members can view and download (see Open questions).
- Customers cannot edit, void or discount an invoice. A dispute is a request that lands on the Board and pauses reminders for that invoice.
- Agent (as the customer): View, explain, download. **Gated (customer's yes):** any payment, every time. The agent never stores or reads a card number; it opens hosted checkout or charges a saved method only after the customer approves the exact amount.
- Sensitive fields: internal notes, cost lines, tax setup details, other customers' invoices.

## Pages and states

- **Tabs:** Open (`/portal/invoices`: unpaid, oldest due first), Paid (`/portal/invoices/paid`), All (`/portal/invoices/all`).
- **List row:** number, issue date, due date, amount, balance due, status chip (Open info, Due soon warn, Overdue bad, Paid good, Disputed warn). One primary action: Pay for open invoices, Download for paid ones.
- **Select and pay:** select several open invoices; the floating bar shows the total and "Pay $1,240.00".
- **Record:** URL modal `?invoice=<number>`: lines, tax, total, payments applied, balance, related order or job, PDF download, Pay, Dispute.
- **Pay:** amount (full balance by default; partial if the business allows), saved method or new card or bank debit through hosted checkout, then a receipt screen and receipt email.
- **States:** empty Open says "You're paid up." Loading skeleton rows. Error with Retry. Payment failure returns to the record with the rail's reason in plain words ("Card declined. Try another card.").
- **Disabled with reason:** Pay disabled with "Payment is being processed" while a bank debit is pending; with "Online payment isn't set up. Reply to any of our emails to pay." when the payments rail is off.
- **Badge:** count of Open invoices that are due within 7 days or overdue, same scope as the list.

## Data model

- Owns no tables. Reads `invoices`, `payments`, `tax_rates` (Money) through row rules on `customer_id` or store `company_id`.
- Writes `payments` (status `pending`, then `succeeded` or `failed` from the rail webhook), and `cards` (Board) for disputes. A dispute sets `invoices.custom.disputed = true`, which pauses reminders.
- Saved payment methods are stored on the rail; YEA keeps only the rail's customer id and the last four digits and brand for display.
- Anchors: `invoice:<number>`, `payment:<id>`.
- Knobs (on Money): `fields.partial_payments` (default off), `fields.pay_methods` (card, bank debit), `fields.surcharge` (default off). Portal knob: `fields.invoices.members_can_pay` (default off). Sample: `invoices`.

## Agent actions

| Action | Tool | Verb | Gated | Writes to `change_log` | Undo |
|---|---|---|---|---|---|
| What do I owe | `query_db` | V | No | Nothing | n/a |
| Explain an invoice line | `get_record`, `highlight` | V | No | Nothing | n/a |
| Send me a copy of invoice 2041 | `email_invoice_copy` | V | No (a reply to the person who asked) | Nothing (logged in `messages`) | n/a |
| Pay one or more invoices | `pay_invoices` | $ | Yes, never relaxable for the agent | `payments` insert | No; refunds go through the business |
| Dispute an invoice | `file_request` | C | No | Board card, `invoices.custom.disputed` before and after | Yes while card is New |

Background jobs (owned by Money, surfaced here): reminder emails before due, on due and after due (stop when paid or disputed), payment receipt, failed payment notice.

## Integrations

- **Payments** (default Stripe): hosted checkout, saved methods, bank debit, webhooks for succeeded, failed and refunded. Contract: YEA creates a payment intent with the invoice number in metadata; the webhook is the only thing that marks an invoice paid.
- **Email delivery:** reminders, receipts.
- **Books:** paid invoices flow to the books export in Money; the portal does not talk to the books.
- Webhooks in: payment events. Secrets: `PAYMENTS_SECRET_KEY`, `PAYMENTS_WEBHOOK_SECRET` (shared with the shell).

## SaaS replaced

| Product | Risk | Migration |
|---|---|---|
| QuickBooks Online (client invoice and pay pages) | Careful | Moves last, with Money. Export open invoices and customer balances; import into Money with the same numbers. Parallel run through one full month-end close with invoices issued from YEA and books still in the old tool. Cut over customer payment links only after the close reconciles. Cancel only if Money runs the books (`fields.books`); otherwise keep it and sync. |
| FreshBooks (client portal) | Careful | Same steps as QuickBooks Online. |
| Wave (client invoice pages) | Careful | Same steps as QuickBooks Online. |
| Xero (online invoice pages) | Careful | Same steps as QuickBooks Online. |

## Acceptance criteria

1. A shopper never sees Invoices in the nav, and a deep link to `/portal/invoices?invoice=2041` shows the not-found page.
2. Every agent write on Invoices (a payment, a dispute) appears in Log with before and after, and Undo works on a dispute while it is New.
3. Asked to pay everything overdue, the agent shows "Pay invoices 2041 and 2044, $1,240.00, Visa ending 4242" with one Approve button and charges nothing until approved.
4. Every submit button on Invoices, including Pay, shows a spinner and disables while it runs.
5. A client pays an invoice by card; the invoice moves to Paid only after the rail confirms, and a receipt email arrives.
6. A failed card shows the rail's reason in plain words and the invoice stays Open.
7. The nav badge shows 2 when the customer has one overdue invoice and one due in 5 days, and 0 after both are paid.
8. A buyer disputes an invoice; reminders for that invoice stop and a Board card appears for the team with the invoice linked.
9. A store member (not manager) sees Pay hidden and can still download the PDF, when `members_can_pay` is off.

## Open questions

1. **Allow partial payments?** Default: off; the business turns it on in Money.
2. **Autopay for recurring invoices?** Default: off at launch; offer it after Money runs one clean month-end close.
3. **Pass card fees to the customer?** Default: no surcharge; bank debit is offered as the cheaper method.
4. **Can store members pay?** Default: managers only.
