# Design system: shell, left nav, record views, chips

Part of the YEA docs. Revised 2026-10-31.

One shell for every signed-in user. Owner, Admin, Staff, Contractor and Customer all see the same frame: left nav, work area, chat on the right. What changes is the nav items, the labels and the data. Build the shell once and never fork it per user type.

## 1. The shell

```
+-----------+-------------------------------------------+--------------+
| Logo      | Top bar: page title, search, chat button  |              |
|-----------+-------------------------------------------|   Chat       |
| Home      |                                           |   (right     |
| Inbox  3  |   Work area                               |   panel,     |
| GROW      |   list, record, board, chart              |   docked,    |
|  Leads 5  |                                           |   resizable) |
|  ...      |                                           |              |
| SELL      |                                           |              |
| ...       |                                           |              |
|-----------|                                           |              |
| You menu  |                                           |              |
+-----------+-------------------------------------------+--------------+
```

- **Left nav:** 240px, collapsible to a 64px icon rail. Collapse state in a cookie so the server renders it right on first paint.
- **Top bar:** page title (the module label), global search, the chat button. Always the same spot.
- **Work area:** fluid. Content max width 1280px for lists, full width for boards and maps.
- **Chat:** docked right, pushes the page, 420px default, 340px to 50vw. Spec in `shared/chat.md`.
- **Mobile (under 1024px):** nav becomes a drawer from the left behind a menu button; chat becomes a full-screen sheet from the right.

## 2. Left nav

- Order: **Home**, **Inbox**, then the groups **Grow, Sell, Make, Know, Run** (order is a config knob). Then a divider, then the **You** menu.
- One level of nesting: group, then item. Never two. Pages inside a module are tabs, not nav items.
- Render the nav from config plus permissions: a module shows only if it is enabled and the user has view. A group with no visible items disappears. No lock icons, no greyed-out items.
- **Badges** show live counts of the queue that needs a person. Same scope as the list (a Contractor's badge counts only their records). A collapsed group shows the sum of its badges.
- Active item: filled background in the brand tint plus a 2px brand bar on the left edge.
- Group labels are small caps text, not links. Clicking a group label collapses it.
- Customer side: public pages use a top nav. Signed-in customers get this same shell with portal items.

## 3. Lists

- A table or card grid, one primary action per row: the highest verb the user has on that row (Approve, Submit, Reply, Open). Never two primary buttons, never a disabled one.
- **Filters are collapsed** behind a Filter button. Saved filters are called **views** and show as quick-view chips above the list ("Needs reply", "Assigned to me", "Stuck").
- Every filter, sort and view lives in the URL, so every list is a link.
- Bulk actions: select rows, a floating action bar appears at the bottom with only the actions the user has on every selected row.
- Empty state: one sentence on what goes here, and one button to add the first one or to ask the agent.

## 4. Record views

- **Records open read-only.** An **Edit** button switches to edit mode. Fields the role cannot change render as plain text in edit mode, not as disabled inputs.
- Simple records open as a **URL modal** over the list (`/admin/leads?lead=12`). Records with tabs get a full route (`/admin/pipeline/[id]`).
- **Esc closes** a modal. Back closes it too, since it is a URL.
- **No new tabs** for anything inside the app. Links out to other sites can open a new tab.
- Layout: header (title, status chip, owner, primary action), then tabs (Overview, Activity, Files, then module tabs), then a right column with key facts.
- Every record has an **Activity** timeline that includes agent writes, each with an "Agent" byline and Undo for users with edit.

## 5. Chips

Chips are small rounded labels. Three kinds, one component.

| Kind | Used for | Look |
|---|---|---|
| **Status** | Stage or state of a record (New, Paid, Waiting on approval) | Tinted background from the status color map, text in the darker shade, no border |
| **Filter / view** | Quick views above a list | Outline when off, filled when on, an × when on |
| **Context** | Items handed to the chat | Kind icon, label truncated at 40 characters, × to remove. Hover rings the item on the page. Greyed with "not on this page" when its item is elsewhere. Spec in `shared/chat.md` |

Status color map (each module maps its stages onto these): neutral (new, draft), info (in progress, sent), warn (waiting, stuck), good (won, paid, done), bad (lost, failed, overdue).

## 6. Buttons, forms and feedback

- **Every submit button shows a spinner and disables while it runs.** No exceptions. Re-enables with an inline result.
- Disabled is only for a temporary or fixable state, and always shows a one-line reason under the button ("Add a mailing address to send").
- Every tap gets feedback: a pressed state, a spinner, or a toast. Toasts sit bottom center, last 4 seconds, and carry Undo when the action can be undone.
- Destructive actions confirm in a modal that names the record. Esc cancels.
- Forms: labels above fields, one column, inline validation on blur, the error says how to fix it.

## 7. Look

- Tight and quiet. Neutral surfaces, hairline borders (1px, low contrast), small radius (6px on controls, 10px on cards), little shadow.
- Type: one sans family. 14px body in the app, 13px in dense tables, tabular numbers in every number column.
- Spacing on a 4px grid.
- Color comes from config: `company.colors.brand` and `company.colors.accent`. Everything else is neutrals plus the five status colors. Check contrast at AA for every text and chip pairing.
- Motion: short and functional (150 to 200ms). No text animating in. Respect `prefers-reduced-motion`.
- Visuals over text: a chart, a thumbnail or a status chip beats a sentence.

## 8. Tokens

Name tokens by role, not by color, so a business can rebrand by config.

```
--bg, --surface, --surface-2, --border, --text, --text-muted,
--brand, --brand-tint, --accent,
--status-neutral, --status-info, --status-warn, --status-good, --status-bad,
--radius-control: 6px, --radius-card: 10px,
--nav-width: 240px, --nav-rail: 64px, --chat-width: 420px
```
