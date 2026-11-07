# Design system: shell, left nav, record views, chips

Part of the YEA docs. Revised 2026-11-02.

One shell for every signed-in user. Owner, Admin, Staff, Contractor and Customer all see the same frame: left nav, work area, chat on the right. What changes is the nav items, the labels and the data. Build the shell once and never fork it per user type.

## 0. Rules that hold on every page

1. **The URL is the state.** A user can refresh or paste the link at every key point and land on exactly the same view: the tab, the open record, the filters, the sort, the search, the page of results, the quick view, the chat panel and its thread. If a person can change it and would want to share it, it goes in the query string. Filter and sort in the URL are required on every list, no exceptions. Use `replace` for keystroke-level changes (typing in search) and `push` for deliberate ones (opening a record, switching a tab), so Back does what people expect.
2. **Layout state the server must know goes in a cookie,** not local storage: nav collapsed or not, chat open and its width, the theme. The server reads it and renders the first paint right, with no flash and no jump.
3. **First-party tracking only.** No Google Analytics, no third-party tags by default. The app sets its own first-party cookie and writes its own page views. See `admin/know/insights/PRD.md`.
4. **Light and dark on both sides.** The public site and the back office each have a theme switch. Defaults differ: **light for the marketing site, dark for the back office.** See section 7.
5. **Sign out is never loose on the page.** It lives in the profile menu only (section 2a).

## 1. The shell

```
+-----------+-------------------------------------------+--------------+
| Logo      | Top bar: page title, search               |              |
|-----------+-------------------------------------------|   Chat       |
| Home      |                                           |   (right     |
| Inbox  3  |   Work area                               |   panel,     |
| GROW      |   list, record, board, chart              |   docked,    |
|  Leads 5  |                                           |   resizable) |
|  ...      |                                           |              |
| SELL      |                                           |              |
| ...       |                                           |              |
|-----------|                                     (FAB) |              |
| [CJ] Name v                                           |              |
|      Role |                                           |              |
+-----------+-------------------------------------------+--------------+
```

- **Left nav:** 240px, collapsible to a 64px icon rail. Collapse state in a cookie so the server renders it right on first paint.
- **Top bar:** page title (the module label), global search. No sign-out, no profile, no theme switch up here (those live in the profile menu).
- **Work area:** fluid. Content max width 1280px for lists, full width for boards and maps.
- **Chat:** docked right, pushes the page, 420px default, 340px to 50vw. Summoned by the round **FAB bottom right** or **Cmd/Ctrl+J**. Spec in `shared/chat.md`.
- **Mobile (under 1024px):** nav becomes a drawer from the left behind a menu button; chat becomes a full-screen sheet from the right.

## 2. Left nav

- Order: **Home**, **Inbox**, then the groups **Grow, Sell, Make, Know, Run** (order is a config knob). Then a divider, then the **profile** block pinned to the bottom (section 2a).
- One level of nesting: group, then item. Never two. Pages inside a module are tabs, not nav items.
- Render the nav from config plus permissions: a module shows only if it is enabled and the user has view. A group with no visible items disappears. No lock icons, no greyed-out items.
- **Badges** show live counts of the queue that needs a person. Same scope as the list (a Contractor's badge counts only their records). A collapsed group shows the sum of its badges.
- Active item: filled background in the brand tint plus a 2px brand bar on the left edge.
- **Only one top-level group is open at a time.** Opening a group closes the one that was open (an accordion). On load, the group holding the current page is the open one. Clicking the open group's label closes it.
- Group labels are the same size and case as the items under them, **one weight step bolder** (for example 600 over 500). Very slightly bolder, not a heading. They are toggles, not links.
- Customer side: public pages use a top nav. Signed-in customers get this same shell with portal items.

### 2a. Profile block and menu

- Always at the bottom of the left nav, on every signed-in page, admin and portal.
- One row: avatar (photo if set, **initials by default** on a brand-tint circle), then name on top and role underneath in muted text, then a **caret on the right**.
- Clicking anywhere on the row opens a popup menu above it. Esc or a click outside closes it. Arrow keys move through it.
- Menu items, in order: **My account**, **Dark mode** (one row with an on/off switch, never a multi-option selector), **Terms**, **View site** (admin) or **Back to the site** (portal), **Switch view** (demo only), divider, **Sign out**.
- **Sign out lives here and nowhere else.** Never a loose button or icon in the left nav, on the dashboard, in the top bar or in a page header. A build with sign out in the open is not done.
- On the 64px icon rail the block shrinks to the avatar; the menu opens the same way.

## 3. Lists

- A table or card grid, one primary action per row: the highest verb the user has on that row (Approve, Submit, Reply, Open). Never two primary buttons, never a disabled one.
- **Filters are collapsed** behind a Filter button. Saved filters are called **views** and show as quick-view chips above the list ("Needs reply", "Assigned to me", "Stuck").
- Every filter, sort, search, page and view lives in the URL, so every list is a link and a refresh changes nothing (section 0).
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
- Color comes from config: `company.colors.brand` and `company.colors.accent`. Everything else is neutrals plus the five status colors. Check contrast at AA for every text and chip pairing, in both themes.
- **Themes.** Light and dark on both sides. Defaults: **light on the public marketing site, dark in the back office** (admin and portal). The user's pick (light or dark) is saved in a cookie per side, so the server renders the right theme on first paint with no flash. The public site has a small switch in the footer; the back office has it in the profile menu. Brand colors get a dark-theme variant checked at AA, not just the light one reused.
- Motion: short and functional (150 to 200ms). No text animating in. Respect `prefers-reduced-motion`.
- Visuals over text: a chart, a thumbnail or a status chip beats a sentence.

## 8. Tokens

Name tokens by role, not by color, so a business can rebrand by config. Every token has a light and a dark value, switched by `data-theme` on `<html>`.

```
--bg, --surface, --surface-2, --border, --text, --text-muted,
--brand, --brand-tint, --accent,
--status-neutral, --status-info, --status-warn, --status-good, --status-bad,
--radius-control: 6px, --radius-card: 10px,
--nav-width: 240px, --nav-rail: 64px, --chat-width: 420px
```
