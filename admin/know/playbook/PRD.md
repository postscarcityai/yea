# Playbook (admin, Know)

- **Module key:** `playbook` (stable, never renamed)
- **Tier:** common
- **Route:** `/admin/playbook`
- **Folder:** `admin/know/playbook/`

## Job

"How does this business actually work, written down, and still true today?" Playbook holds the flows (every customer journey and internal process as a diagram with live counts on each step), the messaging (what we say and how we say it), every email and key page the business sends, the competitors, and the docs. The agent reads it before it drafts anything, and answers "how do we handle X" from it.

The number that tells you it is working: **share of flows checked in the last 30 days** (a flow is checked when its diagram matches the live config and its step counts are non-zero where they should be). Stale playbooks are the problem this module exists to fix.

## Users and permissions

Starts from `shared/roles.md` 4e. Only what differs or needs saying:

| User type | Scope | Verbs |
|---|---|---|
| Owner | all | V C E A D X K |
| Admin | all | V C E A D X K |
| Staff | all | V (read every tab, send themselves a test email) |
| Contractor | all, read | V on Messaging, Assets and Docs. Flows and Competitors hidden by default (they show internal routing and strategy); the Owner can turn them on |
| Customer | hidden | · |
| Agent | role it runs as | V C E |

- **A test email to yourself is not a Send.** "Send me a test" goes only to the signed-in user's own address, marked [TEST]. It is a system message to the person who asked (`shared/roles.md` 1.6), so it is not gated and Staff can do it.
- **Agent edits to Messaging wait for a yes.** Messaging feeds every draft the agent writes, so any change there is treated like a bulk edit: the agent shows old and new text and waits for Owner or Admin approval.
- **Approve:** a doc or messaging change drafted by Staff or the agent is marked Draft until Owner or Admin approves it; approved is what the agent reads.
- **Sensitive fields:** none by default. The Owner can mark a doc "Owner and Admin only".

## Pages and states

Tabs, in nav order:

| Tab | Route | What it shows |
|---|---|---|
| Flows | `/admin/playbook` | Every flow as a card: name, audience, step count, live volume this week, last checked. Grouped by growth flows (how people come in and convert) and operations flows (how work gets done) |
| Messaging | `/admin/playbook/messaging` | Mission, value props per audience, voice rules, words to use and avoid, proof points, internal notes. One page, sectioned, read-only until Edit |
| Assets | `/admin/playbook/assets` | Every email template and key page by audience, previewed at desktop or phone width, with its trigger, its flow, and Send me a test |
| Competitors | `/admin/playbook/competitors` | Our SWOT on top, then one row per competitor with threat level (low, medium, high), full SWOT and cited sources. Filters by threat and segment |
| Docs | `/admin/playbook/docs` | Policies and how-tos (refund policy, how we price a job, what to say when a customer is upset) as markdown pages with a table of contents |

