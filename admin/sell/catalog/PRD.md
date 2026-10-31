# Catalog (admin, Sell)

- **Module key:** `catalog` (stable, never renamed)
- **Tier:** common
- **Route:** `/admin/catalog`
- **Folder:** `admin/sell/catalog/`

## Job

"What we sell, what it costs each kind of customer, what is in stock, and what is on sale, in one place that the shop, the portal and the reps all read from." A price change is scheduled, logged and reversible. A promotion starts and ends on its own.

The number: **out-of-stock variants that are still live in the shop** (target zero), with the count of variants under their low-stock threshold next to it.

## Users and permissions

Start from `shared/roles.md` section 4c. What differs or needs saying:

- **Owner, Admin:** every verb on every tab. Price changes and promotions are `$` actions: a person with the verb applies them directly; the agent asks first.
- **Staff:** View plus Edit on **Inventory only** (count, adjust, receive stock). Products, Pricing and Promotions open read-only. Cost and margin columns are hidden.
- **Contractor:** View only. Sees products, variants, stock status and the tier prices of the customers in their book, so they can sell and place orders. No cost, no margin.
- **Customer:** never sees this admin module. Shop product pages and Portal Reorder read from it at the customer's tier price.
- **Agent:** V E on stock. Every price change, every promotion, every promo code is `$` and gated. Bulk price edits over 5 variants always state the full list and wait, even if relaxed.
- **Sensitive fields (column grants):** `variants.cost_cents`, margin (computed), `price_changes.reason_internal`. Owner and Admin by default; a named role (Bookkeeper) can be granted them.

## Pages and states

Tabs, in nav order (each a sub-route):

1. **Products** `/admin/catalog`: grid or table of products, one row per product with variant count, stock status chip, 90-day units sold, status (draft, live, archived). Primary action per row: **Open**.
2. **Pricing** `/admin/catalog/pricing`: the pricing center. One row per variant: cost, retail, one column per tier from `fields.tiers`, margin per tier. Inline and bulk edits; each change is applied now or on a date; every change can be rolled back.
3. **Inventory** `/admin/catalog/inventory`: on hand, reserved by open orders, available, last counted date, low and out flags. Actions: Count, Adjust (with reason), Receive. Hidden when `fields.inventory` is off.
4. **Promotions** `/admin/catalog/promotions`: timed sales by product, variant, type or tag; promo codes with limits. States: scheduled, running, ended.

**Record view:** full route `/admin/catalog/[slug]`. Tabs: **Overview** (name, description, images from Library, status, tags), **Variants** (SKU, options, barcode, weight, stock), **Prices** (every tier for every variant plus the scheduled changes), **Sales** (90-day units and revenue by channel, read from Orders), **History** (every edit from `change_log` with Undo). Records open read-only with an **Edit** button. A promotion opens as a URL modal `?promo=<id>`.

**Quick views:** Live, Drafts, Low stock, Out of stock but live, Price change scheduled, On promotion. Filters behind Filter: type, tag, status, tier, stock state.

**States:**

- Empty: "No products yet. Add one, or ask the agent to import a CSV." Buttons: **New product**, and the chat tip.
- Loading: grid skeleton.
- Error: "Catalog did not load. Try again." with retry.
- No access: Customers get not found. Everyone else without view gets the no-access page.
- Read-only (Staff on Products, Pricing, Promotions): no Edit button, no inline inputs; the Inventory tab keeps its Count and Adjust actions.
- Disabled with reason: **Publish** reads "Add a price for every tier first". **Apply now** on a bulk change reads "Waiting on approval" while the agent's request is open.

**Badge:** none on the nav. The Inventory tab shows the count of variants low or out.

## Data model

Owned tables (each also carries `org_id`, `created_at`, `updated_at`, `deleted_at`):

| Table | Columns |
|---|---|
| `products` | `id`, `slug text unique per org`, `name`, `description text`, `type text`, `tags text[]`, `status text` (draft, live, archived), `image_file_ids uuid[]`, `owner_id`, `custom jsonb` |
| `variants` | `id`, `product_id`, `sku text unique per org`, `options jsonb` (size, flavor, pack), `barcode text`, `weight_oz int`, `cost_cents int`, `retail_cents int`, `currency`, `status text` |
| `price_tiers` | `id`, `key text` (from `fields.tiers`), `label`, `sort int` |
| `tier_prices` | `id`, `variant_id`, `tier_key`, `price_cents int`, `min_qty int` |
| `price_changes` | `id`, `variant_id`, `tier_key null` (null = retail), `from_cents`, `to_cents`, `effective_at timestamptz`, `status text` (scheduled, applied, rolled_back), `batch_id uuid`, `requested_by`, `approval_id → approvals null`, `reason_internal text` |
| `inventory` | `id`, `variant_id`, `location text default 'main'`, `on_hand int`, `reserved int`, `low_at int`, `last_counted_at` |
| `inventory_moves` | `id`, `variant_id`, `delta int`, `kind text` (count, adjust, receive, order, return), `reason text`, `order_id null` |
| `promotions` | `id`, `name`, `scope jsonb` (product ids, variant ids, types, tags), `kind text` (percent, amount, fixed_price), `value int`, `starts_at`, `ends_at`, `status text`, `tiers text[]` |
| `promo_codes` | `id`, `promotion_id`, `code text`, `max_uses int null`, `used int`, `per_customer int null` |

Foreign keys into shared tables: `files` (product images), `approvals` (price changes, promotions), `change_log` (every write), `users` (requested_by).

**Row rules for `own`:** Catalog has no owned rows for Contractors; they read all live products. Their tier-price view is filtered to tiers held by customers in their book.

