# Portal: Reorder (customer, portal)

- **Module key:** `portal.reorder` (stable, never renamed)
- **Tier:** follows Orders and Catalog (`orders`, `catalog`, common). Shows only when Orders is enabled.
- **Route:** `/portal/reorder`
- **Folder:** `customer/portal/reorder/`

## Job

Let a repeat customer, most often a business buyer, place the next order in under a minute at their own price, without a rep or a phone call. The number that tells you it is working: **share of repeat orders placed self-serve** (portal page or portal chat) versus by phone, email or rep.

## Users and permissions

- Customer kinds `shopper`, `buyer`, `member`: View, Create. Buyers order at their store's price tier (`price_tiers` in Catalog) and can order for any store they belong to.
- Store members can build and place an order; whether a member's order needs a manager's yes is a store setting (`membership_role` rules, see Open questions).
- Payment: card through hosted checkout, or on account terms when the store has terms set in Money (an invoice is created instead of a charge).
- Agent (as the customer): View, Create a draft cart. **Gated (customer's yes):** placing the order and any charge. The agent always shows the full cart, total and payment method before it places.
- Sensitive fields: cost, margin, other tiers' prices, stock counts (show "In stock" or "Back soon", never a number), promotions not offered to this customer.

## Pages and states

One page, three blocks:

1. **Your usual:** products this customer (or store) bought before, with last quantity, last ordered date and the current tier price. Quantity steppers respect case packs and minimums from Catalog.
2. **Everything else:** the rest of the catalog the customer may buy, searchable, at their tier price.
3. **Cart summary** (sticky on the right on desktop, bottom sheet on mobile): lines, subtotal, promotions applied, shipping estimate, tax, total, store (buyers), ship-to, PO number (optional), payment method (card or terms), and one button, Place order.

Header shortcuts: **Same as last time** (fills the cart with the last order's lines) and a store selector for buyers.

States:
- **Empty:** a first-time customer sees only Everything else, with "Your usual fills in after your first order."
- **Loading:** skeleton rows; prices load with the rows, never after.
- **Error:** a price or stock check that fails blocks Place order with "Couldn't confirm prices. Retry."
- **Disabled with reason:** Place order is disabled with a reason when the cart is under the minimum ("Add $40 more to reach the $250 minimum"), when a required tax document is missing for a buyer ("Upload your resale certificate on Account to order at wholesale"), or when the store's terms are on hold ("Your account has an overdue invoice. Pay it to order on terms, or pay by card.").
- **Out of stock:** the line shows "Back soon" and the stepper is disabled with that reason.
- Badge: none. Home shows "Reorder due" when the store's usual cadence has passed.

## Data model

- Owns `reorder_carts`: `id`, `org_id`, `customer_id` (person), `company_id` (store, nullable), `lines jsonb` (variant sku, quantity; keys are content hashes, not positions), `source` (page, chat), `created_at`, `updated_at`, `deleted_at`. One open cart per person per store; it survives sign-out.
- Reads `products`, `variants`, `price_tiers`, `tier_prices`, `inventory`, `promotions` (Catalog), past `orders` and `order_lines` (Orders), terms and open invoices (Money).
- Writes on Place order: `orders` and `order_lines` (Orders) with `channel = portal`, then either a payment on the rail or an `invoices` row on terms (Money). The cart is soft-deleted.
- Reorder cadence per store: median days between the store's last five orders, computed nightly into `companies.custom.reorder_cadence_days`.
- Anchors: `product:<slug>`, `variant:<sku>`, `cart_line:<hash>`, `order:<number>` after placing.
- Knobs: `fields.reorder.min_order_cents` per tier, `fields.reorder.allow_terms` (default on for buyers with terms in Money), `fields.reorder.member_needs_manager` (default off). Sample: `orders` plus `products`.

## Agent actions

| Action | Tool | Verb | Gated | Writes to `change_log` | Undo |
|---|---|---|---|---|---|
| Build a cart from a sentence ("same as last time, double the large size") | `build_cart` | C | No | `reorder_carts` before and after | Yes |
| Answer price and availability at my tier | `query_db` | V | No | Nothing | n/a |
| Point at a product row | `highlight` | none | No | Nothing | n/a |
| Apply an offer the customer holds | `apply_offer` | E | No | cart line and offer claim | Yes |
| Place the order | `place_order` | C, $ | Yes, every time | `orders`, `order_lines`, payment or invoice | Cancel while Placed, per Orders |

Background jobs:
- **Reorder due nudge:** when a store passes its cadence by 3 days, a system email "Time to restock? Your usual is ready" with a link to `/portal/reorder?prefill=last`. Sent at most once per cadence. Counts as a reply-type system message only if the customer opted into reminders on Account; otherwise it is a send and goes through Campaigns.

## Integrations

- **Payments:** hosted checkout for card orders; saved payment methods per store. Terms orders create invoices in Money.
- **Email delivery:** order confirmation (from Orders), reorder nudge.
- Webhooks in: payment succeeded and failed (through Orders). Secrets: none of its own.

## SaaS replaced

| Product | Risk | Migration |
|---|---|---|
| Shopify (wholesale reorder and B2B price lists) | Plan it | Export price lists and customer-to-tier assignments; import into Catalog tiers. Export order history so Your usual is filled on day one. Parallel run: keep the old wholesale channel open for one full reorder cycle. Cut over by emailing each buyer a portal invite with their usual prefilled. Cancel the wholesale add-on after the cycle. |
| BigCommerce (B2B reorder) | Plan it | Same steps as Shopify. |

## Acceptance criteria

1. A partner or client never sees Reorder in the nav, and a deep link to `/portal/reorder` shows the not-found page.
2. Every agent write on Reorder (cart edits, placed order) appears in Log with before, after and a working Undo where the order can still be cancelled.
3. The agent asked "reorder my usual" fills the cart, then shows "Place order for Corner Store: 6 lines, $412.00, on terms (invoice due in 30 days)" with one Approve button and places nothing until approved.
4. Every submit button on Reorder shows a spinner and disables while it runs.
5. A buyer on the wholesale tier sees wholesale prices; the same product shows the retail price to a shopper.
6. A buyer with a cart under the minimum sees Place order disabled with the exact amount still needed.
7. A buyer presses Same as last time and the cart matches the last order's lines and quantities at today's prices.
8. A buyer with an overdue invoice sees terms unavailable with the reason and can still pay by card.
9. A customer adds items, signs out, signs in on another device and finds the same cart.

## Open questions

1. **Should a store member's order need a manager's yes?** Default: no; the store manager can turn it on per store.
2. **Show a suggested order from the agent (based on cadence and last quantities)?** Default: yes, as a "Suggested" chip above Your usual that the customer must accept; never auto-placed.
3. **Allow scheduled repeat orders (every 4 weeks)?** Default: no at launch; reorder nudges cover it without charging anyone automatically.
