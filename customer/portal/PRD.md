# Portal (customer, portal)

- **Module key:** `portal` (stable, never renamed)
- **Tier:** core (the shell, sign-in, Home and Account are core; every other page follows the admin module that feeds it)
- **Route:** `/portal`, sign-in at `/portal/login`
- **Folder:** `customer/portal/`

This PRD covers the portal shell: sign-in, the left nav, which pages show for which customer, the store switcher, admin preview, and the customer chat. Each page folder below has its own PRD.

## Job

Give every signed-in customer their own app: the same shell and chat the team uses, showing only their records, so they can reorder, book, pay, sign and ask without emailing anyone. The number that tells you it is working: **share of customer requests that finish inside the portal** (reorders, payments, reschedules, signatures) instead of arriving by email or phone.

## Users and permissions

- **Customer** is the only type that signs in here. Every grant is `own` scope. A customer holds one or more kinds (`shopper`, `buyer`, `member`, `partner`, `client`); kinds stack on one login. The page-by-kind table in `shared/roles.md` section 4g is the source of truth.
- A page renders only when all three hold: the customer has a kind that grants View on it, the feeding admin module is enabled, and the page is listed in `fields.pages`. Home and Account always render.
- **Owner and Admin** can preview the portal as any customer from People (`View as customer`). Preview is read-only: every write button is hidden, a top banner reads "Previewing as Jane Doe. Read-only." and the preview is logged on Log > Sign-ins. Staff, Contractor and Agent never preview.
- **Agent** in the portal runs as the signed-in customer with that customer's verbs and scope. It never sees another customer, staff notes, cost, margin, payout or any field marked sensitive. Every `$` action and every delete waits for the customer's own yes in the chat. See `shared/roles.md` section 5.9.
- **Buyer accounts with several stores:** one login can act for several companies. `portal_memberships` holds one row per (user, company, kind). Store members have a membership role: `manager` (can invite teammates and pay) or `member` (can order and view).
- Sensitive fields: none rendered in the portal. Cost, margin, internal notes, assignee names beyond a first name, and routing rules are stripped from every portal query and from the agent's tool results.

## Pages and states

- **Sign-in** `/portal/login`: one email field, button "Email me a sign-in link". The link lands on `/portal/auth/[token]` and follows the same-browser check in `admin/run/team/PRD.md` (Sign-in flow): the browser that asked for the link goes straight in; any other browser gets one "Continue to sign in" button that signs in on POST, so a mail scanner opening the link cannot spend it. Error states: expired link ("This link expired. Send a new one." with the email prefilled), used link, unknown email (same success message as a known email, so the page never reveals who is a customer).
- **Claim and invite** `/portal/claim/[token]` and `/portal/join/[token]`: one screen naming the business or store being claimed or joined, one button. First visit asks for name and phone only if missing.
- **Shell:** the admin shell from `shared/design-system.md`, unchanged. Left nav in this order, each hidden unless granted: Home, Orders, Reorder, Bookings, Documents, Invoices (badge), Rewards, Leads (badge), Listing, Posts, Kit, Account. No groups on the portal side; the nav is one flat list. Labels follow each feeding module's `label` knob (Bookings shows as "Appointments" if Bookings is relabeled).
- **Top bar:** page title, the store switcher (only when the login holds more than one company), the points pill when Rewards is on ("1,240 points"). The chat opens from the FAB bottom right or Cmd/Ctrl+J.
- **Store switcher:** a select in the top bar. The chosen company is in the URL (`?store=<id>`) so every view is a link. Lists show the chosen store; Home can show "All stores".
- **States:** loading uses skeleton rows; error shows one sentence and Retry; empty states say what goes there and offer one next step. A deep link to a page the customer cannot see returns the normal not-found page; nothing about the record leaks.
- **Mobile:** nav is a drawer, chat is a full-screen sheet, same as admin.
- **Profile block:** bottom of the left nav, initials avatar, name, kinds held as the role line, caret. Menu: My profile (Account), Theme, Back to the site, Sign out. Sign out lives nowhere else. See `shared/design-system.md` section 2a.

## Data model

Portal reads every feeding module's tables through row rules filtered on `customer_id` (or `company_id` through `portal_memberships`). It owns two tables:

| Table | Columns |
|---|---|
| `portal_memberships` | `id`, `org_id`, `user_id` (fk `users`), `person_id` (fk `people`), `company_id` (fk `companies`, null for an individual shopper), `customer_kind` (shopper, buyer, member, partner, client), `membership_role` (manager, member), `status` (invited, active, paused), `invited_by`, `created_at`, `updated_at`, `deleted_at` |
| `portal_preview_log` | `id`, `org_id`, `viewer_user_id`, `as_user_id`, `started_at`, `ended_at` |

