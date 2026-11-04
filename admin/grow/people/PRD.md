# People (admin, Grow)

- **Module key:** `people`
- **Tier:** core
- **Route:** `/admin/people`
- **Folder:** `admin/grow/people/`

## Job

"Every human we have touched, in one list, with one timeline each." A lead, a client, a vendor, a partner, someone you hired, someone you parted ways with, a subscriber, a press contact: one row per person, forever, never split, with their companies, orders, messages and consent in one place.

The number: **duplicate rate**, the share of people rows the merge check flags as likely duplicates (target under 1 percent). Second number: share of people with a known consent state for email.

## One person, many relationships

A person is permanent. What they are to the business changes, so that lives in `relationships`, not on the person. Each relationship has a kind, a stage, a start and an end. A person can hold several at once, and the same kind more than once over the years.

Example, at the fictional Quillback marina. Dana Reyes:

| When | What happens | Relationship rows |
|---|---|---|
| March | Fills in the contact form | `lead` opens |
| April | Starts doing rigging work for the yard | `lead` closes as converted, `vendor` opens |
| The next year | Starts sending boat owners over too | `partner` opens, `vendor` stays open |
| Two years on | The work stops | `vendor` and `partner` end, with a reason |
| Three years on | The marina hires Dana to run the yard | `team` opens |

That is still one person, with one timeline, and every message and invoice from the first day on it. The ordinary path is the shortest one: a lead becomes a client.

The rules:

- **Moves are free.** Any kind can follow any other. A lead can become a client, a vendor, a partner or a hire. Nothing is one-way.
- **Ending is never deleting.** An ended relationship stays on the record with its dates and reason. Deleting a person is a separate act, covered under hard delete below.
- **Coming back opens a new row.** A second stint is a new row, so each stint keeps its own dates. A person has at most one open row per kind.
- **Relationships don't grant access.** Sign-in and permissions come from Team and Portal. Ending `team` deactivates the login. Ending the last relationship that used the Portal turns Portal access off. Coming back asks for access again, chosen fresh, and old permissions never return by themselves.
- **Ending doesn't touch consent.** Email preferences and do-not-contact stay as they are until the person or an Owner changes them.

## Users and permissions

Starts from `shared/roles.md` section 4b. Differences only:

| User type | People |
|---|---|
| Owner, Admin | all |
| Staff | V C E. No D, X, K. Cannot merge |
| Contractor | own: V E. Own = people linked to a company or lead they own. Cannot create people outside their book except through a lead |
| Customer | own: V E D X on their own profile, through Portal Account (edit details, email preferences, download data, delete account) |
| Agent | V C E, D* (merge), X* |

- **Gated agent verbs:** D (merge or delete) and X (any export of personal data). Merges always ask first, even when relaxed, because a merge touches more than one record.
- **Per-module relax:** "fill blanks from public sources: Go ahead" is the only relax that makes sense here, capped per day in Costs.
- **Hiring and ending:** opening or ending a `team` relationship is Owner only, because it moves access. Ending any other kind needs E.
- **Sensitive fields:** `relationships.end_reason`, date of birth, home address, health or case details in `profile_answers` marked sensitive, government ids. Hidden without the column grant; stripped from agent query results for that user.
- **Hard delete:** a Customer deleting their own account, and the Owner emptying Trash. Both logged without content.

## Pages and states

Tabs in nav order:

| Tab | Route | What it shows |
|---|---|---|
| Everyone | `/admin/people` | All people, sortable by last activity. Columns: name, kind chips, company, email, phone, last touch, consent state |
| Clients | `/admin/people/customers` | People with an open customer relationship, with lifetime value, orders, bookings or jobs count, last purchase. The label comes from `fields.customer_label`: Clients for service businesses, Customers for shops, Members, Patients. The route never changes |
| Vendors | `/admin/people/vendors` | People with an open vendor relationship, with stage, what they do, last paid, last touch |
| Partners | `/admin/people/partners` | People with an open partner relationship, with stage, what they send or sell, last touch |
| Subscribers | `/admin/people/subscribers` | Everyone with an email preference record: subscribed, unsubscribed, bounced, source of signup |
| Press | `/admin/people/press` | Press and media contacts with outlet, beat, last pitch, reply state |
| Merge duplicates | `/admin/people/merge` | Pairs the check flagged, side by side, with which fields differ and the agent's pick |
| Settings | `/admin/people/settings` | Kinds, custom fields, profile questions. Hidden without K |

