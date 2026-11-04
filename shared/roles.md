# YEA roles: six user types and the permission matrix

Part of the YEA docs. Revised 2026-10-31. The module list and the "Sees" floor come from `shared/modules.md`.



---

## 1. The calls I made, and why

1. **Six types, fixed. Named roles sit on top.** Every user has exactly one type: Owner, Admin, Staff, Contractor, Customer or Agent. A type is a ceiling. The owner can create named roles from a type ("Bookkeeper", "Viewer", "Reviewer") that trim verbs, never add them. This closes the gap every proven app had (one admin role, or a role column nothing enforced) without inventing a role editor nobody uses.
2. **Eight verbs, the same on every module.** View, Create, Edit, Approve, Send/Publish, Delete, Export, Configure. Spend is not a ninth verb: it is a flag on any Edit or Send that moves money or incurs cost, and it is gated like Send.
3. **Scope is a second axis, not more roles.** Every grant is `all` or `own`. Contractor and Customer grants are always `own`. "Own" means records they created, are assigned, or belong to (their book, their orders, their job).
4. **The agent is a user, never a superuser.** In chat it runs as the signed-in person. In the background it runs as a named role the owner picks. Its verbs are that role's verbs minus Approve and Configure. Every write it makes is logged with Undo. Every Send, Publish, Spend and Delete waits for a human yes until the owner relaxes that module.
5. **Approve is always human.** No setting lets an agent approve, including its own drafts. Relaxing a module removes the need for approval; it does not make the agent an approver.
6. **A reply to the person who asked is not a send.** Receipts, sign-in links, order status, the report a customer requested, a booking confirmation: these are system messages and need no approval. "Send" means a message the recipient did not just ask for: a campaign, an outreach step, a reply drafted to an inbound thread, a public post.
7. **Deletes are soft.** Delete moves a record to Trash for 30 days, logged with Undo. Hard delete exists for two cases only: the Owner emptying Trash, and a customer deleting their own data. Both are logged without the content.
8. **Export is a send.** An export takes data out of the app. Personal data exports are logged on Log > Exports and gated for the agent.
9. **No access shows as nothing, not as a locked thing.** Hidden beats disabled. Read-only is the default way every record opens anyway, so "no Edit" just means the Edit button is not there. Section 6 has the full rules.

---

## 2. Verbs and scope

| Code | Verb | Means |
|---|---|---|
| V | View | See the module in the nav, open its lists and records |
| C | Create | Add a record, a draft, an upload, a request |
| E | Edit | Change fields, status, stage, assignment. Includes quick actions on a read-only record |
| A | Approve | Say yes to someone else's draft or request: a campaign, an application, a refund, a pending order, a giveaway, an agent's gated action |
| P | Send / Publish | Something leaves the app or goes public: email, SMS, DM, post, page live, invoice reminder |
| D | Delete | Soft delete to Trash (30 days, Undo) |
| X | Export | CSV, PDF bundle, books export, data download |
| K | Configure | The module's knobs: stages, kinds, custom fields, tabs, rules, templates, label |
| $ | Spend (flag) | A C, E or P that moves money or incurs cost: refunds, payouts, price changes, lead debits, ad budgets, paid calls over a cap |

Scope: `all` (default for O, A, S) or `own` (always for C and Cu). Agent scope is the scope of the role it runs as.

Permission keys are `<module>.<verb>` (`leads.view`, `campaigns.approve`, `money.send`). The stored grant is `{ role, module, verb, scope, gated }`. `gated` is only meaningful for the Agent and is true by default for P, D, X on personal data, and every `$` action.

---

## 3. The six user types

### Owner
The person who owns the business and answers for it. There is one Owner per business (ownership can be transferred, never shared). The Owner can do every verb on every module, and is the only type that can change Team permissions, Agent permissions, which modules are on (Settings > Modules), the payment and banking rails, and spend caps. **Home** opens on Today with the approval queue first: everything waiting on a yes (agent sends, campaigns, refunds, applications, giveaway rules), each row with one button, Approve. Below it the Numbers tiles (revenue, leads, cost per lead, cash owed) and the Feed of the latest changes with who made them. The morning summary the agent writes sits at the top of Today and is also emailed at the hour the Owner picks.

