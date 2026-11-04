# Board (admin, Run)

- **Module key:** `board` (stable, never renamed)
- **Tier:** core
- **Route:** `/admin/board`
- **Folder:** `admin/run/board/`

## Job

"Everything anyone asked for, from the chat, a call, an email, a customer or the team, tracked until it is done, with proof." The Board is where a request stops being a sentence in a thread and becomes a card with an owner, a stage and a due date. The agent files cards from chat and voice, hands outside work to people through cards, and closes cards with proof of what it did.

The number that tells you it is working: **median days from card filed to Done** (by kind), with **cards stuck over 7 days** as the warning tile.

## Users and permissions

Start from `shared/roles.md` section 4f.

| User type | Scope | Differs from the matrix how |
|---|---|---|
| Owner | all | Configures stages and kinds. |
| Admin | all | All verbs including configure. |
| Staff | all | V C E. D only on cards they created. |
| Contractor | own | V C E on cards they filed or are assigned. Cannot see the rest of the Board. |
| Customer | own | V C from the Portal: file a request, see its status and public comments. Never sees internal comments, assignee notes or other customers' cards. |
| Agent | as its role | V C E. Files, moves and comments on cards; closes with proof. Delete is not granted. |

- **Gated verbs for the agent:** none by default. Moving a card to Done with an outward effect (a customer-visible status change that emails them) is a system message, not a send.
- **Per-module relax:** not applicable.
- **Sensitive fields:** `internal` comments are hidden from Customers always. Cards filed from a sensitive record inherit that record's grant on the body.

## Pages and states

| Tab | Route | Holds |
|---|---|---|
| Board | `/admin/board` | Kanban by stage. Columns from `fields.stages`; default New, Triaged, In progress, Waiting, Done. Drag to move. Each card: title, kind chip, urgency, assignee avatar, source icon, age, comment count, votes. |
| Requests | `/admin/board?tab=requests` | List of cards filed by customers, contractors and the agent that are still New or Triaged, sortable by votes and urgency. The triage queue. Quick view **Feature requests** (`?tab=requests&kind=feature`) shows every "the app should do this" the chat has heard, so the Owner sees what to build next. |
| Mine | `/admin/board?tab=mine` | Cards assigned to the viewer, any stage but Done. Default for Staff and Contractor. |

- **Record view:** URL modal `?card=<id>` over the current tab. Opens read-only: title, body, kind, stage, urgency, assignee, due date, source (with a link back to the chat message, thread, call or record that started it), linked records as chips, comments (internal and public), activity with agent bylines and Undo, proof (links, files, change ids). Edit button for users with E. Esc closes.
- **Look at (work waiting on a reviewer):** when an agent or person hands finished work to a reviewer, the card opens with a **Look at** block above everything else: one or more options, each one tap. A video plays right in the card. A before and after shows both, one tap apart. A page gets its exact live URL, a feature gets its exact screen, each with what to try in a few words. A pull request can be listed, last and small, and never counts on its own: the reviewer is judging the work, not the code. A note naming a whole tab is not an option. No new tabs, Esc closes, every tap shows feedback, and it works at phone width.
- **Customer view:** Portal shows "My requests" with stage, public comments and a comment box. Specified on the Portal pages; the data lives here.
- **Empty states:** Board: "No cards yet. Ask the chat to track something, or add a card." Requests: "No new requests." Mine: "Nothing assigned to you."
- **Loading:** column skeletons with 3 cards each. A dragged card shows a pending state until the move saves; it snaps back with a toast if the save fails.
- **Error:** list load failure shows Retry; a failed move snaps the card back with "Couldn't move this card. Try again."
- **Permission states:** hidden for nobody admin-side by default (everyone has V). Without E, drag is off and cards open read-only. Without D, Delete is not in the menu. Contractors deep-linking to a card outside their scope get the no-access page.
- **Quick views:** Urgent, Stuck (no movement in 7 days), From customers, From the agent, Waiting on me. Collapsed filters: kind, assignee, source, label, due.
- **Badge count:** cards in New or Triaged that have no assignee, plus cards assigned to the viewer that are overdue. Same scope as the list.

## Data model

Shared table `cards` is defined in `shared/data-model.md`; Board owns it and adds two tables.

**`cards`**

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | Shown as a short number to people ("#214") via `number` |
| `number` | int | Sequential per org |
| `org_id` | uuid | |
| `title` | text | |
| `body` | text | Markdown |
| `kind` | text | Key from `fields.kinds`; default request, task, bug, idea, feature |
| `status` | text | Key from `fields.stages` |
| `urgency` | text | now, soon, whenever |
| `assignee_id` | uuid null | |
| `owner_id` | uuid | Who filed it (or on whose behalf the agent filed it) |
| `customer_id` | uuid null | Set when a customer filed it |
| `source` | text | chat, inbox, call, person, portal, agent |
| `source_ref` | text null | Anchor of the origin: `message:<id>`, `thread:<id>`, `chat_message:<id>` |
| `linked` | jsonb | Anchors of related records |
| `due_at` | timestamptz null | |
| `proof` | jsonb | `[{ kind: "link" | "file" | "change", ref, note }]`, content-hash keys |
| `look_at` | jsonb | `[{ kind: "video" | "page" | "screen" | "pr", label, url, hint }]`, what the reviewer can open. Structured, never parsed out of prose. |
| `closed_at` | timestamptz null | |
| `custom` | jsonb | `fields.custom` |
| `created_at`, `updated_at`, `deleted_at` | | |

**`card_comments`**: `id`, `card_id`, `author_kind` (person, agent, system), `author_id`, `body`, `visibility` (internal, public), `at`.

