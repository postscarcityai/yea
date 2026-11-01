# Creator, community or event brand

You build an audience with content, then turn it into tickets, sponsors and members.

Machine-readable copy: `lib/yea-finale/playbooks/archetypes.ts` in the postscarcity-ai repo, id `creator-membership`. Back to [all playbooks](README.md).

## Who pays and how

- Fans join a waitlist for free, then buy tickets to the drop (ticket links were built on the card rail).
- Sponsors pay in tiers, from headline to in-kind, and grants count as a tier.
- Memberships are not built yet in any of our builds; the portal and shop modules carry them from the spec.

## The core loop

1. **Capture.** Fans join the list, with a welcome and a founder alert. `~/dev/bootyverse/fn/waitlist.ts`
2. **Footage in.** Phone footage uploads straight to the shared drive. `~/dev/bootyverse/fn/uploads.ts`
3. **Make.** Clips are tagged and searchable; templates render posts and carousels. `~/dev/bootyverse/tools/engine/worker.mjs`
4. **Send.** Campaigns to your own list, tracked, with suppression. `~/dev/bootyverse/fn/campaigns.ts`
5. **Fund.** Sponsors researched, tracked by stage, goals read live. `~/dev/bootyverse/fn/sponsors.ts`

## Modules on

| Module key | Label we used | Why |
|---|---|---|
| `people` | Waitlist | everyone on the list |
| `pipeline` | Sponsors | sponsors by tier and stage |
| `library` | Library | every clip and photo, searchable |
| `studio` | Studio | brand templates and renders |
| `content` | Series | recurring shows and skits |
| `campaigns` | Emails | campaigns to the list |
| `goals` | Goals | goals tied to live numbers |
| `social` | Social | posts for review and approval |

Core modules (Home, Inbox, People, Views, Goals, Team, Agents, Board, Log, Settings, Site, Intake, Portal) are always on as well. See `shared/modules.md`.

## Stages we actually used

- **sponsor** (`pipeline`): prospect, ready, approved, contacted, talking, committed, not_now, declined, past. `~/dev/bootyverse/fn/sponsors.ts`
- **campaign** (`campaigns`): draft, queued, sending, sent. `~/dev/bootyverse/fn/campaigns.ts`
- **upload session** (`library`): free, claimed, done, failed. `~/dev/bootyverse/migrations/0006_uploads.sql`
- **render job** (`studio`): queued, running, done, error. `~/dev/bootyverse/fn/engine.ts`

## The agent's first three jobs

1. Tag every new clip and stack the duplicates, so the editor finds the shot in seconds.
2. Draft this week's posts and the list email from what was shot.
3. Research the next ten sponsors, fill only blank fields, and tee them up for a person to contact.

## Hero workflow: Find the shot, make the post