Tabs can be hidden through `fields.tabs` (a business with no press drops Press). The Team tab is not here: staff live in Team, and a person who is on the team shows a `team` chip that links there.

**Record view:** full route `/admin/people/[id]`. Header: name, avatar, kind chips, primary action (Email, or Reply if a thread is waiting), Add relationship. Tabs:

1. **Profile**: contact details, custom fields, profile answers, tags.
2. **Relationships**: every relationship they have ever had, newest first, with kind, stage, dates and end reason. Open rows have Move stage and End. Ended rows have Open again.
3. **Companies**: companies they belong to and their role at each.
4. **Leads**: every lead row for this person with stage.
5. **Orders** (or **Bookings**, **Jobs**, following the Sell modules that are on).
6. **Messages**: every thread in Inbox with them.
7. **Consent**: per channel state, verbatim text, when and where granted or revoked, do-not-contact flag.
8. **Rewards**: points and claims, only when Programs is on.

**Quick views:** Recently active, Former (nothing open now), Worked with us before (ended vendor, partner or team), Customers who bought twice, Never contacted, Unsubscribed, Do not contact, Likely duplicates. Filters: kind, tag, company, consent state, last touch window, custom fields.

**States:**

- **Empty:** "Everyone you deal with lands here: leads, customers, subscribers." Buttons: Add a person, Import CSV.
- **Loading:** table skeleton.
- **Error:** "People didn't load. Try again." with Retry.
- **Permission:** without `people.view`, nav hidden and deep links show no-access. Without E, records open read-only. Merge duplicates tab is hidden without D. Export in the bulk bar is hidden without X.
- **Disabled with reason:** Email shows "Unsubscribed on 2026-09-14" or "On do-not-contact" when the person cannot be emailed; Merge shows "Pick exactly two people" in select mode.

**Badge:** none. People is a directory, not a queue.

## Data model

Owned tables (the shared `people` and `companies` tables hold the core rows):

| Table | Columns |
|---|---|
| `relationships` | `id`, `org_id`, `person_id`, `kind` (from `fields.kinds`), `stage` (from `fields.relationship_stages`), `started_at`, `ended_at` null, `end_reason` null, `opened_from` (anchor of what started it, such as `lead:<id>`), `owner_id`, `custom` jsonb, `created_at`, `updated_at`. Unique on `person_id` and `kind` where `ended_at` is null |
| `company_people` | `id`, `company_id`, `person_id`, `role` text, `primary` bool, `from_at`, `to_at` |
| `subscribers` | `id`, `org_id`, `person_id`, `list_key`, `status` (`subscribed`, `unsubscribed`, `bounced`, `complained`), `source` (form, import, checkout, event), `confirmed_at` (double opt-in), `changed_at` |
| `email_prefs` | `id`, `person_id`, `topic_key`, `on` bool, `changed_at`, `changed_by` (person, customer, system) |
| `profile_answers` | `id`, `person_id`, `question_key`, `answer` jsonb, `sensitive` bool, `answered_at` |
| `do_not_contact` | `id`, `org_id`, `person_id` null, `email` null, `phone` null, `domain` null, `reason`, `added_by`, `added_at` |
| `person_merges` | `id`, `kept_id`, `merged_id`, `field_choices` jsonb, `merged_by`, `merged_at`, `undone_at` |

