# Nonprofit, donor funded

You run programs for people who cannot pay, funded by donors, sponsors and grants.

Machine-readable copy: `lib/yea-finale/playbooks/archetypes.ts` in the postscarcity-ai repo, id `nonprofit`. Back to [all playbooks](README.md).

## Who pays and how

- Donors give through a giving rail, from one giving page with tiers, the tax status and the EIN.
- Sponsors and funders give in tiers; grants and in-kind count.
- Raffles and giveaways need rules and a recorded draw.

## The core loop

1. **Tell the mission.** The home page shows the gap the programs fill. `~/dev/healing-alliance/src/app/page.tsx`
2. **Give.** Every button goes to one giving page, then out to the giving rail. `~/dev/healing-alliance/src/app/donate/page.tsx`
3. **Show impact.** Real figures, or a plain note that they are coming. `~/dev/healing-alliance/src/app/donate/page.tsx`
4. **Fund.** Sponsors and funders tracked by tier and stage. `~/dev/bootyverse/fn/sponsors.ts`
5. **Keep in touch.** Updates to donors from your own list. `~/dev/bootyverse/fn/campaigns.ts`

## Modules on

| Module key | Label we used | Why |
|---|---|---|
| `site` | Site | mission, team, resources, giving page |
| `shop` | Donate | giving tiers |
| `pipeline` | Funders | sponsors, funders and grants by stage |
| `people` | Donors | everyone who gave or signed up |
| `campaigns` | Updates | donor updates |
| `goals` | Goals | the raise and program goals, live |
| `programs` | Raffles | raffles with rules and a draw |
| `playbook` | Approved copy | the words the board signed off |

Core modules (Home, Inbox, People, Views, Goals, Team, Agents, Board, Log, Settings, Site, Intake, Portal) are always on as well. See `shared/modules.md`.

## Stages we actually used

- **funder** (`pipeline`): prospect, ready, approved, contacted, talking, committed, not_now, declined, past. `~/dev/bootyverse/fn/sponsors.ts`
- **raffle** (`programs`): draft, scheduled, live, closed, drawn, fulfilled. `~/dev/peels/lib/giveaways.ts`
- **update** (`campaigns`): draft, queued, sending, sent. `~/dev/bootyverse/fn/campaigns.ts`

## The agent's first three jobs

1. Thank every donor the day they give, in the board's approved words.
2. Research funders and grants that match the mission and tee them up by stage.
3. Keep the impact panel honest: update it when real numbers come in, never invent one.

## Hero workflow: Ten funders that fit, ready for Monday

Signed in as the admin, approved by the owner. The agent is "Development desk". Shows the play [Sponsors, researched and tracked](#sponsor-crm).

Steps on screen: Pin the mission > Ask > Research > Shortlist > Director approves > Logged with Undo.

- **Pinned:** Doc "Mission and programs"
- **Ask:** "Find funders who back peer support for veterans in our county and line them up."
- **Agent works:** Read the mission and the three programs; Found 14 funders with matching giving history; Filled only blank fields, kept what we had; Ranked 10 by fit and gift size.
- **Reply:** "Ten funders are on the left, ranked by fit. Three gave to peer support in the county last year. Nothing has been sent; each one has a drafted first note."
- **Approval:** "Move these ten to Ready for Monday's outreach?" [Not yet] [Approve], then "Approved. Ten funders moved to Ready."
- **Log, with Undo:** Development desk moved 10 funders to Ready. Approved by the director.

Names in the script are fictional.

## What it lets them cancel

Wix, Mailchimp, Typeform, Airtable. Prices and risk for each are in [shared/saas.md](../shared/saas.md).

## Rails kept

Vercel, Twilio SendGrid, Giving rail (hosted donation form).

## Plays

Innovation plays first: things we built that most businesses like this do not have yet.

### Impact without made-up numbers (innovation)

<a id="honest-impact"></a>The impact panel shows real figures or says they are coming, with the program-spend goal, never invented stats.

- **Id:** `honest-impact`
- **Modules:** `site`, `goals`
- **Fits when you see:** impact, mission, programs, served, nonprofit
- **Proved in:**
  - `~/dev/healing-alliance/src/app/donate/page.tsx`: coming-soon stats panel and direct-services goals

### Sponsors, researched and tracked (innovation)

<a id="sponsor-crm"></a>Sponsors and funders in tiers with stages; the agent researches and fills only blank fields, and nothing sends without a person.

- **Id:** `sponsor-crm`
- **Modules:** `pipeline`, `people`
- **Fits when you see:** sponsors, sponsorship, partners, grant, underwriting, donors, funders
- **Proved in:**
  - `~/dev/bootyverse/fn/sponsors.ts`: tiers headline to grant, stages prospect to committed, no send endpoint

### Giveaways with an audit trail (innovation)

<a id="giveaway-audit"></a>Official rules drafted for approval, a recorded draw, winner claims with deadlines, and an audit PDF at the end.

- **Id:** `giveaway-audit`
- **Modules:** `programs`, `social`
- **Fits when you see:** giveaway, contest, sweepstakes, raffle, win
- **Proved in:**
  - `~/dev/peels/lib/giveaways.ts`: draft, scheduled, live, closed, drawn, fulfilled
  - `~/dev/peels/lib/giveaway-draw-core.mjs`
  - `~/dev/peels/lib/giveaway-audit-pdf.mjs`

### One path to give

<a id="one-donate-path"></a>Every button on the site goes to one giving page with tiers, the tax status and the EIN, then out to the giving rail.

- **Id:** `one-donate-path`
- **Modules:** `site`, `shop`
- **Fits when you see:** donate, give, donation, support our, 501 c 3, tax deductible
- **Proved in:**
  - `~/dev/healing-alliance/src/lib/site.ts`: DONATE_URL, DONATE_CHECKOUT_URL, ORG_EIN
  - `~/dev/healing-alliance/src/app/donate/page.tsx`: TIERS

### One source of approved copy

<a id="approved-copy-source"></a>Copy the board approved lives in one file, and the site renders from it word for word.

- **Id:** `approved-copy-source`
- **Modules:** `playbook`, `site`
- **Fits when you see:** board, mission, foundation, approved
- **Proved in:**
  - `~/dev/healing-alliance/content/SOURCE-COPY.md`

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

### Goals tied to live numbers

<a id="goals-live-numbers"></a>Goals read their number straight from the data, so the goal board is never a spreadsheet someone forgot to update.

- **Id:** `goals-live-numbers`
- **Modules:** `goals`
- **Fits when you see:** goal, target, raise, launch
- **Proved in:**
  - `~/dev/bootyverse/fn/goals.ts`
  - `~/dev/bootyverse/admin/engine/goals.js`

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

## Not proven yet

The generator must not show these as done.

- Donor records inside the app: gifts live with the giving rail today.
- Recurring gift management.
- Volunteer scheduling.

## Built from

- `~/dev/healing-alliance`: the giving page, honest impact, approved copy
- `~/dev/bootyverse`: sponsor tracking, own email, live goals
- `~/dev/peels`: giveaways with rules, draw and audit

## Signals that point here

nonprofit, non profit, 501 c 3, donate, donation, donors, foundation, charity, mission, volunteers, grant, fundraiser, tax deductible