### Admin
The operator who runs the business day to day with the Owner's trust: a general manager, an office manager, a partner who runs ops, or the outside team that set the app up. Admins can view, create, edit, send, delete, export and configure every module that is on, and approve everything the Owner has not kept for themselves. They cannot change Team permissions or Agent permissions, cannot switch modules on or off, cannot touch payment or banking rails, and see Team and Agents read-only. **Home** opens on Today: the act-now queue across every module (Needs reply, Stuck, Due today), then the approvals the Owner has delegated, then Numbers. Same layout as the Owner, minus the tiles that need Owner-only data (spend caps, payouts to the Owner).

### Staff
Employees who do the work: the front desk, the warehouse, the coordinator, the writer, the person answering the inbox. Staff view and work every module that is on for them, create and edit records, reply to customers, and submit drafts for approval. By default they do not approve, do not delete anything they did not create, do not export, do not configure, and do not see cost, margin or payout fields. **Home** opens on Today filtered to what is assigned to them (Assigned to me in Inbox, their leads, their tasks on the Board, jobs due), then the team queue, then a short Numbers row the Owner chooses for Staff.

### Contractor
People outside the payroll who work part of the book: field sales reps, freelancers, agents on commission, partner technicians, an outside bookkeeper. They get the same admin shell, filtered to their own records. Every list, count, chart and search shows only what they own or are assigned. They can work their own records (log activity, reply, place an order as pending, update a job) but cannot see the rest of the business, approve, delete, export or configure. **Home** opens on their own Today (who to call, what is due, replies waiting), their scorecard (goal, progress, commission this month) and the leaderboard if the business runs one.

### Customer
Anyone who buys from, books with, or partners with the business and signs in: a shopper, a business buyer, a member, a partner (a firm that buys leads or keeps a listing), a client with a job or case. Customers live in the portal (`/portal`), the same shell and chat as admin with their own nav. They see only their own records and act on them: reorder, book, reschedule, pay, sign, upload, request, edit their profile and listing, download their data, delete their account. One login can hold several customer kinds (a shopper who also buys for two stores). **Home** opens on their open items (an invoice due, a document to sign, a booking tomorrow), their last order or booking with its status, their balance, and one next step.

### Agent
The AI that works for the business. It is a user with its own entry on Agents, its own row in every Log line ("Agent, on behalf of Dana" or "Agent, scheduled, as Admin"), and its own permissions. In the chat panel it acts as the person who opened the chat, with that person's verbs and scope. In the background (scheduled runs, inbound triggers) it acts as the role the Owner set for it on Agents. Either way it can never Approve or Configure, every write it makes lands in Log with before, after and Undo, and every Send, Publish, Spend and Delete waits for a human yes until the Owner relaxes that module. Bulk edits over 5 records and anything ambiguous: it says exactly what it will change and waits for a yes. **Home** for the Agent is the Agents module: what it ran, what it changed, what is waiting on a person, and what it cost this month.

---

## 4. The matrix

How to read a cell:
- Letters are the verbs from section 2. `all` means every verb that applies to that module.
- `own:` means scoped to their own or assigned records.
- `·` means the module is hidden for that type.
- In the Agent column, `*` means the action waits for a human yes by default (the Owner can relax it per module, see section 5). `!` means it waits for a yes and cannot be relaxed.
- `A†` means the Owner can delegate this approval to Admin (it is Owner-only by default).
- The Agent column shows the background agent running as Admin, the default. In chat, the agent gets the signed-in person's cell with the same `*` and `!` rules applied.
- Customer cells are portal and public pages. Which customer kinds see which page is in section 4g.

Verbs that do not apply to a module are left out (nobody "publishes" a Goal).

### 4a. Pinned

| Module | Owner | Admin | Staff | Contractor | Customer | Agent |
|---|---|---|---|---|---|---|
| Home | V K | V K | V | own: V | own: V | V, E (pin a tile) |
| Inbox | all | V C E P D X K | V C E P | own: V E P | own: V C (their thread) | V C E, P*, D* (spam) |

### 4b. Grow

