# Portal: Home (customer, portal)

- **Module key:** `portal.home` (stable, never renamed)
- **Tier:** core
- **Route:** `/portal`
- **Folder:** `customer/portal/home/`

## Job

The first screen a customer sees: what needs them right now, where their last order or booking stands, what they owe, and the one next step. The number that tells you it is working: **share of open customer items (invoice due, document to sign, booking to confirm) closed within 48 hours of first sign-in that shows them**.

## Users and permissions

- Customer, every kind, `own` scope: View. Home has nothing to edit except dismissing a next step.
- What Home shows is filtered by the customer's kinds and the pages they can see. A tile for a hidden page never renders.
- Owner and Admin see this page through View as customer (read-only).
- Agent: View, plus dismiss a next step on the customer's request. No gated verbs on Home itself; actions launched from a tile follow the target page's gates.
- Sensitive fields: none rendered.

## Pages and states

One page, no tabs. Sections top to bottom:

1. **Open items:** a list of things waiting on the customer, newest due first. Sources: invoices due or overdue (Invoices), documents waiting for a signature or an upload (Documents), a booking in the next 48 hours (Bookings), a reorder that is due by the customer's usual cadence (Reorder), new leads not yet viewed (Leads), a listing checklist item missing (Listing). Each row has one primary action: Pay, Sign, Upload, View, Reorder, Finish listing.
2. **Latest:** the last order with its status chip and tracking, or the next booking with date, time and place. Whichever is more recent. A buyer with several stores sees one row per store.
3. **Balance:** what they owe (sum of open invoices) or, for partners, their prepaid balance. Shown only when Invoices or Leads is visible.
4. **Points:** points balance and the nearest offer they can claim, when Rewards is visible.
5. **Next step:** one card chosen by rule (below), with one button and a Dismiss link.

States:
- **Empty:** a new customer with nothing open sees "You're all set." plus the next-step card (for example "Book your first visit" or "Finish your listing").
- **Loading:** skeleton rows per section; sections load independently so a slow source does not block the rest.
- **Error:** a failed section shows one line and Retry inside that section only.
- **Permission:** sections tied to hidden pages are not rendered.
- No badge on Home itself. The nav badges on Invoices and Leads use the same counts as Open items.

Next-step rule, first match wins: overdue invoice, then a document to sign, then an unconfirmed booking, then a reorder due, then an incomplete listing, then an unclaimed offer, then a business-chosen default from `fields.home.default_step`.

## Data model

- Owns no tables. Reads `invoices` (Money), `documents` and `signatures` (Documents), `bookings` (Bookings), `orders` (Orders), `assignments` and `ledger_entries` (Marketplace), `points_ledger` and `offers` (Programs), `prospects` (Listing checklist), all through row rules.
- Dismissed next steps are stored on `users.prefs jsonb` under `portal.dismissed_steps` with the step key and dismiss time; a dismissed step returns after 7 days if still true.
- Anchors: `queue_item:<module>:<id>` for each open item, `tile:balance`, `tile:points`, `tile:latest`, `tile:next_step`.
- Knobs: `fields.home.sections` (order and subset of the five sections), `fields.home.default_step` (key and label of the fallback next step). Sample: reads the feeding modules' samples.

## Agent actions

| Action | Tool | Verb | Gated | Writes to `change_log` | Undo |
|---|---|---|---|---|---|
| Explain an open item ("why is this overdue") | `get_record` | V | No | Nothing | n/a |
| Open the record behind an item | `navigate` | none | No | Nothing | n/a |
| Summarize "what do I need to do" | `query_db` | V | No | Nothing | n/a |
| Dismiss a next step | `update_record` on `users.prefs` | E | No | `users.prefs` before and after | Yes |
| Start the item's action (pay, sign, reorder) | hands to the target page's tool | per page | per page | per page | per page |

Background jobs: none owned. The weekly customer digest is an option (see Open questions).

## Integrations

- Reads only. Email delivery is used only if the weekly digest is turned on.
- No webhooks. No secrets beyond the shell's.

## SaaS replaced

None on its own. Home is part of the portal shell; see `customer/portal/PRD.md` for the products the portal replaces.

## Acceptance criteria

1. A customer without View on Home cannot exist (Home is core); a signed-out visitor deep-linking to `/portal` is sent to `/portal/login`, and a customer deep-linking to a page they cannot see gets the not-found page.
2. Every agent write on Home (a dismissed next step) appears in Log with before, after and a working Undo.
3. A gated action started from a Home row (Pay) waits for the customer's yes in the chat and shows the exact amount and card before charging.
4. Every submit button on Home shows a spinner and disables while it runs.
5. A client with an unsigned agreement and an invoice 3 days overdue sees both under Open items, with the invoice first and the next-step card reading "Pay invoice 2041".
6. A shopper never sees the Balance section or a Leads row.
7. A buyer with two stores sees the latest order for each store under Latest.
8. A customer dismisses the next step; it disappears, and a toast offers Undo for 4 seconds.
9. When the invoices source fails to load, Open items shows "Couldn't load invoices. Retry." and the other sections still render.

## Open questions

1. **Weekly email digest of open items?** Default: off. Turn on per business with `fields.home.digest = weekly`; it is a system message to the customer, not a campaign, so it is not gated.
2. **Show a "recently changed" feed (order shipped, document signed) on Home?** Default: no; Latest and Open items cover it and keep Home short.
3. **Let a business pin a custom announcement to every customer's Home?** Default: yes, one line from Settings, shown above Open items, dismissible.
