# Settings (admin, Run)

- **Module key:** `settings` (stable, never renamed)
- **Tier:** core
- **Route:** `/admin/settings`
- **Folder:** `admin/run/settings/`

## Job

"The business, the brand and the switches, in one place." Settings holds what the whole app reads: the business's name and hours, the brand the agent writes in, which modules are on and what they are called, the channels and senders messages go out through, checkout rules, and data hygiene (do not contact, merges, trash, retention). Every module's own knobs sit on that module's last tab; Settings holds the ones that cross modules.

The number that tells you it is working: **setup completeness** (share of the required settings filled: business, brand, one verified sender, one channel, checkout when Shop or Orders is on), shown as a checklist until it reaches 100 percent.

## Users and permissions

Start from `shared/roles.md` section 4f.

| User type | Scope | Differs from the matrix how |
|---|---|---|
| Owner | all | Every tab. Only type that can switch modules on or off, and change payment, banking and domain rail connections. |
| Admin | all but Modules and rails | V E K on Business, Brand, Channels (not rail credentials), Email (not domain records), Checkout (not the payment connection), Data. Sees Modules read-only. |
| Staff, Contractor | none | Hidden. |
| Customer | own | Not this module. Their account and email preferences live on Portal Account. |
| Agent | as its role | V to answer questions. Every change is E!: it drafts the change and waits for a human yes, every time, never relaxable. |

- **Gated verbs for the agent:** all writes (`!`, never relaxable, `shared/roles.md` section 5 rule 7).
- **Sensitive fields:** rail credentials are never shown after save (last 4 characters only), never sent to the agent, never written to `change_log` values (logged as "changed").

## Pages and states

| Tab | Route | Holds |
|---|---|---|
| Business | `/admin/settings` | Name, legal name, industry, address, time zone, hours, phone, response target, logo, the public URL. |
| Brand | `/admin/settings?tab=brand` | Colors (brand, accent), fonts, logo variants, voice notes (how the business writes: words to use, words to avoid, sign-off), sample paragraphs. The agent's system prompt reads this tab. |
| Modules | `/admin/settings?tab=modules` | Every module with on or off (core shows "Always on"), label, group, nav order, tier chip. Group order and labels. Owner only to change. |
| Channels | `/admin/settings?tab=channels` | Connected channels: email domain, SMS numbers and their registration status, web chat on the Site, social accounts for DMs and posts. Connect and disconnect. |
| Email | `/admin/settings?tab=email` | Senders and aliases, domain authentication records (SPF, DKIM, DMARC) with live check, mailing address for bulk mail, default signature, unsubscribe footer. |
| Checkout | `/admin/settings?tab=checkout` | Payment connection, currency, tax rates, shipping rules, order email templates. Shown when Shop, Orders or Money is on. |
| Data | `/admin/settings?tab=data` | Do not contact list, merges (people and companies), Trash (30 days), retention, legal hold, full data export, sample data load or clear. |

- **Record view:** none. Each tab is a form that opens read-only with an Edit button per section (Business, Address, Hours). Save per section.
- **Agent change cards:** when the agent proposes a change, the section shows a pending banner ("Agent wants to change hours: Sat 9 to 1 to closed. Approve or Change.") and the same row is on Home > Today.
- **Empty states:** Channels, none connected: "Connect email first. Every other channel can wait." Data > Do not contact: "No one on the list." Trash: "Trash is empty."
- **Loading:** form skeletons per section. Domain record check shows a spinner per record.
- **Error:** a failed save keeps the edited values and shows the reason under the field. A failed domain check lists which record is missing and the exact value to add.
- **Permission states:** hidden for Staff, Contractor, Customer. Admin sees Modules as a read-only table (no switches rendered). Rail connection buttons are not rendered for Admin. Disabled only for fixable states ("Verify the domain to send from this address").
- **Quick views:** Data tab lists only: Trash by module, Do not contact by source.
- **Badge count:** none in the nav. The Settings item shows a dot while setup completeness is under 100 percent (Owner and Admin).

## Data model

| Table | Columns | Notes |
|---|---|---|
| `tenant` | maps to `orgs` (`shared/data-model.md`): `name`, `legal_name`, `industry`, `url`, `address jsonb`, `timezone`, `hours jsonb`, `phone`, `response_target_minutes` | One row |
| `brand` | `org_id`, `colors jsonb`, `fonts jsonb`, `logo_file_ids jsonb`, `voice jsonb` (`{ use: [], avoid: [], signoff, samples: [] }`) | One row |
| `module_config` | `org_id`, `key`, `enabled`, `label`, `group`, `position`, `fields jsonb`, `sample` | One row per module, the ModuleConfig from `shared/modules.md` section 5. Source of truth; `orgs.config` is rebuilt from these rows in the same transaction on every save |
| `channels` | `id`, `org_id`, `kind` (email, sms, web_chat, dm), `provider`, `external_id`, `status` (connected, pending, failed), `registration jsonb`, `credential_ref` | `credential_ref` points at a secret, never the secret |
| `sender_settings` | `id`, `org_id`, `address`, `display_name`, `domain`, `verified bool`, `mailing_address`, `default bool` | Shared with Inbox and Campaigns |
| `tax_rates` | `id`, `org_id`, `region`, `rate_bps`, `applies_to` | Basis points, never floats |
| `shipping_rules` | `id`, `org_id`, `name`, `match jsonb`, `price_cents`, `currency` | |
| `do_not_contact` | `id`, `org_id`, `person_id` null, `value` (email or phone), `reason`, `added_by`, `at` | Every sender checks it alongside `suppressions` |
| `merges` | `id`, `org_id`, `kind` (person, company), `kept_id`, `merged_id`, `before jsonb`, `merged_by`, `at` | Undo restores `merged_id` |