| Module | Owner | Admin | Staff | Contractor | Customer | Agent |
|---|---|---|---|---|---|---|
| Leads | all | all | V C E P | own: V C E P | own: V (their submission) | V C E, P*, D* |
| Pipeline | all | all | V C E P | own: V C E P | · | V C E, P* |
| People | all | all | V C E | own: V E | own: V E D X (their profile) | V C E, D* (merge), X* |
| Prospects | all | all | V C E | · | own: V E (their listing) | V C E |
| Outreach | all | all | V C E P | own: V C E P | · | V C E, P* (with daily cap) |
| Campaigns | all | V C E P D X K, A† | V C E (drafts) | · | · | V C E (drafts, test to team), A never, P! |
| Reviews | all | all | V C E P | · | C (by private link) | V C E, P* |
| Programs | all | V C E P D X K, A† (giveaways) | V C E | · | own: V C (claim, enter, refer) | V C E, P*, $* (payouts) |
| Reps | all | all | V | own: V (scorecard, leaderboard) | · | V C E (notes) |

### 4c. Sell

| Module | Owner | Admin | Staff | Contractor | Customer | Agent |
|---|---|---|---|---|---|---|
| Orders | all | all | V C E P | own: V C (placed as pending) | own: V C (order, reorder) | V C E, P*, $* (refunds) |
| Catalog | all | all | V E (inventory only) | V | V (shop, at their tier price) | V E (stock), $* (price changes) |
| Bookings | all | all | V C E P | own: V C E P | own: V C E D (book, move, cancel) | V C E, P* |
| Jobs | all | all | V C E P | own: V E | own: V (client view, if on) | V C E, P* |
| Marketplace | all | all | · | · | own: V X (purchased leads, balance) | V E, $* (route and debit) |
| Documents | all | all | V C E P | own: V C | own: V A X (sign, download) | V C E, P* |
| Money | all | V C E A P X, $ | · | own: V (payouts, commission) | own: V, $ (pay their invoice) | V C (draft invoices), P* (reminders), $! (money out) |

### 4d. Make

| Module | Owner | Admin | Staff | Contractor | Customer | Agent |
|---|---|---|---|---|---|---|
| Content | all | all | V C E (submit for publish) | · | own: V C E (contributions) | V C E, P* |
| Social | all | all | V C E (submit for publish) | · | own: V C E P (posts for their channels) | V C E, P* |
| Library | all | all | V C E, D (own uploads) | · | own: C (uploads) | V C E, D* |
| Studio | all | all | V C E X | V X (kit, signature) | own: V X (kit, posts) | V C E X |

### 4e. Know

| Module | Owner | Admin | Staff | Contractor | Customer | Agent |
|---|---|---|---|---|---|---|
| Insights | V X K | V X K | V | · | · | V X |
| Search | V C X K | V C X K | V | · | · | V C (audit runs) |
| Views | all | all | V C E, D P (own views, share) | own: V C E D | · | V C E |
| Goals | all | all | V C E | own: V E | · | V C E |
| Costs | all | V X | · | · | · | V |
| Playbook | all | all | V | V | · | V C E |

### 4f. Run

| Module | Owner | Admin | Staff | Contractor | Customer | Agent |
|---|---|---|---|---|---|---|
| Team | all | V | · | · | · | C! (draft an invite), never E |
| Agents | all | V | · | · | · | V, E (pause its own schedule) |
| Board | all | all | V C E, D (own cards) | own: V C E | own: V C (requests) | V C E |
| Log | V E X K | V E X | own: V E | own: V | · | own: V E (undo its own changes) |
| Settings | all | V E K (all tabs but Modules and rails) | · | · | own: V E (Account, email prefs) | V, E! |

Log has no Delete for anyone. E on Log means Undo.

### 4g. Customer side

| Module | Owner | Admin | Staff | Contractor | Customer | Agent |
|---|---|---|---|---|---|---|
| Site | all | all | V C E (drafts) | · | public | V E, P* (ship copy) |
| Intake | all | all | V | · | own: V C D (run it, resume, see report, delete their data) | V C (reports, sent to the requester as a system message) |
| Shop | all | all | V | · | V C $ (browse, cart, pay) | V E (answer, apply an offer) |
| Portal | V (preview as any customer) | V (preview) | · | · | own: per kind below | runs as the customer in their chat |

