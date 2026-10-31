# Campaigns (admin, Grow)

- **Module key:** `campaigns`
- **Tier:** common
- **Route:** `/admin/campaigns`
- **Folder:** `admin/grow/campaigns/`

## Job

"Email and text campaigns to our own list, built by the agent, approved by the owner." The agent proposes what to send, builds the audience, writes it, sends a test to the team and waits. A person approves; only then does it go.

The number: **revenue or bookings attributed per campaign sent** in the 7 days after send. Second number: **unsubscribe rate per send** (watch it stays under 0.5 percent).

## Users and permissions

Starts from `shared/roles.md` section 4b. Differences only:

| User type | Campaigns |
|---|---|
| Owner | all. Approves by default |
| Admin | V C E P D X K. Approves only when the Owner delegates it (`fields.approval = admin`) |
| Staff | V C E on drafts. Submit for approval only |
| Contractor | hidden |
| Customer | hidden. Customers see email preferences and one-click unsubscribe in the portal and on the Site |
| Agent | V C E on drafts, sends a test to the team. Never approves. Send is `!` (never relaxable) |

- **Gated agent verbs:** P is never relaxable on Campaigns. Approve is human, always. A test send to addresses on the team list is not a send.
- **Automatic flows** (welcome, abandoned cart, post-purchase) are approved once as a flow; each email the flow then sends is a system message. Editing an approved flow returns it to review.
- **Sensitive fields:** none on the module; audience rules respect People's column grants (a rule cannot filter on a field the user cannot see).

## Pages and states

Tabs in nav order:

| Tab | Route | What it shows |
|---|---|---|
| Campaigns | `/admin/campaigns` | Every campaign: name, channel, audience size, status (Idea, Draft, In review, Approved, Scheduled, Sending, Sent, Cancelled), send time, opens, clicks, revenue |
| Automatic | `/admin/campaigns/automatic` | Flows and system emails (welcome, receipt, order status, abandoned cart, post-purchase, review request): status, last edit, sends this month |
| Audiences | `/admin/campaigns/audiences` | Rule-built audiences with a live count and a sample of 10 who matched |
| Templates | `/admin/campaigns/templates` | Starters written in the business's voice, with [brackets] to fill |
| Reports | `/admin/campaigns/reports` | Per campaign and over time: delivered, opens, clicks, unsubscribes, bounces, spam reports, revenue attributed |
| Settings | `/admin/campaigns/settings` | Sender name, reply-to, mailing address, channels, approver, starters. Hidden without K |

**Record view:** full route `/admin/campaigns/[id]` (the editor) and `/admin/campaigns/[id]/report`. Editor: subject, preview text, block editor with a photo picker from Library, autosave, live preview at desktop and phone width, the agent's rationale ("why this, why now, who"), Send test, Submit for approval, Approve (approver only), Schedule. After send the HTML is frozen and the report tab opens.

**Quick views:** In review, Ideas from the agent, Scheduled, Sent this month. Filters: channel, status, audience, date.

**States:**

- **Empty:** "Your first campaign takes five minutes. Pick a starter or ask the agent for ideas." Buttons: New from a starter, Ask for ideas.
- **Loading:** list skeleton; the editor preview shows a frame first.
- **Error:** "Campaigns didn't load. Try again." A send that fails partway shows Sending paused with the reason and a Resume button; sends are idempotent per recipient.
- **Permission:** hidden for Contractor and Customer. Staff see Submit for approval instead of Send. Approve is rendered only for the approver. Settings hidden without K.
- **Disabled with reason:** Send shows "Add a mailing address in Settings to send" when none is set; "Audience is empty"; "Waiting on Owner approval"; "Sending… 1,240 of 3,013" with a spinner.

**Badge:** campaigns In review, for the approver; drafts returned with changes, for the drafter.

## Data model

