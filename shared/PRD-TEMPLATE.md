# PRD template

Every module folder holds one `PRD.md` with these nine headings, in this order. Write it so an agent with no other context can build the module from the PRD plus the files in `shared/`.

Copy everything below the line into a new `PRD.md`.

---

# <Module label> (<admin or customer>, <group>)

- **Module key:** `<key>` (stable, never renamed)
- **Tier:** core, common or industry
- **Route:** `/admin/<key>` or the customer path
- **Folder:** `admin/<group>/<key>/`

## Job

One or two sentences. What this module does for the business, in the owner's words. Then the one number that tells you it is working (for example "median time to first reply on a new lead").

## Users and permissions

- Which user types see it, and their scope (all or own). Start from the matrix in `shared/roles.md`; only write what differs.
- Gated verbs for the agent, and any per-module relax with its limit.
- Sensitive fields (column-level grants).

## Pages and states

- Tabs in nav order, each with its route (tabs are sub-routes, so every view is a link).
- Record view: URL modal (`?<kind>=<id>`) or full route (`/[id]`), and its tabs.
- For each page: empty, loading, error, and permission states (hidden, read-only, disabled with reason). See `shared/design-system.md`.
- Quick views and filters that ship by default, and the query param each one writes (`?status=open&sort=-created`).
- Badge count: what it counts.

## Data model

- Tables with columns and types, owned by this module.
- Foreign keys into shared tables (`people`, `companies`, `change_log`, `files`). See `shared/data-model.md`.
- Row rules for `own` scope.
- Anchor kinds this module renders for the chat (`lead:<id>`, `field:lead:<id>.<field>`). See `shared/chat.md`.
- Config knobs (`fields.*`) and the sample data type that seeds it.

## Agent actions

A table: action, tool name, verb, gated or not, what it writes to `change_log`, Undo behavior. Include the background jobs (scheduled or triggered) and what they produce.

## Integrations

- Rails it plugs into (hosting, database, email delivery, SMS, payments, domains, banking, payroll tax, DNS, passwords). Name the default and the contract, not just the vendor.
- Platform APIs it needs (a social network, a search engine, an ad platform).
- Webhooks in and out.
- Secrets it needs, by name only.

## SaaS replaced

Products from `shared/saas.md` this module replaces, with their risk label (No brainer, Easy, Plan it, Careful) and the migration step for each: export, import, parallel run, cutover, cancel.

## Acceptance criteria

Numbered, testable statements. Each one names the user type, the action and the visible result. Include at least:

1. A user without the view verb never sees the nav item, and a deep link shows the no-access page.
2. Every agent write appears in Log with before, after and a working Undo.
3. A gated agent action waits for a human yes and shows exactly what will happen.
4. Every submit button shows a spinner and disables while it runs.
5. Every tab, filter, sort, search and open record is in the URL: refresh, or paste the link in another browser, and the same view comes back.

## Open questions

Anything the builder must decide or ask the owner. Each with a recommended default, so a build never stalls on it.
