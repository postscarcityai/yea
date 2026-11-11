# Changelog

Newest first. Every change to this reference gets an entry. See `shared/updating.md`.

Format: what changed, why it's better, where it's proven, and `must-review` if it applies.

## 2026-11-11: Agents are directives with editable instructions, tools and call rules

- **What changed:** `admin/run/agents/PRD.md`: new section. An agent is a directive plus tools; every step's built-in instructions are editable with Reset to built-in; tools switch steps off; call rules default to join every meeting, narrowed by business hours and per record; one default agent, Owner manages by default.
- **Module keys:** `agents`, `calls`.
- **Why it's better:** businesses want more than one agent, each for a different job, without losing the one that already works. Locked prompts made tuning a code change.
- **Where it's proven:** not yet proven; being built in one production app.

## 2026-11-11: Themes out of the box, full screen mode, live dot, worker hosts

- **What changed:**
  - `shared/design-system.md`: Light, Dark and System ship with every app's first release. New **full screen mode** (same route, `?full=1`, Esc returns). New **live dot** on a nav item while something is happening now.
  - `README.md` stack: Supabase is a database option alongside Neon. New **Workers** row and a "Where workers run" note: Fly for small always-on workers, Beam for bursty, scale-to-zero or GPU work.
- **Module keys:** shell, `calls`.
- **Why it's better:** a single theme kept getting shipped and patched later. Full screen as its own page lost the nav, the chat and the URL. Live work (a call in progress) needs to be findable from anywhere. Worker hosting was unspecified, and the cheap answer depends on whether the worker idles.
- **Where it's proven:** Supabase, Fly and Beam each run in one production app. Full screen mode and the live dot are not yet proven.

## 2026-11-11: Spec rebase, nothing required, modes, optional multi-tenant

- **What changed:**
  - `shared/updating.md`: keeping up is now named the **spec rebase**. New `docs/yea-own.md` lists what the business built on purpose; a change touching it can only be Adapt or Skip. New section on the first rebase of an app that came before YEA (inventory, common factors, deltas, cherries). New rules for apps that have forked for years: talk in module keys and intent, never file paths.
  - `README.md`, `shared/modules.md`, `admin/run/settings/PRD.md`, the playbooks: **nothing is required.** Core means on by default; any module can be switched off, and an app can start as one or two modules.
  - `shared/design-system.md` section 2: the collapsible rail is required on every app, every nav item has an icon, the rail shows labels in a tooltip on hover, and groups are optional for small apps.
  - `shared/design-system.md` new section 2b, `shared/roles.md`, `shared/modules.md`: **modes.** Growth modes (the simple app, then larger ones with previews of modules to come), role modes (see the app as an assistant sees it, read-only), work modes (Marketing, Accounting). Modes are config and easy to delete. "Switch view" in the profile menu becomes "Modes". `README.md` step 2 shows the owner two or three growth modes when starting a project.
  - `shared/roles.md` new section 8: **optional multi-tenant** apps with a platform superuser above Owner, read-only when it opens an org, every action in that org's Log. Recommended when a new app may serve more than one business; not needed on a rebase.
  - `admin/home/PRD.md`: the first Home is plain counts and the next thing due, no trends until the data earns them.
- **Module keys:** `home`, `settings`, all modules (tiers), shell.
- **Why it's better:** a strict core list pushed small apps to build modules nobody used. A protected list keeps the spec's average from flattening the thing a business pays for. Modes let an owner see the path to a full operating system without building it, and the same mechanism narrows a big app back down later. Builders who serve many businesses were rebuilding tenancy by hand.
- **Where it's proven:** the multi-tenant shape (orgs, switch workspace, read-only superuser banner) runs in one production app. Spec rebase, modes and previews are not yet proven.
- **must-review:** if your app forces any module on, let the owner switch it off. Add `docs/yea-own.md` on your next check-in.

## 2026-11-07: Theme lives on My account, three options

