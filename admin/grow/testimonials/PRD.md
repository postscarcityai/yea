# Testimonials (admin, Grow)

- **Module key:** `testimonials` (stable, never renamed)
- **Tier:** common
- **Route:** `/admin/testimonials`, and the guest's recording page `/t/[token]`
- **Folder:** `admin/grow/testimonials/`

> **Not yet proven end to end.** The testimonial records (a person with many testimonials, status, where each is used) run in production on postscarcity.ai since 2026-11-02, seeded from the quotes already on its site. The **video interview** (section "The video interview") is specced from the owner's brief and not built yet. Build it from this spec and test it hard on real guests before a link goes to a client.

## Job

"Get my best clients on camera saying what working with me did for them, without me scheduling a shoot. I send a link, they talk to an interviewer for five minutes, and the video is in my app, ready to post."

Testimonials are named, owner-collected proof: a client, a partner, a collaborator speaking about the business or the owner by name. That is the difference from Reviews (public star ratings from customers at large).

The number that tells you it is working: **share of interview links that come back as a usable video within 7 days**, target over 50 percent. Second number: **published testimonials per quarter**.

## Users and permissions

Start from `shared/roles.md`.

| User type | Scope | Differs from the matrix how |
|---|---|---|
| Owner | all | Sends links, approves and publishes. Only the Owner can publish a video. |
| Admin | all | Same as Owner, except publishing a video waits for the Owner. |
| Staff | all | Reads, adds quotes as drafts, sends links to people they own. |
| Contractor | none | Hidden. |
| Customer | own | Only the guest page `/t/[token]` for the link they were sent. Never the admin. |
| Agent | all | Drafts quotes from emails and calls, cuts clips from recorded videos, drafts the post. Never publishes. |

- **Gated verbs for the agent:** sending an interview link to anyone, publishing anything, and posting a clip to Social. Each waits for an Owner yes. Not relaxable.
- **Sensitive fields:** the raw recording and the guest's email. Consent is stored with the timestamp the guest gave it; without it nothing can be published.

## Pages and states

| Tab | Route | Holds |
|---|---|---|
| Testimonials | `/admin/testimonials` | One row per **person**, newest first: avatar, name and company, their latest words, testimonial count, a pill (green "2 published" or yellow "None live"), age, one **Open** button. Top action: **Add a quote**. |
| Links | `/admin/testimonials?tab=links` | Interview links sent: who, when, status chip (sent, started, recorded, expired), one action per row (Copy link, Resend, or Open the recording). |

- **Record view:** URL modal `?p=<person_id>`, read view. Header: person, title, company. Body: every testimonial from that person, newest first, each with its status pill (Draft yellow, Approved blue, Published green, Archived gray), kind (quote, video), source (on the site, added here, video interview, email, review), age, where it is used, the quote or the player, and **one** next-step button: Approve, Mark published, Archive or Restore. Footer: **Another quote from <first name>** (textarea + Add quote) and **Send an interview link**.
- **Add a quote:** URL modal `?add=1`: who said it, their role, company, the quote. Matches an existing person by name before making a new one.
- **States:** empty (ghost: "Add the first quote, or send someone a link to record one"), link expired, recording failed (with Resend), camera denied on the guest side.
- **Badge count:** recordings waiting for review.

## The video interview

Built on the shared interview tool (`shared/interview-tool.md`) with `video` on: a guest link for people without an account, the signed-in link for anyone who has one.

