# Changelog

Newest first. Every change to this reference gets an entry. See `shared/updating.md`.

Format: what changed, why it's better, where it's proven, and `must-review` if it applies.

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