- **Shared:** `people` (one row forever; kind chips are the open `relationships` rows, never a column), `consents` (owned by Leads, read here), `companies`, `activities`, `threads`, `messages`, `tags`, `change_log`.
- **Row rules for `own`:** Contractors read `people` rows linked through `company_people` or `leads` to a record they own. Customers read and write only the `people` row whose `user_id` is theirs, plus their `email_prefs`.
- **Anchor kinds:** `person:<id>`, `relationship:<id>`, `field:person:<id>.<field>`, `merge:<id>` (a flagged pair on Merge duplicates).
- **Config knobs:** `label` (People, Contacts, Clients, Members, Waitlist), `fields.kinds` (default lead, customer, vendor, partner, team, subscriber, press), `fields.customer_label` (default Clients), `fields.relationship_stages` (by kind; vendor defaults to candidate, trial, active, paused, ended; partner to prospect, invited, agreed, active, paused, ended; customer to active, paused, ended), `fields.custom`, `fields.profile_questions`, `fields.tabs`, `fields.double_opt_in` (default on).
- **Sample type:** `contacts`. Seeds 120 people across kinds, one person with the full path above, 4 likely duplicate pairs, 10 unsubscribed, 2 on do-not-contact, `.example` emails, 555-01xx phones.

## Agent actions

| Action | Tool | Verb | Gated | Writes to `change_log` | Undo |
|---|---|---|---|---|---|
| Open a relationship | `open_relationship` | E | Asks first for `team`, which only the Owner can approve | `relationships` insert, `opened_from` | Removes the row |
| Move a relationship stage | `update_record` | E | No (bulk over 5 asks) | `stage` before, after | Restores the stage |
| End a relationship | `end_relationship` | E | Yes, always asks, and says what access will change | `ended_at`, `end_reason`; for `team`, the Team deactivation | Reopens the row; access comes back only through Team |
| Find and propose duplicate merges | `find_duplicates` | read | No | Nothing (proposals only) | n/a |
| Merge two people | `merge_people` | D | Yes, always asks | `person_merges` row, moved child rows, soft deleted loser | Unmerge restores both rows and their children |
| Fill blank fields from public sources | `enrich_person` | E | No (relaxable cap) | Each filled field with its source URL in `custom.sources` | Clears the filled fields |
| Tag people by kind or behaviour | `tag_records` | E | No (over 5 asks) | `taggings` rows | Removes tags |
| Build a list from a sentence ("bought twice, never reviewed") | `build_list` | C | No | A saved view or an audience (Campaigns) with the query | Deletes the view |
| Export a list | `export_people` | X | Yes | Export event on Log > Exports | Not undoable; logged |
| Add to do-not-contact | `update_record` | E | No | `do_not_contact` row | Removes the row |
| Draft an email to selected people | `draft_email` | C | No | Draft | Deletes the draft |

**Background jobs:**

- **Duplicate check (nightly):** match on email, phone, then name plus company; writes candidate pairs to Merge duplicates with a confidence score.
- **Bounce and complaint sync (on webhook):** sets `subscribers.status`, adds hard bounces and spam complaints to suppression.
- **Data export for a customer (on request):** builds a zip of their own records within 24 hours and emails the link as a system message.

## Integrations

- **Email delivery** (default SendGrid; contract: event webhook for bounce, spam report, unsubscribe, group unsubscribe ids map to `email_prefs.topic_key`). One-click unsubscribe (RFC 8058) on every non-system email.
- **SMS** (default Twilio): STOP and START write `consents`.
- **Database** (default Neon Postgres) with row rules.
- **Platform APIs (optional):** a public business directory or search API for enrichment, budget capped in Costs.
- **Webhooks in:** email events; newsletter signup from Site.
- **Secrets by name:** `SENDGRID_API_KEY`, `SENDGRID_WEBHOOK_KEY`, `TWILIO_AUTH_TOKEN`, `ENRICH_API_KEY` (optional).

## SaaS replaced

`shared/saas.md` re-keys the CRM category to Pipeline and People. People takes the contact half:

