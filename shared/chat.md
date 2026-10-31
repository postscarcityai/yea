# The chat panel

The chat lives on the right side of every signed-in screen, admin and portal. It is not a page and has no nav item. It can see what is on the screen, the user can hand it anything on the page, and it can point back at the page and change what is there.

One rule over everything: **the left is the data, the right is the agent, and the anchor is the contract between them.** If a thing on the page has an anchor, the user can hand it to the agent, and the agent can point back at it.

This pattern runs in production in two separate apps today. Everything below marked **new** is an addition for YEA that neither had.

---

## 1. The anchor contract

- Every row, card, field and section a user might ask about renders `data-anchor="<kind>:<id>"` and `data-anchor-label="<short human label>"`. Optional `data-anchor-ctx` carries extra text the agent should get (for example a row's hidden columns).
- One helper renders the attributes: `anchor(kind, id, label, ctx?)`.
- Ids come from the database. Items stored inside a JSON column get a content-hash key, never a list position, so sorting never shifts ids.
- Field-level anchors use `field:<kind>:<id>.<field>` (for example `field:lead:12.email`).
- Server-rendered record pages include a hidden page marker (`<span data-chat-page>`) with the record label and related ids. The deepest marker on the page wins.
- `data-no-chat-pick` opts an element out.
- Every module PRD lists its anchor kinds. The full list is in `shared/modules.md` under each module.

## 2. Open and close

- A chat button in the top bar, always in the same spot. **Cmd/Ctrl+J** toggles. Ctrl+/ is the fallback where the browser keeps Ctrl+J.
- **Esc closes.** Respect `defaultPrevented`, so Esc inside a modal closes the modal first and a second Esc closes the chat. When chips exist and the composer is focused, the first Esc blurs the composer and the second closes. Chips are kept on close.
- Opening focuses the composer.
- **Desktop (1024px and up):** docked right, pushes the page (no overlay). Default 420px, drag-resizable from 340px to half the viewport, arrow keys on the edge step 24px, double-click the edge resets. Open state and width live in a cookie the server reads, so a reload lands already sized with no layout jump.
- Drawer state is also in the URL (`agent_panel`, `agent_thread`), so a pasted link opens the same view.
- When closed, nothing floats over the page on desktop. The top bar button is the way in.

## 3. Select mode

- **Select mode is on whenever the chat is open.** No separate toggle. The empty chat shows one tip line: "Click any row or card to bring it in. Select text to quote it."
- **Hover:** a soft ring on the innermost anchored element only (`[data-anchor]:hover:not(:has([data-anchor]:hover))`), `cursor: copy`.
- **Click:** toggles the element into the composer as a chip. Links, buttons and fields inside a card keep working. A card that is itself one big link gets selected instead of followed while the chat is open.
- **Shift+click** on a table row selects the range from the last picked row. **New.**
- **Add all** in a table header (only while the chat is open) adds the visible rows up to the cap. If the table holds more than the cap, it adds one `query:` chip carrying the current filter instead ("Orders: paid, last 7 days, 214 rows"), and the agent reads the rows itself. **New.**
- **Text:** select 3 or more characters anywhere on the page and an "Ask" button floats above the selection. Clicking it adds a quote chip and opens the chat if it is closed. The float hides on scroll and never appears in inputs or editors.
- Selected elements keep a visible ring on the page while the chat is open.
- **Cap:** 12 chips plus one `query:` chip. The oldest drops off with a short "Removed oldest" note.

## 4. Chips

- Chips sit in a row above the composer: a kind icon, the label (truncated at about 40 characters), and a remove button.
- **Hover a chip:** its element on the page gets the ring and scrolls into view. **Click a chip:** navigates to it if it lives on another page.
- Quote chips show the quote in curly quotes.
- **Chips survive navigation** through `?ctx=a,b`. On a new page, element chips whose cards are not present stay in the composer, greyed, with "not on this page". The chip's stored text still goes to the agent. A user often picks a customer on one page and an invoice on another and asks about both. **New** (the earlier versions dropped them).
- After send, the chips move into the sent message as small read-only chips, so the thread shows what each question was about.

## 5. What the agent receives

Every turn, ahead of the user's text:

```
<page_context>{
  path, kind, tab, record_ids, label,
  view: { ...every query param: filters, sort, search, focused record },
  visible: [{ anchor, text }],               // up to 40 anchored elements in the viewport, innermost only, 150 chars each
  pills:   [{ anchor, kind: "element" | "quote" | "query", label, text }]   // up to 12 + 1 query
}</page_context>
```

System prompt rule: "this", "these" and "here" mean the chips first, then the record on screen, then the visible anchors.

Photos: the composer accepts photos (a business card, a badge, a receipt, a damaged part). Shrink them in the browser to 1600px on the long edge and send them as image blocks.

The agent also gets an `<access>` note when the user is read-only, so it does not offer edits it cannot make.

## 6. What the agent can do

1. **Read** any selection in full through tools. `get_record(anchor)` resolves any `kind:id`. The chip text is a preview, not the source of truth.
2. **Act** on it: edit fields, change status, move a card, log an activity, draft an email to the selected people, build a view or chart from the selected rows. Every write goes through `can()` for the signed-in user, lands in `change_log` with before and after, and gets Undo in the Changes tab. Bulk edits over 5 records, money changes and anything ambiguous: the agent states exactly what it will change and waits for a yes. See `shared/roles.md` section 5.
3. **Point back at the page** with three typed UI events:
   - `navigate { href, anchor }`: route there, wait for the anchor to render (up to 6 seconds), open any folded section, clear a filter that hides it, scroll it to center, pulse it.
   - `highlight { anchors[], color: "gold" | "red" | "green" | "blue", label }`: outline rows and cards with a caption ("3 overdue"). Private to this user, cleared on refresh.
   - `changed { change_ids, items: [{ anchor, op }] }`: removed rows collapse out, the page re-renders with fresh data, changed rows flash.
4. **Cite** with chips back to anchors. In the reply text: `[[order:1042|Order 1042]]`. Clicking one navigates and pulses.
5. **Draw a chart** inline in the reply. Any chart can be pinned to Views as a tile (the tile stores its read-only query).

**Identity.** The agent always acts as the signed-in user, never as a superuser. Two checks: role permissions in the tool layer, and row rules in the database, so `own` scope holds even if a tool is wrong.

## 7. Tools

Every module PRD lists its tools under **Agent actions**, split three ways:

| Kind | Examples | Gate |
|---|---|---|
| Read | `query_db` (read-only role, sensitive columns stripped for this user), `describe_schema`, `get_record`, `search`, module summaries | Needs View on the module |
| Write | `update_record`, `log_activity`, `move_card`, `draft_email`, `add_to_view`, `file_request`, `hand_off`, `undo_change` | Needs the verb on the module. Logged. Gated per `shared/roles.md` |
| UI | `navigate`, `highlight`, `show_chart` | None. Never writes |

The agent loop runs up to 8 tool rounds per turn.

## 8. Streaming

The chat endpoint streams server-sent events:

| Event | Carries |
|---|---|
| `meta` | thread id, message id |
| `text` | a chunk of the reply |
| `tool_start` | tool name and a short human label ("Looking up order 1042") |
| `tool_end` | tool name, ok or error |
| `chart` | a chart spec to render inline |
| `ui` | one of `navigate`, `highlight`, `changed` |
| `approval` | a gated action waiting for a yes: what will happen, Approve, Change |
| `error` | a message the user can read |
| `done` | end of turn, cost of the turn |

## 9. Drawer tabs

- **Chat**: the current thread, with thread tabs to switch or start a new one.
- **Changes**: every change made through chat by this user, newest first, each with Undo. Undo restores the before state; if a later change touched the same field, Undo shows both and asks.
- A small notice when a teammate changes the page you are on ("Dana updated this lead"), with a refresh.

## 10. Voice

Voice is a mode of the chat panel, not a separate page: a Talk button in the panel header. Requests made on a call land on the Board. The conversation record lands on the person it was about. It is a knob on Agents (`fields.voice`).

## 11. Mobile (under 1024px)

- The chat is a full-screen sheet that slides in from the right. The page underneath stops scrolling. It is a dialog with focus trapped.
- Closed: a round icon-only chat button bottom right, above the safe area.
- **Pick from page** (**new**): a button in the composer. Tapping it slides the sheet down to a 64px bar showing the chip count and Done. Tapping anchored elements toggles them (ring on, light haptic where supported). Done slides the sheet back up.
- Long-press on any anchored element (chat closed) shows "Ask about this", which opens the sheet with that chip.
- Text select: use the native selection menu where possible. Fallback is the same "Ask" float, placed below the selection.
- Esc on a hardware keyboard and the system back gesture both close the sheet.

## 12. Keyboard and accessibility

| Key | Action |
|---|---|
| Cmd/Ctrl+J (Ctrl+/) | Toggle chat |
| Esc | Close chat, after any modal. First Esc blurs the composer if chips exist |
| Enter / Shift+Enter | Send / new line |
| Cmd/Ctrl+Shift+K | Clear chips |
| Arrow keys on the resize edge | Resize 24px |
| Space on a focused anchored element, chat open | Toggle it into the chat (**new**) |

- On desktop the drawer is `<aside aria-label="Chat">`, not a modal.
- Chips are buttons. The remove action is labeled "Remove <label>".
- `prefers-reduced-motion`: no slide, no pulse; a static outline instead.

## 13. Customer side

The portal uses the same component. The agent runs as the customer: their records, their verbs. It answers about their orders, invoices, bookings and documents, reorders, reschedules, and files requests to the Board. It never sees another customer's data, staff notes, cost or margin. Public pages have no chat panel unless Site turns on a web chat channel, which lands in Inbox.

## 14. Build split

Keep the pieces separate. One file per job:

| Piece | Job |
|---|---|
| `chat-shell` | open state, width, keyboard, mobile sheet |
| `drawer` | chrome: thread tabs, Changes tab, close |
| `chat-store` | threads, chips, sending, the SSE reader, UI events, click-to-attach |
| `page-context` | builds `page_context` from the URL, the page marker, visible anchors and chips |
| `ui-actions` | applies `navigate`, `highlight`, `changed` to the page |
| `selection-ask` | the text-select "Ask" float |
| `chat-page-meta` | the hidden record marker server pages render |
| `resize-handle` | the drag edge and its cookie |
| `chat` types (shared) | chip, page context, UI event, SSE event and tool label types, used by client and server |

Write the system prompt per business from `docs/interview.md` and Settings > Brand. Never copy another business's prompt: prompts collect names, prices and phone numbers.
