# Product brand with stores, reorders and reps

You make a product, sell it direct and through stores, and win the shelf with reps.

Example: **Quillback Marine Supply**, a marine supply brand with a store, reorders and accounts. The companies, people and numbers in these pages are made up. The patterns come from real builds. Back to [all playbooks](README.md).

## Who pays and how

- Shoppers pay retail at checkout; shipping and tax from your own rules.
- Stores and distributors buy at their own set discounts off retail, on card or net terms.
- Reps earn commission on accounts they own at the time of the order; paid months lock.

## The core loop

1. **Find and score.** Every store in your markets, ranked by fit to your best accounts.
2. **Work the lead.** Drafted sequences and rep visits move a store from target to applied.
3. **Apply and vet.** The store applies; the agent checks it is real and routes it to the rep for that state.
4. **First order.** The first order turns the lead into an account.
5. **Pack and ship.** Paid orders queue to pack, then weigh and label.
6. **Reorder and commission.** Each account's rhythm raises the reorder; commission credits the rep.

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

- **company lifecycle** (`leads`): target, prospect, engaged, applied, customer, lapsed, closed_lost.
- **order** (`orders`): pending, paid, packed, shipped, delivered, cancelled.
- **account now item** (`pipeline`): follow_up, unanswered, order, reorder, winback, quiet, sample.
- **email campaign** (`campaigns`): draft, in_review, approved, scheduled, sending, sent, cancelled.
- **giveaway** (`programs`): draft, scheduled, live, closed, drawn, fulfilled.

## The agent's first three jobs

1. Every morning, list the accounts due to reorder and the ones going quiet, with the email already drafted.
2. Vet each wholesale application and route it to the rep who owns that state.
3. Draft next week's posts from real photos and what sold last week.

## Hero workflow: The reorder that was about to slip

