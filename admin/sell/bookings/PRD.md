# Bookings (admin, Sell)

- **Module key:** `bookings` (stable, never renamed)
- **Tier:** common
- **Route:** `/admin/bookings`
- **Folder:** `admin/sell/bookings/`

## Job

"Customers book themselves into open time, get reminded, and every date that matters to the business sits on one calendar." Appointments, consults, sessions and deadlines from Jobs share one calendar; a cancellation gets filled from the waitlist instead of going empty.

Status: **not yet proven** in production (`shared/modules.md` section 1, call 8). This PRD starts from the spec. Build it to the spec and prove it on the first business that turns it on.

The number: **booked hours as a share of available hours this week**, with no-show rate next to it.

## Users and permissions

Start from `shared/roles.md` section 4c. What differs or needs saying:

- **Owner, Admin:** every booking, every calendar, every verb, plus Availability and Booking pages.
- **Staff:** View, Create, Edit, Send on all bookings. Can book, move and cancel for a customer and send a reminder. Cannot edit Booking pages or other people's availability unless granted `bookings.configure`.
- **Contractor:** `own` scope. Sees and works the bookings assigned to them and their own availability. Cannot see other staff calendars beyond free or busy.
- **Customer:** portal (`/portal/bookings`) and public booking pages only. Books, moves and cancels their own bookings inside the business's rules (notice window, deposit). Covered in `customer/portal/bookings/PRD.md`.
- **Agent:** V C E. Booking, moving and confirming for the person who asked is not a Send. Reminders are system messages to the person who booked and need no approval. A message to fill a cancellation from the waitlist is a Send and is gated. Taking or refunding a deposit is `$` and gated.
- **Sensitive fields:** `bookings.notes_internal`, intake answers marked sensitive on the booking type (health, case details). Hidden from Contractors unless the booking is theirs; never sent to a model unless the Owner allows it on the booking type.

## Pages and states

Tabs, in nav order (each a sub-route):

1. **Calendar** `/admin/bookings`: day, week and month views, one column per staff member in day view. Shows bookings, blocked time and events from Jobs. Click empty time to book; drag to move (with a confirm that names the customer).
2. **Bookings** `/admin/bookings/list`: table of upcoming and past bookings. Columns: when, customer, type, with, status chip, deposit. Primary action per row: **Confirm** (pending), **Check in** (today), **Open**.
3. **Availability** `/admin/bookings/availability`: weekly hours per person, date overrides, buffers, minimum notice, maximum per day. Contractors see only their own.
4. **Booking pages** `/admin/bookings/pages`: one public page per booking type (`/book/<slug>` on the Site) with duration, price or deposit, intake questions, who can take it, and the confirmation text.

**Record view:** URL modal `?booking=<id>` over the current tab. Blocks: when and with whom, customer (link to People), type, status, intake answers, deposit, reminders sent, history with Undo. Read-only with an **Edit** button. Esc closes.

**Quick views:** Today, Needs confirmation, No-shows this week, Waitlist, Cancelled in last 24 hours. Filters: type, staff, status, date range.

**States:**

- Empty: "No bookings yet. Set your hours, then share your booking page." Buttons: **Set availability**, **Copy booking link**.
- Loading: calendar grid skeleton.
- Error: "Calendar did not load. Try again." with retry. A failed external calendar sync shows a banner with the account name and **Reconnect**, never a blank calendar.
- No access: no nav item, deep link shows the no-access page.
- Read-only: a Contractor opening another person's booking sees free or busy only, no customer name.
- Disabled with reason: **Book** reads "Outside this person's hours" or "Inside the 24 hour notice window".

**Badge:** bookings needing confirmation plus today's bookings not yet checked in, same scope as the list.

## Data model

Owned tables (each also carries `org_id`, `created_at`, `updated_at`, `deleted_at`):