**Anchor kinds:** `product:<slug>`, `variant:<sku>`, `promo:<id>`, `field:variant:<sku>.<field>` (for example `field:variant:TEA-12.retail_cents`). Pricing grid cells render `field:` anchors so a user can pin "this price" and ask about it.

**Config knobs:**

- `label`: Catalog, Products, Menu or Services.
- `fields.tiers`: default retail, wholesale, distributor. A service business often runs retail only.
- `fields.inventory`: on or off. Off hides Inventory, stock chips and low-stock jobs (services, digital goods).
- `fields.kinds`: product types (physical, digital, service, bundle).
- `fields.custom`: extra product fields (ingredients, warranty, duration).
- **Sample:** `products`.

## Agent actions

| Action | Tool | Verb | Gated | Writes to `change_log` | Undo |
|---|---|---|---|---|---|
| Answer price, stock and sales questions | `query_db`, `get_record`, `show_chart` | V | No | Nothing | n/a |
| Adjust stock after a count the user reports | `adjust_stock` | E | No; over 5 variants it states the list and waits | `inventory.on_hand`, `inventory_moves` insert | Writes the reverse move |
| Schedule a price change | `schedule_price_change` | E, `$` | Always gated (Approve card lists every variant, tier, old and new price, effective date) | `price_changes` insert, then `tier_prices` or `variants.retail_cents` at apply time | Rollback: a new `price_changes` row back to `from_cents`, status `rolled_back` on the original |
| Set up a timed promotion | `create_promotion` | C, `$` | Always gated | `promotions` and `promo_codes` insert | Ends the promotion now; codes stop working |
| Draft a new product from a description or photo | `draft_product` | C | No (lands as draft, not live) | `products`, `variants` insert | Deletes the draft |
| Publish a product | `update_record` | E | Gated (it goes live in the shop) | `products.status` | Sets back to draft |
| Flag low stock | background | V | No | Nothing on records; files a Board card | n/a |

**Background jobs:**

- **Apply scheduled prices** (every 15 minutes): applies due `price_changes` rows, writes `change_log` as system, posts one Feed line per batch.
- **Promotion clock** (every 15 minutes): starts and ends promotions on time.
- **Low stock** (daily, inventory on): lists variants at or under `low_at` and any out-of-stock variant still live; files one Board card and adds it to the Owner's morning summary.
- **Reserve** (on order Approved and Cancelled): moves `reserved` up or down.

## Integrations

- **Rails:** none required. Prices are stored here; charging happens in Shop and Money through the payments rail.
- **Files:** product images live in `files` on the business's object storage (default the hosting provider's blob store).
- **Webhooks out:** `catalog.price_changed`, `catalog.stock_low`, for marketplaces or feeds the business publishes to.
- **Platform APIs (optional):** a shopping feed for a search engine or a social shop, built as an export, not a sync engine in v1.
- **Secrets (names only):** `BLOB_STORAGE_TOKEN`.

## SaaS replaced

| Product | Risk | Migration |
|---|---|---|
| Shopify (catalog half) | Plan it | Export: products CSV with variants, images and inventory. Import: map to `products`, `variants`, `inventory`; keep handles as `slug` so product URLs survive. Parallel run: Shop reads YEA while the old store stays live but unlisted; compare prices variant by variant. Cutover: 301 every old product URL to the new slug. Cancel: after two weeks with no traffic on old URLs. |
| BigCommerce (catalog half) | Plan it | Same steps: export products and inventory, import with URL slugs kept, parallel run, 301 redirects, cancel. |
| Gumroad (catalog half) | Easy | Export: products and files. Import: each product as a `digital` kind with its file in Library. Cutover: change the links in bio and emails to the Shop page. Cancel the same day; every sale after cutover keeps the platform fee. |

## Acceptance criteria

1. A Customer opening `/admin/catalog` gets a not found page, and Staff without the module on gets the no-access page; neither sees a product name.
2. Every agent write (a stock adjustment, an applied price change) appears in Log with before, after and a working Undo; Undo on a price change restores the old price on the shop within one page load.
3. When the agent schedules a price change on 12 variants, the Admin sees one approval card listing all 12 with old price, new price, tier and effective date, and one Approve button; nothing changes before Approve.
4. Every submit button (Save, Publish, Apply now, Schedule, Count) shows a spinner and disables while it runs.
5. Staff opens a product; the Edit button is not rendered on Overview, Prices shows no cost or margin column, and the Inventory tab still offers Count and Adjust.
6. An Admin schedules a retail price change for tomorrow 09:00; at 09:15 the shop shows the new price and the Pricing tab shows the change as applied with a Rollback button.
7. A promotion with an end time passes that time; within 15 minutes its codes are rejected at checkout with "This code has ended" and the promotion shows Ended.
8. A Contractor opens a product; tier prices show only for tiers their customers hold, and no cost field renders.
9. A variant reaches zero on hand while live; it appears in Out of stock but live and in the next morning summary.
10. An Admin switches `fields.inventory` off; the Inventory tab, stock chips and the low-stock job stop on the next load.

## Open questions

1. **Does the shop hide out-of-stock variants or show them as sold out?** Recommended default: show as sold out with a "Tell me when it is back" option that adds the person to a Campaigns audience.
2. **Multiple stock locations?** Recommended default: one location (`main`) in v1; the column exists so a second location is a config change, not a migration.
3. **Do tier prices follow retail when retail changes?** Recommended default: no. Each tier is its own price; the Pricing tab offers "apply the same percent to every tier" as a bulk action.
4. **Who approves promotions?** Recommended default: Admin or Owner; the agent drafts only.
5. **Digital delivery?** Recommended default: a `digital` kind attaches a Library file and Orders sends a signed download link as the confirmation, valid 72 hours.