- **Own scope:** not applicable (no Staff, Contractor or Customer access).
- **Anchor kinds:** `setting:<key>` (for example `setting:business.hours`, `setting:modules.leads.label`), `field:setting:<key>.<field>`.
- **Config knobs:** none of its own (it holds everyone else's). Sample type: `settings`.

## Agent actions

| Action | Tool | Verb | Gated | Writes to `change_log` | Undo |
|---|---|---|---|---|---|
| Answer a question about a setting | `get_record`, `query_db` | V | No | Nothing | n/a |
| Point at a setting on the page | `navigate`, `highlight` | UI | No | Nothing | n/a |
| Propose a change (hours, label, brand voice, tax rate) | `propose_setting` | E | **Always** (`!`) | On approval: before, after | Restores the before value |
| Propose a module on or off | `propose_setting` | E on Modules | **Always**, and only the Owner can approve | On approval: `module_config.enabled` before, after | Switches it back |
| Add to do not contact | `update_record` on `do_not_contact` | E | **Always** | insert | Removes the row |
| Propose a merge | `propose_merge` | E | **Always** | On approval: `merges` row plus record changes | Splits the records back |
| Check domain records | `check_domain` | V | No | Nothing | n/a |

**Background jobs**

- `settings.domain_check` (daily, and on demand): checks SPF, DKIM and DMARC for every sender domain; a failure puts an item on Home > Now and marks the sender unverified (sends from it stop).
- `settings.trash_purge` (daily): hard-deletes Trash older than 30 days, logged without content.
- `settings.config_compile` (on every save): rebuilds `orgs.config` from `module_config` and busts the nav cache.

## Integrations

- **Domains and DNS** (default: whatever registrar and DNS host the business uses; contract: the app shows the exact records to add and verifies them by lookup; it never needs registrar credentials).
- **Email delivery** (default SendGrid): domain authentication and sender verification through its API.
- **SMS** (default Twilio): number purchase and registration status, read through its API.
- **Payments** (default Stripe): connected account and webhooks. YEA never sees a card number.
- **Platform APIs:** social account connections (OAuth) used by Inbox and Social.
- **Webhooks in:** payment provider events are received by Money and Orders, not Settings. Settings only stores the connection.
- **Secrets:** stored in the host's secret store or a team vault (1Password is on the keep list), referenced by name: `SENDGRID_API_KEY`, `TWILIO_AUTH_TOKEN`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `SOCIAL_CONNECTOR_KEY`.

## SaaS replaced

None. Settings replaces no product in `shared/saas.md`. It holds the connections to the rails YEA keeps (hosting, database, email delivery, SMS, payments, domains, DNS, banking, payroll tax, passwords).

## Acceptance criteria

1. A Staff user never sees the Settings nav item, and a deep link to `/admin/settings` shows the no-access page with Request access.
2. Every agent change to a setting, once approved, appears in Log with before, after and a working Undo; secret values show only as "changed".
3. An agent asked "change our Saturday hours to closed" shows the exact change with Approve and Change, on the Settings page and on Home > Today, and nothing changes until a human approves; there is no switch anywhere that lets it skip the yes.
4. Every submit button (Save section, Connect, Check records, Approve) shows a spinner and disables while it runs.
5. An Admin opens Modules and sees every module with its state as text, with no switches rendered.
6. The Owner switches Reviews off; the Reviews nav item disappears for every user on next page load, and a deep link to `/admin/reviews` shows the no-access page.
7. The Owner relabels Leads to "Inquiries"; the nav, page title and chat references read "Inquiries" and `/admin/leads` still works.
8. A sender whose DKIM record is missing shows "Not verified" with the exact record to add, and sends from that address are blocked with that reason.
9. Adding an email to Do not contact stops every Outreach and Campaign send to it, shown as "dropped: do not contact" in the send preview.
10. Merging two people keeps one record with both histories; Undo splits them back with their original fields.
11. A stored payment key shows only its last 4 characters after save and never appears in chat page context.
12. The setup checklist reaches 100 percent only when business, brand, one verified sender and one channel are set, and the Settings dot disappears.

## Open questions

1. **Can the Owner delegate Modules to an Admin?** Recommended: no. Switching a module on or off changes what every user sees and what the agent can touch; it stays Owner only.
2. **Where do module-specific knobs live, here or on the module?** Recommended: on the module's own last tab (Configure). Settings > Modules only holds on or off, label, group and order.
3. **Brand voice source.** Recommended: filled during onboarding from the owner interview (`docs/interview.md`) plus three sample paragraphs the owner approves.
4. **Full data export format.** Recommended: one zip of CSV per table plus the `files` objects, Owner only, logged on Log > Exports.
5. **Legal hold.** Recommended: an Owner-only switch on Data that pauses retention purges for chosen modules until switched off.