- **What changed:** `shared/design-system.md`, `shared/modules.md`, `customer/portal/PRD.md`: the theme comes out of the profile menu. My account has one **Theme** row with **Light**, **Dark** and **System**. The menu is My account, Terms, View site or Back to the site, Switch view (demo only), Sign out. This replaces the two 2026-11-06 entries below.
- **Why it's better:** the theme is set once, so it belongs with account settings, not in a menu opened every day. One clear choice of three beats a switch plus a second setting that turns each other off.
- **Where it's proven:** live in one production back office.
- **must-review:** if you added a Dark mode switch or Match my device, remove both and put the three-option Theme on My account.

## 2026-11-06: Match my device lives in My account

- **What changed:** `shared/design-system.md`: following the device's theme comes back as a **Match my device** switch in My account. The Dark mode switch in the profile menu shows what is on screen, and using it turns matching off.
- **Why it's better:** people still need the theme to follow their device. The setting you pick once sits in account, and the switch you use often stays one tap away.
- **Where it's proven:** live in one production back office.
- **must-review:** if you dropped the system theme, add this back.

## 2026-11-06: Dark mode is one switch

- **What changed:**
  - `shared/design-system.md`: the Light, Dark, System selector becomes one Dark mode row with an on/off switch. The saved choice is light or dark.
  - `shared/modules.md`, `customer/portal/PRD.md` and `customer/site/PRD.md` updated to match.
- **Why it's better:** a three-way selector in a small menu is more control than the choice deserves. One row with one switch reads at a glance and is easy to hit.
- **Where it's proven:** live in one production back office.
- **must-review:** replace any multi-option theme selector.

## 2026-11-06: The profile menu holds account, terms, theme and sign out

- **What changed:**
  - `shared/design-system.md` section 2a: **My profile** becomes **My account**, **Terms** joins the menu, and a build with sign out in the open is not done.
  - `shared/modules.md` and `customer/portal/PRD.md`: profile entries updated to match.
- **Why it's better:** sign out kept getting built as a loose button or icon in the nav even though the rule was written down. Stating the failure plainly makes it a check, and terms now have a home every signed-in person can reach.
- **Where it's proven:** live in one back office, at desktop and phone width.
- **must-review:** check your shell against section 2a.

## 2026-11-04: A card in review carries what to look at

- **What changed:**
  - `admin/run/board/PRD.md`: new Look at block, `look_at` field, and acceptance check. No card reaches a review stage without something to open, and a pull request alone doesn't count.
  - `shared/modules.md`: Board entry updated to match.
- **Why it's better:** a note pointing at a whole tab leaves the reviewer hunting. Options are one tap, so reviewing takes the time it should.
- **Where it's proven:** live in one production back office, covering video in the card, before and after, pages and screens, at desktop and phone width.

## 2026-11-03: One person, many relationships, and a Clients tab

- **What changed:**
  - `admin/grow/people/PRD.md`: new `relationships` table. A person holds a stint per kind (lead, client, vendor, partner, team), each with a stage, dates and an end reason. New Clients, Vendors and Partners tabs, a Relationships tab on the record, and rules for ending and coming back.
  - `shared/data-model.md`: `people.kind` is gone. Kind chips are the open relationship rows.
  - `admin/grow/leads/PRD.md`: a lead converts to a client, vendor, partner or hire by closing one relationship and opening the next.
  - `admin/run/team/PRD.md`: deactivating ends the `team` relationship. Rehiring reuses the same person, with a role chosen fresh.
  - `shared/modules.md`: People entry updated to match.
- **Why it's better:** one `kind` column can't say someone is both a vendor and a partner, or that they left and came back, so the history got overwritten. Clients had no named section, and partners had no home in People.
- **Where it's proven:** partner and vendor stages run in one production back office. The full path, including ending and rehiring, is not yet proven. Migrating: write one open `relationships` row per person from their `kind`, with `started_at` set to `created_at`, then drop the column.

## 2026-11-03: Change videos are a step, security cut to the basics