What the guest gets (Owner's brief, 2026-11-02): a link. They open it, and it looks like a video call. The interviewer is an AI voice. Their own camera sits in the bottom right so they can see what they look like. It takes five to seven minutes and asks them about the owner and the work. Recording starts when they press start, and when they hang up the video is already in the admin.

- **The link:** `/t/[token]`, one per person, 30-day expiry, token stored hashed. Opening it shows the owner's name and photo, what this is in one line ("A five-minute video interview about working with Chris. You'll talk to an AI interviewer."), the consent checkbox ("You can use this video and my name to promote <business>"), a camera and mic check, and **Start**.
- **The call screen:** full window, dark. The interviewer is a large tile (the business's mark, a waveform that moves with the voice, captions). The guest's camera is a small tile bottom right, mirrored. A visible timer and a red recording dot. **End** bottom center. No other controls.
- **The interviewer:** a realtime speech-to-speech model (default: OpenAI Realtime; ElevenLabs Agents works with the same brief). It runs an interview brief exactly like `admin/know/interviews/` with five topics and one big question each: how they met the owner, what they needed, what it was like to work together, what changed (ask for a number or a moment), and who they'd tell. It keeps its own turns to one line, quotes the guest back once per topic, and wraps at seven minutes whatever happens.
- **Recording:** the browser records the guest's camera and the mixed audio (guest + interviewer) with MediaRecorder, in 5-second chunks uploaded as they are made (resumable), so a dropped connection loses seconds, not the video. The transcript is saved with timestamps.
- **When it ends:** the request goes to `recorded`, a `video` testimonial is created as a Draft with the video, poster frame, duration and transcript, and the Owner gets one notification. The agent drafts two or three clip suggestions (start and end times, with the line that makes each one worth posting) and a pull quote from the transcript.
- **Posting it right away:** from the record, **Approve** then **Mark published** puts it on the site's testimonials block and offers **Post a clip** (Social, gated). Nothing is public before the Owner presses it.

## Data model

```sql
create table testimonials (
  id serial primary key,
  tenant_id int not null references tenants(id) on delete cascade,
  person_id int not null references people(id) on delete cascade,   -- shared people table: one person, many testimonials
  kind text not null default 'quote' check (kind in ('quote', 'video')),
  quote text, video_url text, poster_url text, transcript text, duration_s int,
  source text not null default 'manual',                             -- site, manual, interview, email, review
  status text not null default 'draft' check (status in ('draft', 'approved', 'published', 'archived')),
  consent_at timestamptz,
  used_on text[] not null default '{}',                              -- page paths and posts it appears on
  notes text, created_by int references users(id), created_at timestamptz, updated_at timestamptz,
  check (quote is not null or video_url is not null)
);
create table testimonial_requests (
  id serial primary key, tenant_id int not null, person_id int not null references people(id),
  token_hash text not null unique,
  status text not null default 'sent' check (status in ('sent', 'started', 'recorded', 'expired')),
  testimonial_id int references testimonials(id), created_by int references users(id),
  created_at timestamptz, started_at timestamptz, completed_at timestamptz, expires_at timestamptz
);
```

- Files (recording chunks, the assembled video, the poster) live in `files` (`shared/data-model.md`), linked by `testimonial_id`.
- Anchor kinds for the chat: `testimonial:<id>`, `person:<id>` (shared).
- Config knobs: `fields.testimonials.subject` (who the interview is about, default the Owner), `fields.testimonials.minutes` (default 6), `fields.testimonials.topics`. Sample data: `testimonials`.

## Agent actions

| Action | Tool | Verb | Gated | Writes to change_log | Undo |
|---|---|---|---|---|---|
| Draft a quote from an email or call | `draft_testimonial` | create | No | The draft, its source | Delete |
| Send an interview link | `send_testimonial_link` | send | Yes, always | The request, recipient | Expire the link |
| Suggest clips and a pull quote | `suggest_clips` | update | No | Clip times on the testimonial | Clear |
| Move a status | `set_testimonial_status` | update | Approve: no. Publish: yes | Before and after | Previous status |
| Post a clip | (Social) | publish | Yes, always | The post | Delete the post |

Background: expire links after 30 days; one reminder to the guest at day 5 if the link was never opened (Owner's yes on first send covers it).

## Integrations

- **Realtime voice:** OpenAI Realtime over WebRTC by default (ElevenLabs Agents as the alternative), short-lived session tokens minted server side; the browser never holds the API key.
- **Recording and storage:** browser MediaRecorder; chunked uploads to the app's file storage (Vercel Blob or the tenant's S3); a worker assembles and transcodes to MP4 and cuts the poster.
- **Email delivery** for the link. **Social** module for posting clips.
- **Secrets, by name:** `OPENAI_API_KEY` (or `ELEVENLABS_API_KEY`), `BLOB_READ_WRITE_TOKEN`, the email sender key.

## SaaS replaced

| Product | Risk | Migration |
|---|---|---|
| VideoAsk, Vocal Video, Testimonial.to | Easy | Export existing videos and quotes, import as published testimonials with their people. |
| Boast, Trustmary | Easy | Same. |
| A booked video shoot | No brainer | Nothing to migrate. |

## Acceptance criteria

1. An Owner opens Testimonials: one row per person; a person with three testimonials shows "3 testimonials".
2. Opening a person shows every testimonial they gave, each with its status pill and exactly one next-step button.
3. **Add a quote** with a name that already exists attaches the quote to that person instead of creating a second one.
4. Approve, then Mark published: the pill turns green and the change is in Log with a working Undo.
5. The agent cannot send an interview link or publish without an Owner yes, and shows exactly who gets what.
6. A guest opens `/t/<token>`: nothing records until they tick consent and press Start.
7. During the call the guest sees their own camera bottom right, a timer and a recording dot, and hears the interviewer within two seconds of Start.
8. The call wraps by minute seven even if the guest keeps talking.
9. The guest's connection drops at minute four: everything up to the last 5-second chunk is kept, and the link offers to finish.
10. Within two minutes of the call ending, a Draft video testimonial with poster, duration and transcript is on the person's record, and the Owner has one notification.
11. Nothing from a recording appears on the site or Social before the Owner publishes it.
12. An expired link shows a plain "This link has expired" page and records nothing.

## Open questions

- **Interview about the business or the owner?** Recommended: the owner by name, set by `fields.testimonials.subject`; founders sell on trust in the person.
- **Show the interviewer as a face?** Recommended: no. The business's mark and a waveform. A fake face reads as a trick.
- **Auto-publish after approval?** Recommended: no. Two steps, because a video with a name is the one thing you can't take back once it's shared.
