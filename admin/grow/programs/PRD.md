# Programs (admin, Grow)

- **Module key:** `programs`
- **Tier:** industry (consumer brands)
- **Route:** `/admin/programs`
- **Folder:** `admin/grow/programs/`

## Job

"The programs that make customers come back and bring friends." Rewards points, referrals, influencer codes, giveaways, claimable offers and customer photos, run from one place with every rule, draw and payout on the record.

The number: **repeat purchase rate of program members versus non-members** over 90 days. Second number: share of new customers who came through a referral or influencer code.

## Users and permissions

Starts from `shared/roles.md` section 4b. Differences only:

| User type | Programs |
|---|---|
| Owner | all. Approves giveaway rules and payouts |
| Admin | V C E P D X K. Approves giveaways only when delegated (A†) |
| Staff | V C E. Review customer photos, adjust points with a reason, manage offers. No approvals, no payouts |
| Contractor | hidden |
| Customer | own: V C in Portal Rewards: see balance, claim offers, enter giveaways, share a referral link, upload photos; influencers see their hub |
| Agent | V C E, P* (posts, winner emails), $* (payouts and point grants over a cap) |

- **Gated agent verbs:** P on giveaway posts and winner notices; `$` on any payout or a points grant over `fields.points_grant_cap`. Moving money out is `!` (never relaxable).
- **Always human:** approving official giveaway rules, running the final draw confirmation, marking an influencer statement paid.
- **Sensitive fields:** influencer payout details (`influencers.payout_details`), winner shipping address, date of birth for age-gated giveaways. Column grants; Staff off by default.

## Pages and states

Tabs in nav order (each tab can be hidden with `fields.tabs`):

| Tab | Route | What it shows |
|---|---|---|
| Rewards | `/admin/programs` | Members, points issued and redeemed, top members, adjust points with a reason, earn and burn rules |
| Referrals | `/admin/programs/referrals` | Referral links, clicks, sign-ups, first orders, rewards owed |
| Influencers | `/admin/programs/influencers` | Codes and links, clicks, orders, commission, statements, requests to join |
| Giveaways | `/admin/programs/giveaways` | Giveaways by status (Draft, Rules in review, Live, Drawing, Winners notified, Closed), entries, prizes |
| Offers | `/admin/programs/offers` | Claimable items at `/claim/[code]`: limit, claims, on or off |
| Customer content | `/admin/programs/content` | Customer photos and videos to approve, feature or take down, with reward caps |
| Settings | `/admin/programs/settings` | Points name, earn and burn rules, caps, tabs. Hidden without K |

**Record views:** full routes `/admin/programs/giveaways/[id]` (tabs: Setup, Rules, Entries, Draw, Winners, Posts, Audit) and `/admin/programs/influencers/[id]` (tabs: Overview, Orders, Statements, Content). Offers and content items open as URL modals (`?offer=<id>`, `?ugc=<id>`).

**Quick views:** Rules in review, Draws due, Statements to pay, Content to review, Offers running low. Filters vary per tab.

**States:**

- **Empty Rewards:** "Give customers a reason to come back. Name your points and set one earn rule." Button: Set up rewards.
- **Empty Giveaways:** "Plan a giveaway. The agent drafts the official rules for you to approve." Button: New giveaway.
- **Loading:** tab skeletons.
- **Error:** "Programs didn't load. Try again." A draw that fails never picks partial winners; it shows "Draw didn't run. Nothing changed." with Retry.
- **Permission:** hidden for Contractor. Staff never see Approve or Mark paid. Settings hidden without K. Payout details are not rendered without the grant.
- **Disabled with reason:** Go live shows "Rules waiting on Owner approval"; Draw shows "Entries close on <date>"; Mark paid shows "Add payout details for this influencer".

**Badge:** none on the nav by default (the queues surface on Home > Today). Tab counts show Content to review and Rules in review.

## Data model

| Table | Columns |
|---|---|
| `points_ledger` | `id`, `org_id`, `person_id`, `delta` int, `reason` (`order`, `review`, `referral`, `content`, `adjust`, `redeem`), `ref_kind`, `ref_id`, `actor_id`, `at` (append only; balance is a sum) |
| `offers` | `id`, `org_id`, `code`, `title`, `item` (fk Catalog variant), `limit_total`, `limit_per_person`, `starts_at`, `ends_at`, `on` bool |
| `offer_claims` | `id`, `offer_id`, `person_id`, `order_id` null, `claimed_at` |
| `referrals` | `id`, `referrer_id`, `code`, `referred_person_id`, `first_order_id`, `reward_status` (`pending`, `granted`, `void`) |
| `influencers` | `id`, `person_id`, `code`, `link_slug`, `discount_pct`, `commission_pct`, `status`, `payout_details` jsonb (sensitive) |
| `influencer_payouts` | `id`, `influencer_id`, `period` (month), `orders_count`, `amount_cents`, `currency`, `status` (`draft`, `approved`, `paid`), `approved_by`, `paid_at`, `payment_ref` |
| `giveaways` | `id`, `org_id`, `title`, `prize` jsonb, `rules_md`, `rules_status` (`draft`, `in_review`, `approved`), `rules_approved_by`, `opens_at`, `closes_at`, `eligibility` jsonb (age, regions), `status` |
| `giveaway_entries` | `id`, `giveaway_id`, `person_id`, `entered_at`, `source`, `disqualified_reason` |
| `winners` | `id`, `giveaway_id`, `entry_id`, `rank`, `notified_at`, `claimed_at`, `shipping` jsonb (sensitive) |
| `draw_log` | `id`, `giveaway_id`, `seed`, `entries_hash`, `picked` jsonb, `run_by`, `run_at` |
| `ugc_posts` | `id`, `person_id`, `file_id`, `caption`, `status` (`pending`, `approved`, `featured`, `taken_down`), `points_awarded`, `reviewed_by` |

