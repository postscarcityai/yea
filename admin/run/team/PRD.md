# Team (admin, Run)

- **Module key:** `team` (stable, never renamed)
- **Tier:** core
- **Route:** `/admin/team`
- **Folder:** `admin/run/team/`

## Job

"Who works here, what each person can do, and how they sign in." Team is where the Owner invites people, gives each one a user type or a named role, trims what that role can do, and cuts access the minute someone leaves. Sign-in is by emailed link or passkey; there are no passwords to manage.

The number that tells you it is working: **time from "remove this person" to every session of theirs revoked** (target under one minute), and **share of invites accepted within 7 days**.

## Users and permissions

Start from `shared/roles.md` section 4f.

| User type | Scope | Differs from the matrix how |
|---|---|---|
| Owner | all | The only type that invites, changes roles, edits grants on Roles (trim only), deactivates, and transfers ownership. |
| Admin | all, read | V only: sees members, roles, invites and sessions. Cannot invite or change anything. Can sign themselves out of other devices from the profile menu. |
| Staff, Contractor | none | Hidden. Their own profile and devices are on the profile menu, not here. |
| Customer | none | Hidden. Customer logins are People records with Portal access; they are invited from People, not Team. |
| Agent | none to write | C! only: drafts an invite for the Owner to send. It never edits a member, a role or a grant. |

- **Gated verbs for the agent:** C (draft invite) is gated and never relaxable. Any change to permissions is never relaxable and has no tool.
- **Guards:** nobody can demote or deactivate the last Owner. The Owner cannot demote themselves; ownership moves only by Transfer, which the new Owner must accept.
- **Sensitive fields:** member phone numbers and session IPs are visible to Owner only.

## Pages and states

| Tab | Route | Holds |
|---|---|---|
| People | `/admin/team` | Every admin-side user: avatar, name, email, type chip, named role, last seen, status (active, invited, deactivated). Agents appear here too, with type Agent and a link to their Agents record. |
| Roles | `/admin/team?tab=roles` | The six types and named roles. Each role opens a grid of modules by verbs with `all` or `own` and sensitive field checkboxes. The type's ceiling shows as the maximum; boxes above the ceiling are not rendered. Presets ship: Viewer, Bookkeeper, Reviewer, Sales without personal data (`shared/roles.md` section 7). |
| Invites | `/admin/team?tab=invites` | Pending invites: email, role, invited by, sent, expires, Resend, Cancel. Agent-drafted invites wait here with Approve and Change. |
| Sessions | `/admin/team?tab=sessions` | Active sessions per user: device, location, last active, Sign out. "Sign out everywhere" per user. |

- **Record view:** URL modal `?member=<id>`, read-only with Edit: name, email, phone, type, named role, status, joined, last seen, sessions, recent changes (from Log). Actions: Change role, Deactivate, Send sign-in link. Role record: `?role=<key>` URL modal with the grant grid.
- **Sign-in flow (magic link with a same-browser check):** the sign-in page asks for an email and shows "Check your email". At that moment the server sets a short-lived, HttpOnly, SameSite=Lax **sign-in cookie** in that browser holding a random nonce, and stores its hash on the `login_links` row. The emailed link lands on `/auth/[token]`, and a GET never signs anyone in by itself:
  - **Same browser** (the cookie is present and its hash matches the row): sign in at once and go straight to the page they asked for. One click, from the email.
  - **Different browser or device, or no cookie:** show one button, "Continue to sign in", and only spend the token on that POST. This second click exists only to get past email security software (link scanners, Safe Links) that opens every link in a message and would otherwise burn the token or sign a bot in.
  - Either way the token is single use, 15 minutes, and the sign-in cookie is cleared once used. The same flow serves the portal (`customer/portal/PRD.md`).
- **Invite flow:** Owner enters email, name, role. The invite email holds a one-time link (7 days). The invitee lands on a two-step welcome (confirm name, phone, title), then straight into `/admin`.
- **Empty states:** People with only the Owner: "Just you so far. Invite the first person." Invites: "No pending invites." Sessions: "No other active sessions."
- **Loading:** table skeletons. Sending an invite shows a spinner on the button; the row appears as "Sending…" then "Invited".
- **Error:** invite email bounced: the row shows "Bounced" with the reason and Edit email. Grant save that would exceed the type's ceiling is rejected with the reason.
- **Permission states:** hidden for Staff, Contractor, Customer. Admin sees everything read-only: no Invite button, no Edit, no grant checkboxes (values render as text).
- **Quick views:** People: Active, Invited, Deactivated, Agents. Sessions: Unusual location, Older than 30 days.
- **Badge count:** none.

## Data model

Shared tables (`shared/data-model.md`): `users`, `roles`, `user_roles`, `role_grants`, `sessions`, `auth_log`. Team owns `roles`, `user_roles`, `role_grants` and adds:

**`invites`**: `id`, `org_id`, `email`, `name`, `role_key`, `invited_by`, `drafted_by_agent bool`, `approval_id` null, `token_hash`, `expires_at`, `accepted_at` null, `status` (draft, sent, accepted, expired, cancelled, bounced).

