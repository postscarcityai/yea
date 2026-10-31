# Shop (customer, public)

- **Module key:** `shop` (stable, never renamed)
- **Tier:** common
- **Route:** `/shop`, `/products/[slug]`, `/cart`, `/order/[number]`
- **Folder:** `customer/shop/`

## Job

The storefront. A shopper finds a product, adds it to the cart and pays in one page. A signed-in business buyer sees the same store at their tier price, with case packs first. Shop owns no catalog and no order queue: it reads Catalog and writes Orders, so there is one product list and one order list for every channel.

The number that tells you it is working: **cart to paid order conversion rate** (carts with at least one item that become a paid order within 24 hours, last 30 days). Secondary: checkout errors per 100 attempts.

## Users and permissions

Starts from `shared/roles.md` section 4g (Shop row) and the Catalog and Orders rows in 4c. What differs or needs saying:

- **Public visitors:** browse, search, filter, add to cart and check out as a guest when `fields.guest_checkout` is on. Guest checkout creates a `people` row with `kind = 'customer'` and no login; a sign-in link is offered on the order page.
- **Customer, shopper:** same as public plus saved cart, saved addresses, order history link to Portal Orders, and rewards balance if Programs is on.
- **Customer, buyer:** sees tier prices (`fields.business_pricing`), minimums and case packs, can buy for any store their login belongs to (store switcher in the top nav), and can pay by invoice if Money is on and the buyer's terms allow it. A buyer never sees retail margin or another tier's price.
- **Owner, Admin:** see Shop as the customer would, plus a preview bar to view it as any customer kind or tier. All editing happens in Catalog (products, prices, promotions) and Orders (fulfilment, refunds).
- **Staff:** read the storefront and preview it. No Shop-specific verbs.
- **Contractor:** hidden. A Contractor places orders for their own accounts through Orders, where they land as pending.
- **Agent, customer chat:** the portal chat runs as the signed-in customer. It answers product questions from Catalog data, checks stock, builds a cart, and applies an offer the customer is eligible for. **It never charges a card**: checkout is always a tap by the customer. Applying an offer that is not on the customer's account is gated (`$*`) and goes to Admin.
- **Agent, background:** runs as Admin. Price changes and new promotions belong to Catalog and are gated there (`$*`).
- **Sensitive fields:** cost, margin and other tiers' prices are never sent to the storefront or the customer chat. Payment details never touch the app; the payments rail holds them.

## Pages and states

Public top nav (from Site): Shop, then Cart with a live count and a hover peek. Signed-in customers also see their account menu and, if Programs is on, a rewards pill.

| Page | Route | What it shows |
|---|---|---|
| Shop | `/shop` | Product grid. Filters (collapsed): category, type, price, in stock. Sort: featured, newest, price. Buyers see case packs first. Every filter and sort in the URL |
| Product | `/products/[slug]` | Gallery, title, price (tier price for buyers), variant picker, stock line, buy box, description, specs, published reviews, questions with answers |
| Cart | `/cart` | Cart and checkout on one page: lines, quantity, remove, promo code, shipping method, address, contact, consent checkboxes, "How did you hear about us?", Pay |
| Order | `/order/[number]?k=<key>` | Order status by private key: lines, totals, status steps (Placed, Approved, Packed, Shipped, Delivered from Orders `fields.stages`), tracking, receipt download, a sign-in link to see it in Portal |

- **Record view:** none on the public side. The product page is the record. In the portal chat, a product is pinnable as `product:<slug>`.
- **Empty states:** no products live: "Nothing for sale yet." with a link home (and for Owner preview, a button to Catalog). Empty cart: "Your cart is empty." with the three best sellers. Filters with no match: "No products match these filters." with Clear filters.
- **Loading:** product grid and product page are cached; the cart shows line skeletons while prices and stock refresh. The Pay button holds a spinner until the payments rail answers.
- **Error:** out of stock between add and pay: the line turns red with "Only 2 left" and an update button, and Pay is disabled with that reason. Payment declined: the rail's plain message under Pay, cart kept. Shop off in config: `/shop` returns 404 and the nav item is gone.
- **Permission states:** a buyer price is never rendered to a signed-out visitor; it says "Sign in for business pricing" when `fields.business_pricing` is on. A pending business buyer (application not approved) sees retail prices and a status line.
- **Quick views (filters shipped by default):** In stock, New, On sale, and for buyers, Reorder favorites.
- **Badge:** the Cart count in the top nav (items in the current cart).