- **What changed:**
  - New `shared/change-video.md`: when a video is required, the agent's steps, the script and the rules.
  - New `change-video/`: the kit that turns a script into a video, with the voice checked against the script.
  - Build order, `shared/updating.md` and `shared/agent-platform.md` now run through it.
  - `shared/security.md` cut to seven basics. The advisory system and the register of apps are gone.
- **Why it's better:** owners can judge a video, and most can't judge a pull request. The security page asked for more machinery than anyone needs yet.
- **Where it's proven:** the kit made a real plan film for a live business. The gate has not run on a live app yet.

## 2026-11-03: Conformance kit, security across many apps, gating by video

**`must-review`**: the app's database login must not be the owner. Check yours with `conformance/`.

- **What changed:**
  - New `conformance/`: runnable checks for the database login, row rules, audit coverage, log integrity, grants, guards on actions and routes, and dependencies.
  - New `shared/security.md`.
  - `shared/updating.md`: nobody reads pull requests. The owner gates on a video of the change, after conformance passes.
  - `shared/agent-platform.md`: a fresh agent learns from this reference. No longer an open question.
  - `README.md`: the app's database login is a requirement, and the smallest YEA now fits the build order. `shared/data-model.md`: write the log with a trigger. `practices/traps.md`: new Safety section.
- **Why it's better:** apps drift and nobody reads their code, so behavior has to be testable. The reference also said "core is always on" and "ship three modules first" at once.
- **Where it's proven:** the kit passes against one production back office on a clean database and on a copy of live data, and it caught a real half-applied migration while being built. The video gate is not yet proven. No app has been built from this reference alone.

## 2026-11-03: Playbooks speak in generalities

- **What changed:** Playbooks describe patterns only. Each archetype names one of the fictional example companies, and every company, person and number in them is made up.
- **Why it's better:** This repo is public. It carries what we learned, never whose business we learned it in.
- **Where it's proven:** The pages generate from a private map, and the generator refuses to write a page with a private detail in it.

## 2026-11-03: Every play is a recipe that stands alone

- **What changed:**
  - Every play in `playbooks/` (51) now carries a recipe: the rule, the data it needs, the steps, and what breaks.
  - Plays add a "Not proven by the code behind this play" list wherever the code does less than the promise says.
  - `playbooks/README.md` opens with what a recipe is and how to read it.
- **Why it's better:** a play used to be a promise and a private file path nobody outside could open. An outside agent can now build from the words alone, and it can see what is and isn't real before it pitches a play.
- **Where it's proven:**
  - Each recipe was written from the files behind that play, read for this change. Some of those builds run in production, and some have parts switched off or not connected. The not-proven lists say which.
  - No recipe has been rebuilt from its words alone yet, so standing alone is not yet proven.

## 2026-11-03: Vercel plus Beam, the back office first, MCP on trial

- **What changed:** in `shared/agent-platform.md`, the back office is the main way in for Hermes, and MCP becomes a read-only test. Compute is Vercel plus Beam with a Mac mini on top, not a ladder. An agent instance is defined, starting on Beam. Hand-over is day 90. One-repo results added.
- **Why it's better:** it's simpler, and nothing gets built on MCP until a test shows it helps.
- **Where it's proven:** the back office runs in production. One repo with Vercel and Beam was tested from GitHub Actions. The MCP test is not done. An always-on Hermes instance has only been run as a short test.

## 2026-11-03: A reference, an agent platform, and practices

**`must-review`**: subscription login is out of the spec, based on a reading of Anthropic's terms.

- **What changed:**
  - `README.md` now opens as a reference, and says how you get an app and keep it current.
  - New `shared/agent-platform.md`, `shared/updating.md` and `practices/`.
  - `shared/roles.md` and `admin/run/agents/PRD.md` gain YOLO and quiet mode.
- **Why it's better:** the agent side was barely written down. Lessons from real builds sat in private notes, and there was no way to take in new ideas after the first build.
- **Where it's proven:**
  - `practices/` comes from running agents in production.
  - One repo with several deploy targets runs in production.
  - MCP, the native agent's learning, the Mac mini tier and the check-in in `shared/updating.md` are not yet proven.
