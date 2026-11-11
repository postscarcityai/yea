# Keeping up with YEA: the spec rebase

Part of the YEA docs. Written 2026-11-03, revised 2026-11-11.

Your app is yours. It has no upstream, and nothing here ever overwrites it. This reference keeps learning from real builds, so your agent reads what changed and decides what is worth taking.

We call this a **spec rebase**. A code rebase replays someone else's commits on top of yours. A spec rebase replays someone else's *ideas* on top of yours: your agent reads the spec, finds what your app shares with it and where it differs, and takes only the cherries, plugged in your way. It is never a blanket merge. The lowest common denominator in this reference never replaces something a business built on purpose.

---

## 1. Why you compare the spec, not the code

After a few months your code has diverged, and it should have. A code merge would be mostly conflicts. A change in this reference says what got better and why, in words, and your agent can apply that to whatever your code looks like now.

The same method has to work in ten years, when your app may look nothing like any other YEA app. Section 6 has the rules that keep it working that long.

---

## 2. What your repo keeps

| File | Holds |
|---|---|
| `yea.lock.json` | The last commit of this reference you reviewed, and the date: `{ "commit": "<sha>", "reviewed_at": "2026-11-03" }` |
| `docs/yea-decisions.md` | The rebase log. One entry per rebase, one line per change you looked at: the commit, Adopt, Adapt or Skip, and why |
| `docs/yea-own.md` | What is yours. The features, flows and choices this business built on purpose, each with one line on why it is protected |

Write all three when you build the app, or on your first rebase if the app came first (section 4).

`docs/yea-own.md` is the most important of the three. It is how the agent knows that your custom call screen, your pricing page or your odd approval flow is a feature and not drift. Add a line every time the business builds something its own way on purpose.

---

## 3. The check-in

On a schedule the owner picks (monthly is a good start), the agent does this:

1. Read `yea.lock.json`, `docs/yea-own.md`, and the last entry in `docs/yea-decisions.md`.
2. Read `CHANGELOG.md` and the diff of this repo from that commit to now.
3. Skip anything about a module that is off in `yea.config.json`, and anything already in `docs/yea-decisions.md`.
4. Decide each change:
   - **Adopt:** it's better, and it fits. Build it.
   - **Adapt:** the idea is right, but your business needs a different shape. Build your version.
   - **Skip:** it doesn't fit, or what you have is better. Say why, so it never comes up again.
   - A change that touches anything in `docs/yea-own.md` can only be **Adapt** or **Skip**. Never Adopt it as written.
5. Write a dated rebase entry in `docs/yea-decisions.md` with every decision.
6. Build each adopted change on its own branch. Check the affected PRD's acceptance criteria and run `conformance/`. Make a video where `shared/change-video.md` calls for one.
7. Move `yea.lock.json` to the commit you reviewed.
8. Tell the owner in one short message what was adopted, what was skipped, and what's waiting on them.

---

## 4. The first rebase: an app that came before YEA

An app does not have to be built from this reference to use it. A business with a working app can rebase onto YEA the same way:

1. **Inventory the app.** List its pages, roles, data and the agent features it has today.
2. **Find the common factors.** Match each part to a YEA module, shared spec or rule (`shared/modules.md`, `shared/design-system.md`, `shared/chat.md`, `shared/roles.md`). Use the YEA module key even when the app calls it something else.
3. **Find the deltas.** Everything the app does that YEA does not, or does differently. Decide for each one: is it a reason the business uses this app (it goes in `docs/yea-own.md`), or is it just how it happened to get built (a candidate to take from YEA)?
4. **Pick the cherries.** From what YEA has and the app lacks, choose a few to take now. Start with the shell (left nav, profile block, chat FAB): they are cheap and every later change assumes them.
5. **Write the three files** from section 2, with this reference's current commit in `yea.lock.json`. The first entry in `docs/yea-decisions.md` holds the inventory, the matches and the picks.

From then on the app keeps up with the check-in in section 3, like any other YEA app.

---

## 5. The rules

- **Gate on what changed, not on the code.** Nobody reads pull requests. The agent makes a short video of the change, and the owner says yes or no. See `shared/change-video.md`. Changing Team or Agent permissions always asks (`shared/roles.md` section 5).
- **Conformance has to pass first.** A video shows what the owner can see. `conformance/` covers what they can't: permissions, row rules, the log.
- **Must-review changes go first.** Anything marked `must-review` in the changelog (data loss, a legal or vendor rule) gets read before anything else and can't be skipped without the owner's yes.
- **A critical security fix doesn't wait for the check-in.** It ships, and the owner hears right after.
- **Migrations move carefully.** Back up first, and write down how to reverse it.
- **What's yours stays yours.** Nothing in `docs/yea-own.md` is replaced by a spec change. If the spec has a better idea for one of those parts, the agent brings it to the owner as an Adapt, built around what is already there.
- **Disagreeing is fine.** If you built something better, keep it. If it would help others, tell PostScarcity.

---

## 6. Built to last ten years

Apps fork hard over time, and that is the point. These rules keep the rebase working when an app no longer looks like any other:

- **Talk in module keys and intent, never in file paths.** Changelog entries and decisions name the module key (`leads`, `calls`) and say what the change is for. Your code may have no file with that name; the agent finds where the idea lives in your app.
- **The decisions log is the memory.** A Skip with its reason is as valuable as an Adopt. It keeps the same question from coming back every month, for years.
- **Map your names once.** When the business relabels or reshapes a module, note it in `docs/yea-own.md` ("Deals is our `pipeline`"), so every later rebase finds the match.
- **A module you never took is not a gap.** Being far from the spec is fine. The rebase only asks whether a change is worth taking, never how to get closer to the reference.

---

## 7. What every change here must say

A diff alone doesn't tell an agent why something is better. So every change to this repo gets a `CHANGELOG.md` entry with:

- **What changed**, and which files.
- **Which module keys** it touches, so an app that has forked far can still find it.
- **Why it's better.**
- **Where it's proven:** running in production, partly proven, or not yet proven.
- **`must-review`**, if it applies.
