# Product brand with stores, reorders and reps

You make a product, sell it direct and through stores, and win the shelf with reps.

Machine-readable copy: `lib/yea-finale/playbooks/archetypes.ts` in the postscarcity-ai repo, id `product-brand`. Back to [all playbooks](README.md).

## Who pays and how

- Shoppers pay retail at checkout; shipping and tax from your own rules.
- Stores buy at wholesale (50% off retail) and distributors at 60% off, on card, net 15 or net 30.
- Reps earn commission on accounts they own at the time of the order; paid months lock.

## The core loop

1. **Find and score.** Every store in your markets, ranked by fit to your best accounts. `~/dev/peels/lib/fit-core.ts`
2. **Work the lead.** Drafted sequences and rep visits move a store from target to applied. `~/dev/peels/lib/sequences.ts`
3. **Apply and vet.** The store applies; the agent checks it is real and routes it to the rep for that state. `~/dev/peels/lib/vetting.ts`
4. **First order.** The first order turns the lead into an account. `~/dev/peels/app/order-actions.ts`
5. **Pack and ship.** Paid orders queue to pack, then weigh and label. `~/dev/peels/lib/pack.ts`
6. **Reorder and commission.** Each account's rhythm raises the reorder; commission credits the rep. `~/dev/peels/lib/accounts/now-core.ts`

## Modules on

| Module key | Label we used | Why |
|---|---|---|
| `orders` | Orders | every order, retail and wholesale |
| `leads` | Leads | stores from target to applied |
| `pipeline` | Accounts | stores that buy, with what to do now |
| `outreach` | Outreach | drafted sequences |
| `reps` | Reps | territories, leaderboard, goals |
| `prospects` | Markets | ideal customer and fit scores |
| `catalog` | Products | products, price tiers, inventory |
| `programs` | Giveaways | giveaways, offers, influencers |
| `social` | Posts | posts and what worked |
| `money` | Commission | commission and accounting exports |
| `shop` | Shop | the storefront |

Core modules (Home, Inbox, People, Views, Goals, Team, Agents, Board, Log, Settings, Site, Intake, Portal) are always on as well. See `shared/modules.md`.

## Stages we actually used

- **company lifecycle** (`leads`): target, prospect, engaged, applied, customer, lapsed, closed_lost. `~/dev/peels/db/072_lifecycle_engaged.sql`
- **order** (`orders`): pending, paid, packed, shipped, delivered, cancelled. `~/dev/peels/lib/pack.ts`
- **account now item** (`pipeline`): follow_up, unanswered, order, reorder, winback, quiet, sample. `~/dev/peels/lib/accounts/now-core.ts`
- **email campaign** (`campaigns`): draft, in_review, approved, scheduled, sending, sent, cancelled. `~/dev/peels/lib/email-campaigns.ts`
- **giveaway** (`programs`): draft, scheduled, live, closed, drawn, fulfilled. `~/dev/peels/lib/giveaways.ts`

## The agent's first three jobs

1. Every morning, list the accounts due to reorder and the ones going quiet, with the email already drafted.
2. Vet each wholesale application and route it to the rep who owns that state.
3. Draft next week's posts from real photos and what sold last week.

## Hero workflow: The reorder that was about to slip