| Table | Columns |
|---|---|
| `booking_types` | `id`, `slug`, `label`, `duration_min int`, `buffer_before_min int`, `buffer_after_min int`, `price_cents int null`, `deposit_cents int null`, `currency`, `staff_ids uuid[]`, `questions jsonb`, `sensitive bool`, `min_notice_min int`, `max_per_day int null`, `status text` |
| `availability` | `id`, `user_id`, `weekday int`, `start_time time`, `end_time time`, `timezone text` |
| `availability_overrides` | `id`, `user_id`, `date date`, `start_time null`, `end_time null`, `reason text` (null times = off all day) |
| `bookings` | `id`, `booking_type_id`, `customer_id → people`, `assignee_id → users`, `owner_id`, `starts_at timestamptz`, `ends_at timestamptz`, `timezone`, `status text` (key from `fields.stages`), `answers jsonb`, `notes_internal text`, `deposit_cents`, `payment_ref text null`, `job_id → jobs null`, `source jsonb`, `manage_key text` (unguessable, for the reschedule link), `custom jsonb` |
| `booking_reminders` | `id`, `booking_id`, `channel text` (email, sms), `send_at`, `sent_at null`, `message_id → messages null` |
| `waitlist_entries` | `id`, `booking_type_id`, `customer_id`, `window jsonb` (days and hours they can do), `status text`, `offered_at null` |
| `calendar_events` | `id`, `subject_kind text`, `subject_id`, `title`, `starts_at`, `ends_at`, `all_day bool`, `user_ids uuid[]`, `external_ref text null` (deadlines from Jobs, blocked time, synced busy blocks) |

Foreign keys into shared tables: `people` (customer), `users` (staff), `messages` (confirmations and reminders), `approvals` (waitlist offers, deposits), `change_log`.

**Row rules for `own`:** a Contractor sees a booking when `assignee_id` or `owner_id` is them. A Customer sees a booking when `customer_id` is their `people` row.

**Anchor kinds:** `booking:<id>`, `event:<id>`, `booking_type:<slug>`, `field:booking:<id>.starts_at`. The calendar renders each block with its anchor, so "move this to Thursday" works on a pinned block.

**Config knobs:**

- `label`: Bookings, Appointments, Sessions or Reservations.
- `fields.booking_types`: the starting list (label, duration, price).
- `fields.deposit`: off, fixed amount, or percent of price. Default off.
- `fields.stages`: default Requested, Confirmed, Checked in, Completed, No-show, Cancelled.
- `fields.reminders`: default email 24 hours before, SMS 2 hours before when the customer gave SMS consent.
- `fields.cancel_notice_min`: default 1440 (24 hours); inside it the portal shows "Call to cancel".
- **Sample:** `appointments`.

## Agent actions

| Action | Tool | Verb | Gated | Writes to `change_log` | Undo |
|---|---|---|---|---|---|
| Find open time and answer "when can she come in" | `find_slots` | V | No | Nothing | n/a |
| Book a customer into a slot | `create_booking` | C | No (confirmation is a system message) | `bookings` insert, `booking_reminders` insert | Cancels the booking and sends nothing further |
| Move a booking | `move_booking` | E | No for one; over 5 at once it states the list and waits | `bookings.starts_at`, `ends_at` | Moves it back if the old slot is still free; otherwise asks |
| Confirm a pending booking | `update_record` | E | No | `bookings.status` | Restores Requested |
| Offer a cancelled slot to the waitlist | `offer_slot` | P | Gated unless relaxed (limit: business hours, 3 offers per slot) | `waitlist_entries.status`, `messages` insert | Withdraws the open offer |
| Take or refund a deposit | `charge_deposit`, `refund_deposit` | `$` | Always gated; refunds over the cap never relaxable | `bookings.payment_ref`, Money `payments` | Refund only, through Money |
| Add a Jobs deadline to the calendar | `create_event` | C | No | `calendar_events` insert | Deletes the event |

**Background jobs:**

- **Reminders** (every 5 minutes): sends due `booking_reminders` by email, and by SMS only when `people.consent` holds SMS consent.
- **Daily agenda** (07:00 in the business timezone): each staff member gets their day; the Owner gets every overdue deadline and today's bookings.
- **No-show sweep** (hourly): bookings past `ends_at` not checked in move to No-show after 30 minutes and land in the No-shows view.
- **Calendar sync** (every 10 minutes, if connected): pulls busy blocks from each staff member's external calendar into `calendar_events` so double booking cannot happen. Write-back is off by default.

