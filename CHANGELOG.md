# Changelog

Newest first. Every change to this reference gets an entry. See `shared/updating.md`.

Format: what changed, why it's better, where it's proven, and `must-review` if it applies.

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