Signed in as the contractor, approved by the contractor. The agent is "Account desk". Shows the play [Reorder rhythm](#reorder-rhythm).

Steps on screen: Pin the account > Ask > Order rhythm > Draft > Rep approves > Logged with Undo.

- **Pinned:** Account "Fernhill Market"
- **Ask:** "Fernhill used to order every few weeks. What happened and what should I send?"
- **Agent works:** Read 9 orders since March; Normal gap is 24 days, this one is at 37; Checked their last order: no Ginger Lime; Drafted a reorder note with a sample offer.
- **Reply:** "They are 13 days past their usual reorder and their last order skipped Ginger Lime, their best seller. The draft offers a free case of the new flavor with a reorder this week."
- **Approval:** "Send the reorder note to Dana at Fernhill from your address?" [Edit] [Send], then "Sent. Follow-up set for Thursday."
- **Log, with Undo:** Account desk sent the reorder note to Fernhill Market. Approved by the rep.

Names in the script are fictional.

## What it lets them cancel

Shopify, HubSpot Sales Hub Starter, Klaviyo, Mailchimp, Hootsuite, Canva, Gorgias. Prices and risk for each are in [shared/saas.md](../shared/saas.md).

## Rails kept

Vercel, Neon, Twilio SendGrid, Card processor (planned, not connected), Shipping label API (pending), Social posting API.

## Plays

Innovation plays first: things we built that most businesses like this do not have yet.

### Reorder rhythm (innovation)

<a id="reorder-rhythm"></a>The app learns each account's normal gap between orders and raises a reorder or win-back the day it slips.

- **Id:** `reorder-rhythm`
- **Modules:** `pipeline`, `orders`, `reps`
- **Fits when you see:** wholesale, reorder, stores, stockists, retailers, distributor, accounts
- **Proved in:**
  - `~/dev/peels/lib/accounts/now-core.ts`: median order gap, 30-day fallback under 3 orders, urgency score
  - `~/dev/peels/lib/accounts/now.ts`
  - `~/dev/peels/lib/email-flows.ts`: reorder nudge flow

### Territories, commission, leaderboard (innovation)

<a id="rep-territory-commission"></a>Reps own states, applications route to the right rep, commission sticks to the rep who owned the account, paid months lock.

- **Id:** `rep-territory-commission`
- **Modules:** `reps`, `money`
- **Fits when you see:** sales reps, reps, brokers, territory, territories, ambassadors, field sales
- **Proved in:**
  - `~/dev/peels/db/012_rep_routing.sql`
  - `~/dev/peels/db/013_commission.sql`
  - `~/dev/peels/lib/commission.ts`
  - `~/dev/peels/lib/leaderboard.ts`
  - `~/dev/peels/db/081_account_owner_history.sql`

### Which post sold (innovation)

<a id="post-to-order-attribution"></a>Every order is tied back to the post or email that brought it, and the agent drafts next week from what worked.

- **Id:** `post-to-order-attribution`
- **Modules:** `social`, `insights`, `orders`
- **Fits when you see:** instagram, tiktok, social, influencers, content, posts
- **Proved in:**
  - `~/dev/peels/lib/what-worked-core.mjs`
  - `~/dev/peels/db/055_order_attribution.sql`
  - `~/dev/peels/lib/post-learning-core.mjs`
  - `~/dev/peels/lib/auto-drafts-core.mjs`: weekly drafts from real assets only

### Wholesale applications, vetted

<a id="wholesale-application-vetting"></a>A store applies, the agent checks the email domain, the phone, the website and past records, and says looks legit, check, or red flags.

- **Id:** `wholesale-application-vetting`
- **Modules:** `leads`, `intake`
- **Fits when you see:** wholesale, become a retailer, stockist, carry our, apply
- **Proved in:**
  - `~/dev/peels/app/(store)/wholesale/page.tsx`
  - `~/dev/peels/lib/vetting.ts`
  - `~/dev/peels/lib/vetting-core.ts`
  - `~/dev/peels/lib/app-match.ts`

### The whole market, ranked by fit

<a id="icp-fit-scoring"></a>Rebuild the ideal customer from real customers, score every prospect with reasons, and work the list top down.

- **Id:** `icp-fit-scoring`
- **Modules:** `prospects`
- **Fits when you see:** b2b, stores, retailers, accounts, businesses, wholesale
- **Proved in:**
  - `~/dev/peels/lib/icp.ts`
  - `~/dev/peels/lib/fit-core.ts`
  - `~/dev/peels/lib/markets.ts`
  - `~/dev/peels/lib/prospecting-daily.ts`

### Sequences the agent drafts, a person sends

<a id="drafted-sequences"></a>Every step of a sequence is drafted for that account; it waits for a person to press Send unless auto-send is on, and stops on a reply.

- **Id:** `drafted-sequences`
- **Modules:** `outreach`
- **Fits when you see:** outreach, follow up, sales, prospects, b2b
- **Proved in:**
  - `~/dev/peels/lib/sequences.ts`
  - `~/dev/peels/db/082_sequence_auto_send.sql`
  - `~/dev/peels/app/api/cron/outreach/route.ts`
  - `~/dev/waterdamageiq/lib/outreach-sequence.ts`

### Price tiers and terms

<a id="wholesale-price-tiers"></a>Retail, wholesale and distributor prices from one list, with card or net terms per account.

- **Id:** `wholesale-price-tiers`
- **Modules:** `catalog`, `orders`
- **Fits when you see:** wholesale, distributor, net 30, bulk, case pack, msrp
- **Proved in:**
  - `~/dev/peels/db/001_init.sql`: price_tiers, tier_prices, accounts.terms
  - `~/dev/peels/lib/pricing.ts`
  - `~/dev/peels/lib/quote.ts`

### Pack, then label

<a id="pack-flow"></a>Paid orders queue to pack; a packed order waits on weight and a label, with slips and labels printed from the app.

- **Id:** `pack-flow`
- **Modules:** `orders`
- **Fits when you see:** shipping, ships, orders, fulfillment, free shipping
- **Proved in:**
  - `~/dev/peels/app/admin/pack/PackFlow.tsx`
  - `~/dev/peels/app/admin/pack/actions.ts`
  - `~/dev/peels/lib/pack.ts`
  - `~/dev/peels/lib/labels.ts`
  - `~/dev/peels/db/085_pack_flow.sql`

### Giveaways with an audit trail

<a id="giveaway-audit"></a>Official rules drafted for approval, a recorded draw, winner claims with deadlines, and an audit PDF at the end.

- **Id:** `giveaway-audit`
- **Modules:** `programs`, `social`
- **Fits when you see:** giveaway, contest, sweepstakes, raffle, win
- **Proved in:**
  - `~/dev/peels/lib/giveaways.ts`: draft, scheduled, live, closed, drawn, fulfilled
  - `~/dev/peels/lib/giveaway-draw-core.mjs`
  - `~/dev/peels/lib/giveaway-audit-pdf.mjs`

### One login, many hats

<a id="one-login-many-hats"></a>One person can be a shopper, a store member, an influencer and a rep, with one login and the right view for each.

- **Id:** `one-login-many-hats`
- **Modules:** `portal`, `team`
- **Fits when you see:** influencers, ambassadors, affiliates, members, reps
- **Proved in:**
  - `~/dev/peels/db/032_hats.sql`
  - `~/dev/peels/lib/hats.ts`

### Books export, not a books rebuild

<a id="books-export"></a>Orders and payouts export in the accounting tool's own import layout, so the books stay where the accountant wants them.

- **Id:** `books-export`
- **Modules:** `money`
- **Fits when you see:** quickbooks, accounting, bookkeeper, invoices, xero
- **Proved in:**
  - `~/dev/peels/app/admin/accounting/export/[kind]/route.ts`
  - `~/dev/peels/lib/accounting.ts`

### Every agent edit, logged with Undo

<a id="agent-change-log"></a>The agent edits records from chat, and every change lands in a log a person can undo.

- **Id:** `agent-change-log`
- **Modules:** `agents`, `log`
- **Fits when you see:** team, office, staff, admin
- **Proved in:**
  - `~/dev/dili/apps/worker/src/chat/changes.ts`
  - `~/dev/dili/apps/worker/src/chat/tools/edit.ts`
  - `~/dev/peels/lib/agent/tools.ts`

### Your own email engine

<a id="own-email-engine"></a>Campaigns to your own list with open and click tracking, a signed delivery webhook, suppression and an audit log.

- **Id:** `own-email-engine`
- **Modules:** `campaigns`
- **Fits when you see:** newsletter, email list, subscribers, mailing list, updates
- **Proved in:**
  - `~/dev/bootyverse/fn/campaigns.ts`
  - `~/dev/bootyverse/fn/sendgrid.ts`
  - `~/dev/bootyverse/fn/audit.ts`
  - `~/dev/amc/lib/email/campaign-sender.ts` (at `origin/main`)

## Not proven yet

The generator must not show these as done.

- Live card capture: the processor is planned, not connected.
- Bought shipping labels: practice labels until the label API is connected.

## Built from

- `~/dev/peels`: commerce OS: storefront, wholesale, reps, pack flow, content

## Signals that point here

wholesale, retail, stores, stockists, retailers, distributor, reorder, sales reps, brand, products, shop now, cpg, snack, beverage, skincare, where to buy
