# Security across many apps

Part of the YEA docs. Written 2026-11-03. Every app has its own repo, its own database and no upstream, so nobody can patch them all at once. This page is how security holds anyway. `conformance/` runs today. The rest is direction, not yet proven.

---

## 1. Keep the damage small

Separate apps are the best security property YEA has. A break-in at one business can't reach another, as long as nothing joins them.

- **Nothing shared.** Each business gets its own database login, model keys, deploy tokens and agent tokens. Never reuse a key across two apps.
- **The vendor is the weak point.** A machine or account that holds every client's keys undoes the separation. Hold access per client, make it expire, and drop it at hand-over. Use a scoped app or token per repo, not one person's login.
- **No database login on an agent's machine.** Agents reach data through the app's tools, under a role.
- **The app's own login is not the owner.** `conformance/` checks this.

---

## 2. Test behavior, on every deploy

Nobody reads the code, so run `conformance/` in CI on every change and on a nightly schedule. The nightly run matters: a new dependency advisory can break an app nobody touched. A failure opens a Board card.

---

## 3. Advisories don't wait for the check-in

The monthly check-in in `shared/updating.md` is too slow for a live hole. A security fix here also ships as an advisory:

- **What it says:** severity, who is affected, how to fix it in words, since code differs per app.
- **A check that proves it.** Each advisory adds a check to `conformance/`, so an app can tell whether it is exposed and whether the fix worked.
- **Agents look daily,** not monthly. Exposed means fix it now.
- **Critical fixes ship, then tell the owner.** Waiting on a video yes leaves the hole open. Everything else goes through the normal gate.

---

## 4. Dependencies update themselves

Turn on automated dependency updates in every repo. Patch releases merge by themselves if CI and conformance pass. Major versions go through the normal gate.

---

## 5. One list of every app

A vendor running many apps keeps one private register: the app, the reference commit from `yea.lock.json`, the last conformance result and the date. CI reports those few fields and nothing from the business's data. It answers "who is exposed?" in one query. After hand-over, reporting continues only if the business agrees.

---

## 6. Treat what agents read as hostile

An agent reads email, web pages and customer messages, and any of them can carry instructions. The defense is the rule that already exists: the agent acts as a role, and nothing leaves the organization without a person's yes (`shared/roles.md` section 5). Don't relax it for inbound-triggered work.
