# Interviews (admin, Know)

- **Module key:** `interviews` (stable, never renamed)
- **Tier:** common
- **Route:** `/admin/interviews`
- **Folder:** `admin/know/interviews/`

> **Partly proven.** Voice interviews run in production: briefs with topics, share links, calls that pick up where the last one stopped, notes per topic and a written handoff, used for discovery interviews with real clients. Running them inside the admin (the call in the record modal, the topic lighting up as the agent moves) went live on postscarcity.ai on 2026-11-02. The **review** pattern (section "Reviews"), where the agent reads the owner what the business already says and asks for reactions, shipped the same day and has not run end to end yet. Build that part from this spec and test harder.

The call itself (engine, screen, brief format, tools, links, data) is the shared interview tool: `shared/interview-tool.md`. This page is the admin module that lists and runs interviews for the business's own people.

## Job

"Have my agent interview me. It walks me through something one topic at a time, I answer out loud while I'm walking or driving, and it writes up what I said so the work gets done without a meeting."

An interview is a brief the agent runs over voice: a role, a goal, a handful of topics, an opening line and a close. It can take several calls; each call picks up at the first topic that isn't covered. Two kinds ship:

- **Discovery.** The agent asks big open questions and listens: the owner's story, the business, the customers. Output: raw material for the site, the bio, the playbook.
- **Review.** The agent tells the owner what the business currently says or does (pages of the site, a proposal, a process, a price list), section by section, then asks one question per section. Output: an edit list, page by page.

The number that tells you it is working: **share of interviews finished within a week of being created**, target over 70 percent. Second number for reviews: **share of review notes that became a shipped change**.

## Users and permissions

Start from `shared/roles.md`.

| User type | Scope | Differs from the matrix how |
|---|---|---|
| Owner | all | Takes any interview. Creates, edits and archives them, or asks the agent to. |
| Admin | all | Same as Owner. |
| Staff | own | Interviews addressed to them (audience "team"). |
| Contractor | own | Same as Staff. |
| Customer | none | Hidden here. A customer interview runs from their Portal or a share link, never from the admin. |
| Agent | all | Drafts interviews, reads notes and handoffs, turns notes into Board cards. Never starts a call. |

- **Gated verbs for the agent:** creating an interview addressed to a customer, and sending its link. Drafting one for the owner is not gated: it does nothing until the owner taps Start.
- **Sensitive fields:** anything the speaker marks off the record. It never leaves the voice service's own admin: not in the embed, not on this page, not in the handoff's shared copy.

## Pages and states

| Tab | Route | Holds |
|---|---|---|
| Interviews | `/admin/interviews` | One row per interview: title, agent, topic count, about how long, a status pill, call count, age, one **Open** button. |

- **Record view:** URL modal, `?i=<id>`, read view (`shared/design-system.md` section 4).
  - Header: title; "With Monk · 2 of 4 covered · 1 call · about 35 min"; close.
  - Action bar: one primary button. **Start interview** (no calls yet), **Continue** (some topics open), **Talk again** (all covered). One line of help next to it. During a call the bar holds **End call** and **Mute** instead.
  - Call stage, only while a call is on or just ended: the breathing orb, the live caption ("Monk: ..." or "You: ..."), a count of points noted this call. Errors say what to do ("Allow mic access for this site and try again").
  - Topics: numbered, one row each, status pill (Not started, In progress, Partly covered, Covered, Skipped). The topic the agent is on gets an accent border, a **Now** pill and opens by itself. Open shows the topic's list (for a review: the pages, as plain tags), its summary and the notes captured under it. Quotes render in quotation marks.
  - Last call: the last call's summary, under the topics.
- **Status pill on the list:** red **Not started**, yellow **2 of 4**, green **Done**.
- **States:** voice service not connected (an empty state naming the two settings), voice service down ("Voice didn't answer. Try again in a minute."), no interviews (ghost empty state: "Ask your agent for one"), mic denied, call didn't connect, session expired.
- **Mid-call safety:** Esc, the close button and navigating away all ask "Hang up with Monk?" first. Unmounting the modal hangs up.
- **Badge count:** interviews not started.

## Data model

The interviews live in the voice service, not in this app's database. This module reads them and runs calls against them.