**`card_votes`**: `card_id`, `user_id`, `at` (one vote per user per card; customers and staff can vote on ideas and requests).

- **Own scope:** Contractor and Customer rows are those where `owner_id`, `assignee_id` or `customer_id` is them. Customers read only `visibility = public` comments.
- **Anchor kinds:** `card:<id>`, `field:card:<id>.status`, `field:card:<id>.assignee`, `comment:<id>`.
- **Config knobs:** `label` (Board, Requests, Tasks), `fields.stages` (default `["new","triaged","in_progress","waiting","done"]` plus a hidden `wont_do`), `fields.kinds`, `fields.custom`. Sample type: `cards`.

## Agent actions

| Action | Tool | Verb | Gated | Writes to `change_log` | Undo |
|---|---|---|---|---|---|
| File a card from a chat request | `file_request` | C | No | `cards` insert, `source = chat`, `source_ref` = the message | Soft-deletes the card |
| File a card from a voice call | `file_request` | C | No | `cards` insert, `source = call` | Soft-deletes the card |
| File a feature request when asked for something the app cannot do | `file_request` | C | No | `cards` insert, `kind = feature`, `source = chat`, page path and chips in `linked` | Soft-deletes the card |
| Set urgency, assignee, due date | `update_record` | E | No | before, after | Restores |
| Move a card | `move_card` | E | No | `status` before, after | Moves it back |
| Post what it did | `comment_card` | C | No | `card_comments` insert, internal | Deletes the comment |
| Hand finished work to a reviewer | `move_card` | E | No | `status` and `look_at` before, after. Refused without at least one option that isn't a `pr`, on every write path, enforced in the database. | Moves it back |
| Close with proof | `close_card` | E | No | `status` to done, `proof` before, after | Reopens to the prior stage |
| Hand outside work to a person | `hand_off` (Agents) | C | No | `cards` insert plus `handoffs` row | Soft-deletes both |
| Merge duplicate requests | `merge_cards` | E | Bulk rule: states the merge and waits for a yes when more than 5 cards | Kept card after, merged cards `deleted_at`, votes moved | Restores the merged cards and their votes |

**Background jobs**

- `board.stale_sweep` (daily): cards with no movement in 7 days get an internal comment tagging the assignee and land in the Stuck view. Cards with `urgency = now` and no assignee after 2 hours go to Home > Now for Owner and Admin.
- `board.customer_status` (triggered on stage change of a card with `customer_id`): sends the customer a status note. This is a system message (a reply about their own request), logged on the card, not gated.

## Integrations

- **Email delivery** (default SendGrid): customer status notes and assignment notifications. Contract: transactional send with category `board_status`.
- **Voice:** call transcripts arrive from the chat panel's Talk mode; the agent files cards from them. No separate rail.
- **Platform APIs:** none.
- **Webhooks in:** none (cards come from the app itself). **Out:** none.
- **Secrets:** `SENDGRID_API_KEY` (shared).

## SaaS replaced

| Product | Risk | Migration |
|---|---|---|
| Asana | No brainer | Export projects to CSV. Import tasks as cards (project becomes a label, section becomes stage). Run one week, cancel. |
| Trello | No brainer | Export boards as JSON. Lists map to stages, labels to labels, checklists to the card body. Cancel. |
| monday.com | No brainer | Export boards to Excel. Groups map to stages, people columns to assignee. Run one week, cancel. |
| Basecamp | No brainer | Export to-dos as cards and message threads as card comments; files go to Library. Cancel. |
| ClickUp | No brainer | Export tasks as cards. Docs go to Playbook. Run one week, cancel. |

## Acceptance criteria

1. A user without `board.view` never sees the Board nav item, and a deep link to `/admin/board?card=<id>` shows the no-access page with no card title shown.
2. Every agent write (file, move, comment, close, merge) appears in Log with before, after and a working Undo.
3. When the agent proposes merging 8 duplicate cards, it lists all 8 and waits for a human yes before changing any of them.
4. Every submit button (Add card, Save, Comment, Close, Merge) shows a spinner and disables while it runs.
5. An Owner says in chat "track that we need a new price sheet by Friday"; a card appears in New with due date Friday, `source = chat`, and the reply cites the card number as a chip that opens `?card=<id>`.
6. A request made on a voice call appears as a card with `source = call` and a link to the call record on the person.
7. A Customer files a request in the Portal; it appears on Requests with their name, and they see its stage change and public comments but never internal comments.
8. A Contractor sees only cards they filed or are assigned, and the badge counts only those.
9. Dragging a card to a new stage saves; if the save fails, the card snaps back and a toast says so.
10. The agent closes a card only with at least one proof item (a link, a file or a change id), and the card shows that proof.
10a. No card can reach a review stage without something to open, from the UI, an agent tool or direct SQL. A pull request alone is refused. A video option plays inside the card at desktop and phone width, and a before and after swaps on one tap.
11. A card with no movement for 7 days appears in the Stuck view and gets one internal comment tagging its assignee.
12. Relabeling `label` to "Tasks" changes the nav item and page title without changing any route.

## Open questions

1. **Default stages.** Recommended: New, Triaged, In progress, Waiting, Done, plus a hidden Won't do reachable from the card menu.
2. **Can customers vote on each other's ideas?** Recommended: no by default (customers see only their own cards). Turn on a public roadmap later as a Site page if the business wants it.
3. **Do Staff see every card or only their team's?** Recommended: every card, with Mine as their default tab. Businesses that need walls use a named role with `own` scope.
4. **Recurring tasks.** Recommended: not on the Board. Recurring work is an agent schedule on Agents that files a card each time it runs.
5. **Card numbers per org or global.** Recommended: per org, starting at 1, shown as "#214".