Signed in as the staff, approved by the owner. The agent is "Studio desk". Shows the play [Search footage by what is in it](#library-search-by-picture).

Steps on screen: Footage lands > Ask > Search by what is in it > Draft post > Owner approves > Logged with Undo.

- **Pinned:** Folder "Rehearsal, Oct 28"
- **Ask:** "Find the clip where the whole crew lands the jump, and make a post for Friday."
- **Agent works:** Searched 1,240 clips for a group jump; Found 3 takes, stacked 2 duplicates; Framed the best take on the crew; Rendered the post from the Friday template.
- **Reply:** "Take 2 from Oct 28 has all six landing together. The Friday post is drafted on the left with the clip framed on the crew."
- **Approval:** "Schedule it for Friday at 6 PM?" [Change] [Approve], then "Approved. Scheduled for Friday 6 PM."
- **Log, with Undo:** Studio desk scheduled the Friday post from take 2. Approved by Juno Reyes.

Names in the script are fictional.

## What it lets them cancel

Linktree, Mailchimp, Typeform, Canva, Later, Dropbox. Prices and risk for each are in [shared/saas.md](../shared/saas.md).

## Rails kept

Vercel, Neon, Twilio SendGrid, Square, Google Drive, Voice API.

## Plays

Innovation plays first: things we built that most businesses like this do not have yet.

### Phone footage straight to the drive (innovation)

<a id="phone-upload-to-drive"></a>Shoot on a phone, upload from a link, and full-size footage lands in the shared drive, resuming after a dropped signal.

- **Id:** `phone-upload-to-drive`
- **Modules:** `library`, `studio`
- **Fits when you see:** video, footage, shoot, filming, content, creator, events
- **Proved in:**
  - `~/dev/bootyverse/fn/uploads.ts`
  - `~/dev/bootyverse/admin/engine/uploads.js`: 16 MB chunks, resume
  - `~/dev/bootyverse/tools/uploads/pool.mjs`: the Mac mints resumable sessions ahead
  - `~/dev/bootyverse/migrations/0006_uploads.sql`

### Search footage by what is in it (innovation)

<a id="library-search-by-picture"></a>Find any clip by typing what is in it, with auto-tags, duplicate stacks and crops centred on people.

- **Id:** `library-search-by-picture`
- **Modules:** `library`
- **Fits when you see:** photos, videos, footage, library, content, media
- **Proved in:**
  - `~/dev/bootyverse/tools/engine/tag.py`: local image model
  - `~/dev/bootyverse/migrations/0002_media_clip_vector.sql`: vector search

### Call your back office (innovation)

<a id="voice-persona"></a>Talk to the business's agent by voice inside the app; it answers from the real records and files what you ask.

- **Id:** `voice-persona`
- **Modules:** `agents`, `board`
- **Fits when you see:** voice, phone, podcast, talk, calls
- **Proved in:**
  - `~/dev/bootyverse/admin/engine/voice.js`
  - `~/dev/bootyverse/fn/admin.ts`: ask_back_office reaches the live agent

### Waitlist with a welcome

<a id="waitlist-welcome"></a>Sign-ups land in your own list, rate-limited, with a welcome email and a founder alert on every one.

- **Id:** `waitlist-welcome`
- **Modules:** `intake`, `people`, `campaigns`
- **Fits when you see:** waitlist, join the list, coming soon, early access, sign up, launch
- **Proved in:**
  - `~/dev/bootyverse/fn/waitlist.ts`
  - `~/dev/bootyverse/fn/ratelimit.ts`
  - `~/dev/bootyverse/fn/autoemails.ts`
  - `~/dev/bootyverse/fn/alerts.ts`

### Your own email engine

<a id="own-email-engine"></a>Campaigns to your own list with open and click tracking, a signed delivery webhook, suppression and an audit log.

- **Id:** `own-email-engine`
- **Modules:** `campaigns`
- **Fits when you see:** newsletter, email list, subscribers, mailing list, updates
- **Proved in:**
  - `~/dev/bootyverse/fn/campaigns.ts`
  - `~/dev/bootyverse/fn/sendgrid.ts`
  - `~/dev/bootyverse/fn/audit.ts`
  - `~/dev/amc/lib/email/campaign-sender.ts` (at `origin/main`)

### Brand templates the agent fills

<a id="studio-templates"></a>Carousels and cards render from brand templates with framed photos, queued to a render worker.

- **Id:** `studio-templates`
- **Modules:** `studio`, `social`
- **Fits when you see:** instagram, carousel, brand, design, canva, graphics
- **Proved in:**
  - `~/dev/bootyverse/admin/studio/runtime.js`: framing reads x, y, zoom
  - `~/dev/bootyverse/tools/engine/studio.mjs`
  - `~/dev/bootyverse/tools/engine/worker.mjs`

### Sponsors, researched and tracked

<a id="sponsor-crm"></a>Sponsors and funders in tiers with stages; the agent researches and fills only blank fields, and nothing sends without a person.

- **Id:** `sponsor-crm`
- **Modules:** `pipeline`, `people`
- **Fits when you see:** sponsors, sponsorship, partners, grant, underwriting, donors, funders
- **Proved in:**
  - `~/dev/bootyverse/fn/sponsors.ts`: tiers headline to grant, stages prospect to committed, no send endpoint

### Goals tied to live numbers

<a id="goals-live-numbers"></a>Goals read their number straight from the data, so the goal board is never a spreadsheet someone forgot to update.

- **Id:** `goals-live-numbers`
- **Modules:** `goals`
- **Fits when you see:** goal, target, raise, launch
- **Proved in:**
  - `~/dev/bootyverse/fn/goals.ts`
  - `~/dev/bootyverse/admin/engine/goals.js`

### Approve posts from your phone

<a id="social-review-hub"></a>Drafted posts and videos wait in one review queue; comment, request changes or approve, and it posts to each channel.

- **Id:** `social-review-hub`
- **Modules:** `social`
- **Fits when you see:** instagram, social, facebook, linkedin, tiktok, posts
- **Proved in:**
  - `~/dev/amc/app/admin/social/[id]/page.tsx` (at `origin/main`)
  - `~/dev/amc/lib/admin/social.ts` (at `origin/main`): statuses and channels
  - `~/dev/amc/app/api/webhooks/zernio/route.ts` (at `origin/main`)

### Explainer videos from a script

<a id="explainer-video-pipeline"></a>Stills, voice, music and captions assembled into short explainers from a written script, on a repeatable recipe.

- **Id:** `explainer-video-pipeline`
- **Modules:** `studio`, `social`
- **Fits when you see:** video, youtube, reels, explainer, tiktok
- **Proved in:**
  - `~/dev/amc/scripts/video/noir/build.mjs` (at `origin/main`)
  - `~/dev/amc/docs/COMIC-NOIR-VIDEO-PLAYBOOK.md` (at `origin/main`)

### Which post sold

<a id="post-to-order-attribution"></a>Every order is tied back to the post or email that brought it, and the agent drafts next week from what worked.

- **Id:** `post-to-order-attribution`
- **Modules:** `social`, `insights`, `orders`
- **Fits when you see:** instagram, tiktok, social, influencers, content, posts
- **Proved in:**
  - `~/dev/peels/lib/what-worked-core.mjs`
  - `~/dev/peels/db/055_order_attribution.sql`
  - `~/dev/peels/lib/post-learning-core.mjs`
  - `~/dev/peels/lib/auto-drafts-core.mjs`: weekly drafts from real assets only

## Not proven yet

The generator must not show these as done.

- Paid memberships and member logins.
- Ticket checkout inside the app: tickets used hosted card-rail links.

## Built from

- `~/dev/bootyverse`: waitlist, library, studio, uploads, emails, sponsors, voice
- `~/dev/amc`: social review hub and explainer videos
- `~/dev/peels`: post learning and attribution

## Signals that point here

creator, community, members, membership, event, events, tickets, festival, waitlist, videos, podcast, youtube, followers, sponsors, fans, show, dance, fitness class