| Table | Columns |
|---|---|
| `campaigns` | `id`, `org_id`, `name`, `channel` (`email`, `sms`), `status`, `audience_id`, `subject`, `preview_text`, `body` jsonb (blocks), `frozen_html` text, `rationale` text, `scheduled_for`, `submitted_by`, `approved_by`, `approved_at`, `sent_at`, `owner_id`, `created_at`, `updated_at`, `deleted_at` |
| `campaign_sends` | `id`, `campaign_id`, `person_id`, `address`, `status` (`queued`, `sent`, `dropped`, `failed`), `drop_reason`, `provider_message_id`, `sent_at` |
| `email_events` | `id`, `send_id` (campaign or flow), `event` (`delivered`, `open`, `click`, `bounce`, `spam`, `unsubscribe`), `url`, `at` |
| `audiences` | `id`, `org_id`, `name`, `rules` jsonb, `last_count` int, `counted_at` |
| `flows` | `id`, `org_id`, `kind` (`welcome`, `abandoned_cart`, `post_purchase`, `review_request`, `winback`), `steps` jsonb, `status` (`draft`, `in_review`, `live`, `paused`), `approved_by`, `approved_at` |
| `email_templates` | `id`, `org_id`, `name`, `kind` (`starter`, `system`), `draft` jsonb, `published` jsonb, `published_at` |
| `sender_settings` | `org_id`, `from_name`, `from_email`, `reply_to`, `mailing_address`, `sms_number` |

- **Shared:** `people`, `subscribers`, `email_prefs`, `suppressions` (shared with Outreach), `consents`, `files`, `approvals`, `change_log`.
- **Row rules:** org only (no `own` scope on this module). Staff can edit only drafts they created until submitted.
- **Anchor kinds:** `campaign:<id>`, `audience:<id>`, `flow:<id>`, `field:campaign:<id>.subject`, `block:campaign:<id>.<hash>` (editor blocks, content-hash keys).
- **Config knobs:** `fields.channels` (email, sms), `fields.approval` (`owner` or `admin`), `fields.starters` (template set), `fields.attribution_days` (default 7), `fields.batch_size` (default 500 per minute).
- **Sample type:** `campaigns`. Seeds 6 sent campaigns with reports, 2 in review, 3 audiences, 4 flows, `.example` addresses.

## Agent actions

| Action | Tool | Verb | Gated | Writes to `change_log` | Undo |
|---|---|---|---|---|---|
| Propose campaign ideas (weekly) | `propose_campaigns` | C | No | Campaigns with status Idea and a rationale | Deletes ideas |
| Build an audience from rules, with live count and sample | `build_audience` | C | No | `audiences` row | Deletes or restores rules |
| Write the email or text with its rationale | `draft_campaign` | C/E | No | `body`, `subject`, `rationale` | Restores prior version |
| Send a test to the team | `send_test` | C | No (team addresses only; refuses any other) | Test event | n/a |
| Submit for approval | `submit_for_approval` | E | No | `status = in_review`, `approvals` row | Withdraws |
| Approve | none | A | Agent cannot | n/a | n/a |
| Send or schedule | `send_campaign` | P | `!` Never relaxable | Only after a human Approve and the human pressing Send or Schedule | Cancel before send; not undoable after |
| Read results and write the "what worked" note | `summarize_report` | read | No | Note on the report | n/a |

**Send rules (enforced in the send job, not just the UI):** confirm the exact count before send; block without a mailing address; drop unsubscribed, bounced, complained and do-not-contact; SMS only to people with SMS consent and inside quiet hours; one-click unsubscribe header and footer link on every email.

**Background jobs:**

- **Monday ideas:** three campaign ideas with rationale and an audience each, landing as Idea.
- **Scheduled sends:** batches of `fields.batch_size`, resumable, re-queue stuck sends hourly.
- **Flows:** run on their trigger (signup, cart left 4 hours, delivered plus N days).
- **Daily digest (quiet if nothing happened):** sends, deliveries, opens, clicks, unsubscribes, bounces, spam reports.

