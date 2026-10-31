# Portal: Rewards (customer, portal)

- **Module key:** `portal.rewards` (stable, never renamed)
- **Tier:** follows Programs (`programs`, industry, consumer brands). Shows only when Programs is enabled.
- **Route:** `/portal/rewards`
- **Folder:** `customer/portal/rewards/`

## Job

Give customers a reason to come back and bring friends: their points, what they can claim, their referral link, and for creators, their influencer numbers. The number that tells you it is working: **repeat purchase rate of customers who opened Rewards in the last 90 days** versus those who did not, and **orders from referral links per month**.

## Users and permissions

- Customer kinds `shopper`, `buyer`, `member`: View and Create (claim an offer, redeem points, enter a giveaway, share a referral link, submit customer content). Partners and clients do not see Rewards.
- Buyers see the store's points (one balance per store), not a personal balance.
- **Influencer** is a hat on a customer (a row in `influencers` from Programs), not a kind. Customers with that hat see the Influencer tab.
- Customers cannot change their points balance. Points come from rules in Programs (orders, reviews, approved content, referrals) and manual adjustments by staff.
- Agent (as the customer): View, claim, redeem, enter, share. **Gated (customer's yes):** redeeming points (spends a balance), and anything that applies points to an order total.
- Sensitive fields: point rules' internal costs, other customers' entries, influencer payout rates for other influencers, giveaway draw seeds before the draw.

## Pages and states

Tabs (labels follow `fields.points_name` from Programs, so "Points" may read "Stars"):

| Tab | Route | Shows |
|---|---|---|
| Points | `/portal/rewards` | Balance, ledger (earned, spent, expired, with reason and order link), how to earn more |
| Offers | `/portal/rewards/offers` | Offers this customer can claim (free item, discount, early access), with claim button and expiry |
| Refer | `/portal/rewards/refer` | Personal referral link and code, copy and share buttons, friends who joined and what each earned |
| Influencer | `/portal/rewards/influencer` | Code, link, clicks, orders, commission by month, payout statements (read-only), socials on file |
| Share | `/portal/rewards/share` | Upload photos or videos of the product for points; status per upload (pending, approved, featured, declined) |
| Giveaways | `/portal/rewards/giveaways` | Giveaways entered, status, official rules link, winner notice |

- Record views: offers and giveaways open as URL modals (`?offer=<id>`, `?giveaway=<id>`).
- **States:** empty Points says "Earn your first points with your next order." Empty Offers says "No offers right now. We'll email you when one opens." Loading skeletons. Error with Retry.
- **Disabled with reason:** Redeem disabled with "You need 300 more points"; Claim disabled with "Claimed" or "Ended Nov 30".
- The points pill in the top bar shows the balance whenever Rewards is visible.
- Badge: none (Home shows the nearest claimable offer).

## Data model

- Owns no tables. Reads and writes Programs tables through row rules on `customer_id` (or store `company_id` for buyers): `points_ledger` (insert only, never update), `offers`, `offer_claims`, `referrals`, `influencers`, `influencer_payouts` (read), `giveaways`, `giveaway_entries`, `winners`, `ugc_posts`.
- Balance is the sum of `points_ledger` for the customer; never a stored number that can drift.
- Uploads on Share create `files` (Library) with consent recorded on `consents` (the customer grants use of their content with the exact text shown), and a `ugc_posts` row in `pending`.
- Anchors: `offer:<id>`, `giveaway:<id>`, `ugc:<id>`, `influencer:<id>`, `points_entry:<id>`, `referral:<id>`.
- Knobs (on Programs): `fields.points_name`, `fields.tabs`. Portal knob: `fields.rewards.tabs` (subset and order of the six tabs). Sample: `rewards`.

## Agent actions

| Action | Tool | Verb | Gated | Writes to `change_log` | Undo |
|---|---|---|---|---|---|
| How many points do I have, how do I earn more | `query_db` | V | No | Nothing | n/a |
| Claim an offer | `claim_offer` | C | No | `offer_claims` insert | Yes until used |
| Redeem points for a reward or apply to an order | `redeem_points` | C, $ | Yes | `points_ledger` debit, `offer_claims` | Yes until used, by a reversing ledger entry |
| Get my referral link | `get_record` | V | No | Nothing | n/a |
| Enter a giveaway | `enter_giveaway` | C | No | `giveaway_entries` insert | Yes until the draw |
| Submit a photo from chat for points | `submit_ugc` | C | No | `files`, `ugc_posts`, `consents` | Yes while pending |
| Explain a commission statement | `get_record` | V | No | Nothing | n/a |

Background jobs (owned by Programs, surfaced here): points on order delivered, points on approved content (with monthly caps), offer expiry, giveaway draw with audit trail and winner notice, monthly influencer statement for approval in admin.

## Integrations

- **Email delivery:** claim confirmations, winner notices, statement ready.
- **Payments:** influencer payouts run in admin Money after approval; the portal only shows statements.
- **Platform API:** none required. Share buttons use the device share sheet.
- Webhooks: none. Secrets: none of its own.

## SaaS replaced

None from `shared/saas.md`. The loyalty, referral, giveaway and customer-content tools this page replaces are not priced in the explorer yet; see admin Programs for the list the inventories saw.

## Acceptance criteria

1. A partner or client never sees Rewards in the nav, and a deep link to `/portal/rewards/offers` shows the not-found page.
2. Every agent write on Rewards (claim, redeem, entry, upload) appears in Log with before, after and a working Undo where the PRD allows it.
3. Asked to use points on the next order, the agent shows "Redeem 500 points for $5.00 off order 1051" with one Approve button and spends nothing until approved.
4. Every submit button on Rewards shows a spinner and disables while it runs.
5. A shopper's balance equals the sum of their ledger rows; a staff adjustment in admin appears in the ledger with its reason on the next load.
6. A buyer sees the store's balance, and switching stores changes the balance and ledger.
7. A customer without the influencer hat never sees the Influencer tab.
8. A customer uploads a photo on Share; it shows as Pending, and after staff approve it in admin the points appear in the ledger.
9. A shopper copies their referral link; a friend orders through it; the Refer tab shows the friend and the points earned after delivery.
10. With `points_name = "Stars"`, every label and the top bar pill read Stars.

## Open questions

1. **Do points expire?** Default: 12 months after the last activity, with an email 30 days before.
2. **Show a leaderboard of top referrers?** Default: no; it exposes other customers.
3. **Let customers pick a charity instead of a reward?** Default: no at launch.
