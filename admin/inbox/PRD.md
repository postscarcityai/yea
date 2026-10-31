# Inbox (admin, pinned above the groups)

- **Module key:** `inbox` (stable, never renamed)
- **Tier:** core
- **Route:** `/admin/inbox`
- **Folder:** `admin/inbox/`

## Job

"Every message to the business lands in one place, threaded, with a reply already drafted, and nobody wonders who is answering it." Email to any address on the domain, SMS, web chat from the Site, DMs and comments from social channels, and messages customers send from the Portal all become threads here, linked to the person and company they are about.

The number that tells you it is working: **median time to first human or approved reply on a new inbound thread** (business hours). Second: share of threads closed with zero manual linking (the agent matched the person right).

## Users and permissions

Start from `shared/roles.md` section 4a.

| User type | Scope | Differs from the matrix how |
|---|---|---|
| Owner | all | Also manages aliases and the auto-send knob. |
| Admin | all | V C E P D X K. Can edit Rules and aliases. |
| Staff | all | V C E P. Replies, assigns, archives. Cannot delete, export or edit Rules. |
| Contractor | own | Sees only threads assigned to them or linked to a person in their book. Can reply (P) and edit status (E). No compose to new recipients outside their book. |
| Customer | own | Not in the admin Inbox. Their own thread history shows on Portal Account, and new messages they send from Portal, Site or Intake land here as threads. |
| Agent | as its role | V C E. P* (sending a reply is a send, gated by default). D* only for moving a thread to Spam. |

- **Gated verbs for the agent:** P (any reply or new message, including DM and comment auto-replies), D (Spam), X (export of threads, personal data).
- **Per-module relax (Agents > Permissions):** P can be relaxed with limits: channels (for example DM and comment replies only), business hours only, and a daily cap (default 50). `fields.auto_send` lists which thread kinds are eligible at all; a kind not listed always waits for a person even if P is relaxed. Default: `fields.auto_send = []` and P "Ask me first".
- **A reply to the person who asked is still a send.** `shared/roles.md` rule 6 treats a reply drafted to an inbound thread as a send. System messages (receipts, sign-in links, booking confirmations) never go through Inbox drafts; they are sent by their own module and logged on the thread as `kind = system`.
- **Sensitive fields:** message bodies on threads linked to a record the Owner marked sensitive (health or case details) follow that record's column grant; without it the thread shows sender, subject and time only. Attachments follow the same rule.

## Pages and states

Two panes on desktop: list left (380px), thread right. On mobile the list is the page and a thread opens full screen.

| Tab | Route | Holds |
|---|---|---|
| Inbox | `/admin/inbox` | Open threads, newest activity first. Default for Owner and Admin. |
| Assigned to me | `/admin/inbox?tab=mine` | Open threads assigned to the viewer. Default for Staff and Contractor. |
| Archived | `/admin/inbox?tab=archived` | Done threads. A new inbound message reopens a thread into Inbox. |
| Spam | `/admin/inbox?tab=spam` | Auto and manual spam. Kept 30 days, then purged. Not spam moves it back and teaches the rule. |
| Rules | `/admin/inbox?tab=rules` | Routing, auto-link, auto-label and spam rules, plus aliases. Hidden without K. |

- **Record view:** full route `/admin/inbox/[thread]` (the right pane; the URL changes as you click). Compose at `/admin/inbox/new`. Thread view: header (subject, person chip, company chip, status chip, assignee, channel icon, primary action), messages oldest to newest, the agent's draft pinned above the composer, and a right column with person facts and linked records (lead, order, booking, card).
- **The draft:** every inbound thread that needs a reply gets a draft in the business's voice, shown above the composer with "Agent draft" and the sources it used. Buttons: **Send** (if the user has P), **Edit**, **Discard**. With the user lacking P, Send becomes **Submit for approval**.
- **Composer:** pick the from-address (any alias the user may send as), cc, attachments, channel (email, SMS where the person has a number and consent). SMS shows segment count and blocks when consent is missing ("No SMS consent on file").
- **Empty states:** Inbox: "No open threads. New messages to any address land here." Assigned to me: "Nothing assigned to you." Spam: "No spam in the last 30 days." Rules: "No rules yet. The agent links threads to people on its own; add a rule to route by address or keyword."
- **Loading:** list skeleton (8 rows), thread skeleton. Sending: the Send button spins, the message appears in the thread greyed with "Sending…" until the provider accepts it.
- **Error:** send failed: the message stays in the thread marked "Not sent" with the provider's reason and Retry. Inbound parse failure: a system row on Log and an item on Home > Now ("1 message could not be read").
- **Permission states:** without `inbox.view` the nav item is hidden. Without P, Send is replaced by Submit for approval. Without D, Spam is not in the thread menu. Contractor deep link to a thread outside their book: the no-access page, nothing about the thread shown.
- **Quick views (chips above the list):** Needs reply (default for Owner and Admin), Unassigned, Waiting on approval, From customers, From leads. Collapsed filters: channel, alias, assignee, label, date.
- **Badge count:** open threads with an unanswered inbound message, in the viewer's scope (a Contractor's badge counts only their threads).

