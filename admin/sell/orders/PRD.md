# Orders (admin, Sell)

- **Module key:** `orders` (stable, never renamed)
- **Tier:** common
- **Route:** `/admin/orders`
- **Folder:** `admin/sell/orders/`

## Job

"Every order from every channel lands in one queue, and nothing sits there until a customer has to ask where it is." Shop checkout, a business buyer's reorder, a field rep placing an order for a store, and a phone order typed in by staff all become the same record and move through the same stages to delivered.

The number: **median hours from Placed to Shipped**, with the count of orders older than 48 hours in any one stage shown next to it.

## Users and permissions

Start from `shared/roles.md` section 4c. What differs or needs saying:

- **Owner, Admin:** all orders, every verb. Admin can approve pending orders and record refunds up to the Owner's per-refund cap; above it the refund becomes a request to the Owner.
- **Staff:** View, Create, Edit, Send on all orders. Can move stages, edit lines before Packed, print slips, buy labels, resend order emails. Cannot approve a pending order, cannot refund (the button reads **Request refund**), cannot delete, cannot export.
- **Contractor (field rep, partner):** `own` scope only: orders for customers in their book. Can place an order at the customer's tier price; it lands as **Pending** and waits for Admin approval. Read-only after that.
- **Customer:** portal only (`/portal/orders`, `/portal/reorder`), own orders. Covered in `customer/portal/orders/PRD.md`. This module serves their data.
- **Agent:** V C E. Send (customer emails that are not a direct status receipt) is gated. Every refund and every price override on a line is `$` and gated; refunds above the cap are never relaxable. In chat it runs as the signed-in person; a Contractor's chat sees only that Contractor's book.
- **Not a Send:** order confirmation, shipped and delivered notices, and the status page link. These are system messages to the person who ordered (`shared/roles.md` section 1, rule 6).
- **Sensitive fields (column grants):** `order_lines.unit_cost_cents`, line margin, `refunds.reason_internal`, payment method last four. Hidden from Staff and Contractor by default and stripped from the agent's query results for them.

## Pages and states

Tabs, in nav order (each a sub-route):

1. **Orders** `/admin/orders`: the queue. Columns: number, customer, channel, stage chip, total, age in stage, assignee. One primary action per row: **Approve** (Pending, approver), **Pack** (Approved, shipping on), **Open** (everyone else).
2. **Pack queue** `/admin/orders/pack`: two steps. Step one prints a slip and marks Packed. Step two weighs, gets rates, buys a label and marks Shipped. Hidden when `fields.shipping` is off.
3. **New order** `/admin/orders/new`: pick the customer (or a company and one of its locations), then the order form at that customer's tier price with live stock. Contractors see only their book in the picker.

**Record view:** full route `/admin/orders/[number]`. Tabs: **Lines** (items, quantities, tier price, line total, edit until Packed), **Ship-to** (address, address check result, carrier, tracking), **Emails** (every message sent about this order, with resend), **History** (every stage move and edit from `change_log`, agent writes bylined with Undo), **Payments** (payments and refunds against this order, read from Money). Header: number, customer, stage chip, total, primary action. Right column: channel, placed by, assignee, promo code, attribution source.

**Quick views** (chips above the list, collapsed filters behind Filter): Needs approval, Address problem, Ready to pack, Stuck (any stage older than `fields.stuck_hours`), Shipped today, Refund requested. Filters: stage, channel, customer, assignee, date range, has promo.

**States:**

- Empty: "No orders yet. They land here from the shop, the portal and New order." Button: **New order**.
- Empty for a Contractor: "No orders in your book yet." Button: **New order**.
- Loading: table skeleton, 8 rows.
- Error: "Orders did not load. Try again." with a retry button; the filter state survives.
- No access: no nav item. Deep link shows the no-access page with **Request access**.
- Read-only (Staff on a delivered order): Edit is not rendered. Quick actions they have (resend email, add note) remain.
- Disabled with reason: **Buy label** reads "Add a weight to get rates". **Approve** reads "Out of stock on 2 lines" until stock covers it or a person overrides.

**Badge:** count of orders in Placed or Pending plus orders flagged with an address problem, same scope as the list.

## Data model

Owned tables (every table also carries `org_id`, `created_at`, `updated_at`, `deleted_at` per `shared/data-model.md`):

