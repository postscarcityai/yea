# Calls (admin, Know)

- **Module key:** `calls` (stable, never renamed)
- **Tier:** common
- **Route:** `/admin/calls`
- **Folder:** `admin/know/calls/`

> **Partly proven.** Joining a Zoom, Meet or Teams call, the live transcript, the live screen, live checks against the business's own data and the post-call report run in production for investor diligence calls. Asking the business's own agent mid-call (the back office) runs in production on a voice line, not yet on a meeting. Speaking on the call (section "Voice on the call") is not yet proven. Build those two from this spec and test harder.

## Job

"Send an agent into my call. It listens, checks what people say against what we know, tells me on my screen what to ask next, and answers my questions while the call is still going. After the call it writes it up and files the follow-ups."

The agent joins as a named participant. It never speaks unless the owner turns voice on for that call. What it shows is set by a **lens**: a named set of things to watch for (numbers to check, objections, commitments, risks, open questions). The business picks lenses per call type: a sales call, an investor call, a client check-in, a hiring call, a vendor negotiation.

The number that tells you it is working: **share of calls where the owner acted on a live card** (asked the suggested question, corrected a number, filed a follow-up), target over 50 percent.

## Users and permissions

Start from `shared/roles.md`.

| User type | Scope | Differs from the matrix how |
|---|---|---|
| Owner | all | Sets lenses, the back-office agent, voice on or off, recording retention, and which calendars the agent watches. |
| Admin | all | Same as Owner except back-office agent, voice and retention (read-only). |
| Staff | own | Calls they host or were invited to. Can send the agent into their own calls. |
| Contractor | own | Same as Staff, only for calls on records they own. |
| Customer | none | Hidden. A customer on a call sees the agent as a named participant and gets the recording notice. |
| Agent | own | Reads calls it attended. Never joins a call on its own: a person sends it, or a person's calendar rule does. |

- **Gated verbs for the agent:** joining a call (the first time per calendar rule), speaking on a call, posting in the meeting chat, emailing the summary to anyone outside the team, and every write into another module (a new lead, a Board card, a stage change). Each waits for a human yes unless relaxed on Agents > Permissions.
- **Per-module relax:** "Post the summary to the team" and "File follow-ups to the Board" can be relaxed. Speaking on the call and messaging people outside the team are never relaxable.
- **Sensitive fields:** transcript text and recordings. A user sees a call's transcript only if they could see the records it is linked to. Recordings follow the retention setting, default 7 days at the meeting vendor, transcript kept.

## Pages and states

| Tab | Route | Holds |
|---|---|---|
| Calls | `/admin/calls` | Upcoming and past calls: title, when, who, lens, linked record, status chip (scheduled, joining, waiting room, live, ended, failed). Primary action per row: Open. Top action: Send agent to a call (paste a link, pick a lens, pick the linked record). |
| Lenses | `/admin/calls?tab=lenses` | One card per lens: name, what it watches for, which data it checks against, the questions it suggests, who uses it. Duplicate, edit, archive. |
| Settings | `/admin/calls?tab=settings` | Agent display name, calendars it watches and the rule ("calls with an external guest"), back-office agent and its status, voice on or off, retention. |

- **Record view:** full route `/admin/calls/[id]` with tabs Live (only while the call is on), Transcript, Cards, Report, Follow-ups.
- **Live tab:** three columns on desktop, stacked on a phone.
  - Left: the running transcript with speaker names. A line that produced a card shows a dot; click it to jump to the card.
  - Middle: live cards, newest on top. Each card has a kind chip (check, mismatch, risk, ask next, commitment, answer), the line it came from, the evidence it found with links to the source, and one action (Ask this, Dismiss, Pin, File).
  - Right: the chat panel from `shared/chat.md`, open by default, scoped to this call. Typing a question sends it to the back-office agent with the transcript so far. Answers land as an `answer` card.
  - Header: status chip, elapsed time, participants, End call, a Voice switch (only when voice is on in Settings).
