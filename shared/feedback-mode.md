# Feedback mode

The owner reads their own site, sees something wrong, and says so on the spot. A staff member signed in to the admin gets a round button bottom right on every public page. Tap it, tap the parts of the page you mean, write one line, save. The comment lands on the Board with everything an agent needs to find the thing and fix it, so nobody has to ask "which page? which bit? on what screen?"

It is not a module and has no nav item of its own. It is a component on the customer side (Site, Shop, Intake, Portal) that only staff ever see, and a **Feedback** tab on the Board where the comments are worked.

Runs in production on postscarcity.ai (site and admin, since 2026-11-02).

---

## 1. Who sees it

- Only a browser with a live admin session: O, A, S, C. Customers and the public never see it, never load its code and never make a request for it.
- The admin session cookie is usually scoped to the admin path (`/admin`), so the public pages can't read it. The admin sets a second cookie that is **not a credential**: `<app>_admin=1`, path `/`, same lifetime as the session, set on any signed-in admin request and cleared on sign-out.
- The site checks that cookie first. No cookie, nothing happens. With it, the site calls `GET /admin/api/site/me` (same origin, so the real session cookie rides along). `200 {ok, name}` loads the button. `401` clears the hint cookie.
- The button's code is lazy-loaded only after `me` says yes, so public visitors pay zero bytes.
- This needs the site and the admin on one origin (the admin served at `/admin` on the business's own domain). Never a subdomain: the session cookie would not reach the site's requests.

## 2. The button and the panel

- **FAB bottom right**, 52px round, dark ink, a speech bubble icon. A small accent badge shows how many open comments exist on this page.
- On admin screens the chat FAB owns bottom right (`shared/chat.md` section 2). Feedback mode only renders on customer-side pages, so the two never meet.
- Tap the FAB: a compact panel opens above it (340px, full width minus 32px on phones) and **picking turns on**. Tap the FAB again or press **Esc** to close. Picks and the draft are kept on close, so reopening picks up where you left off.
- Panel, top to bottom: title and the current path, a **Picking** toggle (off = use the page normally: links work, forms take input), the picked list, the comment box, a note line, "N open on this page" (expands to the list, each one links to its record), and a footer with the signed-in name, the pick count and **Save**.
- **Save** shows a spinner and "Saving…", stays disabled until the request returns, and is disabled while the box is empty. Cmd/Ctrl+Enter saves. Success shows "Saved #12. Open in admin" and clears the picks and the box; the panel stays open for the next one.

## 3. Picking

- While picking, the cursor is a crosshair. Hover outlines the element under the pointer (dashed accent, with a label tag above it). Tap or click picks it: a solid accent outline with a numbered dot. Tap a picked element again to drop it. Up to 12 per comment.
- **Taps on the page are swallowed** while picking (pointerdown, mousedown and click, in the capture phase), so links, buttons and forms don't fire. Scrolling is never blocked: scroll, notice, tap, keep scrolling.
- Outlines follow their elements on scroll, resize and animation (re-measured every frame while anything is picked or hovered).
- **What counts as a part of the page.** Inline text bits (`span`, `strong`, `em`, `code`...) resolve to their nearest box. SVG internals (`path`, `g`, `circle`...) resolve to their `svg`. Anything under 4px resolves to its parent. The panel itself (`data-fb-ui`) is never picked.
- **The key div, not its text.** On desktop, ↑ while hovering widens to the box around it: the nearest ancestor that is visibly bigger, skipping same-size wrappers. ↓ walks back. On touch there is no hover, so each picked row in the panel has a **Wider** button that does the same.
- A new page (client-side navigation) drops the picks; their elements are gone.

## 4. What a comment saves

Enough to find it in the code and see it the way the owner saw it, with no follow-up question.

| Field | What |
|---|---|
| `body` | The comment, up to 5,000 characters. |
| `url`, `path`, `page_title` | Full URL with query, the path alone (for "open on this page"), `document.title`. |
| `targets[]` | Per picked element: `selector`, `tag`, `label`, `section`, `text`, `rect`, `html`. |
| `context` | `viewport` (w, h, devicePixelRatio), `scrollY`, `theme` (color scheme plus any site mode), `ua`, `build` (the deployed commit SHA, passed from the server at render), `referrer`. |
| `status` | `open`, `fixed` or `wontfix`. |
| who and when | `created_by`, `created_at`, `resolved_by`, `resolved_at`, `resolution` (what was done). |

Per target:

- **`selector`**: the shortest CSS selector that matches exactly that element, at least three steps deep so it survives small edits. Starts from the nearest unique `id`, else the body. Each step is the tag, up to two semantic class names (utility classes like Tailwind's are skipped: they say how it looks, not what it is), `[data-section="..."]` when present, and `:nth-of-type()` when siblings share the tag.
- **`label`**: a human name, kind plus content. `Heading 1: Do more with Agents.` `Image: Team at the whiteboard.` `Button: Book a call.` `Block: ...` for the rest.
- **`section`**: the section it sits in, by `data-section`, `id`, `aria-label` or its first heading. Agents search the code for this first.
- **`text`**: the element's visible text, up to 400 characters. **`html`**: its outer HTML, whitespace collapsed, up to 1,200 characters.
- **`rect`**: x, y, width, height in page pixels (scroll included), at the moment of saving.

No screenshot in v1. The viewport, scroll position and rect reproduce the view; WebGL and canvas pages don't survive DOM-to-image capture anyway.

## 5. Where it lands: the Board

- Each save writes one `feedback` row and logs `feedback.create` to the activity log. The Board gets a **Feedback** tab (badge: open count) listing them newest first. Segmented control: **Open, Fixed, Won't fix, All**, each with its count.
- One row per comment: avatar of who left it, first line of the comment, the path and "2 elements", page title, status pill, age, one **Open** button.
- Record view is a URL modal, `?f=<id>`, read-only (`shared/design-system.md` section 4). Header: number, status, who and which page. Action bar: **Mark fixed** (primary) and **Won't fix** while open, **Reopen** after; **Copy for agent**; **Open page** (new tab, it leaves the app). Body: the comment, the resolution if any, then the picked elements as numbered cards with label, section, text and selector. Side column: page link, title, screen, scroll, theme, build, when it was left and when it was resolved.
- **Copy for agent** copies a plain-text brief: page, title, viewport, build, the comment, then each element's label, selector, section, text and box. Paste it into a card or a chat and the agent has everything.
- Fixing stamps who and when; reopening clears both.

## 6. API

Both routes live under the admin and answer JSON. The admin's sign-in middleware lets `/api/site/*` through so a signed-out call gets a `401`, not a redirect to the sign-in page.

- `GET /admin/api/site/me` → `200 {ok: true, name}` or `401 {ok: false}` (and clears the hint cookie).
- `GET /admin/api/site/feedback?path=/pricing` → `{ok, open: [{id, body, created_at}]}`, the open comments on that path, newest first, 20 max.
- `POST /admin/api/site/feedback` with `{body, url, title, targets, context}` → `{ok, id}`. Refused with `403` when the `Origin` header isn't this host. `400` without a body or a parseable URL. Every field is cut to the lengths above on the server; unknown fields are dropped.

## 7. Data

```sql
create table feedback (
  id          serial primary key,
  tenant_id   int not null references tenants(id) on delete cascade,
  body        text not null,
  url         text not null,
  path        text not null,
  page_title  text,
  targets     jsonb not null default '[]',
  context     jsonb not null default '{}',
  status      text not null default 'open' check (status in ('open', 'fixed', 'wontfix')),
  created_by  int references users(id) on delete set null,
  resolved_by int references users(id) on delete set null,
  resolved_at timestamptz,
  resolution  text,
  created_at  timestamptz not null default now()
);
create index feedback_open on feedback (tenant_id, status, created_at desc);
create index feedback_path on feedback (tenant_id, path);
```

Anchor kind for the chat: `feedback:<id>`.

## 8. Agent

- Reads open feedback, finds each target in the code by section, selector and text, fixes it, ships it, checks the live URL, then marks it fixed with the resolution (what changed, the commit, the URL). Marking fixed is not gated; the owner can reopen.
- Never marks something fixed it hasn't verified on the live page.
- Won't fix needs a reason in the resolution, and the owner's yes when the comment came from the owner.

## 9. Acceptance criteria

1. A public visitor (no hint cookie) loads any page: no feedback request is made and the button's code is not downloaded.
2. An Owner signed in to the admin opens any public page: the button shows bottom right within a second of load.
3. The Owner signs out of the admin, then reloads a public page: no button.
4. With the panel open, the Owner clicks a link on the page: nothing navigates, the link's box is picked and numbered.
5. The Owner scrolls 2,000px with three elements picked: each outline stays on its element.
6. On desktop, hovering a word inside a heading outlines the heading. ↑ outlines the block around it. A click picks that block.
7. On a phone, a tap picks the element under the finger, and **Wider** on its row swaps in the box around it.
8. Save with an empty box is disabled. Save with text shows "Saving…", then "Saved #N"; the row is on the Board's Feedback tab with the comment, URL, viewport, scroll, build and every picked element's selector, label, section, text and box.
9. Every saved selector, run with `document.querySelectorAll` on the same build and viewport, matches exactly one element: the one that was picked.
10. Reopening the panel on the same page shows "1 open on this page", linking to that record.
11. **Copy for agent** puts a brief on the clipboard that names the page, the comment and each element's selector.
12. **Mark fixed** shows a spinner, then the record reads Fixed with who and when, and the page's open count drops by one.
13. A `POST` from another origin gets `403` and saves nothing.

## 10. Build split

- **Admin:** the `feedback` table, the two routes, the hint cookie in middleware and sign-out, the Board's Feedback tab and record modal, and the activity entries.
- **Site:** a gate component in the root layout (hint cookie, `me`, lazy load, server-passed build SHA) and the feedback component itself (portal into `body`, inline styles so the site's CSS can't touch it, highest z-index on the page).
- Local dev: the site's `/admin` rewrite takes its target from an env var (`ADMIN_ORIGIN`), so both apps run side by side.
