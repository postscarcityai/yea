# Security: the basics

Part of the YEA docs. Revised 2026-11-03. Do these. Don't build more until something real calls for it.

1. **Nothing shared between businesses.** Each one has its own repo, database, hosting and keys, so a break-in at one can't reach another.
2. **The app's database login is not the owner.** It can't bypass row rules or rewrite the log. The owner login is for migrations.
3. **Agents get no database login.** They reach data through the app's tools, under a role.
4. **Nothing leaves the organization without a person's yes** (`shared/roles.md` section 5). Agents read email and web pages, and any of them can carry hostile instructions.
5. **Run `conformance/` in CI** on every change and nightly. A new advisory can break an app nobody touched.
6. **Turn on automated dependency updates.** Patch releases merge once checks pass.
7. **Vendors hold access per client,** and drop it at hand-over. A critical fix ships first, and the owner hears right after.