- **Empty states:** Calls with none: "No calls yet. Paste a meeting link to send the agent, or connect a calendar." Lenses with none: the shipped starter lenses show instead.
- **Loading:** a joining call shows "Joining" with elapsed time. Waiting room shows "Waiting to be let in. Admit <agent name> in the meeting." and notifies the host once.
- **Error:** a bot that never got in ends as failed with the reason in plain words ("Nobody admitted the agent in 15 minutes."). A dropped live feed shows a grey feed dot and reconnects; cards resume from the last line.
- **Permission states:** hidden for Customer. Staff see only their own calls; others' calls do not appear, and a deep link shows the no-access page.
- **Quick views:** Calls: Today, Live now, Needs follow-up, Failed.
- **Badge count:** none in the nav. Home > Now shows a live call.

### Starter lenses

Ship these. Each one is config, not code.

1. **General.** Commitments ("I'll send that Friday"), open questions, decisions, risks, and an ask-next card when a topic is left half answered.
2. **Sales.** Budget, decision maker, timeline, objections, competitor names, next step. Checks claims about the business's own pricing and terms against Catalog and Playbook.
3. **Investor diligence.** Every number the speaker says checked against the data room and prior calls: true, rounded, off, not in the data. Dodged questions. Cross-call consistency. This is the proven lens.
4. **Client check-in.** Asks, complaints, promised dates, scope changes, anything that should become a Job or a Board card.

## Data model

Shared tables (defined in `shared/data-model.md`): `people`, `companies`, `files`, `change_log`, `cards`, `agents`, `agent_runs`, `model_calls`, `approvals`. Calls owns:

**`calls`**

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | |
| `org_id` | uuid | |
| `title` | text | |
| `meeting_url` | text | Zoom, Meet or Teams link |
| `platform` | text | zoom, meet, teams |
| `starts_at` | timestamptz | null for "join now" |
| `lens_id` | uuid | FK `call_lenses` |
| `record_kind`, `record_id` | text, text | The record the call is about (`lead:12`, `deal:4`, `job:9`). Its data is what the lens checks against. |
| `host_user_id` | uuid | FK `users` |
| `bot_id` | text | Meeting vendor's bot id |
| `status` | text | scheduled, joining, waiting_room, live, ended, failed |
| `status_detail` | text | Plain-words reason for failed |
| `voice_enabled` | bool | Per call, default from Settings |
| `ended_at` | timestamptz | |
| `created_at`, `updated_at`, `deleted_at` | timestamptz | |

**`call_participants`**: `id`, `call_id`, `vendor_participant_id`, `name`, `person_id` FK `people` (matched by name or email, nullable), `side` (us, them, unknown), `joined_at`, `left_at`.

**`call_lines`**: `id`, `call_id`, `seq int`, `participant_id`, `text`, `started_at`, `ended_at`. Unique `(call_id, seq)` so a reconnect never duplicates.

**`call_cards`**: `id`, `call_id`, `line_id` (the line it came from), `kind` (check, mismatch, risk, ask_next, commitment, answer, note), `title`, `body`, `evidence jsonb` (list of `{source, ref, quote}`), `status` (open, asked, dismissed, pinned, filed), `filed_ref` (the Board card or record it became), `created_at`.

**`call_lenses`**: `id`, `org_id`, `key`, `name`, `watch jsonb` (list of things to catch, each with a label and an instruction), `checks_against jsonb` (which modules and record fields are the source of truth), `suggest jsonb` (question bank), `report jsonb` (sections of the post-call report), `archived_at`.

**`call_reports`**: `call_id` PK, `summary`, `decisions jsonb`, `commitments jsonb`, `open_questions jsonb`, `sections jsonb` (lens report sections), `generated_at`.