Portal pages by customer kind. A page also needs its feeding module on (see the module map, section 3b).

| Portal page | shopper | buyer | member | partner | client |
|---|---|---|---|---|---|
| Home, Account | V E | V E | V E | V E | V E |
| Orders, Reorder | V C | V C (tier price, several stores) | V C | · | · |
| Bookings | V C E | V C E | V C E | · | V C E |
| Documents | · | V | · | V A | V A X |
| Invoices | · | V $ | V $ | V $ | V $ |
| Rewards | V C | V C | V C | · | · |
| Leads | · | · | · | V X | · |
| Listing | · | · | · | V E | · |
| Posts, Kit | · | V C E P X | · | · | · |

---

## 5. Agent rules

1. **Identity.** The agent always acts as a user. In chat: the signed-in person. In the background: the role set for it on Agents (default Admin; the Owner can pick Staff or a named role). Never the database superuser. Two checks on every call: the role permission in the tool layer, and row rules in the database so `own` scope holds even if a tool is wrong.
2. **Ceiling.** Agent verbs = the role's verbs minus Approve and Configure. A chat agent opened by a Contractor can only touch that Contractor's book.
3. **Every write is logged.** `change_log` row with actor kind (person or agent), on behalf of whom, the chat thread and message, before, after, and an Undo. The reply in chat cites the change number. Undo restores the before state; if a later change touched the same field, Undo shows both and asks.
4. **Gated by default.** P (send, publish), D (delete), X on personal data, and every `$` action wait for a human yes. The agent shows exactly what will happen ("Send to 412 people. 9 dropped as unsubscribed. Mailing address present.") with one button, Approve, and a Change link. The yes can come from the chat, from Home > Today, or from the phone notification. Any human whose role has that verb on that module can give it.
5. **Bulk and ambiguous.** Edits to more than 5 records at once, any money field, and any request the agent is not sure it read right: it states the change and waits for a yes, even where the module is relaxed.
6. **The Owner relaxes per module, per verb.** On Agents > Permissions, each module shows the gated verbs with a switch: "Ask me first" (default) or "Go ahead". Relaxing can carry a limit: a daily cap (Outreach, 50 sends a day), business hours only, a dollar cap per action and per month ($ actions), or "only after a person approved the draft" (Social posts at the planned slot). Every relaxed action is still logged with Undo where Undo is possible.
7. **Never relaxable (`!`).** Approve anything. Configure anything. Change Team or Agent permissions. Send a Campaign. Move money out (payouts, refunds over the cap, transfers). Settings changes. Hard delete. These need a person every time.
8. **YOLO.** One switch for one agent, Owner only, that sets every relaxable verb to "Go ahead." It does not touch rule 7, and nothing reaches outside the organization without a person's yes: no text, email, post or call to anyone outside the business. Everything is still logged. There is no stronger mode. See `shared/agent-platform.md` section 7.
9. **Spend cap.** Every model call the agent makes is logged with its real cost on Costs. At the monthly cap set by the Owner, the agent stops and files a Board card asking for more.
10. **Customer-facing agent.** The chat in the portal runs as the customer: their records, their verbs. It can answer, reorder, reschedule and file requests to the Board. It never sees another customer's data, staff notes, cost or margin.

---

## 6. How permissions show in the UI

The admin look: records open read-only with an Edit button, one primary action per row, collapsed filters, URL modals that close on Esc, no new tabs for in-app navigation. Permissions follow that look.

### 6a. Three states, and when each is used

| State | Used when | What the user sees |
|---|---|---|
| **Hidden** | The user does not have the verb, or the module is off | The nav item, tab, button, column or menu item is not rendered. No lock icons, no greyed-out placeholders |
| **Read-only** | The user has V but not E on a record | The record opens the way every record opens (read view). The Edit button is not there. Quick actions they do have (log activity, copy, reply) still show |
| **Disabled** | The user has the verb but it cannot run right now | The button shows with a one-line reason under it ("Add a mailing address to send", "Waiting on Owner approval", "Sending…" with a spinner) |

Disabled is never used for "you are not allowed". It is only for a temporary or fixable state, and it always says why.

