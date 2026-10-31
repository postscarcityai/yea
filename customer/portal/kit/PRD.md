# Portal: Kit (customer, portal)

- **Module key:** `portal.kit` (stable, never renamed)
- **Tier:** follows Studio (`studio`, common). Shows only when Studio is enabled.
- **Route:** `/portal/kit`
- **Folder:** `customer/portal/kit/`

## Job

Give a business customer print-ready brand material with their own store details on it (posters, counter cards, shelf talkers) and an email signature, in a few clicks, so the brand shows up right at the shelf without a design request. The number that tells you it is working: **share of active stores that downloaded at least one kit piece in the last 90 days**.

## Users and permissions

- Customer kind `buyer` only: View, Create, Edit and Export on their own kit pieces (`shared/roles.md` 4g).
- Kit pieces belong to the store; every member of the store can build and download them. The email signature belongs to the person.
- Brand marks, colors and layouts lock to Studio templates. The store fills only the fields the template exposes (store name, address, hours, a short line, a QR target).
- Agent (as the buyer): View, Create and Edit pieces, render PDFs and PNGs, build the signature. **Gated (customer's yes):** ordering printed copies, when that option is on (it costs money).
- Sensitive fields: none of the brand's internal templates beyond what the store can fill.

## Pages and states

- **Tabs:** Print (`/portal/kit`), Signature (`/portal/kit/signature`).
- **Print:** a grid of available pieces (poster 11x17, counter card 4x6, shelf talker, window cling), each with a thumbnail. Pick one, fill the exposed fields (prefilled from the store's record), see a live preview, then Download PDF (print-ready with bleed) or PNG. A QR code on each piece points at the store's page on the Site's store locator, or a link the store picks from a short list.
- **Signature:** the brand frame with the person's name, title, store, phone and links prefilled from Account. Live preview. Copy as HTML (survives the common mail clients) and step-by-step paste instructions per mail client.
- **Record:** URL modal `?piece=<id>` showing the saved piece with its fields and Download.
- **States:** empty saved list says "Pick a piece to make your first one." Loading shows the preview skeleton. Render error: "That PDF didn't build. Try again." with fields kept.
- **Disabled with reason:** Download disabled with "Add your store address to finish" when a required field is empty.
- Badge: none.

## Data model

- Owns no tables. Uses Studio's `print_kits` (one row per saved piece: `id`, `org_id`, `customer_id` = store company, `template_key`, `fields jsonb`, `render_file_id`, timestamps) and `renders`; writes rendered files to `files`.
- The signature is stored on `users.prefs.signature` (fields only; the HTML is generated on demand).
- QR targets are the store's own pages only (store locator entry, the brand's shop with the store's referral code); no free-text URLs, so a kit piece can never point somewhere unsafe.
- Anchors: `kit_piece:<id>`, `template:<key>`, `field:kit_piece:<id>.<field>`, `signature:<user_id>`.
- Knobs (on Studio): `fields.templates`, `fields.sizes`, `fields.brand`. Portal knobs: `fields.kit.pieces` (which templates stores see), `fields.kit.print_orders` (default off). Sample: `designs`.

## Agent actions

| Action | Tool | Verb | Gated | Writes to `change_log` | Undo |
|---|---|---|---|---|---|
| Make a poster for my store ("for the weekend sale") | `build_kit_piece` | C | No | `print_kits` insert, `renders`, `files` | Yes (soft delete) |
| Change a field and re-render | `update_record`, `render_kit_piece` | E | No | `print_kits.fields` before and after | Yes |
| Build my email signature | `build_signature` | E | No | `users.prefs.signature` before and after | Yes |
| Point at a piece in the grid | `highlight` | none | No | Nothing | n/a |
| Order printed copies (option) | `order_print` | C, $ | Yes | `orders` insert through Orders | Cancel per Orders |

Background jobs: none. When a brand template changes, saved pieces show "New version available" and re-render on the store's next download.

## Integrations

- **Rendering:** the Studio renderer builds PDFs with bleed and PNGs.
- **Object storage:** files by signed URL.
- **Print vendor** (only when `print_orders` is on): an order to the brand's print partner placed through Orders; the vendor is the brand's choice, contract is an order with a file URL and ship-to.
- Webhooks: none. Secrets: none of its own.

## SaaS replaced

| Product | Risk | Migration |
|---|---|---|
| Canva (print templates shared with stockists) | Easy | Export the print templates and brand kit. Rebuild each as a Studio template with the exposed fields marked. Parallel run one month. Cut over by replacing template links in the stockist email with `/portal/kit`. Cancel the shared team or extra seats. |

## Acceptance criteria

1. A shopper, member, partner or client never sees Kit in the nav, and a deep link to `/portal/kit/signature` shows the not-found page.
2. Every agent write on Kit appears in Log with before, after and a working Undo.
3. With print orders on, asked to order 20 posters, the agent shows "Order 20 posters, 11x17, shipped to Corner Store, $64.00" with one Approve button and orders nothing until approved.
4. Every submit button on Kit, including Download PDF, shows a spinner and disables while it runs.
5. A buyer picks the counter card; the store name and address are prefilled from the store record; Download gives a PDF with bleed.
6. A buyer cannot edit the brand logo or colors on any piece.
7. The QR code on a downloaded poster opens the store's page on the Site's store locator.
8. A buyer copies the signature HTML, pastes it into a mail client, and the layout and links hold.
9. A buyer with an empty store address sees Download disabled with "Add your store address to finish".

## Open questions

1. **Offer printed copies?** Default: off; download only until the brand picks a print partner.
2. **Which pieces ship by default?** Default: poster, counter card, shelf talker.
3. **Let stores upload their own logo onto a piece?** Default: yes, in a fixed co-brand slot, never replacing the brand's mark.