## Data model

Shop owns only cart state. Products, prices and stock belong to Catalog; orders, payments and refunds belong to Orders and Money.

| Table | Columns |
|---|---|
| `carts` | `id`, `org_id`, `session_id`, `person_id null`, `customer_id null` (signed-in user), `account_id null` (store a buyer is buying for), `tier_key`, `currency`, `promo_code_id null`, `source jsonb` (utm, referrer, "how did you hear"), `status` (open, checking_out, converted, abandoned), `order_id null`, `created_at`, `updated_at` |
| `cart_lines` | `id`, `cart_id`, `variant_id`, `qty int`, `unit_price_cents int` (snapshotted from Catalog at add), `currency` |
| `checkout_attempts` | `id`, `cart_id`, `payment_intent_ref`, `amount_cents`, `currency`, `result` (ok, declined, error), `error_text`, `at` |
| `product_questions` | `id`, `org_id`, `product_id`, `person_id`, `question`, `answer`, `answered_by` (user or agent), `status` (open, answered, hidden), `created_at` |

Foreign keys: `products`, `variants`, `price_tiers`, `tier_prices`, `inventory`, `promotions`, `promo_codes` (Catalog); `orders`, `order_lines` (Orders, written at checkout); `people` (guest or customer); `companies` (buyer's store); `files` (product images, receipts); `change_log`.

At checkout, in one transaction: re-price every line from Catalog, check stock, create the `orders` and `order_lines` rows, reserve inventory, mark the cart converted, write `change_log`. Payment confirmation from the rail moves the order to Placed.

Row rules: a cart is readable only by its `session_id` or `customer_id`. An order page needs its private key or the signed-in customer who owns it. Buyers read tier prices only for tiers on their account.

Anchor kinds (portal chat only, public pages render none): `product:<slug>`, `variant:<sku>`, `cart:<id>`, `cart_line:<id>`, `order:<number>`.

Config knobs: `fields.guest_checkout` (default on), `fields.business_pricing` (default off), `fields.min_order_cents` per tier, `fields.shipping_methods`, `fields.pay_by_invoice` (needs Money), `fields.questions` (product Q and A on or off), `fields.source_question` (the "How did you hear" options). Sample type: `products` (12 products with variants, two tiers, `.example` brand).

## Agent actions

| Action | Tool | Verb | Gated | Writes to `change_log` | Undo |
|---|---|---|---|---|---|
| Answer a product question in the customer chat | `get_record`, `search` | read | No | none | n/a |
| Check stock and price for this customer | `get_price` | read | No | none | n/a |
| Add, change or remove cart lines for the customer | `update_cart` | C, E (customer's own cart) | No | `cart_lines` before and after, actor Agent on behalf of the customer | Restores prior lines |
| Apply a promo the customer is eligible for | `apply_offer` | E | No | `carts.promo_code_id` before and after | Removes the code |
| Apply a discount not on the customer's account | `apply_offer` with `override` | E, $ | **Yes**, Admin approves, shows the new total | same, plus the approval id | Removes the code |
| Answer a stored product question | `answer_question` | E | Yes until the Owner relaxes Shop answers to "Go ahead" (it appears on a public page) | `product_questions` before and after | Restores prior answer |
| Send the shopper to checkout | `navigate` to `/cart` | UI | No | none | n/a |
| Charge a card | none | n/a | **Never**. Only the customer's own tap on Pay | n/a | n/a |

Background jobs:

- **Abandoned cart** (hourly): carts open with an identified person for 4 or more hours get one reminder email (a reply to their own action, so a system message, not a gated send), only if the person has not opted out. Marks the cart abandoned after 7 days.
- **Price and stock refresh** (on Catalog change): invalidates cached product and shop pages so a price change shows within a minute.
- **Question digest** (daily): open product questions with drafted answers go to Admin on Home > Today, one Approve per answer.

## Integrations

- **Rails:** payments (default Stripe; contract: the app creates a payment intent or checkout session for the server-computed total, the rail confirms by webhook, the app never sees a card number), email delivery (default SendGrid; order confirmation, receipt, abandoned cart, shipping updates), hosting, database.
- **Platform APIs:** a carrier rate and label API when Orders has shipping on; a sales tax calculation API if the business sells across tax jurisdictions (otherwise `tax_rates` from Settings).
- **Webhooks in:** payment succeeded, payment failed, refund issued, dispute opened (all from the payments rail, signature-checked, idempotent by event id). Carrier tracking updates.
- **Webhooks out:** none by default. Orders emits order events for any downstream system.
- **Secrets (names only):** `PAYMENTS_SECRET_KEY`, `PAYMENTS_WEBHOOK_SECRET`, `PAYMENTS_PUBLISHABLE_KEY`, `EMAIL_API_KEY`, `CARRIER_API_KEY` (if shipping), `TAX_API_KEY` (if used).

## SaaS replaced

| Product | Risk | Migration |
|---|---|---|
| Shopify | Plan it | Export products, variants, customers and order history; import into Catalog, People and Orders; build the redirect map for every product and collection URL; connect the same payments rail; run both stores in parallel for two weeks with the new one on a preview URL and test orders refunded; cut DNS; confirm redirects and order emails; cancel |
| BigCommerce | Plan it | Same as Shopify: catalog, customers, orders and SEO URLs move together, parallel run, cutover, cancel |
| Gumroad | Easy | Export products and buyer list, rebuild product pages in Catalog, move delivery files to Library, point old links at `/products/[slug]`, cancel |
| Kajabi | Plan it | Digital products and memberships only (courses are not a proven module): export members and active subscriptions, recreate the plans on the payments rail without double charging, email members their new sign-in link, run both for one billing cycle, cancel |
| Teachable | Plan it | Same as Kajabi: move members and recurring payments, keep student progress export on file, one billing cycle in parallel, cancel |

## Acceptance criteria

1. With Shop off, a visitor opening `/shop` gets a 404 and no Shop or Cart item renders in the top nav; an Owner previewing Shop with the module off sees the no-access page with a link to Settings > Modules.
2. Every agent write (cart change made in chat, offer applied, question answered) appears in Log with before, after and a working Undo, labeled "Agent, on behalf of" the customer.
3. When the agent tries to apply a discount the customer is not eligible for, the chat shows "Waiting on approval: 15% off, new total $84.00" and the cart total does not change until an Admin approves.
4. Every submit button (Add to cart, Apply code, Pay, Update quantity) shows a spinner and disables while it runs.
5. A signed-out visitor never sees a tier price in HTML, JSON or the chat; a signed-in buyer on the same product page sees their tier price and the case pack first.
6. A shopper who pays successfully lands on `/order/[number]` showing Placed within 3 seconds of the payment webhook, and gets one confirmation email.
7. If stock drops below the cart quantity between add and pay, Pay is disabled with "Only 2 left" under it and no charge is attempted.
8. Replaying the same payment webhook twice creates one order, not two.
9. A customer asks the portal chat "add two of the large size to my cart"; the cart count in the top nav changes, the line flashes, and the Changes tab shows the edit with Undo.
10. The agent never initiates a charge: no tool in the agent tool list can create a payment, and the Pay button is the only path to the payments rail.
11. An abandoned cart with an identified, opted-in person gets exactly one reminder email; a person who opted out gets none.

## Open questions

1. **Guest checkout?** Default: on for shoppers, off for buyers (business pricing always needs a signed-in, approved account).
2. **Hosted checkout page or an embedded payment form?** Default: the payments rail's hosted or embedded element that keeps card data off the app's servers, so PCI scope stays minimal.
3. **Tax calculation?** Default: flat rates from Settings for single-state businesses; switch on a tax API only when the business sells into more than one state.
4. **Pay by invoice for buyers?** Default: off until Money is on and the Owner sets terms per account.
5. **Product questions public?** Default: on, with every answer approved by a person until the Owner relaxes it.
6. **Cart expiry?** Default: 30 days for signed-in carts, 7 days for guest carts.