- Voice side (per interview): `kind` (interview, open line), `audience` (client, team), `title`, `role`, `goal`, `method`, `opening`, `topics[]` (`id`, `title`, `opener`, `examples[]` shown on screen, `notes` agent-only), `closing`, `checklist[]`, `report` (what the handoff contains), `estimatedMinutes`, links (`token`), calls, and per call the topic states (`pending`, `active`, `answered`, `partial`, `skipped`), points (`note`, `quote`, `off_record`), summary, transcript, handoff markdown.
- Read contract (the embed API, server to server with the tenant's key): per conversation `id`, `kind`, `title`, `agentName`, `topicCount`, `covered`, `estimatedMinutes`, `calls`, `lastSummary`, `path` (`/s/<token>`), `createdAt`, and `topics[]` with `id`, `title`, `examples`, `status`, `summary` and **public** `points` only.
- Cached 15 seconds for ownership checks; the record view always reads fresh.
- Anchor kinds for the chat: `interview:<id>`, `interview_topic:<id>.<topic>`.
- Config knobs: `fields.interviews.agent_name`, `fields.interviews.default_minutes`. Sample data: `interviews` (one discovery, one review).

## Agent actions

| Action | Tool | Verb | Gated | Writes to change_log | Undo |
|---|---|---|---|---|---|
| Draft an interview for the owner | `create_interview` | create | No | The brief | Archive |
| Draft one for a customer or teammate | `create_interview` | create | Yes | The brief and its audience | Archive |
| Turn a finished review into cards | `file_review_notes` | create | No | One Board card per page with notes, linking the interview | Delete the cards |
| Mark a review note done | (Board) | update | No | Card status, with the live URL as proof | Reopen |

On the call itself the voice agent uses the voice service's tools: `set_topic` (lights the topic up), `capture_point` (a note, a quote or off the record, under a topic), `complete_topic` (answered, partial, skipped, with a summary), `check_item`, `save_summary`. The admin passes each one through to the voice service in order, one batch in flight at a time, and keeps the latest `set_topic` and `complete_topic` in the call view so the room can draw them.

Background: after a call ends the voice service merges the call into the interview and rewrites the handoff. The page refreshes a few seconds after the call ends to pick up the notes.

## Reviews

The pattern for "read me what we wrote and ask what I think." Use it for the site, a proposal, a price list, an onboarding email series, a process document.

- **One topic per top-level section** (for a site: one per footer column). Four topics is the sweet spot: long enough to cover everything, short enough to finish in one sitting.
- **`examples` = the items in that section** (the page names), so the owner sees the list on screen while the agent talks.
- **`notes` = a spoken digest of each item:** headline, promise, main points, the proof it uses, two to four sentences an item, under 3,000 characters a topic. Never the full text read aloud: twenty pages of copy is an hour of speech. Add one-line **flags** where the agent spotted a likely problem (a swapped quote, a claim that no longer holds) so it raises them when it gets there.
- **`method`:** per topic, say the section name and item count; walk the items in order without stopping; then ask the opener, once; capture each reaction as a point that starts with the item's path in brackets (`[/services/lobster-herding] cut the backstory to one line`), `[column]` for the section as a whole; at most one follow-up, only when a reaction is too vague to edit from.
- **`report`:** an edit list, not a summary. Top fix; then per item Keep, Change, Cut with his words where he gave wording, "No notes" where none; section-level notes; each flag confirmed or dismissed; open questions.
- **Close** by asking what's missing from the set and which single fix matters most.
- **After the call** the agent files one Board card per item with notes, ships the changes, verifies each on the live site and closes the card with the URL.

The first one: "Site review: the footer pages" on postscarcity.ai, 22 pages in Services, Who it's for, Answers and How we work.

## Integrations

- **Voice service** (the rail): briefs, links, calls, notes and handoffs. Default: the PSAI Voice app on ElevenLabs Agents over WebRTC. Contract: the embed listing above, the public session API (`GET /api/session/<token>`, `POST .../start` returns a short-lived conversation token, `POST .../events` takes the call's events in order), proxied through the admin so the browser never holds the tenant key.
- **Speech:** ElevenLabs (voice, turn taking, the LLM behind the agent). The voice service syncs the brief to the voice agent on every call start.
- **Secrets, by name:** `VOICE_URL`, `VOICE_API_KEY` (the tenant's client key).
- Browser: microphone permission, the vendored ElevenLabs client loaded on first call.

## SaaS replaced

| Product | Risk | Migration |
|---|---|---|
| Typeform, Google Forms (feedback surveys to the owner) | No brainer | Nothing to export: rewrite the questions as topics. |
| Loom review threads, async video feedback | Easy | Keep old threads read-only; new reviews run here. |
| Interview and research tools (Dovetail, Grain notes) | Plan it | Export past notes to the Library; run new interviews here in parallel for a month. |

## Acceptance criteria

1. An Owner opens Interviews: every interview of the tenant is listed with its topic count, status pill and call count.
2. An Owner opens one: the modal shows its topics in order, the first uncovered one open with its list.
3. The Owner taps **Start interview**, allows the mic: within five seconds the orb is live and the agent's opening line shows as a caption.
4. When the agent moves to a topic, that topic gets the accent border and the **Now** pill and opens by itself, without the owner touching anything.
5. The Owner presses Esc during the call: a confirm appears; Cancel keeps the call going.
6. The Owner hangs up after covering two of four topics: within a minute the modal shows "2 of 4 covered", the notes under those two topics, and the button reads **Continue**.
7. **Continue** starts at topic three: the agent welcomes them back and does not repeat the first two.
8. A point marked off the record never appears on this page.
9. A call where the owner never spoke does not count as a call.
10. A Staff user sees only interviews addressed to them; a Customer never sees the nav item.
11. After a review finishes, the agent files one Board card per item that got notes, each naming the item's URL and his words.
12. Every tab and open record is in the URL: paste `/admin/interviews?i=<id>` in another browser and the same interview opens.

## Open questions

- **Create interviews in the admin, or only by asking the agent?** Recommended: by asking the agent for now. Briefs are prompts; a form invites bad ones. Add a read-only brief tab first.
- **Show the handoff here?** Recommended: yes, as a second section under the topics, once the voice service exposes a version with off-the-record parts removed.
- **Customer reviews** (a customer reviewing a proposal by voice). Recommended: run them from Portal with the same pattern; same module, audience "client".
