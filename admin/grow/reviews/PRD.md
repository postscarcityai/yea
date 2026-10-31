# Reviews (admin, Grow)

- **Module key:** `reviews`
- **Tier:** common
- **Route:** `/admin/reviews`
- **Folder:** `admin/grow/reviews/`

## Job

"Ask every happy customer for a review, answer every review, and reuse the best ones." Requests go out after a delivery or a finished job, every review gets a reply, and the good ones become quote cards for Social and proof on the Site.

The number: **review request conversion** (reviews received divided by requests sent). Second number: **median time to reply to a public review**.

## Users and permissions

Starts from `shared/roles.md` section 4b. Differences only:

| User type | Reviews |
|---|---|
| Owner, Admin | all |
| Staff | V C E P. Moderate, reply, send requests. No D, X, K |
| Contractor | hidden |
| Customer | C by private link only (`/review/[token]`). They see their own published review on product and Site pages like anyone else |
| Agent | V C E, P* |

- **Gated agent verbs:** P: publishing a reply, publishing a review to the Site, and sending a review request that is not part of an approved automatic flow. A request sent by an approved flow (Campaigns > Automatic) is a system message.
- **Per-module relax:** "Reply to 4 and 5 star reviews: Go ahead" with a daily cap. Replies to 1 to 3 star reviews always ask.
- **Moderation is E, not A.** Hiding a review from the Site is an edit with a required reason; the review is never deleted.
- **Sensitive fields:** reviewer email and order link are hidden on public surfaces and from Staff without the People grant. Reviews in regulated industries (health, legal) that mention care or case details are flagged sensitive and never auto-published.

## Pages and states

Tabs in nav order:

| Tab | Route | What it shows |
|---|---|---|
| To moderate | `/admin/reviews` | New reviews waiting on Publish or Hide, with the agent's flags (possible personal details, off-topic, profanity) and a drafted reply |
| Published | `/admin/reviews/published` | Live reviews by source (own, public listing), rating, product or service, reply state |
| Requests | `/admin/reviews/requests` | Requests sent, opened, completed, reminder due; per order or job |
| Quote cards | `/admin/reviews/cards` | Approved quotes turned into cards, ready to send to Social |
| Settings | `/admin/reviews/settings` | Request delay, sources, reminder, auto-publish rules. Hidden without K |

**Record view:** URL modal `/admin/reviews?review=<id>`: the review, rating, source, the order or job it came from, the reviewer (link to People), reply editor with the agent's draft, Publish or Hide, Make quote card.

**Quick views:** Needs reply, Low ratings, Has photos, From a public listing, Requests not opened. Filters: rating, source, product or service, date.

**States:**

- **Empty:** "Reviews land here after you ask for them. Turn on requests after delivery." Button: Turn on requests (K), or for Staff: Send a request.
- **Loading:** list skeleton.
- **Error:** "Reviews didn't load. Try again." A public listing that cannot be reached shows "Couldn't sync <source> since <date>" on the Published tab header.
- **Permission:** hidden for Contractor; Customer gets a not found page on any admin route. Settings hidden without K.
- **Disabled with reason:** Reply on a public listing review shows "Connect the listing in Settings to reply here"; Make quote card shows "Publish the review first".

**Badge:** reviews in To moderate plus public reviews with no reply.

## Data model

| Table | Columns |
|---|---|
| `reviews` | `id`, `org_id`, `source` (`own`, `public_listing`), `external_id`, `person_id` null, `order_id` or `job_id` null, `subject_kind` (product, service, business), `subject_id`, `rating` int 1 to 5, `title`, `body`, `photos` (fk `files`), `status` (`pending`, `published`, `hidden`), `hidden_reason`, `sensitive` bool, `flags` jsonb, `published_at`, `created_at`, `updated_at`, `deleted_at` |
| `review_requests` | `id`, `org_id`, `person_id`, `order_id` or `job_id`, `token` (unguessable), `channel` (email, sms), `sent_at`, `opened_at`, `completed_at`, `reminder_sent_at`, `expires_at` |
| `review_replies` | `id`, `review_id`, `body`, `status` (`draft`, `published`), `author_kind`, `author_id`, `published_at`, `external_reply_id` |
| `quote_cards` | `id`, `review_id`, `quote` text, `attribution` text (first name and city, or initials), `file_id` (rendered card), `sent_to_social_at` |

