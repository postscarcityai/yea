# Contributing: sending learnings back

This reference compounds. Every business built from it hits a few snags, and every snag sent back is one the next business never hits. This file is for the agent that does the sending. Follow it exactly.

---

## 1. The rule that comes before everything

**Nothing personal leaves the business. Ever.** A learning is an issue and a better way to do it. It is never about who had the issue.

Before you write a single line, the owner has said yes in plain words (README section 8). No yes, no pull request. A yes for one build is not a yes for the next.

---

## 2. What a learning is

One thing that cost real time, written so any agent on any stack can use it:

- **What happened.** What it looked like from the outside: the error, the symptom, the wrong result.
- **Why.** The cause, once you found it.
- **The fix.** What worked.
- **What the reference should say.** The sentence that would have saved the time, and the file it belongs in (`README.md` section, a `shared/` file, a module `PRD.md`, or `practices/traps.md`).

Good: "A relative redirect in middleware crashed sign-out behind a proxy. Build the Location from the forwarded host as an absolute URL."

Not a learning: a bug in your own code that the spec already covers, a preference, a product idea with no snag behind it (open an issue for those instead), anything you did not see happen.

---

## 3. What must never be in it

Check every line against this list before you show the owner. If a line needs any of these to make sense, rewrite it in general terms or drop it.

- Names: the business, its people, its customers, its vendors, its domain, its repo, its accounts.
- Anything that identifies the business: its city, its niche when that narrows it to a few, its brand words, its product names.
- Numbers from the business: revenue, prices, counts of customers or leads, costs, dates of its events.
- Links, file paths, IP addresses, emails, phone numbers, account or project ids.
- Keys, tokens, env values, connection strings, even partial or expired ones.
- Logs, stack traces, screenshots or recordings that hold any of the above. Paraphrase the error instead.
- Your conversation with the owner, quoted.

Software names, versions and public vendor behavior are fine: "Vercel CLI 48 pulled env with sensitive values blank."

---

## 4. How to send it

1. **Write it in the business's repo first**, in `docs/learnings.md`, as you go.
2. **Make the shareable copy.** Apply section 3 line by line. Keep only learnings that someone else could hit.
3. **Show the owner the exact text** that will be public, and the GitHub account it will come from. Change anything they ask. Send only on a yes.
4. **Fork `postscarcityai/yea`** with `gh repo fork`, branch `learnings/<YYYY-MM-DD>-<short-topic>`.
5. **Add one file**, `practices/learnings/<YYYY-MM-DD>-<short-topic>.md`, using the template in `practices/learnings/README.md`. One file per build. Do not edit `traps.md`, the README or any PRD yourself: the maintainer folds learnings in, so many builds never fight over the same lines.
6. **Commit and open the pull request** with `gh pr create`. Title: `Learnings: <short topic>`. Body: how many learnings, which parts of the reference they touch, and the stack used (framework, database, host). No business details in the title, body, branch name or commit message: they are public too.
7. **Tell the owner** the pull request link, and write it in `docs/learnings.md` so the next agent knows it was sent.

---

## 5. What happens next

A maintainer reads every pull request. A learning that holds up gets folded into `practices/traps.md`, the README or the PRD it belongs in, with a `CHANGELOG.md` entry, and the learnings file is removed. Every app built from this reference picks it up on its next spec rebase (`shared/updating.md`). That is the compounding: your snag, fixed once, for everyone after you.
