# Portal: Orders (customer, portal)

- **Module key:** `portal.orders` (stable, never renamed)
- **Tier:** follows Orders (`orders`, common). Shows only when Orders is enabled.
- **Route:** `/portal/orders`, record `/portal/orders/[number]`
- **Folder:** `customer/portal/orders/`

## Job

Every order the customer placed, from any channel, with where it is right now, so nobody has to ask "where is my order". The number that tells you it is working: **"where is my order" messages per 100 orders** (falls as customers check here or ask the portal chat).

## Users and permissions

- Customer kinds `shopper`, `buyer`, `member`: View, Create (through Reorder). Partners and clients do not see Orders.
- Buyers see orders for the store chosen in the switcher; a manager sees every order for their stores, a member sees every order for their stores too (orders belong to the store, not the person).
- Customers can request a cancel, report a problem and request a return. They cannot cancel or refund directly: those land with the team as requests. Cancel is direct only while the order is still `placed` and unpaid, when Orders allows it (`fields.customer_cancel`).
- Agent (as the customer): View, Create requests. **Gated (customer's yes):** cancel an order, request a refund.
- Sensitive fields: cost, margin, internal notes, pick and pack assignee, carrier account. Never rendered.

## Pages and states

- **List** `/portal/orders`: table of orders, newest first. Columns: number, date, items (first item plus "and 3 more"), total, status chip, tracking link. One primary action per row: Track when shipped, Open otherwise.
- **Quick views:** Open (not yet delivered), Delivered, All. Filter (collapsed): date range, store (buyers).
- **Record** `/portal/orders/[number]` (full route, so it can be sent as a link). Tabs: Overview (lines with quantity and price, ship-to, payment summary, status timeline), Shipments (carrier, tracking, delivered date), Messages (emails the business sent about this order). Header actions: Reorder this, Report a problem, Download receipt.
- **States:** empty list says "No orders yet." with a button to Shop or Reorder. Loading skeleton rows. Error with Retry. An order number that is not theirs returns not found.
- Status chips map Orders stages: Placed (neutral), Approved (info), Packed (info), Shipped (info), Delivered (good), Cancelled (bad), Pending approval (warn, for orders a rep placed for them).
- Badge: none (Home shows open problems).

## Data model

- Owns no tables. Reads `orders`, `order_lines`, `shipments`, `refunds`, `order_emails` (Orders) through row rules on `customer_id` or store `company_id`.
- Writes: `cards` (Board) for problems and return requests with `source = portal` and `subject_kind = order`; `refunds` with `status = requested` for a return request; `orders.status = cancelled` only in the direct-cancel case.
- Anchors: `order:<number>`, `order_line:<id>`, `shipment:<id>`.
- Knobs: `fields.customer_cancel` (on Orders: allow direct cancel while placed and unpaid, default on), `fields.return_window_days` (default 30). Sample: `orders`.

## Agent actions

| Action | Tool | Verb | Gated | Writes to `change_log` | Undo |
|---|---|---|---|---|---|
| Where is my order | `get_record`, `query_db` | V | No | Nothing | n/a |
| Show tracking and point at the row | `highlight`, `navigate` | none | No | Nothing | n/a |
| Report a problem (damaged, missing item, wrong address) | `file_request` | C | No | Board card linked to the order, with photos if attached | Yes while card is New |
| Fix the ship-to before it is packed | `request_address_change` | C | No | Board card plus a proposed address on the order, applied by staff | Yes while pending |
| Cancel an order (direct-cancel case) | `cancel_order` | E | Yes | `orders.status` before and after | Yes until the business acts on it |
| Request a return or refund | `request_refund` | C, $ | Yes | `refunds` row `requested` | Yes while requested |
| Reorder this order | hands to Reorder | C | per Reorder | per Reorder | per Reorder |

Background jobs (owned by Orders, surfaced here): order status emails on each stage change, delivery confirmation, review request after delivery (Reviews).

## Integrations

- **Email delivery:** status emails already sent by Orders show on the Messages tab.
- **Payments:** receipts come from the payment record; refunds run on the rail only after a person approves in admin Orders.
- **Carrier label API** (where Orders shipping is on): tracking numbers and status webhooks feed Shipments.
- Webhooks in: carrier tracking events (through Orders). Secrets: none of its own.

## SaaS replaced

| Product | Risk | Migration |
|---|---|---|
| Shopify (customer order history) | Plan it | Moves with Shop, Catalog and Orders. Export orders with lines and customers; import to Orders keyed on the old order number so links still resolve. Parallel run while both stores take orders. Cut over with the storefront DNS. Cancel after the last old order ships. |
| BigCommerce (customer order history) | Plan it | Same steps as Shopify. |

## Acceptance criteria

1. A partner or client never sees Orders in the nav, and a deep link to `/portal/orders/1042` shows the not-found page.
2. Every agent write on Orders (a cancel, a refund request, a filed problem) appears in Log with before, after and a working Undo.
3. Asked to cancel order 1042, the agent shows "Cancel order 1042, 3 items, $86.00. You will not be charged." with one Approve button and changes nothing until approved.
4. Every submit button on Orders shows a spinner and disables while it runs.
5. A shopper opens a shipped order and sees the carrier, tracking number and a Track link that opens the carrier page in a new tab.
6. A buyer with two stores switches stores and the list shows only that store's orders.
7. A customer reports a damaged item with a photo; a Board card appears for the team with the photo and the order linked, and the order shows "Problem reported" on the customer's record.
8. A customer opens a delivered order 45 days old with a 30 day window; Request a return is not shown, and Report a problem still is.
9. Asked "where is my order" with no number, the agent finds the customer's open orders and answers with status and tracking for each, citing `[[order:1042|Order 1042]]`.

## Open questions

1. **Allow customers to edit quantities before packing?** Default: no; they cancel and reorder, or file a request.
2. **Show orders placed by a rep on the customer's behalf before they are approved?** Default: yes, as Pending approval, so the buyer can see what is coming.
3. **Return labels self-serve?** Default: no; a return request creates a Board card and staff send the label.