| Table | Columns |
|---|---|
| `orders` | `id`, `number text unique per org`, `customer_id → people`, `company_id → companies null`, `channel text` (key from `fields.channels`), `stage text` (key from `fields.stages`), `placed_by_id → users`, `owner_id`, `assignee_id`, `subtotal_cents int`, `discount_cents int`, `shipping_cents int`, `tax_cents int`, `total_cents int`, `currency text`, `promo_code_id → promo_codes null`, `ship_to jsonb`, `address_status text` (ok, problem, fixed), `status_key text` (unguessable key for the public status page), `source jsonb` (attribution), `custom jsonb` |
| `order_lines` | `id`, `order_id`, `variant_id → variants`, `sku text`, `name text`, `qty int`, `unit_price_cents int`, `unit_cost_cents int`, `tier_key text`, `line_total_cents int` |
| `shipments` | `id`, `order_id`, `carrier text`, `service text`, `tracking text`, `label_file_id → files`, `weight_oz int`, `rate_cents int`, `status text`, `shipped_at`, `delivered_at` |
| `refunds` | `id`, `order_id`, `amount_cents int`, `currency`, `reason text`, `reason_internal text`, `requested_by`, `approval_id → approvals`, `payment_ref text`, `status text` (requested, approved, sent, failed) |
| `order_emails` | `id`, `order_id`, `kind text` (confirmation, shipped, delivered, address_problem, review_request, custom), `message_id → messages`, `sent_at`, `status text` |

Foreign keys into shared tables: `people`, `companies`, `users`, `files` (labels, slips), `messages` (every email), `approvals` (refunds, pending orders), `change_log` (every write).

**Row rules for `own`:** a Contractor sees an order when `orders.owner_id` is them or the customer's `people.owner_id` is them. A Customer sees an order when `orders.customer_id` maps to their `people` row or a company they belong to.

**Anchor kinds:** `order:<number>`, `order_line:<id>`, `field:order:<number>.<field>` (for example `field:order:1042.ship_to`). The record page renders a page marker with the order number, customer id and company id.

**Config knobs:**

- `fields.stages`: default Placed, Approved, Packed, Shipped, Delivered. Cancelled and Refunded are terminal states every business gets.
- `fields.shipping`: on or off. Off hides Pack queue, Ship-to tracking and the Packed stage.
- `fields.channels`: default retail, wholesale. Add phone, rep, marketplace as needed.
- `fields.stuck_hours`: default 48.
- `fields.refund_cap_cents`: per-refund cap for Admin and for a relaxed agent. Default 10000.
- `fields.review_after_days`: days after Delivered to queue a review request. Default 7. Needs Grow > Reviews on.
- `fields.custom`: extra order fields (PO number, delivery window).
- **Sample:** `orders`.

## Agent actions

| Action | Tool | Verb | Gated | Writes to `change_log` | Undo |
|---|---|---|---|---|---|
| Answer "where is my order" | `get_record`, `query_db` | V | No | Nothing | n/a |
| Find orders stuck in a stage and highlight them | `query_db`, `highlight` | V | No | Nothing | n/a |
| Create an order for a customer from chat (a reorder they asked for) | `create_order` | C | No for the customer's own reorder at list tier; yes when a price override or promo is applied (`$`) | `orders` and `order_lines` insert | Cancels the order if not yet Approved |
| Move an order to the next stage | `update_record` | E | No (bulk over 5: states the change and waits) | `orders.stage` before and after | Restores the prior stage |
| Fix a ship-to address the customer confirmed | `update_record` | E | No | `orders.ship_to`, `address_status` | Restores the old address |
| Flag an address problem and email the customer | `flag_address`, `draft_email` | E, P | The email is gated unless the module is relaxed | `orders.address_status`, `order_emails` insert | Clears the flag; a sent email cannot be unsent, the log says so |
| Draft a refund | `draft_refund` | C, `$` | Always gated. Above `fields.refund_cap_cents` never relaxable | `refunds` insert (requested), `approvals` insert | Withdraws the request before approval |
| Resend an order email | `resend_order_email` | E | No (system message to the person who ordered) | `order_emails` insert | n/a, logged |
| Add a note | `log_activity` | E | No | `activities` insert | Deletes the note |

**Background jobs:**