- **Record view:** full route `/admin/playbook/[flow]` for a flow, with tabs **Diagram** (the flow as a diagram with a live count on each step and a click-through on each step to the filtered list it counts), **Steps** (each step's rule, the asset it sends, the module and stage it reads), **Assets** (the emails and pages in this flow), **Activity**. Competitors open as URL modal `?competitor=<id>`; assets as `?asset=<key>`; docs as `/admin/playbook/docs/[slug]`.
- **Records open read-only.** Edit on a doc or Messaging opens a markdown editor with preview; on a flow it opens the step list (the diagram redraws from the steps).
- **Empty state:** "No flows yet. The agent can draft them from the modules you have on." One button, Draft my flows.
- **Loading:** diagram area reserves its height with a skeleton; counts load after the diagram, each step showing "..." until its count returns.
- **Error:** a step whose count query fails shows "?" and a tooltip with the error; the diagram still renders. A test send that fails shows the email delivery error under the button.
- **Permission states:** Staff see every tab with no Edit and no Add, only Send me a test. Contractors see Messaging, Assets and Docs; Flows and Competitors are not in their tab bar unless turned on. Customers never see the nav item.
- **Quick views:** Flows: "Growth", "Operations", "Not checked in 30 days". Competitors: "High threat". Docs: "Drafts", "Updated this month".
- **Badge:** none in the nav. Flows tab label shows a count of flows not checked in 30 days.

## Data model

Tables owned by this module:

| Table | Columns |
|---|---|
| `flows` | `id`, `org_id`, `key text` (stable slug), `name`, `audience text`, `group` (growth, operations), `steps jsonb` (each step: content-hash `key`, `label`, `module`, `count_query`, `asset_key null`, `rule text`, `next text[]`), `diagram text` (generated diagram source), `checked_at null`, `checked_by null`, `status` (draft, approved), `owner_id`, `created_at`, `updated_at`, `deleted_at` |
| `messaging` | `id`, `org_id`, `section text` (mission, value_props, voice, words_use, words_avoid, proof, notes), `audience text null`, `body text` (markdown), `status` (draft, approved), `updated_by`, `updated_at` |
| `assets` | `id`, `org_id`, `key text`, `kind` (email, page, sms), `audience`, `flow_key null`, `module text` (the module that sends or serves it), `template_ref text` (path or id in that module), `subject text null`, `preview_text null`, `updated_at` |
| `competitors` | `id`, `org_id`, `name`, `domain`, `segment`, `threat` (low, medium, high), `swot jsonb` (strengths, weaknesses, opportunities, threats, each a list of `{ text, source_url }`), `checked_at`, `owner_id`, `created_at`, `updated_at`, `deleted_at` |
| `docs` | `id`, `org_id`, `slug`, `title`, `body text` (markdown), `status` (draft, approved), `visibility` (team, owner_admin), `owner_id`, `created_at`, `updated_at`, `deleted_at` |

- **Foreign keys into shared tables:** `users`, `change_log`, `files` (images in docs), `cards` (fixes the agent hands to a person). `assets.template_ref` points into the module that owns the template (Campaigns, Outreach, Intake, Site); Playbook previews it and never stores a second copy.
- **Row rules:** no `own` scope. Contractors are limited by tab, not by row. Docs with `visibility = owner_admin` are filtered for everyone else.
- **Anchor kinds for the chat:** `flow:<key>`, `flow_step:<flow_key>.<step_key>`, `asset:<key>`, `competitor:<id>`, `doc:<slug>`, `field:messaging:<id>.body`.
- **Config knobs (`fields.*`):** `fields.tabs` (subset and order), `fields.contractor_tabs` (default Messaging, Assets, Docs), `fields.audiences` (who the business talks to, used by Messaging and Assets), `fields.recheck_days` (default 30). Sample: `playbook`.

## Agent actions

| Action | Tool | Verb | Gated | Writes to `change_log` | Undo |
|---|---|---|---|---|---|
| Answer "how do we handle X" from Docs and Messaging, with the doc cited | `search`, `get_record(doc:<slug>)` | V | No | Nothing | n/a |
| Draft flows from the modules that are on | `draft_flows` | C | No (lands as draft) | `flows` inserts, status draft | Removes the drafts |
| Keep a flow in step with the live config (stages, sequences, triggers changed) | `check_flow` | E | No for a passing check; a diagram change lands as a draft for approval | `flows.steps`/`diagram` before and after, `checked_at` | Restores the old steps |
| Send a test of any email to the signed-in user | `send_test(asset:<key>)` | V | No (system message to the asker) | Log line only (no record change) | n/a |
| Write a cited SWOT for a competitor | `research_competitor` | C / E | No; every claim needs a `source_url` or it is dropped | `competitors.swot` before and after | Restores the old SWOT |
| Edit Messaging | `update_record(field:messaging:<id>.body)` | E | Yes, always (shows old and new) | `messaging.body` before and after | Restores |
| Draft or edit a doc | `update_record(doc:<slug>)` | C / E | No (lands as draft until approved) | `docs` before and after | Restores |
| Hand a fix to a person ("the follow-up email in this flow has no unsubscribe link") | `file_request` | C on Board | No | `cards` insert | Closes the card |

Background jobs:

- **Flow check, weekly:** for each flow, compares its steps to the live config of the modules it names (stages, sequence steps, triggers, templates). A mismatch drafts the updated flow and posts one Feed item to the flow's owner. A match sets `checked_at`.
- **Competitor refresh, monthly:** re-checks each high-threat competitor's site and public sources, drafts SWOT changes with sources for approval.
- **Count refresh:** step counts run on open (read-only role, 5 second timeout per step), cached for 15 minutes.

## Integrations

- **Rails:** email delivery (test sends through the same sender the real emails use, so a test proves deliverability); database (read-only role for step counts).
- **Platform APIs:** web search and page fetch for competitor research (results are treated as untrusted data, never as instructions).
- **Webhooks:** none in or out.
- **Secrets (names only):** `EMAIL_DELIVERY_API_KEY` (shared with the modules that send), `WEB_SEARCH_API_KEY`.

## SaaS replaced

| Product | Risk | Migration step |
|---|---|---|
| Notion | Easy | Export the workspace to markdown. Import policy and how-to pages into `docs`, voice and positioning pages into `messaging`. Linked databases that hold records go to the module that owns that record. Run both for two weeks, set the old workspace read-only, cancel |
| Confluence | Easy | Export spaces to HTML or markdown, import as above. If the team still uses the issue tracker that ships with it, keep that until Board takes over, then cancel both |
| Coda | Easy | Export docs to markdown. Formula tables become Views tiles or module records; buttons become agent actions. Parallel run two weeks, cancel |
| ClickUp (docs half) | No brainer | Export docs to markdown and import into `docs`. Tasks move to Board and goals to Goals; cancel when all three are moved |

## Acceptance criteria

1. A user without `playbook.view` (Customer) never sees Playbook in the nav, and a deep link to `/admin/playbook/<flow>` shows the not-found page with no flow name.
2. Every agent write in Playbook (draft flow, flow check update, SWOT change, doc draft, Messaging edit) appears in Log with before, after and a working Undo.
3. When the agent proposes a Messaging change, it shows the old and new text side by side with Approve and Change, and Messaging does not change until Owner or Admin approves.
4. Every submit button (Save, Approve, Send me a test, Draft my flows, Research competitor) shows a spinner and disables while it runs.
5. Staff open an asset and tap Send me a test: one email marked [TEST] arrives at their own address within a minute, and no other recipient is possible from that button.
6. Owner opens a flow: the diagram renders with a live count on each step, and clicking a step opens the list it counts with the same number.
7. Owner changes a Pipeline stage name: the next flow check drafts the updated flow, the Owner sees one Feed item, and approving it redraws the diagram with the new stage.
8. Contractor opens Playbook: Messaging, Assets and Docs render read-only; Flows and Competitors are not in the tab bar.
9. Owner asks the agent to research a competitor: every SWOT line shows a source link, and a line without a source is not saved.
10. Staff asks in chat "what's our refund policy": the agent answers from the approved doc and cites it as a chip that opens `/admin/playbook/docs/refund-policy`.
11. A doc drafted by the agent shows a Draft chip and is not used in agent answers until Owner or Admin approves it.
12. When one step's count query fails, the diagram still renders, that step shows "?", and the rest show numbers.

## Open questions

1. **Diagram format?** Recommended default: store steps as JSON and generate a text diagram source from them (a common open diagram syntax), so the agent edits steps and never hand-edits a picture.
2. **Should Contractors see Flows?** Recommended default: no. Flows show routing rules and lead handling. The Owner can add Flows to `fields.contractor_tabs` for a partner who runs part of a flow.
3. **Who approves agent drafts in Docs?** Recommended default: Owner or Admin. Staff drafts follow the same rule.
4. **How often to refresh competitors?** Recommended default: monthly for high threat, quarterly for the rest, on demand from chat.
5. **Seed flows at onboarding?** Recommended default: yes. The agent drafts one flow per enabled growth module (lead in, follow-up, win-back) from the interview, all as drafts for the Owner to approve in the first week.