## Integrations

- **Email delivery** (default SendGrid; contract: bulk send with per-recipient custom args, signed event webhook, suppression groups mapped to `email_prefs`, authenticated sending domain).
- **SMS** (default Twilio; contract: registered campaign under 10DLC, STOP and HELP handling, delivery callbacks).
- **Payments** (default Stripe) read-only, for revenue attribution through orders.
- **Database** (default Neon Postgres).
- **Webhooks in:** email events, SMS status and STOP. Out: none.
- **Secrets by name:** `SENDGRID_API_KEY`, `SENDGRID_WEBHOOK_KEY`, `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_MESSAGING_SERVICE_SID`.

## SaaS replaced

| Product | Risk | Migration step |
|---|---|---|
| Mailchimp | No brainer | Export audience with status and tags, import the unsubscribe and cleaned lists into `suppressions` first, import subscribers, rebuild two or three templates as starters, send the next newsletter from YEA, cancel |
| Constant Contact | No brainer | Export contacts and unsubscribes, import suppressions first, import contacts, send the next newsletter from YEA, cancel |
| Kit (ConvertKit) | Easy | Export subscribers with tags and sequence state, map tags to audience rules, rebuild sequences as flows, run both one week, cancel |
| beehiiv | Easy | Export subscribers; move any paid subscription's Stripe link to Shop or Money first; import; send the next issue from YEA; cancel |
| ActiveCampaign (email half) | Easy | Export contacts with list status, rebuild automations as flows (approved once), parallel run one week, cancel with the CRM half (Pipeline) |
| Klaviyo | Plan it | Export profiles with consent and suppression; rebuild abandoned cart and post-purchase flows; run both for two weeks with Klaviyo flows paused per segment and compare revenue per recipient; cut over when YEA is within 10 percent; cancel |
| SimpleTexting | Plan it | Export the opt-in log with timestamps and keywords; port the number to the SMS rail or register a new 10DLC campaign; import consents before any send; send one campaign from YEA; cancel |

## Acceptance criteria

1. A Contractor or Customer never sees Campaigns in the nav, and a deep link shows the no-access page.
2. Every agent write (idea, audience, draft, submit) appears in Log with before, after and a working Undo.
3. When the agent submits a campaign, the Owner sees the exact recipient count, how many were dropped and why, the mailing address, and a preview, with one Approve button; the agent has no path to send.
4. Every submit button (Send test, Submit, Approve, Send, Schedule) shows a spinner and disables while it runs.
5. A Staff user opens a draft and sees Submit for approval where an Owner sees Send.
6. With no mailing address set, Send is disabled with "Add a mailing address in Settings to send".
7. An Admin builds an audience "bought twice in 90 days, not unsubscribed" and sees a live count and a sample of 10 names before saving.
8. The agent's test send goes only to team addresses; asking it to test to a customer's address is refused in chat.
9. A 3,000 recipient send shows progress ("Sending… 1,240 of 3,013"), and if the job stops it resumes without sending anyone a second copy.
10. A recipient who unsubscribed last month is in the dropped count and gets nothing.
11. After send, the campaign's HTML is frozen; editing is no longer offered, and the report shows delivered, opens, clicks, unsubscribes, bounces and attributed revenue.
12. Editing a live flow moves it to In review and pauses new sends from that flow until approved again.

## Open questions

1. **Who approves by default?** Recommended: Owner. Offer to delegate to Admin or a Reviewer named role after the first five campaigns.
2. **Attribution window?** Recommended: 7 days from click for consumer brands, 30 days for B2B.
3. **SMS on by default?** Recommended: off until the business has a registered number and an imported consent log.
4. **Weekly ideas on by default?** Recommended: on, three ideas every Monday, easy to dismiss.
5. **Send rate?** Recommended: 500 a minute, slower on a new sending domain for the first two weeks.