- **Row rules for `own` scope:** `host_user_id = me` or I am in `call_participants` with `side = us`, or I own the linked record.
- **Anchor kinds:** `call:<id>`, `call_line:<id>`, `call_card:<id>`. Selecting a line or a card pins it into the chat.
- **Config knobs:** `fields.calls.agent_name` (default the business's agent name), `fields.calls.lenses` (which starter lenses ship), `fields.calls.default_lens_by_record` (deal -> investor, lead -> sales).
- **Sample data:** one ended sales call with transcript, cards and report; one ended client check-in.

## Agent actions

| Action | Tool | Verb | Gated | change_log | Undo |
|---|---|---|---|---|---|
| Send the agent to a call | `calls.join` | C | yes, first time per calendar rule | call row | Remove bot (leaves the call) |
| Make a live card | `calls.card` | C | no (only on the call's own screen) | no, cards are call data | Dismiss |
| Answer a question mid-call | `calls.ask` | V | no | no | none |
| Post in the meeting chat | `calls.chat` | E | yes, never relaxable | message text | none, say so before sending |
| Speak on the call | `calls.say` | E | yes, never relaxable | text spoken | none, say so before sending |
| File a card to the Board | `calls.file` | C | yes, relaxable | Board card | Delete card |
| Update the linked record | `calls.update_record` | E | yes | before/after on that record | Undo |
| Send the summary to the team | `calls.share` | E | yes, relaxable | recipients | none |

Background jobs:

- **`calls.calendar_sweep`** every 5 minutes: finds calls matching the calendar rule and schedules the bot. Scheduling is the gated join, so the first time a rule fires it asks.
- **`calls.status_reconcile`** every minute while any call is active: reads bot status from the meeting vendor and moves `status` forward only (scheduled -> joining -> waiting_room -> live -> ended). Never backward.
- **`calls.report`** on end: writes `call_reports`, proposes follow-ups as draft Board cards (gated file).

### The live loop

The loop is the same for every lens. The lens only changes the prompts and the data.

1. The meeting vendor streams final transcript lines over a websocket to the **live worker**. Partial lines are shown, never analyzed.
2. The worker buffers lines until the speaker's turn ends (about 1.5 seconds of silence), then sends the whole turn to a cheap **triage** step: "Is there anything here this lens watches for?" Most turns stop here.
3. A hit goes to the **check** step with the lens instructions and the linked record's data (cached as the system prefix for the whole call). It returns a card with evidence ids that must exist in the data. A card with made-up evidence is dropped.
4. Every few turns, an **ask next** step looks at what is still uncovered and suggests one question.
5. Cards are written to `call_cards`; the live screen subscribes to the call's rows (database realtime or server-sent events) and renders them as they land.
6. Dedup by a normalized key per claim, so a repeated number does not make a second card. On reconnect, rebuild the seen set from `call_cards`.

### The back office

The back office is the business's own agent, the one that knows the business (on Hermes, or any agent deployed with an HTTP endpoint). Calls never talks to a model for answers that need the business's memory. It forwards.

- **Contract:** `POST <back_office_url>` with header `X-Back-Office-Secret`, body `{call_id, conversation: "call-<id>", question, transcript_tail, linked_record, asked_by}`. Response `{answer, sources: [{label, url}]}`. Timeout 60 seconds; the card shows "Asking <agent>..." until then, then "No answer in time" with Retry.
- **One conversation per call,** so follow-up questions keep context.
- **Who can trigger it:** only a signed-in user on the live screen, or (when voice is on) a participant on our side by name. Never someone from the other side of the call.
- **Without a back office:** the ask box answers from the transcript and the linked record only, and says so.

### Voice on the call

Off by default. When on, the agent can speak in the meeting through the vendor's audio output, using the same voice as the chat panel's Talk mode (`shared/chat.md`).

- It speaks only when asked: a person on our side says its name and a question, or the owner presses Say on a card.
- Every spoken reply is shown as text on the live screen first, with a 3 second Cancel, unless the owner turned off the preview.
- It never speaks about sensitive fields, prices or terms it was not given, or anything the lens marks private.

## Integrations

- **Live worker (rail):** a long-running process that holds websockets for the length of a call. Serverless functions time out, so this is not the web app's host. Default: one small always-on machine on Fly.io (`min_machines_running = 1`, health check on `/health`). Contract: `POST /calls/:id/join`, `POST /calls/:id/end`, `POST /calls/:id/ask`, websocket `/ws/:call_id` for the vendor, `GET /health`. Shared secret between the web app and the worker.
- **Meeting bot vendor:** Recall.ai (one API for Zoom, Meet and Teams). Contract: create bot with meeting URL, display name, realtime websocket endpoint and events (`transcript.data`, `transcript.partial_data`, participant join and leave), separate audio streams per speaker when the platform offers them, automatic leave timers. Status webhook in, signed.
- **Transcription:** the vendor's low-latency model by default; Deepgram streaming with smart formatting when the lens checks numbers (decimals and percent signs survive).
- **Voice:** text to speech from the business's voice provider (ElevenLabs by default), played through the vendor's audio output.
- **Calendar:** Google Calendar or Microsoft 365, read-only, for the calendar sweep.
- **Back office:** the business's agent endpoint (contract above).
- **Webhooks in:** meeting vendor status (`/webhooks/recall`).
- **Secrets:** `RECALL_API_KEY`, `RECALL_WEBHOOK_SECRET`, `WORKER_SHARED_SECRET`, `BACK_OFFICE_URL`, `BACK_OFFICE_SECRET`, `DEEPGRAM_API_KEY` (optional), `ELEVENLABS_API_KEY` (voice only), model provider key.

## SaaS replaced

| Product | Risk | Migration |
|---|---|---|
| Otter, Fireflies, Fathom, Read (note takers) | Easy | Export past transcripts if wanted, run both for a week, cancel. |
| Gong, Chorus (sales call intelligence) | Plan it | Rebuild their trackers as a Sales lens, run in parallel for a month, compare, cancel. |
| Zoom, Meet, Teams AI add-ons | No brainer | Turn off the add-on. The meeting app itself stays. |

## Acceptance criteria

1. A user without `calls` view never sees the nav item, and a deep link to `/admin/calls/[id]` shows the no-access page.
2. Staff pastes a Meet link, picks the General lens and presses Send. Within 30 seconds the row shows Joining, then Waiting room or Live.
3. In the waiting room, the host gets one notification that says to admit the agent by name. Nobody admits it for 15 minutes: the call ends as failed with "Nobody admitted the agent in 15 minutes."
4. While live, a final line appears on the Live tab within 2 seconds of the vendor sending it.
5. A speaker states a number that is in the linked record with a different value. A mismatch card appears within 10 seconds, showing the said value, the record value and a link to the source.
6. The same number said again does not make a second card.
7. The worker restarts mid-call. The feed dot goes grey, then green; no line is duplicated and no card repeats.
8. A user types a question in the live chat. An answer card from the back-office agent appears, with sources, within 60 seconds, or a "No answer in time" card with Retry.
9. A participant from the other side says the agent's name and a question with voice on. The agent does not answer.
10. With voice off, nothing is ever spoken or posted in the meeting chat.
11. On End call, the report appears within 2 minutes, with proposed follow-ups as drafts that need a yes before they reach the Board.
12. Every agent write into another module appears in Log with before, after and a working Undo.
13. A gated action (file to Board, speak, post in chat) waits for a human yes and shows exactly what will happen.
14. Every submit button shows a spinner and disables while it runs.

## Open questions

1. **Consent notice.** Some places need everyone's consent to record. Default: the agent posts one line in the meeting chat when it joins ("<name> is taking notes for <business>"), and that one post is pre-approved by turning the module on.
2. **Own bot vs vendor.** Default: the vendor. Self-hosting a meeting bot is a project of its own and breaks often.
3. **Where the worker lives.** Default: Fly.io, one machine per business. Several businesses may share one worker if each call carries its org and the worker scopes every query to it.
4. **Retention.** Default: recording 7 days at the vendor, transcript and cards kept with the call.
5. **Who the agent is.** Default: the same agent as the chat panel, same name, same voice, so the business has one agent, not one per tool.
