# Portal: Account (customer, portal)

- **Module key:** `portal.account` (stable, never renamed)
- **Tier:** core
- **Route:** `/portal/account`
- **Folder:** `customer/portal/account/`

## Job

The customer's own profile, contact preferences, message history, team (for business customers), balance and data, in one place they can fix without asking anyone. The number that tells you it is working: **profile and preference changes made by the customer versus requested from staff** (target: over 90 percent self-serve).

## Users and permissions

- Customer, every kind, `own` scope: View and Edit on their profile and preferences; Export and Delete on their own data (`shared/roles.md` 4b People row: own V E D X).
- Buyer store **managers** also see the Team tab for each store they manage: invite and remove store members. Store **members** see the tab read-only.
- Partners see the Balance tab (prepaid balance from Marketplace).
- Owner and Admin: View as customer, read-only.
- Agent (as the customer): View, Edit profile fields and preferences. **Gated (customer's yes):** delete account, export data, remove a store member. Hard delete of a customer's own data is one of the two allowed hard deletes in `shared/roles.md` 1.7 and is logged without content.
- Sensitive fields: the customer sees their own data in full. Internal tags, staff notes, lead score and source attribution are never shown.

## Pages and states

Tabs (sub-routes, so each is a link), in this order, each hidden unless it applies:

| Tab | Route | Shows |
|---|---|---|
| Profile | `/portal/account` | Name, email, phone, mailing and shipping addresses, company details for business kinds (legal name, tax id document upload where the business requires it), profile questions the business asks (from People `profile_answers`) |
| Notifications | `/portal/account/notifications` | Email and SMS preferences by topic (order updates, reminders, news, offers); one-click unsubscribe from all marketing. System messages (receipts, sign-in links) cannot be turned off and say so |
| Messages | `/portal/account/messages` | Their own thread history from Inbox (every message to and from the business, any channel), read-only, with "Send a message" that starts a new Inbox thread |
| Team | `/portal/account/team` | Buyer kinds: members of each store, invite by email, remove, change manager or member |
| Balance | `/portal/account/balance` | Partner kind: prepaid balance, ledger of deposits and lead debits, "Add funds" |
| Data | `/portal/account/data` | Download my data, delete my account |

Record view: none. Profile opens read-only with an Edit button (`shared/design-system.md` 4). Team member rows open as a URL modal `?member=<id>`.

States:
- **Empty:** Messages with no history shows "No messages yet." and Send a message. Team with only you shows "Just you so far." and Invite.
- **Loading / error:** per tab skeleton; error with Retry.
- **Disabled with reason:** Invite is disabled for a store member with "Ask a store manager to invite people". Add funds is disabled with "Payments are set up by the business" when the payments rail is off.
- **Delete account:** a modal names the account, lists what will be removed and what the business must keep by law (paid invoices, signed agreements), and requires typing the email.
- Badge: none.

## Data model

- Owns no tables. Writes `users` (name, phone, avatar), `people` (addresses, `custom`), `email_prefs` and `consents` (People), `profile_answers` (People), `portal_memberships` (Team tab), and reads `threads` and `messages` (Inbox, own person only) and `ledger_entries` (Marketplace).
- Every change to `email_prefs` and `consents` stores the source (`portal`), time and the exact text shown, so consent holds up later.
- **Export:** builds a zip of JSON and CSV for every row tied to the customer's person id across modules, delivered as a signed link valid 24 hours, logged on Log > Exports.
- **Delete:** soft-deletes the login and memberships, then a scheduled job hard-deletes personal data after 30 days, except records the business must keep (paid invoices, signed documents), which are kept with the person reduced to name and id. The job writes `change_log` with `op = delete` and no content.
- Anchors: `person:<id>`, `field:person:<id>.<field>`, `thread:<id>` (own), `member:<membership_id>`, `ledger_entry:<id>`.
- Knobs: `fields.account.tabs` (subset and order), `fields.account.profile_questions` (which People questions to ask), `fields.account.require_tax_doc` (buyer kind). Sample: `contacts`.

## Agent actions

| Action | Tool | Verb | Gated | Writes to `change_log` | Undo |
|---|---|---|---|---|---|
| Update my phone, address, name | `update_record` | E | No | `people` or `users` row, before and after | Yes |
| Change my email preferences ("stop the offers") | `update_record` on `email_prefs` | E | No | `email_prefs` before and after, plus a `consents` row | Yes (re-subscribe needs the customer's explicit yes in chat) |
| Show my last messages with the business | `query_db` | V | No | Nothing | n/a |
| Send a message to the business | `hand_off` | C | No | New Inbox thread | No |
| Invite a teammate to my store | `update_record` on `portal_memberships` | C | No (it is a reply to the person who asked) | membership row with status invited | Yes until accepted |
| Remove a teammate | `update_record` | D | Yes | membership soft-deleted | Yes |
| Export my data | `export_my_data` | X | Yes | Log > Exports row | n/a |
| Delete my account | `delete_my_account` | D | Yes, never relaxable | soft delete now, hard delete job scheduled | Yes for 30 days, by contacting the business |

Background jobs: the 30-day hard-delete job; the export builder.

## Integrations

- **Email delivery:** invite emails, export-ready link, deletion confirmation. Unsubscribe uses one-click list-unsubscribe headers (RFC 8058) on every marketing email so Notifications stays in sync.
- **SMS:** opt-out (STOP) replies update the same `email_prefs` and `consents` rows.
- **Payments:** Add funds opens hosted checkout for partners.
- Webhooks in: email unsubscribe and complaint events, SMS STOP.
- Secrets: shell secrets only.

## SaaS replaced

| Product | Risk | Migration |
|---|---|---|
| Mailchimp (preference center and unsubscribe pages) | No brainer | Export the audience with its unsubscribed and cleaned lists. Import into `email_prefs` and suppressions before the first send. Parallel run is not needed. Cut over by pointing every email footer at Notifications. Cancel with Campaigns. |
| Kit (ConvertKit) (subscriber preferences) | Easy | Same steps as Mailchimp; map tags to preference topics before import. |

## Acceptance criteria

1. A customer without View on a tab (a shopper and the Team tab) never sees the tab, and a deep link to `/portal/account/team` shows the not-found page.
2. Every agent write on Account appears in Log with before, after and a working Undo.
3. Asked "delete my account", the agent shows exactly what will be removed and what the business keeps, with one Approve button, and does nothing until the customer approves.
4. Every submit button on Account shows a spinner and disables while it runs.
5. A customer turns off Offers on Notifications; the next offer campaign skips them, and the change shows on admin People with source `portal`.
6. A customer presses unsubscribe in an email footer; Notifications shows all marketing off on the next page load.
7. A store manager invites `sam@store.example`; Sam gets an email, accepts at `/portal/join/[token]`, and appears on the Team tab as member.
8. A store member sees the Invite button disabled with "Ask a store manager to invite people".
9. A customer requests their data; within 10 minutes they get an email with a link that downloads a zip, and Log > Exports shows the export.
10. A customer deletes their account; they are signed out, cannot sign in again, and 30 days later their personal fields are gone while their paid invoices remain with name only.

## Open questions

1. **Can a customer change their sign-in email themselves?** Default: yes, with a confirmation link sent to the new address; the old address gets a notice.
2. **Show staff names on Messages?** Default: first name only, never the full name or role.
3. **Grace period before hard delete?** Default: 30 days, matching Trash. A business with a legal hold can extend it per customer from admin People.
4. **Let partners add funds by card in the portal?** Default: yes when the payments rail is connected; otherwise "Reply to any of our emails to add funds" and a Board card to the team.