Signed in as the contractor, approved by the contractor. The agent is "Account desk". Shows the play [Reorder rhythm](#reorder-rhythm).

Steps on screen: Pin the account > Ask > Order rhythm > Draft > Rep approves > Logged with Undo.

- **Pinned:** Account "Harbor Point Marina"
- **Ask:** "Harbor Point used to order every few weeks. What happened and what should I send?"
- **Agent works:** Read 9 orders since March; Normal gap is 24 days, this one is at 37; Checked their last order: no bottom paint; Drafted a reorder note with a sample offer.
- **Reply:** "They are 13 days past their usual reorder and their last order skipped bottom paint, their best seller. The draft offers a free case of the new formula with a reorder this week."
- **Approval:** "Send the reorder note to Dana at Harbor Point from your address?" [Edit] [Send], then "Sent. Follow-up set for Thursday."
- **Log, with Undo:** Account desk sent the reorder note to Harbor Point Marina. Approved by the rep.

Names in the script are fictional.

## What it lets them cancel

Shopify, HubSpot Sales Hub Starter, Klaviyo, Mailchimp, Hootsuite, Canva, Gorgias. Prices and risk for each are in [shared/saas.md](../shared/saas.md).

## Rails kept

Vercel, Neon, Twilio SendGrid, Card processor (planned, not connected), Shipping label API (pending), Social posting API.

## Plays

Innovation plays first: things we built that most businesses like this do not have yet.

### Reorder rhythm (innovation)

<a id="reorder-rhythm"></a>The app learns each account's normal gap between orders and raises a reorder or win-back the day it slips.

**The rule.** Compute each account's rhythm at read time from its own order dates, and key the alert to its last order number. A new order changes the key, so old snoozes and dismissals never mute the next cycle.

**The data it needs**

- Orders: account, number, status, created date, minus cancelled and refunded.
- Account stage: customer or lapsed.
- Item state per account and item key: snoozed_until, dismissed_at.

**The steps**

1. Turn order dates into calendar days in the business time zone, count same-day orders once, and take the gaps.
2. Rhythm is the median gap, minimum 1 day. Under 3 orders, use 30 days and mark the basis as fallback.
3. Stage customer and days since last order at or past the rhythm: raise a reorder item keyed to the last order number.
4. Stage lapsed: raise a win-back item instead, with lateness measured past the rhythm.
5. Urgency is a rule base plus overdue days capped at 99, with reorder and win-back at base 300, below follow-ups, unanswered messages and stuck orders. Rule order beats lateness.
6. Skip dismissed items, hold snoozed ones until their time, and sort accounts by urgency.

**What breaks**

- Split shipments on one day would drag the median toward zero. Same-day orders count once.
- One order proves no rhythm. The fallback basis changes the wording to "expecting one every ~30 days".

**Not proven by the code behind this play**

- Reorder uses the rhythm test. Win-back fires on lapsed stage, which is set outside the cited code.
- The rhythm raises a to-do for a person. It sends no email, and the cited email flows use fixed windows.

- **Id:** `reorder-rhythm`
- **Modules:** `pipeline`, `orders`, `reps`
- **Fits when you see:** wholesale, reorder, stores, stockists, retailers, distributor, accounts

### Territories, commission, leaderboard (innovation)

<a id="rep-territory-commission"></a>Reps own states, applications route to the right rep, commission sticks to the rep who owned the account, paid months lock.

**The rule.** A database trigger stamps the owner onto each order at insert, and commission reads that stamp, never the current owner. A paid month stores a snapshot beside the live recalculation, so a later change shows as a difference.

**The data it needs**

- Rep: states array, commission percent.
- Account: current owner. Order: stamped rep, channel, status, product subtotal, created date.
- Invoice: terms, payments.
- Owner history: account, from, to, at.
- Payout: rep, month, sales, rate, commission, order count, unique on rep and month.

**The steps**

1. Give each application the rep whose states cover it. A new account inherits that rep.
2. A before-insert trigger copies the account owner onto an order with no rep.
3. A trigger on the owner column writes a history row, so no write path can skip it.
4. Statement: sum product subtotal of the rep's B2B orders by order month, for paid through delivered statuses. Net-terms orders also need payments covering the invoice.
5. Commission is sales times rate over 100, using the payout row's rate when one exists.
6. Leaderboard: credit a door to the rep on an account's first counted order, rank by a chosen metric, share ranks on ties.

**What breaks**

- Moving an account would rewrite past pay. Old orders keep their stamp.
- The leaderboard checks status only, so shipped net-terms orders count there before commission.
- A net-terms order settled after its month was marked paid lifts the live total above the snapshot. Nothing adjusts it: the owner sees the difference.

**Not proven by the code behind this play**

- Paid months do not lock. A snapshot sits beside a live recalculation, and only the rate is frozen.
- The state lookup that assigns the rep sits outside the cited code.

- **Id:** `rep-territory-commission`
- **Modules:** `reps`, `money`
- **Fits when you see:** sales reps, reps, brokers, territory, territories, ambassadors, field sales

### Which post sold (innovation)

<a id="post-to-order-attribution"></a>Every order is tied back to the post or email that brought it, and the agent drafts next week from what worked.

**The rule.** Label every credit by how sure it is: code and link are confirmed, page-view guesses and checkout answers are estimated. Report rows must sum to the sales summary, so unclaimed orders show as Unattributed. The draft writer learns from an engagement score, not revenue.

**The data it needs**

- Order: visitor cookie, session, post id. Attribution: order, post, method (code, utm, estimated, survey), revenue.
- Post metric snapshots, daily visits, follower snapshots.
- Real assets: media library, approved customer posts.

**The steps**

1. At checkout, set the post from a code, else the browser's last post-link touch inside 30 days. A daily job fills the rest as estimated.
2. Weekly report: rank by revenue, orders, visits, engagement, reach. Show top 3 and change against last week.
3. Score posts older than 3 days: (likes + 2 comments + 4 saves + 4 shares) per 1,000 reached, times (reach / followers)^0.25 clamped 0.5 to 1.5.
4. Shrink group averages with 2 prior posts. Patterns need lift of 1.15 or more, or 0.87 or less.
5. Weekly, if no batch exists, pick 3 to 5 assets unused for 42 days. The model writes text only, shaped by those patterns.
6. Save as proposed. Approval moves posts to draft. Nothing publishes.

**What breaks**

- Under 4 scored posts: no patterns, formats rotate.
- Bad model JSON: template text fills in.
- A fetch guard blocks image and video hosts, and a draft without a real asset throws.
- Demo posts carry fake numbers and never teach the writer.

**Not proven by the code behind this play**

- Attribution covers posts, not emails, and some orders stay Unattributed.
- The draft writer learns from engagement, not orders or revenue.
- Weekly drafts default to off.

- **Id:** `post-to-order-attribution`
- **Modules:** `social`, `insights`, `orders`
- **Fits when you see:** instagram, tiktok, social, influencers, content, posts

### Wholesale applications, vetted

<a id="wholesale-application-vetting"></a>A store applies, the agent checks the email domain, the phone, the website and past records, and says looks legit, check, or red flags.

**The rule.** Code runs every check and writes a one-line finding. The model reads the application and findings and writes the score, verdict and reasons, but any failed abuse check forces Red flags at 35 or less. Nothing auto-declines.

**The data it needs**

- Application: business, contact, email, phone, address, website, tax document.
- Past records: retail logins, retail orders with promo codes, other applications with status.
- Lists: free mail, disposable mail, parked-page phrases, trade keywords.

**The steps**

1. On submit, mark the rating running and rate after the response.
2. In parallel, gather MX records, website text, a business listing, and past-record matches on email, phone and normalized address.
3. Give each check pass, warn, fail or skipped. Abuse checks: retail login match, declined match, promo code in 90 days, repeat application, no footprint.
4. Score from base 55 with per-check points: disposable fail -40, retail match fail -35, parked page -25.
5. Red flags: abuse fail, or under 45 with any fail. Looks legit: 70 or more, no fails, plus a live store page or listing. Otherwise Check.
6. The model answers in SCORE, VERDICT and REASON lines. An unparsable reply leaves the rules in charge.

**What breaks**

- A missing API key must not punish an applicant. Skipped checks score 0, so thin evidence lands on Check.
- A stalled run would show "Checking" forever. Errors save as failed, and a run over 3 minutes reads as failed.
- Small shops often lack working https. The fetch retries over http before calling the site down.

**Not proven by the code behind this play**

- When the model answers, code enforces only the abuse floor. The model can return Looks legit without a live page or listing.

- **Id:** `wholesale-application-vetting`
- **Modules:** `leads`, `intake`
- **Fits when you see:** wholesale, become a retailer, stockist, carry our, apply

### The whole market, ranked by fit

<a id="icp-fit-scoring"></a>Rebuild the ideal customer from real customers, score every prospect with reasons, and work the list top down.

**The rule.** Fit and legitimacy stay separate numbers. The rule score explains itself check by check, and the parser clamps the model to 15 points either side. Each rebuild starts from default weights, so learned boosts never compound.

**The data it needs**

- Company: type, state, map pin, metro, stage, demo flag.
- Sourced facts: what it carries, rating, independent or not.
- Profile version: weights, signals, team notes, customer count.
- Metros with radius and priority, state rules with allowed types.

**The steps**

1. For each type with customers, weight is the lesser of 30 and its default plus 3 per customer. Add 2 to the competitor weight when 40% carry a competitor.
2. Each morning, assign pinned companies to the nearest active metro in radius, rebuild if the customer count changed, and re-score up to 25 new or stale companies.
3. Rule score sums checks such as type weight, +16 adjacent category, +10 competitor, +6 rating 4.3 or more, +6 independent, +10 or +5 metro priority, +5 within 60 km of a customer, -25 chain, -30 type not allowed in state.
4. Bands: hot 70, warm 50, cold 30, otherwise not a fit.

**What breaks**

- Demo accounts would poison the profile. They are excluded.
- Quoted text breaks JSON replies. The model answers in SCORE and REASON lines, and a bad reply falls back to rule reasons.
- The rebuild compares counts only, so swapping one customer for another changes nothing until the count moves.

**Not proven by the code behind this play**

- Learning changes type weights and one competitor bump, nothing else.
- It scores companies already on record, 25 stale ones per pass. The cited code has no market discovery and no ranked worklist.

- **Id:** `icp-fit-scoring`
- **Modules:** `prospects`
- **Fits when you see:** b2b, stores, retailers, accounts, businesses, wholesale

### Sequences the agent drafts, a person sends

<a id="drafted-sequences"></a>Every step of a sequence is drafted for that account; it waits for a person to press Send unless auto-send is on, and stops on a reply.

**The rule.** Advancing a sequence only creates a task, and an email task carries a finished draft. The model rewrites a merged template, and a reply that fails the checks leaves the template in place. One open task per enrollment holds the next step back.

**The data it needs**

- Sequence: auto_send off by default. Step: position, kind, wait days, subject, body.
- Enrollment: account, owner, status, step position, next due, started at. One active per company.
- Task: position, recipients, draft, status, sending_at, unique on enrollment and position.

**The steps**

1. Hourly and after each task, find active enrollments that are due with no open task.
2. Stop on a reply or application since the start, any order, a closed stage or do-not-contact.
3. For email steps, ask the model for the same ask, same length or shorter, one or two facts, nothing invented. Other kinds queue a task with a note.
4. Finishing a task sets next due to now plus the next wait: 0, 3, 4, 7, 7 days.
5. With auto_send on, send on weekdays from 9 to 17 in the recipient's time zone, under 25 per owner per day, after re-checking stop rules.

**What breaks**

- Two runs could send twice. Each send claims sending_at with a 10 minute timeout.
- A failed send clears the claim, logs a note and waits for a person.
- A reply during an open draft is not caught, because advance skips enrollments with an open task. Only auto-send re-checks.

**Not proven by the code behind this play**

- Only email steps get a draft. Other kinds queue a task with a note.
- A reply during an open draft does not stop the sequence.
- Live auto-send is hard-coded off. Auto-send runs in test mode only.

- **Id:** `drafted-sequences`
- **Modules:** `outreach`
- **Fits when you see:** outreach, follow up, sales, prospects, b2b

### Price tiers and terms

<a id="wholesale-price-tiers"></a>Retail, wholesale and distributor prices from one list, with card or net terms per account.

**The rule.** Retail lives on the variant. A tier stores a percent off retail, and an override row wins only where one exists, so no tier needs a full price table. Every edit is a ledger row, which gives you scheduling and undo.

**The data it needs**

- Variant: SKU, retail in integer cents. Tier: name, percent off. Tier price: tier, variant, cents.
- Account: tier, terms (card, net15, net30, prepaid), default card.
- Price change: batch, variant, field, tier, old cents, new cents, effective time, status.

**The steps**

1. Validate: retail is a positive integer. A blank tier value deletes the override, so the percent applies again.
2. Give the edit set one batch code. Copy current values into old cents, one change row per edit.
3. No date: write now, status applied. Date given: status scheduled, rejected if over 60 seconds past.
4. On price load, probe for one due row. If found, flip all due rows to applied in one update and write them in id order.
5. Rollback: a scheduled batch becomes cancelled. An applied batch replays old values as a new batch and becomes rolled_back.

**What breaks**

- Double rollback: a batch no longer applied refuses, so old values never replay twice.
- Old cents are captured at scheduling, not at apply. A later rollback overwrites any edit made in between.
- Net orders ship before payment, so paid status alone cannot gate shipping.

**Not proven by the code behind this play**

- The function that resolves override then percent at order time sits outside the cited code, so its rounding is unknown.
- Retail is a variant column, not a tier. Tier names are free data.

- **Id:** `wholesale-price-tiers`
- **Modules:** `catalog`, `orders`
- **Fits when you see:** wholesale, distributor, net 30, bulk, case pack, msrp

### Pack, then label

<a id="pack-flow"></a>Paid orders queue to pack; a packed order waits on weight and a label, with slips and labels printed from the app.

**The rule.** One queue, oldest first, two steps per order: seal the box, then weigh and label. The buy step claims the order with a timestamp first, so a double click cannot buy two labels. Status moves call the order page's own function, so permissions, logs and emails stay in one place.

**The data it needs**

- Order: status, ship-to, ship method, label service, weight, box, label time, practice flag, tracking.
- Variant weight in ounces. Box presets: item ceiling, empty-box tare.
- To pack = paid plus open (net-terms orders ship unpaid).

**The steps**

1. Opening an order prints the slip from a hidden iframe.
2. The packer taps each line. The seal button unlocks when all are ticked and moves the order to packed.
3. Prefill weight from line weights plus tare. The packer types the scale reading. Quotes debounce 300 ms and a sequence counter drops stale replies.
4. Preselect the cheapest rate, or priority when the paid method reads as fast.
5. Buy: update label time where status is in the queue and label time is null or over 2 minutes old. No row means stop. A failed buy clears the claim.
6. Mark shipped, print the label, offer the next order.

**What breaks**

- No carrier API wired: table rates, generated tracking, label prints PRACTICE. The tracking email is suppressed while email is live.
- Wrong box: void within 20 hours returns the order to packed and warns if the shipped email went.
- No ship-to address blocks the buy.

**Not proven by the code behind this play**

- No carrier is connected. Every label is a practice label with table rates and a generated tracking number.
- Voiding resets the order row and makes no carrier call.

- **Id:** `pack-flow`
- **Modules:** `orders`
- **Fits when you see:** shipping, ships, orders, fulfillment, free shipping

### Giveaways with an audit trail

<a id="giveaway-audit"></a>Official rules drafted for approval, a recorded draw, winner claims with deadlines, and an audit PDF at the end.

**The rule.** Commit before you pick: log the hash of the seed and of the eligible list, then reveal the seed and draw. Anyone holding the export can rerun the draw and get the same winners. Rules approval is a hash of the rendered text, so any text change voids it.

**The data it needs**

- Giveaway: status, dates, winner and alternate counts, claim days, eligibility lists, rules text, approved hash.
- Entry: email, region, age confirmed, status. Unique on giveaway and lowercased email.
- Log: seq, kind, actor, payload, prev hash, hash.

**The steps**

1. Scheduling requires approved rules with no blanks. A text-changing edit returns it to draft.
2. Every read syncs status by date. The entry insert rechecks dates in SQL.
3. Screen entries with a reason each: flagged, age, region, outside dates, team email, already picked.
4. Commit sha256 of a 32-byte seed plus sha256 of the sorted eligible ids.
5. Draw by partial Fisher-Yates. Each index comes from HMAC-SHA256(seed, snapshot:counter), first 48 bits, with rejection sampling. First picks win, the rest are ordered alternates.
6. Chain each entry: sha256(prev hash + canonical JSON).
7. The PDF prints verification result, chain head, algorithm and every entry.

**What breaks**

- JSON columns reorder keys, so hash canonical JSON with sorted keys.
- A redraw commits with winner count 0 and skips earlier picks.
- Standard PDF fonts cannot draw every character, so swap them first.

**Not proven by the code behind this play**

- The cited code defines log kinds for notify, claim, forfeit and promote. The claim flow and its deadline enforcement sit outside it.
- Rules drafting sits outside the cited code. Approval by hash is in it.

- **Id:** `giveaway-audit`
- **Modules:** `programs`, `social`
- **Fits when you see:** giveaway, contest, sweepstakes, raffle, win

### One login, many hats

<a id="one-login-many-hats"></a>One person can be a shopper, a store member, an influencer and a rep, with one login and the right view for each.

**The rule.** A login keeps one email and hats are computed, never stored as a list. Store access and influencer status are separate rows, while rep and team come from the role column. Shopper is the leftover hat: true only with no store, no team role and no rep role.

**The data it needs**

- User: email, role, last account used.
- Store member: user, account, status (active, invited, removed), invite hash, invited time. Unique on user and account.
- Influencer: user as key, unique code, discount and commission percent, active.
- Order: archived personal flag.

**The steps**

1. Hats query: active memberships on stores not paused, closed, disabled or removed, plus active influencer row, plus role.
2. Add a member by upsert, set last account so sign-in lands there, archive earlier consumer orders by user id or lowercased email.
3. Invite an existing login: store sha256 of a 24-byte token, send the raw token. A re-invite never downgrades an active member.
4. Accept only when status is invited and under 14 days old. Accepting clears the hash.
5. Remove by status change, never by deleting the row.

**What breaks**

- The archive flag keeps personal orders out of store totals.
- A paused store drops access at once because the query filters it. Reactivating restores members untouched.
- Pausing returns unpaid, unpacked orders to pending with a note, so they get reviewed before shipping.

**Not proven by the code behind this play**

- Shopper drops once a login has a store, team or rep role, and rep and team come from one column, so a login cannot hold all four at once.
- The cited code computes hats and a landing store. View switching sits outside it.

- **Id:** `one-login-many-hats`
- **Modules:** `portal`, `team`
- **Fits when you see:** influencers, ambassadors, affiliates, members, reps

### Books export, not a books rebuild

<a id="books-export"></a>Orders and payouts export in the accounting tool's own import layout, so the books stay where the accountant wants them.

**The rule.** The app never tries to be the ledger. The accounting tool keeps bank feeds, bills, payroll and taxes, and the app produces CSVs with the exact headers of QuickBooks Online's import screen. The header row and date format are the whole integration.

**The data it needs**

- Accounts with first contact, variants with stock and reorder point, order lines with their own unit price.
- Invoice: number from order digits, order, account, terms, issue and due dates, amount. Payments.

**The steps**

1. Before reading, insert one invoice per wholesale order where none exists, due date = order date plus terms days.
2. Auto-record a card payment for customer-placed card-terms orders with none yet.
3. Compute status on read: void if the order is cancelled, then paid, overdue, partial, open.
4. Customers: Name, Company, Email, Phone, Website, City, State, Terms, Notes. Products: Product/Service Name, Sales Description, SKU, Type, Sales Price / Rate, Income Account, Quantity On Hand, Reorder Point, plus a Shipping service row.
5. Invoices: InvoiceNo, Customer, InvoiceDate, DueDate, Terms, Item(Product/Service), ItemDescription, ItemQuantity, ItemRate, ItemAmount. One row per line, shipping as its own row, void skipped.
6. Format: MM/DD/YYYY, 2-decimal dollars, CRLF, quote commas, quotes and newlines.

**What breaks**

- Double invoices: not-exists plus on-conflict-do-nothing makes sync repeatable on any page load.
- Tax is in the invoice amount but has no export row, so an imported total runs short when tax is nonzero.
- Exports require an accounting read permission and send no-store.

**Not proven by the code behind this play**

- The import layouts cover customers, products and wholesale invoices. Payouts and consumer orders have none.

- **Id:** `books-export`
- **Modules:** `money`
- **Fits when you see:** quickbooks, accounting, bookkeeper, invoices, xero

### Every agent edit, logged with Undo

<a id="agent-change-log"></a>The agent edits records from chat, and every change lands in a log a person can undo.

**The rule.** Every edit tool must quote the words in the person's latest message that ask for the change, and code checks the quote is there. Text in documents, transcripts or web pages can never trigger an edit. Writes run through the person's own database client, so row-level policy decides what they may change.

**The data it needs**

- Change row: actor, entity type and ID, path, item key, op, payload, before, after, one-line summary, undone-at, undone-by.
- Generated reports: a stored base plus a current version with an updated-at stamp.

**The steps**

1. Normalize case, quotes and whitespace, then require the quote in the latest message: 12 characters minimum, or the whole message if shorter.
2. Apply the change and log before and after. Store as after what the database returned, so undo compares like with like.
3. For generated reports, store the edit as a payload and rebuild from base plus active edits, guarded on updated-at, 3 attempts.
4. Undo: if a later active change hits the same entity, path and item key, or the current value differs from after, refuse and name the conflict. A forced retry overrides.
5. Otherwise write before back, remove added rows, stamp undone-at.

**What breaks**

- A forced undo can wipe newer work, so the agent must ask the person first.
- A report rebuild fails after the log write: the edit is withdrawn, so a retry stacks no duplicate.
- Timestamps return as Z or +00:00. Equality treats them as one instant, so undo raises no false conflict.

**Not proven by the code behind this play**

- Most edit tools write the record first and the log row second, with no rollback. A failed log write leaves an unlogged edit.
- In the second build, a contact insert skips the log and undo has no later-change check.

- **Id:** `agent-change-log`
- **Modules:** `agents`, `log`
- **Fits when you see:** team, office, staff, admin

### Your own email engine

<a id="own-email-engine"></a>Campaigns to your own list with open and click tracking, a signed delivery webhook, suppression and an audit log.

**The rule.** Freeze the campaign at Send: final HTML with per-recipient tokens, plus one row per recipient. Sending then means draining a resumable queue. Tracking runs on your own domain with the provider tracking off, so opens, clicks and unsubscribes are your rows.

**The data it needs**

- Campaign: status draft, sending or sent, frozen HTML, text and subject, ordered link list.
- Send row: email, random token, status, claimed_at, open and click stamps.
- Suppression: unique email, reason. Provider event: unique event ID. Audit: who, IP, path, status, capped body.

**The steps**

1. Send requires a mailing address and a confirmed count matching the suppression-filtered audience, else 409.
2. In one transaction, flip draft to sending with a status guard and insert send rows.
3. Claim 400 queued rows with SKIP LOCKED and send batches of 100 with RFC 8058 headers. An hourly cron requeues claims older than 15 minutes.
4. Serve a pixel for opens and a redirect by link index for clicks. A click also stamps the open.
5. Verify the webhook ECDSA P-256 signature over timestamp plus raw body, dedupe on event ID, then suppress hard bounces, spam reports and unsubscribes.
6. Write an audit row in the background after each non-GET admin call. Keep 365 days.
7. A second build sends per recipient with a worker pool of 8, honouring Retry-After on 429 with 3 retries.

**What breaks**

- Mail scanners prefetch links, so an unsubscribe GET only shows a button and POST does the work.
- A dead function strands claimed rows, so the cron requeues them. A rare duplicate beats a lost email.
- A dev machine holding the key would blast the list, so the second build needs a separate live-mode flag and simulates sends otherwise.

**Not proven by the code behind this play**

- The two builds differ: the second turns provider tracking on and sends one request per recipient. The first is the pattern above.

- **Id:** `own-email-engine`
- **Modules:** `campaigns`
- **Fits when you see:** newsletter, email list, subscribers, mailing list, updates

## Not proven yet

The generator must not show these as done.

- Live card capture: the processor is planned, not connected.
- Bought shipping labels: practice labels until the label API is connected.

## Signals that point here

wholesale, retail, stores, stockists, retailers, distributor, reorder, sales reps, brand, products, shop now, cpg, snack, beverage, skincare, where to buy