- Sign-in uses the shared `sessions` and `auth_log` tables and Team's `login_links` with `audience = 'portal'`. Store only the sha256 of each token; links are single use and expire in 24 hours. The consume step marks the link used in the same UPDATE that checks it. Sessions last 30 days.
- Row rules: a customer reads a row when `customer_id` = their person id, or `company_id` is a company they hold an active membership for. Rules live in the database, not only in the tool layer.
- Every write (by the customer or the agent on their behalf) writes `change_log` with `actor_kind`, `on_behalf_of` and the chat message id when it came from chat.
- Anchors: the portal renders the same anchor kinds as the feeding modules (`order:<number>`, `invoice:<number>`, `booking:<id>`, `document:<id>`), filtered to own records, plus `store:<company_id>` for the store switcher.
- Config knobs: `customer.kinds` (which kinds this business has), `fields.pages` (which portal pages are on, in nav order), `fields.welcome` (one line shown on first sign-in). Sample: per feeding module, plus `contacts` for the customer logins.

## Agent actions

The chat on the right is the same component as admin (`shared/chat.md` section 13). It runs as the customer.

| Action | Tool | Verb | Gated | Writes to `change_log` | Undo |
|---|---|---|---|---|---|
| Answer about any own record | `get_record`, `query_db` (customer role, own rows only) | V | No | Nothing | n/a |
| Point at a row or open a page | `navigate`, `highlight` | none | No | Nothing | n/a |
| File a request or a problem | `file_request` | C | No | Board card, `source = portal`, linked to the record | Yes, deletes the card while it is still New |
| Hand off to a person | `hand_off` | C | No | Inbox thread on the customer's person, with the chat transcript | No (a message was sent to the team) |
| Page-specific actions | see each page PRD | per page | per page | per page | per page |

Background jobs owned by the shell:
- **Sign-in link mailer:** on request, sends the link through the email rail. System message, never gated.
- **Invite reminder:** an invited membership not accepted in 3 days gets one reminder; after 14 days it shows on admin People as "Invite not accepted".

## Integrations

- **Email delivery** (default SendGrid, any provider with templates and event webhooks): sign-in links, invites, every system message the pages send. Contract: send API plus delivered, bounced and complained webhooks into `messages`.
- **Payments** (default Stripe): hosted checkout and saved payment methods used by Reorder, Invoices and Bookings. The portal never touches a card number.
- **Hosting and database:** shared with admin.
- Webhooks in: email events. Webhooks out: none.
- Secrets: `EMAIL_API_KEY`, `PAYMENTS_SECRET_KEY`, `PAYMENTS_WEBHOOK_SECRET`, `SESSION_SECRET`.

## SaaS replaced

| Product | Risk | Migration |
|---|---|---|
| Kajabi (members area and customer login) | Plan it | Export members and active subscriptions. Import members as portal customers of kind `member`. Parallel run one billing cycle with subscriptions still on the old system. Cut over by moving subscriptions to the payments rail without re-charging. Cancel after the first clean cycle. |
| Teachable (student login) | Plan it | Same steps as Kajabi. Course content itself is not a proven module; members-only pages move, courses stay until a course module exists. |
| Shopify (customer accounts) | Plan it | Moves with Shop and Orders, never alone. Export customers and order history, import to `people` and Orders, send each customer a portal invite, parallel run while the store is live on both, cancel with the store. |

## Acceptance criteria

1. A customer without View on a page never sees its nav item, and a deep link to it shows the normal not-found page with no record title or count.
2. Every agent write made from the portal chat appears in admin Log with before, after and a working Undo, and in the customer's chat Changes tab.
3. A gated agent action in the portal (any payment, cancel or delete) waits for the customer's yes and shows exactly what will happen ("Pay invoice 2041, $480.00, card ending 4242") with one Approve button.
4. Every submit button in the portal shows a spinner and disables while it runs.
5. A customer requests a sign-in link and opens it in the same browser: they land on Home with no extra click. Opened in a different browser, the link shows "Continue to sign in" first. Opening a used link again shows "This link was already used".
6. Requesting a link for an email that is not a customer shows the same confirmation as a real one and sends nothing.
7. A buyer whose login belongs to two stores sees the store switcher; switching to the second store changes every list and the URL carries `?store=`.
8. A shopper never sees Invoices, Leads, Listing, Posts or Kit in the nav, even when those admin modules are on.
9. An Owner opens People, picks a customer, presses View as customer, and sees that customer's portal with a read-only banner and no write buttons; the preview appears on Log > Sign-ins.
10. The portal chat, asked about another customer's order number, answers that it cannot find that order.

## Open questions

1. **Passkeys alongside magic links?** Default: magic link only at launch; add passkeys as an option on Account once sign-in volume justifies it.
2. **Self sign-up without an order or invite?** Default: no. A customer record is created by an order, booking, intake, claim or invite; the login form only works for known emails.
3. **Session length for businesses handling sensitive records (client kind)?** Default: 30 days for every kind, 7 days when `customer.kinds` includes `client` and Documents holds signed agreements.
4. **Show the portal on a custom subdomain?** Default: same domain as the Site under `/portal`, no extra DNS work.
