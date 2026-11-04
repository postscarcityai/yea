# Keeping up with YEA

Part of the YEA docs. How a business's app stays current with this reference after it has gone its own way. Written 2026-11-03.

Your app is yours. It has no upstream, and nothing here ever overwrites it. This reference keeps learning from real builds, so your agent reads what changed and decides what is worth taking.

---

## 1. Why you compare the spec, not the code

After a few months your code has diverged, and it should have. A code merge would be mostly conflicts. A change in this reference says what got better and why, in words, and your agent can apply that to whatever your code looks like now.

---

## 2. What your repo keeps

| File | Holds |
|---|---|
| `yea.lock.json` | The last commit of this reference you reviewed, and the date: `{ "commit": "<sha>", "reviewed_at": "2026-11-03" }` |
| `docs/yea-decisions.md` | One line per change you looked at: the commit, the decision, and why |

Write `yea.lock.json` when you build the app, with the commit you built from.

---

## 3. The check-in

On a schedule the owner picks (monthly is a good start), the agent does this:

1. Read `yea.lock.json`.
2. Read `CHANGELOG.md` and the diff of this repo from that commit to now.
3. Skip anything about a module that is off in `yea.config.json`, and anything already in `docs/yea-decisions.md`.
4. Decide each change:
   - **Adopt:** it's better, and it fits. Build it.
   - **Adapt:** the idea is right, but your business needs a different shape. Build your version.
   - **Skip:** it doesn't fit, or what you have is better. Say why, so it never comes up again.
5. Write every decision to `docs/yea-decisions.md`.
6. Build each adopted change on its own branch. Check the affected PRD's acceptance criteria and run `conformance/`.
7. Move `yea.lock.json` to the commit you reviewed.
8. Tell the owner in one short message what was adopted, what was skipped, and what's waiting on them.

---

## 4. The rules

- **Gate on what changed, not on the code.** Nobody reads pull requests. The agent records a short video of the change working, and the owner watches it and says yes or no. A yes ships it. Not yet proven: this is the direction, and we have not run it on a real app. Changing Team or Agent permissions always asks (`shared/roles.md` section 5).
- **Conformance has to pass first.** A video shows what the owner can see. `conformance/` covers what they can't: permissions, row rules, the log.
- **Must-review changes go first.** Anything marked `must-review` in the changelog (data loss, a legal or vendor rule) gets read before anything else and can't be skipped without the owner's yes.
- **Security doesn't wait for the check-in.** See `shared/security.md`.
- **Migrations move carefully.** Back up first, and write down how to reverse it.
- **Disagreeing is fine.** If you built something better, keep it. If it would help others, tell PostScarcity.

---

## 5. What every change here must say

A diff alone doesn't tell an agent why something is better. So every change to this repo gets a `CHANGELOG.md` entry with:

- **What changed**, and which files.
- **Why it's better.**
- **Where it's proven:** running in production, partly proven, or not yet proven.
- **`must-review`**, if it applies.
- **An advisory**, if it's a security fix (`shared/security.md`).