| Product | Risk | Migration step |
|---|---|---|
| Close | Easy | Export contacts with custom fields, import to `people` and `company_people`, parallel run with Pipeline, cancel |
| Pipedrive | Easy | Export persons and organizations, import, run the duplicate check before go-live, cancel |
| Zoho CRM | Easy | Export contacts with custom fields mapped to `fields.custom`, import, check duplicates, cancel |
| HubSpot Sales Hub Starter | Plan it | Export contacts with lifecycle stage, original source and subscription status; import consent and unsubscribe state first so no one unsubscribed gets mail; two week parallel run; cancel |
| Salesforce Starter Suite | Plan it | Export contacts and accounts with ids kept in `custom.legacy_id`; import; reconcile counts by account; two week parallel run; cancel |

Mailing list subscribers from email marketing tools move with Campaigns, landing here as `subscribers` rows.

## Acceptance criteria

1. A user without `people.view` never sees People in the nav, and a deep link to a person shows the no-access page without the person's name.
2. Every agent write (enrich, tag, merge) appears in Log with before, after and a working Undo; unmerging restores both people and their orders and messages.
3. When the agent proposes a merge, the Admin sees both records side by side with the fields that will be kept and one Approve button; nothing merges before Approve.
4. Every submit button (Save, Merge, Import, Export) shows a spinner and disables while it runs.
5. A lead who places an order shows as one person with the lead relationship closed and a customer relationship open, and the timeline holds both the lead and the order.
6. An Admin types "everyone who bought twice and never reviewed" in chat; the agent returns a list with a live count and a sample of 5 names, and offers to save it as a view.
7. A person who clicks unsubscribe shows Unsubscribed on the Consent tab within one minute, and the Email button shows "Unsubscribed on <date>" disabled.
8. A Contractor sees only people linked to their own book; searching another rep's contact by email returns nothing.
9. A Customer opens Portal Account, downloads their data, and receives a link to a zip containing only their own records.
10. A Customer deletes their account; their `people` row and child rows are removed, and Log shows the delete without any of their content.
11. Staff without the sensitive grant open a person and sensitive profile answers are not rendered.
12. Exporting 300 people as the agent waits for a human yes and then appears on Log > Exports with the row count.
13. One person moves through lead, vendor, partner, ended and hired back. There is one `people` row the whole way, four relationship rows show on the Relationships tab with their dates, and messages from the first day are still on the timeline.
14. A lead converted to a client appears on the Clients tab within one refresh, and disappears from it when that relationship ends, while staying on Everyone and on the Former view.
15. Ending a `team` relationship revokes every session in under a minute. Opening `team` again sends a new invite with a role chosen fresh, and the old role does not return by itself.
16. Trying to open a second `vendor` row while one is open is refused with "Already an active vendor". Opening one after the first has ended succeeds and keeps both rows.
17. A Staff user without the sensitive grant sees that a relationship ended and when, but not the reason.
18. Setting `fields.customer_label` to Members changes the tab name without changing its route.

## Open questions

1. **Double opt-in for newsletter signups?** Recommended: on. Turn off only where the business has a reason and the Owner confirms.
2. **Merge confidence to auto-propose?** Recommended: propose at 0.8 and up, never auto-merge.
3. **Show press as its own tab?** Recommended: only when `fields.kinds` includes press; hidden by default for consumer shops.
4. **Enrichment budget?** Recommended: $10 a month cap in Costs to start; raise when the Owner sees the fill rate.
5. **Customer self-delete keeps orders?** Recommended: keep order rows the books need with the person detached and name replaced by "Deleted customer", since tax records must stay.
6. **Same person is staff and a client?** Recommended: one login, with the admin type. Their client records stay reachable from their person record, and the Portal view is opt-in. Separate logins for one human split the timeline.
7. **Warn before re-engaging someone?** Recommended: yes. Opening a relationship on someone with a prior end shows the last end reason to whoever has the grant, with no hard block.