## Integrations

- **Email delivery** (default SendGrid): confirmations, reminders, reschedule links. Attach an `.ics` file to every confirmation.
- **SMS rail** (default Twilio): reminders only, only with consent, with STOP handling written to `people.consent`.
- **Payments rail** (default Stripe): deposits through a payment link or a saved card at booking time. YEA never holds a card number.
- **External calendars (optional):** read-only busy sync from a staff member's existing calendar over CalDAV or the provider's API until the business moves calendars into YEA.
- **Webhooks in:** payment succeeded, SMS STOP, email events.
- **Webhooks out:** `booking.created`, `booking.cancelled`.
- **Secrets (names only):** `EMAIL_API_KEY`, `SMS_ACCOUNT_SID`, `SMS_AUTH_TOKEN`, `PAYMENTS_SECRET_KEY`, `CALENDAR_OAUTH_CLIENT_SECRET`.

## SaaS replaced

| Product | Risk | Migration |
|---|---|---|
| Calendly | No brainer | Export: upcoming events and invitees to CSV. Import: future bookings with their customers into `people`. Parallel run: one week where both links work, YEA busy blocks pulled from the old calendar. Cutover: swap the booking link on the site, email signature and bio. Cancel at the end of the billing period. |
| Cal.com | No brainer | Same steps as Calendly. |
| Acuity Scheduling | Easy | Export: appointments, intake form answers and paid deposits. Import: future appointments first, with intake answers into `answers`; past ones as history. Parallel run: two weeks, so deposits already paid are honored. Cutover: swap links. Cancel after the last pre-paid appointment is served. |
| Google Workspace (calendar half) | Careful | Keep the existing calendar and sync busy time into YEA in v1. Move calendars only after the mail cutover for Inbox is complete, with one full mail cycle in parallel. Cancel only when Inbox has also moved. |

## Acceptance criteria

1. A Contractor without `bookings.view` never sees the nav item, and a deep link to `/admin/bookings?booking=88` shows the no-access page with no customer name or time.
2. Every agent write (a booking created, moved or confirmed) appears in Log with before, after and a working Undo; Undo on a move puts the block back in its old slot on the calendar.
3. When the agent offers a cancelled slot to the waitlist, the Admin sees an approval card naming the slot, the 3 people it will text or email and the message text, with one Approve button; nothing is sent before Approve.
4. Every submit button (Book, Move, Confirm, Save availability, Publish page) shows a spinner and disables while it runs.
5. A Customer books from `/book/consult`; the booking appears on the assigned staff member's calendar within 5 seconds and the customer receives a confirmation email with an `.ics` attachment.
6. Staff tries to book inside a staff member's off hours; the Book button is disabled with "Outside this person's hours".
7. A Customer tries to cancel inside `fields.cancel_notice_min`; the portal shows "Call to cancel" with the business phone instead of a Cancel button.
8. A booking passes its end time by 30 minutes without check in; it shows No-show and appears in the No-shows view.
9. A Contractor opens the day view; other staff columns show only Busy blocks, with no customer names.
10. A Customer with no SMS consent gets email reminders only; the reminder log on the booking shows no SMS row.

## Open questions

1. **Does YEA write bookings back to staff members' external calendars?** Recommended default: no in v1. Read busy time only; staff see bookings in YEA and in the daily agenda email.
2. **Deposits: payment link or saved card?** Recommended default: payment link at booking time; the booking stays Requested until it is paid, and the hold expires after 30 minutes.
3. **Group bookings (classes, tours)?** Recommended default: out of v1. Add `capacity int` to `booking_types` later; the schema leaves room.
4. **Who confirms bookings?** Recommended default: auto-confirm for booking types without a deposit; Requested until paid for those with one.
5. **Timezone shown to the customer?** Recommended default: the customer's browser timezone on the booking page, the business timezone in admin, both on the confirmation email.