- **Shared:** `people`, `files`, `approvals`, `change_log`; reads Orders and Catalog.
- **Row rules for `own`:** a Customer reads only their own `points_ledger`, `offer_claims`, `referrals`, `giveaway_entries`, `ugc_posts`, and, as an influencer, their own `influencers` and `influencer_payouts` rows.
- **Anchor kinds:** `giveaway:<id>`, `influencer:<id>`, `offer:<id>`, `ugc:<id>`, `payout:<id>`, `field:giveaway:<id>.rules_md`.
- **Config knobs:** `label` (Programs, Loyalty, Members), `fields.tabs`, `fields.points_name` (points, stars, any brand word), `fields.earn_rules`, `fields.points_grant_cap` (default 500), `fields.ugc_reward_cap_monthly`.
- **Sample type:** `rewards`. Seeds 200 members with ledgers, 3 influencers with statements, 1 live giveaway with 340 entries, 2 offers, 12 customer photos to review.

## Agent actions

| Action | Tool | Verb | Gated | Writes to `change_log` | Undo |
|---|---|---|---|---|---|
| Draft official giveaway rules | `draft_giveaway_rules` | C | Owner approves (agent cannot) | `rules_md`, `rules_status = in_review` | Restores prior rules |
| Run the draw with an audit trail | `run_draw` | E | Asks first; a person confirms | `draw_log`, `winners` | Void draw (logged) and redraw with a new seed |
| Draft launch, last call and winner posts | `draft_post` (Social) | C | Publishing gated in Social | Social drafts | Deletes drafts |
| Notify winners | `send_message` | P | Yes | `winners.notified_at` | Not undoable once delivered |
| Review customer photos | `flag_ugc` | E | Approve and feature need a person | `flags` on `ugc_posts` | Clears flags |
| Grant or adjust points | `adjust_points` | E ($ over cap) | Over cap gated | `points_ledger` row | Reversing ledger row |
| Build influencer commission statements | `build_statements` | C | Approval and payout are human (`!`) | `influencer_payouts` drafts | Deletes drafts |
| Answer a member in the portal about their balance or a claim | portal chat | read | No | Nothing | n/a |

**Background jobs:**

- **Monthly statements (1st of month):** influencer statements drafted for approval.
- **Monthly content rewards:** points for approved customer content, within caps.
- **Giveaway sync (hourly while live):** entries counted, duplicates and ineligible entries flagged for review.
- **Referral grant (on first order shipped):** referral reward moves from pending to granted.

## Integrations

- **Payments** (default Stripe; contract: payouts or transfers only on a human-approved statement, idempotency key per statement). Banking rail for manual payouts records a `payment_ref`.
- **Email delivery** (default SendGrid) for winner notices and claim emails.
- **Database** (default Neon Postgres); **file storage** through Library for customer content.
- **Platform APIs (optional):** a social network API to pull tagged posts into Customer content.
- **Webhooks in:** order shipped (internal), payout status from the payments rail.
- **Secrets by name:** `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `SENDGRID_API_KEY`, `SOCIAL_API_TOKEN` (optional).

## SaaS replaced

None priced in `shared/saas.md`. Loyalty, referral, affiliate, giveaway and customer-content tools are not in the explorer yet, so no product is listed here. When the explorer adds them, expected risk is Plan it for loyalty and affiliate tools (live point balances and commission owed) and Easy for giveaway tools between campaigns.

Migration pattern for a loyalty or affiliate tool: export balances and unpaid commission as of a cutoff date, import as one opening `points_ledger` row per member and one draft statement per influencer, run both for one statement period, switch codes and links, cancel.

## Acceptance criteria

1. A Contractor never sees Programs, and a deep link shows the no-access page.
2. Every agent write (rules draft, points adjust, flags, statements) appears in Log with before, after and a working Undo.
3. When the agent submits giveaway rules or a commission statement, the Owner sees the full text or the line items and total with one Approve button; the agent cannot approve or pay.
4. Every submit button (Approve, Draw, Mark paid, Claim, Enter) shows a spinner and disables while it runs.
5. A giveaway cannot go live until its rules are approved; the Go live button shows the reason until then.
6. The draw records a seed and an entries hash; re-running the audit with the same seed picks the same winners, and the Audit tab exports a PDF.
7. A Customer opens Portal Rewards and sees their balance, which equals the sum of their ledger rows, and their referral link.
8. A Customer claims an offer at its per-person limit and the second claim shows "You already claimed this".
9. Staff approve a customer photo; points within the monthly cap land on the member's ledger with reason `content`.
10. A points grant over the cap requested by the agent waits for a person.
11. An influencer signed into the portal sees their clicks, orders and commission by month, and never another influencer's.

## Open questions

1. **Points value?** Recommended: 1 point per dollar spent, 100 points = $5 off, set in the interview.
2. **Giveaway eligibility?** Recommended: 18 and up, the business's own country only, no purchase necessary with a free entry route; the agent's rules draft includes both, and the Owner should have counsel read the first set.
3. **Payout rail?** Recommended: record manual payouts with a reference first; turn on rail payouts after three clean statement months.
4. **Customer content rewards cap?** Recommended: 3 rewarded posts per member per month.
5. **Show Programs as one item or split?** Recommended: one item with tabs; hide tabs the business does not run.