## Data model

Shared tables `threads` and `messages` are defined in `shared/data-model.md`; Inbox owns their columns and adds the rest.

**`threads`**: `id`, `org_id`, `channel` (email, sms, web_chat, dm; the set in `shared/data-model.md`), `source` (direct, site, intake, portal, social_comment), `subject`, `person_id` FK `people`, `company_id` FK `companies`, `status` (open, archived, spam), `assignee_id`, `owner_id`, `customer_id`, `labels text[]`, `last_inbound_at`, `last_outbound_at`, `needs_reply bool`, `linked jsonb` (anchors of related records: `lead:12`, `order:1042`), `external_ref` (Message-ID root, DM conversation id), `created_at`, `updated_at`, `deleted_at`.

**`messages`**: `id`, `thread_id`, `direction` (in, out), `kind` (message, draft, system, note), `from_addr`, `to_addrs text[]`, `cc_addrs text[]`, `alias_id`, `body_text`, `body_html`, `provider_id`, `status` (received, draft, waiting_approval, queued, sent, delivered, bounced, failed), `approval_id` FK `approvals`, `author_kind` (person, agent, system), `author_id`, `spam_score numeric`, `at`.

**`attachments`**: `id`, `message_id`, `file_id` FK `files`, `filename`, `mime`, `bytes`.

**`inbox_rules`**: `id`, `org_id`, `kind` (route, label, link, spam), `match jsonb` (to-alias, from-domain, keyword, channel), `action jsonb` (assign to, add label, link to company, mark spam, flag to Board), `position`, `enabled`, `hits int`.

**`aliases`**: `id`, `org_id`, `address` (`hello@business.example`), `label`, `default_assignee_id`, `can_send_as text[]` (role keys), `signature`, `catch_all bool`.

**`suppressions`**: `id`, `org_id`, `address_or_phone`, `channel`, `reason` (unsubscribed, bounced, complaint, stop_keyword, manual), `source`, `at`. Shared with Campaigns and Outreach: one list, every sender checks it.

- **Threading:** email by `Message-ID` / `In-Reply-To` / `References`, then by sender plus normalized subject within 14 days. SMS by phone pair. DM by the platform's conversation id.
- **Own scope:** a Contractor sees a thread when `assignee_id` is them or `person_id` belongs to a person they own. Row rule in the database, not just the query.
- **Anchor kinds:** `thread:<id>`, `message:<id>`, `field:thread:<id>.assignee`, `field:thread:<id>.status`.
- **Config knobs:** `fields.channels` (email, sms, web_chat, dm), `fields.aliases` (seed list), `fields.auto_send` (thread kinds eligible for agent sends, default empty). Sample type: `messages`.

## Agent actions

| Action | Tool | Verb | Gated | Writes to `change_log` | Undo |
|---|---|---|---|---|---|
| Summarize a thread, find related records | `get_record`, `search`, `query_db` | V | No | Nothing | n/a |
| Link a thread to a person or company | `link_thread` | E | No | `threads.person_id` / `company_id` before, after | Restores the old link |
| Create a person from a new sender | `update_record` on `people` (insert) | C | No | insert row | Soft-deletes the new person, unlinks the thread |
| Assign or route a thread | `assign_thread` | E | No | `assignee_id` before, after | Restores the previous assignee |
| Label, archive, reopen | `update_record` | E | No | before, after | Restores |
| Draft a reply | `draft_reply` | C | No | `messages` insert with `kind = draft` | Deletes the draft |
| Send a reply or new message | `send_message` | P | **Yes** (relaxable per channel with cap) | `messages.status` draft to sent, with approval id | Cannot unsend. Undo is offered only while queued (first 10 seconds) |
| Mark spam | `mark_spam` | D | **Yes** (relaxable) | `threads.status` before, after; rule hit | Moves back to Inbox |
| Turn a thread into a lead | `create_lead_from_thread` | C on Leads | No | Leads insert, thread `linked` update | Soft-deletes the lead, removes the link |
| Flag a request to the Board | `file_request` | C on Board | No | `cards` insert with `source = inbox` | Soft-deletes the card |
| Export threads | `export` | X | **Yes**, never relaxed for personal data | `exports` row on Log | n/a |

**Background jobs**

- `inbox.ingest` (triggered by the inbound webhook): parse, thread, score spam, apply Rules, link to a person, set `needs_reply`, then queue `inbox.draft`.
- `inbox.draft` (triggered): writes the draft from the thread, the person's history, Playbook answers and Settings > Brand voice. Never sends unless `fields.auto_send` includes the kind and P is relaxed on Agents.
- `inbox.dm_qualify` (triggered, only when `dm` is in `fields.channels`): replies to DMs and comments with the qualifying questions from Playbook, then hands off to a person (assign plus Home > Now) when the person qualifies or asks for a human. Every reply is a send and follows the gate.
- `inbox.spam_purge` (daily): hard-deletes Spam older than 30 days, logged without content.