- **Stuck sweep** (hourly): finds orders older than `fields.stuck_hours` in one stage, sets a Stuck view count, files one Board card per day listing them. Writes `agent_runs` row.
- **Address check** (on Placed): validates the ship-to with the carrier API, sets `address_status`. Problem orders land in the Address problem view and the badge.
- **Delivered sync** (every 2 hours, shipping on): pulls carrier tracking, moves Shipped to Delivered, sends the delivered notice.
- **Review request** (daily): N days after Delivered (`fields.review_after_days`, default 7), queues a review request through Grow > Reviews.

## Integrations

- **Payments rail** (default Stripe; Square or PayPal also fit): charges happen in Shop or Money, never here. Orders reads the payment state by `payment_ref`. Refunds call the rail's refund endpoint only after an approval row says yes. YEA never sees a card number.
- **Email delivery** (default SendGrid; Postmark or Resend fit): confirmation, shipped, delivered, address problem. Contract: send from the business's authenticated domain, record the provider message id on `order_emails`, consume bounce webhooks.
- **Carrier label API** (only when `fields.shipping` is on): rates, label purchase, void, tracking. Any carrier or label aggregator; the contract is `get_rates`, `buy_label`, `void_label`, `track`.
- **Webhooks in:** payment succeeded and refunded (from the payments rail), tracking updates (from the carrier), email events (from email delivery).
- **Webhooks out:** `order.placed`, `order.stage_changed` for anything else the business runs.
- **Secrets (names only):** `PAYMENTS_SECRET_KEY`, `PAYMENTS_WEBHOOK_SECRET`, `EMAIL_API_KEY`, `EMAIL_WEBHOOK_SECRET`, `CARRIER_API_KEY`.

## SaaS replaced

| Product | Risk | Migration |
|---|---|---|
| Shopify (order half) | Plan it | Export: orders and customers to CSV through the admin export. Import: orders as history (stage Delivered, channel retail), matched to `people` by email. Parallel run: new orders flow through YEA while the old store stays read-only for two weeks; compare daily order counts and totals. Cutover: point checkout at Shop, redirect the old order status URLs. Cancel: after one clean billing cycle with no orders landing on the old store. |
| BigCommerce (order half) | Plan it | Same steps as Shopify: export orders, import as history, two-week parallel run, redirect status URLs, cancel after one clean cycle. |

## Acceptance criteria

1. A Contractor or Customer without `orders.view` never sees the Orders nav item, and a deep link to `/admin/orders/1042` shows the no-access page with no order number, customer or total on it.
2. Every agent write (a stage move, an address fix, a refund request) appears in Log with before, after and a working Undo; clicking Undo on a stage move puts the order back in its previous stage and the list re-renders.
3. When the agent drafts a refund, the Admin sees an approval card that states the order number, the amount, the payment method and the reason, with one Approve button; nothing is sent to the payments rail until Approve is clicked.
4. Every submit button (Approve, Mark packed, Buy label, Place order, Record refund) shows a spinner and disables while it runs.
5. A Contractor places an order from New order; it appears in the Admin's Needs approval view as Pending with the Contractor named as placed by, and the Contractor's own list shows the same order as read-only.
6. Staff opens a Placed order; the Refund button reads **Request refund**, and submitting it creates an approval for the Owner or Admin instead of a refund.
7. An Admin switches `fields.shipping` off in the module Settings tab; Pack queue disappears from the tabs and Packed disappears from the stage chips on the next load.
8. Staff opens an order record; no cost or margin column renders on the Lines tab, and asking the agent "what is the margin on this order" returns that the user cannot see cost.
9. An order sits in Approved longer than `fields.stuck_hours`; it appears in the Stuck view and the Orders badge count increases by one.
10. A Customer opens their order status link with the `status_key`; they see stage, lines and tracking, and no other order is reachable from that page.

## Open questions

1. **Where do payments get captured for wholesale orders on terms?** Recommended default: Orders never captures. Wholesale orders on terms create an invoice in Money at Approved; retail orders are paid at Shop checkout before they land.
2. **Can Staff edit lines after Approved?** Recommended default: yes until Packed, and each edit is logged; after Packed, lines are locked and changes go through a refund or a new order.
3. **Partial shipments?** Recommended default: off in v1. One shipment per order; a split ships as a second order linked in the note.
4. **Refund cap for Admin and the relaxed agent?** Recommended default: $100 per refund, $500 per month for the agent, Owner can change it.
5. **Order number format?** Recommended default: a per-org integer sequence starting at 1001, shown without a prefix.
