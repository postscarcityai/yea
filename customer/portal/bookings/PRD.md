# Portal: Bookings (customer, portal)

- **Module key:** `portal.bookings` (stable, never renamed)
- **Tier:** follows Bookings (`bookings`, common, not yet proven). Shows only when Bookings is enabled.
- **Route:** `/portal/bookings`
- **Folder:** `customer/portal/bookings/`

Bookings is not yet proven in production. This page starts from the spec, not from running code.

## Job

Let customers see, book, move and cancel their own appointments inside the business's rules, so the front desk stops playing phone tag. The number that tells you it is working: **share of reschedules and cancellations done self-serve**, and **no-show rate** (should fall with reminders and easy rescheduling).

## Users and permissions

- Customer kinds `shopper`, `buyer`, `member`, `client`: View, Create, Edit (reschedule), Delete (cancel), all `own`. Partners do not see Bookings.
- Rules come from the booking type in Bookings: lead time to book, reschedule window ("up to 24 hours before"), cancel window, deposit and whether it is refunded.
- Inside the window the customer acts directly. Outside it, Reschedule and Cancel become **Request change**, which files a Board card for the team (`shared/roles.md` 6b.5).
- Clients with a Job see bookings tied to that job (Jobs client view).
- Agent (as the customer): View, Create, Edit. **Gated (customer's yes):** book with a deposit, cancel, and any reschedule or cancel that forfeits a deposit.
- Sensitive fields: staff notes, internal calendar events, other customers' slots (only free or busy is shown, never names).

## Pages and states

- **Tabs:** Upcoming (`/portal/bookings`), Past (`/portal/bookings/past`), Book (`/portal/bookings/new`).
- **Upcoming:** cards with date, time, booking type, with whom (first name), place or video link, status chip, and one primary action: Reschedule (inside window) or Request change (outside). Secondary: Add to calendar (.ics), Cancel.
- **Record:** URL modal `?booking=<id>` with details, policy text, deposit paid, and history of changes.
- **Book:** pick a booking type (only types open to this customer kind), then a day, then a slot. Slots come from Bookings availability. If a deposit applies, confirm goes to hosted checkout and returns to the confirmation.
- **Reschedule:** the same slot picker in the modal, with the policy line above it ("Free to move until Tue 3:00 PM").
- **Waitlist:** when no slot fits, "Tell me if something opens" adds them to the waitlist for that type and date range.
- **States:** empty Upcoming says "Nothing booked." with Book. Loading skeleton cards. Error with Retry. Slot taken while confirming: "That time was just taken. Here are the closest open times." with three slots.
- **Disabled with reason:** Cancel outside the window shows "Cancelling now forfeits the $50 deposit" and still runs after confirm when the policy allows it.
- Badge: none. Home shows a booking in the next 48 hours.

## Data model

- Owns no tables. Reads `bookings`, `availability`, `booking_types`, `calendar_events` (busy only) from Bookings; writes `bookings` (create, move, cancel) and `bookings_waitlist` (owned by Bookings) through row rules on `customer_id`.
- Every create, move and cancel writes `change_log`, and moves keep the previous time in `before`.
- Deposits: a `payments` row in Money linked to the booking; refunds follow the type's policy and go through admin approval when over the module's cap.
- Anchors: `booking:<id>`, `booking_type:<key>`, `slot:<type>:<iso_start>`.
- Knobs (on Bookings, read here): `fields.booking_types` with `customer_kinds`, `book_lead_hours`, `reschedule_cutoff_hours`, `cancel_cutoff_hours`, `deposit_cents`, `deposit_refundable`. Portal knob: `fields.bookings.show_staff_name` (default first name). Sample: `appointments`.

## Agent actions

| Action | Tool | Verb | Gated | Writes to `change_log` | Undo |
|---|---|---|---|---|---|
| When is my next appointment | `query_db` | V | No | Nothing | n/a |
| Find open times ("anything Thursday after 4") | `find_slots` | V | No | Nothing | n/a |
| Book a slot with no deposit | `create_booking` | C | No (the customer asked; confirmation is a system message) | `bookings` insert | Yes, cancels inside the window |
| Book a slot with a deposit | `create_booking` | C, $ | Yes | `bookings` insert, payment | Cancel per policy |
| Move a booking inside the window | `move_booking` | E | No | `bookings` start and end before and after | Yes, if the old slot is still free |
| Cancel a booking | `cancel_booking` | D | Yes | `bookings.status` before and after | Yes, if the slot is still free |
| Ask for a change outside the window | `file_request` | C | No | Board card linked to the booking | Yes while New |
| Join the waitlist | `join_waitlist` | C | No | `bookings_waitlist` insert | Yes |

Background jobs (owned by Bookings, surfaced here): confirmation on book and move, reminder 24 hours and 2 hours before (email and SMS where opted in), waitlist offer when a slot opens (first to accept gets it).

## Integrations

- **Email delivery and SMS:** confirmations and reminders. Each carries one link back to `?booking=<id>`.
- **Payments:** deposits through hosted checkout; refunds through Money.
- **Calendar file:** `.ics` download per booking; a private per-customer calendar feed URL is an option.
- Webhooks in: payment succeeded and failed. Secrets: none of its own.

## SaaS replaced

| Product | Risk | Migration |
|---|---|---|
| Calendly | No brainer | Export upcoming events and booking types. Recreate types in Bookings. Import future bookings with customers. Parallel run one week with both links live. Cut over by swapping the link on the Site and in email signatures. Cancel. |
| Cal.com | No brainer | Same steps as Calendly. |
| Acuity Scheduling | Easy | Export appointments with intake answers and deposit status. Move future appointments first, then history. Parallel run two weeks so paid deposits on old bookings are honored. Cut over the booking link. Cancel after the last old appointment. |

## Acceptance criteria

1. A partner never sees Bookings in the nav, and a deep link to `/portal/bookings?booking=88` shows the not-found page.
2. Every agent write on Bookings (book, move, cancel, waitlist) appears in Log with before, after and a working Undo while the old slot is free.
3. Asked to cancel a booking 6 hours out with a non-refundable deposit, the agent shows "Cancel Thu 4:00 PM consult. The $50 deposit will not be refunded." with one Approve button and does nothing until approved.
4. Every submit button on Bookings shows a spinner and disables while it runs.
5. A member reschedules a booking 3 days out to another open slot; the card shows the new time and a confirmation email arrives with the new time.
6. A member tries to reschedule 2 hours before a booking with a 24 hour cutoff; the action reads Request change and files a Board card.
7. Two customers confirm the same slot; the second sees "That time was just taken" with three nearest open times.
8. A customer joins the waitlist for Friday; when a Friday slot opens they get an offer, accept it, and the booking appears under Upcoming.
9. A client sees only booking types that list `client` in `customer_kinds`.

## Open questions

1. **Show staff names and photos on booking cards?** Default: first name only, photo off; the business can turn photos on.
2. **Collect intake questions at booking time?** Default: yes, the booking type can attach an Intake form; answers land on the booking and on Leads for new customers.
3. **Private calendar feed per customer?** Default: off; `.ics` per booking covers most needs without a long-lived URL.
4. **Charge a no-show fee automatically?** Default: no; staff mark a no-show and the fee is a gated `$` action in admin.