## Integrations

- **Email delivery** (default SendGrid; contract: send API with custom from per alias, inbound parse webhook posting raw MIME, event webhook for delivered, bounced, complaint, unsubscribe). Inbound uses MX on a subdomain or a catch-all route; DNS records are set on Settings > Email.
- **SMS** (default Twilio): send API, inbound webhook, STOP/HELP keywords write to `suppressions`. 10DLC registration is the business's, done once on Settings > Channels.
- **Web chat:** the Site's web chat channel posts to `/api/inbox/webchat`; the visitor gets the agent in the widget, the thread lands here.
- **Platform APIs:** each social network's messaging API for DMs and comments, through a posting connector the Social module also uses.
- **Webhooks in:** `/api/inbox/inbound/email`, `/api/inbox/inbound/sms`, `/api/inbox/inbound/dm`, `/api/inbox/events`. Every webhook verifies its signature.
- **Webhooks out:** none.
- **Secrets:** `SENDGRID_API_KEY`, `SENDGRID_INBOUND_SECRET`, `SENDGRID_EVENT_WEBHOOK_KEY`, `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `SOCIAL_CONNECTOR_KEY`.

## SaaS replaced

| Product | Risk | Migration |
|---|---|---|
| Zendesk | Easy | Export tickets and macros. Import tickets as archived threads linked to people. Rewrite macros as Playbook answers the agent drafts from. Point the support address at YEA, run both one week, cancel. |
| Freshdesk | Easy | Same as Zendesk. Help articles go to Playbook. |
| Help Scout | Easy | Export conversations, import as archived threads, repoint the support address, cancel. |
| Gorgias | Easy | Moves with the store. Import tickets after Orders is live so threads link to orders, then cancel. |
| Intercom | Easy | Export conversations. Replace the widget with the Site web chat channel. Run both on the site for one week (split by page), then cancel. |
| Tidio | No brainer | Swap the embed for the web chat channel. Cancel. |
| LiveChat | No brainer | Swap the embed. Cancel. |
| Crisp | No brainer | Swap the embed and forward the shared inbox address. Cancel. |
| Slack (team threads) | Plan it | Internal notes on threads and Board comments replace most channels. Export history first (legal hold), keep Slack in parallel for one month, cancel only when no channel has had a post in two weeks. |
| Google Workspace Gmail | Careful | Moves last, or stays. Start with shared addresses only (hello@, support@) forwarded into Inbox. Personal mailboxes move only after one full mail cycle in parallel and a planned MX cutover; keep the old provider for login recovery until every vendor account is repointed. |

## Acceptance criteria

1. A user without `inbox.view` never sees the Inbox nav item, and a deep link to `/admin/inbox/[thread]` shows the no-access page with no subject or sender shown.
2. Every agent write (link, assign, label, draft, spam) appears in Log with before, after and a working Undo.
3. With P gated, the agent's reply shows in chat and on Home > Today as "Send to dana@example.com from hello@business.example: <first line>" with Approve and Change, and nothing is sent until a human approves.
4. Every submit button (Send, Submit for approval, Save rule, Mark spam) shows a spinner and disables while it runs.
5. An email sent to any alias appears as a new thread within 60 seconds, linked to the existing person when the sender's address matches `people.email`.
6. A reply from the customer to that email threads into the same thread, not a new one, and moves an archived thread back to Inbox.
7. Every new inbound thread that needs a reply shows an agent draft above the composer within 30 seconds of arrival.
8. A Staff user without P sees Submit for approval instead of Send, and after submitting the thread shows "Waiting on approval".
9. A Contractor sees only threads assigned to them or linked to their book; the badge count equals the Needs reply view count in their scope.
10. An SMS reply to a person with no SMS consent is blocked with "No SMS consent on file", and a STOP reply adds the number to `suppressions` within one minute.
11. Owner sets `fields.auto_send = ["dm"]` and relaxes P for DMs with a cap of 50; the 51st DM reply that day waits for approval instead of sending.
12. A thread marked Not spam moves back to Inbox and the spam rule that caught it shows one fewer hit next time it is evaluated.

## Open questions

1. **Inbound email routing: MX on a subdomain or forwarding from the current mail host?** Recommended: forwarding from the existing provider for the first month (no MX change), then a subdomain MX for shared addresses. Personal mailboxes stay where they are until the Careful cutover.
2. **Should the agent draft on every thread or only ones that need a reply?** Recommended: only `needs_reply` threads, skipping newsletters, receipts and auto-replies (detected by headers).
3. **Auto-assign by default?** Recommended: route by alias default assignee, then round robin among Staff with Inbox access during business hours. Off for Contractors unless the thread links to their book.
4. **Where does internal discussion live?** Recommended: `kind = note` messages on the thread, never sent, visible to admin-side users only.
5. **Retention of message bodies?** Recommended: keep forever by default, purge Spam after 30 days, and let the Owner set a retention on Settings > Data for regulated businesses.