- **Shared:** `people`, `files`, `approvals`, `change_log`; reads Orders, Jobs, Catalog for the subject.
- **Row rules:** org only. A Customer's request token grants create on one `reviews` row tied to that request, nothing else.
- **Anchor kinds:** `review:<id>`, `field:review:<id>.body`, `request:<id>`, `card:<id>`.
- **Config knobs:** `fields.request_delay_days` (default 7 after delivery, 1 after a finished job), `fields.sources` (own, public listing), `fields.reminder_days` (default 5, one reminder only), `fields.auto_publish_min_rating` (default off), `fields.attribution_style` (first name and city).
- **Sample type:** `reviews`. Seeds 40 reviews (mostly 4 and 5 stars, a few low), 60 requests, 5 quote cards, fictional reviewer first names.

## Agent actions

| Action | Tool | Verb | Gated | Writes to `change_log` | Undo |
|---|---|---|---|---|---|
| Send a review request after delivery or a finished job | `send_review_request` | P | System message when sent by an approved flow; otherwise gated | `review_requests` row | Cancels an unsent request |
| Flag personal details, off-topic or abuse | `flag_review` | E | No | `flags` | Clears flags |
| Draft a reply | `draft_reply` | C | No | `review_replies` draft | Deletes draft |
| Publish a reply | `publish_reply` | P | Yes (relaxable for 4 and 5 stars with a cap) | Reply status, external id | Unpublish where the source allows; else logged as not undoable |
| Publish or hide a review | `update_record` | E (P when it goes to the Site) | Publish gated | `status`, `hidden_reason` | Restores status |
| Turn an approved review into a quote card | `make_quote_card` | C | No | `quote_cards` row and rendered file | Deletes card |
| Hand a card to Social as a draft post | `hand_off` | C | No; publishing is gated in Social | Social draft | Deletes draft |

**Background jobs:**

- **Request job (daily):** orders delivered or jobs finished `request_delay_days` ago get a request; one reminder after `reminder_days`; never more than one request per person per 30 days.
- **Public listing sync (every 6 hours):** pull new reviews from connected public listings, draft replies.
- **Weekly best-of:** propose 3 quote cards from the week's published reviews.

## Integrations

- **Email delivery** (default SendGrid) and **SMS** (default Twilio) for requests, with unsubscribe and consent honored.
- **Database** (default Neon Postgres); **file storage** for photos and rendered cards through Library.
- **Platform API:** a public review site's or business listing's API to read reviews and post replies.
- **Webhooks in:** listing notifications where the platform offers them. Out: none.
- **Secrets by name:** `SENDGRID_API_KEY`, `TWILIO_AUTH_TOKEN`, `LISTING_API_CLIENT_ID`, `LISTING_API_CLIENT_SECRET`, `LISTING_REFRESH_TOKEN`.

## SaaS replaced

None priced in `shared/saas.md`. Review collection and reputation tools are not in the explorer yet, so no product is listed here. When the explorer adds them, expected risk is Easy for own-site review widgets (reviews export to CSV) and Plan it where review requests ride on an SMS number with consent records.

Migration pattern: export reviews with dates, ratings and verified flags, import as `source = own` with `published_at` kept, swap the product page widget for the Reviews block, turn on the request flow, cancel at term end.

## Acceptance criteria

1. A Contractor never sees Reviews in the nav, and a deep link shows the no-access page; a Customer gets a not found page.
2. Every agent write (flag, draft, publish, hide, card) appears in Log with before, after and a working Undo where the source allows it.
3. A gated reply shows the review, the full reply text and where it will post on an approval card with one Approve button.
4. Every submit button (Publish, Hide, Send request, Make card) shows a spinner and disables while it runs.
5. A Customer opens their private review link, rates two products from their order and submits; both reviews appear in To moderate within one minute.
6. A request link opened a second time after submit shows "Thanks, we have your review" and cannot create another.
7. Hiding a review requires a reason; the review stays in the database and Published no longer lists it.
8. A 2 star review always waits for a person before any reply posts, even with 4 and 5 star replies relaxed.
9. An Admin clicks Make quote card on a 5 star review and sees a rendered card attributed by first name and city, then Send to Social creates a draft post.
10. A person who got a request in the last 30 days does not get another, and no reminder goes after they submit.
11. A review flagged sensitive in a regulated business never auto-publishes, whatever the auto-publish rating.

## Open questions

1. **Auto-publish 5 star reviews?** Recommended: off for the first month, then offer it for 5 stars with no flags.
2. **Request delay?** Recommended: 7 days after delivery for shipped goods, 1 day after a finished service.
3. **Reminders?** Recommended: one reminder at 5 days, never more.
4. **Attribution on quote cards?** Recommended: first name and city; initials only in health and legal businesses.
5. **Incentives for reviews?** Recommended: none tied to the rating. If Programs is on, award points for any honest review, and say so on the request.