### 6b. Rules by surface

1. **Nav.** Render from the permission map: a module shows only with V. A group with no visible modules disappears. Badge counts use the same scope as the list (a Contractor's Leads badge counts only their leads).
2. **Deep links to a hidden module.** Staff, Contractor and Admin get a plain page: "You don't have access to Pipeline. Ask the Owner." with one button, Request access, which files a Board card to the Owner. Customers get a normal not found page. Nothing about the record leaks (no title, no count).
3. **Lists.** One primary action per row, and it is the highest verb the user has on that row: Approve (approver, item pending), Submit (drafter), Reply (inbox), Open (view only). Never two primary buttons, never a disabled one.
4. **Records.** Open read-only. Edit shows only with E. Inside Edit, fields the role cannot change render as plain text, not as disabled inputs.
5. **Gated actions become requests.** When the user (or the agent) lacks the un-gated verb, the button label changes instead of disappearing: Send becomes Submit for approval, Publish becomes Send to review, Refund becomes Request refund. The record then shows a status pill (Waiting on approval) and the approver sees it on Home > Today.
6. **Bulk actions.** Select mode with a floating action bar. The bar shows only the actions the user has on every selected row. Export sits in this bar and is hidden without X.
7. **Configure.** Module knobs live behind a Settings tab on the module (last tab). Hidden without K.
8. **Sensitive fields.** Cost, margin, payouts, and fields the Owner marks sensitive (licence numbers, insurance documents, health or case details) are column-level grants. Without the grant the column is not rendered in lists or records, and it is stripped from the agent's query results for that user.
9. **Contractor and Customer scope.** There is no "All / Mine" switch for them: everything is already theirs. Empty states say so ("No open leads in your book").
10. **The agent's work.** Every agent write shows a small "Agent" byline in the Feed and on the record's timeline, with Undo next to it for users who have E on that record. Gated agent actions appear in chat as a card with one button, Approve, plus the same row on Home > Today.
11. **Demo switcher.** On the page and in demos, the profile picker (company and user type) re-renders the same shell through this exact map. Nothing is faked per type: if a type cannot see it, it is not there.

---

## 7. Data and enforcement (for PSAI-24 PRDs)

```ts
type UserType = "owner" | "admin" | "staff" | "contractor" | "customer" | "agent";
type Verb = "view" | "create" | "edit" | "approve" | "send" | "delete" | "export" | "configure";

type Role = {
  key: string;            // "owner", "staff", or a named role: "bookkeeper"
  type: UserType;         // the ceiling
  label: string;          // relabel: "Staff" -> "Associates"
  customerKind?: "shopper" | "buyer" | "member" | "partner" | "client";
};

type Grant = {
  role: string;
  module: string;         // module key from the module map
  verb: Verb;
  scope: "all" | "own";
  gated: boolean;         // agent only: needs a human yes
  limit?: { daily?: number; perActionUsd?: number; monthlyUsd?: number; hours?: "business"; afterHumanApproval?: boolean };
  fields?: string[];      // sensitive columns this grant can see
};
```

- Tables: `roles`, `role_grants`, `user_roles` (one admin-side type per user; customer kinds can stack), `agent_permissions` (runs-as role plus per-module relax), `approvals` (pending gated actions), `change_log`, `auth_log`.
- One function, `can(user, module, verb, record?)`, used in four places: the nav, the route guard, every server action, every agent tool. A page that relies only on the layout's check is a bug.
- Row rules in the database for `own` scope (owner_id, assignee_id, customer_id on every record table).
- Defaults ship as the matrix above in `role_grants` seed data. The Owner edits grants on Team > Roles (trim only) and agent gates on Agents > Permissions.
- Named role presets shipped with every business:
  - **Viewer** (Staff type): V on every module Staff sees. Can ask the agent, cannot make it change anything.
  - **Bookkeeper** (Admin type, trimmed to Money V E X and Costs V): reads the money, exports to the books, no sends.
  - **Reviewer** (Admin type, trimmed to V and A on Social, Content and Campaigns): approves drafts from a phone, nothing else.
  - **Sales, no personal data** (Staff type): Leads, Pipeline, Outreach, with sensitive fields off.
