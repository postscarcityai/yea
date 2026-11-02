# The interview tool

One way to interview anyone, used by every module that needs someone's words: the owner reviewing their own site, a client recording a testimonial, a new hire's first-week check-in, a customer's intake. The agent runs a short brief over a realtime voice call, topic by topic, and what the person said lands back in the module that asked.

It is a component, not a nav item. Modules use it: Interviews (`admin/know/interviews/`) runs it for the business's own people, Testimonials (`admin/grow/testimonials/`) sends it to clients, and Portal can show it to a signed-in customer.

> **Partly proven.** Voice interviews from a brief, with topics, notes per topic, calls that pick up where the last one stopped and a written handoff, run in production (the Voice service on ElevenLabs Agents, and the postscarcity.ai admin since 2026-11-02). The GPT Realtime engine, the signed-in recipient view and video recording are specced here and not built yet. The first build is a link for one client of a client (a law firm's attorney, inside his own app).

---

## 1. The two ways in

**Signed in.** The person already has an account in the app (any user type, customers included). The link is an ordinary app link: `/admin/interviews/<id>` for staff, `/portal/interviews/<id>` for a customer. If they are signed in, the interview opens right there, inside the shell, and their identity is known: no name form, no email check. If they are not signed in, they sign in first (magic link) and land back on it.

**Guest.** The person has no account. The link is `/i/[token]`: one recipient, 30-day expiry, token stored hashed. It shows who is asking and why, a consent line, a mic (and camera, for video) check, and Start. Nothing records before Start.

Pick by the recipient: if they have an account, always send the signed-in link. A guest link to a signed-in user is a second identity the app can't merge.

## 2. The screen

Same layout in both ways in, full width of the content area (or full window for guests):

- **The interviewer tile:** the business's mark (never a fake face), a waveform that moves with the voice, and the live caption of whoever is speaking.
- **The topic rail:** numbered topics; the one the agent is on gets the accent border and a Now pill and shows its list ("examples": for a review, the pages; for a testimonial, the prompts). Covered topics turn green.
- **Their own camera, bottom right** (video interviews only): a small mirrored tile, so they see what they look like. Timer and red recording dot beside it.
- **Controls:** End (asks first), Mute. Nothing else. Esc and leaving the page ask before hanging up.
- **After:** "Thank you" with what happens next in one line ("Chris will see this today"), and, for signed-in people, the notes under each topic.

Mobile: the interviewer tile on top, the topic rail as a horizontal strip, their camera as a corner tile. Same controls.

## 3. The engine

Default: **OpenAI Realtime** (the current GPT realtime speech-to-speech model) over WebRTC. Alternative: ElevenLabs Agents, which runs the same brief. The engine is a setting, not a rewrite: both take the same system prompt and the same five tools.

- The browser never holds the API key. The app's server builds the system prompt from the brief (section 4), mints a short-lived client secret with the voice, the prompt and the tools already set, and returns only that.
- The browser connects with WebRTC, sends mic audio, plays the model's audio, and runs the tools locally (they draw the screen) while reporting every tool call and transcript turn back to the server in order, one batch in flight.
- Server-side voice activity detection, interruption allowed: the person can talk over the agent and it stops.
- A hard cap: the brief's `minutes` plus two. At the cap the agent is told to close in one turn; one minute later the call ends.

## 4. The brief

What the module hands the tool. Written the way you'd brief a person.

| Field | What |
|---|---|
| `role` | Who the agent is in this conversation and on whose behalf. |
| `goal` | What a good outcome is, in one or two sentences. |
| `audience` | Who is on the call: `owner`, `team`, `customer`, `guest`. Sets tone and what the agent may mention. |
| `method` | How to run it. Empty uses the default: open big, track coverage silently, one follow-up at most, move on as soon as a topic is usable. |
| `opening` | The first line, word for word. |
| `topics[]` | `id`, `title`, `opener` (the one big question), `examples` (shown on screen), `notes` (agent only, under 3,000 characters). |
| `closing` | How to end: the last question, what happens next, goodbye. |
| `report` | What the written handoff must contain. |
| `minutes` | The target length. |
| `video` | Record the camera too. Default off. |
| `context` | What the agent already knows about the person, so it never asks them to repeat it. Never shown to them. |

The brief is snapshotted onto each call, so editing it never rewrites history.

## 5. Tools the agent calls

| Tool | What it does on screen | What it saves |
|---|---|---|
| `set_topic(topic_id)` | Lights up that topic. | The current topic. |
| `capture_point(topic_id, point, kind)` | A note appears under the topic (not for `off_record`). | A point: `note`, `quote` (their exact words) or `off_record` (never shown to anyone but the owner's agent). |
| `complete_topic(topic_id, status, summary)` | The topic turns green (or gray if skipped). | Status `answered`, `partial` or `skipped`, and a two-sentence summary. |
| `log_request(type, title, details)` | A chip: "Logged for Chris". | A Board card draft (`change`, `feature`, `question`...). |
| `save_summary(summary)` | Nothing. | The call summary. |

## 6. What comes back

- Per call: transcript with timestamps, points by topic, topic statuses, summary, and for video the recording (chunked upload, every 5 seconds, so a dropped call loses seconds), poster frame and duration.
- Per interview: progress across calls (a topic covered once stays covered) and the handoff, rewritten after every call by the report prompt.
- Into the module that sent it: Interviews shows notes per topic; Testimonials makes a Draft video testimonial; a review files one Board card per item with notes.
- A call where the person never spoke doesn't count as a call.
- Continue: the next call starts at the first uncovered topic, and the agent welcomes them back instead of restarting.

## 7. Data

```sql
create table interviews (
  id serial primary key, tenant_id int not null,
  module text not null,                  -- interviews, testimonials, portal...
  subject_type text, subject_id int,     -- what it is about, e.g. person:12
  brief jsonb not null,                  -- section 4
  engine text not null default 'openai', -- openai | elevenlabs
  status text not null default 'open',   -- open | done | archived
  created_by int, created_at timestamptz
);
create table interview_links (
  id serial primary key, interview_id int not null references interviews(id) on delete cascade,
  user_id int,                           -- signed-in recipient
  person_id int,                         -- guest recipient (shared people table)
  token_hash text unique,                -- guests only
  sent_at timestamptz, opened_at timestamptz, expires_at timestamptz,
  check (user_id is not null or person_id is not null)
);
create table interview_calls (
  id serial primary key, interview_id int not null, link_id int not null,
  call_number int, brief jsonb not null, started_at timestamptz, ended_at timestamptz,
  status text,                           -- live | completed | ended_early | no_show
  transcript jsonb, topics jsonb, summary text, recording_file_id int
);
```

Anchors: `interview:<id>`, `interview_topic:<id>.<topic>`.

## 8. Rules

- Sending a link to anyone outside the team is gated for the agent, always. The owner sends it, or says yes to the agent sending it, and sees exactly who gets what.
- Off-the-record points never leave the tenant's own agent: not on screen, not in the handoff a client sees, not in the embed.
- Video and anyone's name used publicly need the consent timestamp from the guest screen (or the signed-in person's explicit tick).
- The agent never claims to be a person. The opening line says it is the business's AI interviewer.
- The interviewer speaks in the business's voice rules (`fields.voice`): short turns, no flattery, no summarizing their answer back to them.

## 9. Acceptance criteria

1. A signed-in customer opens an interview link: it runs inside their portal with no name or email form.
2. A signed-out recipient of a signed-in link signs in by magic link and lands on the interview, not the home page.
3. A guest link shows who is asking, the consent line and Start; nothing is recorded before Start.
4. The interviewer speaks within two seconds of Start, and stops when the person talks over it.
5. When the agent moves to a topic, it lights up on screen without anyone touching anything.
6. Hanging up after two of four topics, then opening the link again: the agent welcomes them back and starts at topic three.
7. A call where the person never spoke does not count.
8. The call ends by the cap even if the person keeps talking.
9. For a video interview, a dropped connection at minute four keeps everything up to the last 5-second chunk.
10. The API key never reaches the browser: the network tab shows only a short-lived client secret.
11. Switching the engine setting from OpenAI to ElevenLabs runs the same brief with the same five tools and the same results on screen.
12. An off-the-record point never appears on the recipient's screen or in a client-visible handoff.