**`login_links`**: `id`, `user_id`, `token_hash`, `browser_nonce_hash` null (the same-browser sign-in cookie), `purpose` (sign_in, invite, transfer), `expires_at` (15 minutes for sign-in, 7 days for invite), `used_at` null, `ip`, `same_browser bool` null (set on use, for Log).

**`sessions`** (shared): `id` (hash of the cookie token), `user_id`, `created_at`, `last_seen_at`, `expires_at` (30 days), `ip`, `user_agent`, `revoked_at` null.

**`role_grants`** (shared shape from `shared/roles.md` section 7): `role`, `module`, `verb`, `scope`, `gated`, `limit jsonb`, `fields text[]`. Seeded from the matrix. Edits can only remove rows or narrow scope below the type's ceiling.

- **Only hashes stored:** tokens and session ids are stored as hashes. No passwords by default.
- **Own scope:** not applicable (no own-scope users on this module).
- **Anchor kinds:** `member:<id>`, `role:<key>`, `invite:<id>`, `session:<id>`.
- **Config knobs:** `fields.roles` (relabel the six types, for example "Staff" to "Associates"). Sample type: `team`.

## Agent actions

| Action | Tool | Verb | Gated | Writes to `change_log` | Undo |
|---|---|---|---|---|---|
| Answer who has access to what | `query_db` on `role_grants`, `user_roles` | V | No | Nothing | n/a |
| Draft an invite | `draft_invite` | C | **Always** (`!`). Owner approves, then the invite sends | `invites` insert with `status = draft` | Cancels the draft |
| Change a role, grant or member | none | E, K | **Never.** No tool exists | n/a | n/a |

**Background jobs**

- `team.expire_links` (hourly): marks expired invites and login links.
- `team.stale_sessions` (daily): revokes sessions past `expires_at`; flags sessions idle over 30 days on the Sessions tab.
- `team.deactivate` (triggered by Deactivate): revokes every session and login link for the user in the same transaction, reassigns open Inbox threads and Board cards to the Owner (listed in one Log request so Undo can reverse it).

## Integrations

- **Email delivery** (default SendGrid): invite and sign-in link emails. These are system messages (the recipient asked or was invited), not gated sends.
- **Passkeys:** WebAuthn in the browser; no vendor needed.
- **Passwords vault** (keep list, default 1Password): shared credentials for outside systems live in the vault, never in Team. Team can hold a link to the vault per member.
- **Platform APIs:** none. **Webhooks in:** SendGrid bounce events mark an invite Bounced. **Out:** none.
- **Secrets:** `SENDGRID_API_KEY`, `SESSION_SECRET`.

## SaaS replaced

None priced in `shared/saas.md`. Seat management usually sits inside each tool a business pays for; as those tools move to YEA, their seats collapse into Team. Migration: list every person with a seat in any tool being replaced, invite each with the matching role, and remove their seat in the old tool on the day it is cancelled.

## Acceptance criteria

1. A Staff user never sees the Team nav item, and a deep link to `/admin/team?member=<id>` shows the no-access page with nothing about the member shown.
2. Every Team change (invite sent, role changed, member deactivated) appears in Log with before, after and a working Undo; an agent-drafted invite shows the agent as drafter and the Owner as approver.
3. The agent asked "invite sam@business.example as Staff" shows a draft invite with Approve and Change, and no email goes out until the Owner approves.
4. Every submit button (Send invite, Save role, Deactivate, Sign out, Transfer) shows a spinner and disables while it runs.
5. An invitee clicks the invite link within 7 days, confirms name and phone, and lands on `/admin` with only the modules their role can view.
6. An invite link used twice, or after 7 days, shows "This link has expired. Ask for a new one." and signs nobody in.
7. A Staff user asks for a sign-in link and opens it in the same browser: they are signed in with no extra click. Opening that link in a different browser shows "Continue to sign in" and signs in only after the click. A link scanner that fetches the link with GET signs nobody in and leaves the link usable.
8. The Owner deactivates a member; within one minute every session of theirs is revoked and their next request lands on the sign-in page.
9. Removing `leads.export` from the Staff role hides the Export action on Leads for every Staff user on next page load.
10. The Roles grid never renders a checkbox above the type's ceiling (a Contractor-type role has no `all` scope option).
11. The Owner cannot deactivate or demote themselves while they are the only Owner; the action is not rendered and Transfer is offered instead.
12. An Admin sees People, Roles, Invites and Sessions with no Invite, Edit or checkbox controls.
13. Relabeling Staff to "Associates" in `fields.roles` changes every chip and the Roles tab, and no grant changes.

## Open questions

1. **Sign-in method default.** Recommended: emailed magic link (15-minute, single use) with optional passkey after first sign-in. No passwords.
2. **Session length.** Recommended: 30 days sliding, revoked on deactivate or role change.
3. **Should Admin be allowed to invite Staff?** Recommended: off by default (matrix says read). The Owner can delegate it later as a limited grant if they hire often.
4. **Contractors from another company signing in with their own domain.** Recommended: same magic link flow; no single sign-on in the first build.
5. **What happens to a deactivated user's records?** Recommended: records keep them as owner for history; open threads and cards reassign to the Owner, listed in one Log request.
