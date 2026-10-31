# Studio (admin, Make)

- **Module key:** `studio` (stable, never renamed)
- **Tier:** common
- **Route:** `/admin/studio`
- **Folder:** `admin/make/studio/`

## Job

"Turn one sentence and one of our real photos into an on-brand post, carousel or short video, without opening a design app." Studio holds the business's templates, designs, print kit, email signatures and press kit, and renders finished files into the Library.

The number: **median minutes from request to an approved, rendered design**. Secondary: share of Social posts this month built in Studio.

## Users and permissions

Starts from `shared/roles.md` section 4d. What differs or needs saying:

| Type | Scope | Notes |
|---|---|---|
| Owner | all | Edits templates and brand. |
| Admin | all | Same as Owner except brand colors and logo, which come from Settings > Brand (Owner-only rails stay in Settings). |
| Staff | all, V C E X | Builds and exports designs from templates. Cannot edit or delete templates (Configure). |
| Contractor | own, V X | Print kit and Signatures only: their own signature and the business's posters and cards to download. Designs and Templates tabs hidden. |
| Customer (buyer kind) | own, V X | Portal Kit (posters, counter cards, their signature) and Portal Posts (prompt to post from the business's templates with their store name). Never sees the business's own designs. |
| Agent | as its role | V C E X. Export is not gated for designs with no people; designs that include uncleared media are blocked by Library's consent rule, not by a gate. |

- **Gated agent verbs:** none by default beyond Library consent. Studio does not send or publish; Social and Content do. Delete of a design is a Studio Delete for Owner and Admin only and is not on the agent's verb list.
- **Never relaxable here:** template and brand changes (Configure).
- **Sensitive fields:** none. Signatures show phone and email the person already chose to share.

## Pages and states

Tabs in nav order, each a sub-route.

| Tab | Route | What it shows |
|---|---|---|
| Designs | `/admin/studio` | Gallery of designs, newest first, each a live thumbnail at its main size with a status chip and where it is used. |
| Templates | `/admin/studio/templates` | The business's templates: post, carousel, short video, story, quote card, OG card, poster, counter card. Each with its sizes and editable fields. |
| Print kit | `/admin/studio/print` | Print-ready PDFs: posters, counter cards, flyers, business cards, with bleed and crop marks. Per-store or per-location versions. |
| Signatures | `/admin/studio/signatures` | One email signature per team member, built from Team and Settings > Brand. Copy as HTML, copy for each mail client. |
| Press kit | `/admin/studio/press` | Logo files, colors, fonts, boilerplate, founder photos, product shots: one page and one zip. |
| Settings | `/admin/studio/settings` | Sizes, default template per format, fonts, watermark. Hidden without K. |

**Record view.** Full route `/admin/studio/[design]?size=9x16&slide=2`. Size and slide live in the URL so every state is a link. Layout: live preview in the center at true size scaled to fit; slide strip under it; on the right, read-only facts until **Edit**: template, fields per slide, photos used (with consent status), renders. In Edit: change text fields per slide, pick photos from the Library (opens a Library picker filtered to Liked, cleared consent), drag to move and pinch or scroll to zoom a photo inside its frame, switch size and slide, add or remove slides within the template's limits. Export menu: PNG, JPG, MP4, WebM, GIF, PDF (print). Record tabs: Edit, Renders, Activity.

**Rendering.** Templates are HTML and CSS with motion. Export renders frame-exact in a headless browser on a worker and lands the file in the Library (`source: studio_render`) linked back to the design. A render job shows progress on the record and on Library > Jobs.

**States:**

- **Empty.** Designs: "No designs yet. Tell the agent what to make: 'carousel on our three most asked questions, using the warehouse photos'." with **New design**. Templates: the default set ships with every business, so Templates is never empty.
- **Loading.** Gallery shows grey blocks at each design's aspect. The editor preview shows a skeleton frame, then the design; fonts load before first paint so text never reflows.
- **Error.** A failed render shows on Renders with the reason and **Render again**. A missing photo (deleted from Library) shows an outlined empty frame with "Photo removed. Pick another."
- **Permission.** No V: nav hidden, deep link shows no-access. Contractor and Customer see only Print kit and Signatures (or Portal Kit). Staff on Templates: read-only, no Edit. Disabled for fixable states: "Consent not cleared for 1 photo", "Text runs past the frame on slide 3", "Rendering... 42%" with spinner.

**Quick views (chips above Designs):** Posts, Carousels, Videos, Print, Drafts, Used in Social, Mine. Filters: template, size, created by, date range.

**Badge count:** none in the nav by default (the module map lists Studio without a badge).

## Data model

Every table carries `id`, `org_id`, `owner_id`, `created_at`, `updated_at`, `deleted_at`.

**`templates`**

| Column | Type | Notes |
|---|---|---|
| `key` | text, unique per org | `post-quote`, `carousel-tips`, `video-explainer`, `og-article`, `poster-a3` |
| `label` | text | |
| `format` | text | `post`, `carousel`, `video`, `story`, `og`, `print`, `signature` |
| `sizes` | text[] | Keys from `fields.sizes` plus print sizes (`a4`, `letter`, `a3`, `4x6in`) |
| `slides` | jsonb | `{ min, max, default }` |
| `fields` | jsonb | `[{ key, label, type: "text"|"photo"|"color"|"list", max_chars, per_slide }]` |
| `source` | text | HTML and CSS with motion, versioned |
| `version` | int | Designs pin the version they were built on |
| `thumbnail_file_id` | fk `files` | |

**`designs`**

| Column | Type | Notes |
|---|---|---|
| `template_id`, `template_version` | fk, int | |
| `title` | text | |
| `status` | text | `draft`, `ready`, `used` |
| `slides` | jsonb | `[{ key, fields: {...}, photos: [{ media_id, crop jsonb }] }]`, slides keyed by content hash |
| `sizes` | text[] | Sizes this design renders in |
| `prompt` | text, null | The sentence it was built from |
| `customer_id` | fk `people`, null | Portal designs |
| `assignee_id` | fk `users` | |
| `custom` | jsonb | |

**`renders`**: `design_id`, `size`, `format` (png, jpg, mp4, webm, gif, pdf), `media_id` (the Library item it produced), `status` (queued, running, done, failed), `progress`, `error`, `duration_ms`, `cost_cents`.

**`print_kits`**: `name`, `location` (store or office, null for all), `design_ids uuid[]`, `zip_file_id`, `bleed_mm`, `customer_id` (null for the business).

**`signatures`**: `user_id` or `person_id`, `fields jsonb` (name, title, phone, email, booking link, photo), `html`, `updated_at`.

**`press_kit`**: one row per org: `boilerplate`, `logo_file_ids`, `photo_media_ids`, `fact_sheet jsonb`, `zip_file_id`.

**Foreign keys into shared tables:** Library `media` (photos in and renders out), `files`, `users` and `people` (signatures, portal customers), `orgs.config` (brand colors and fonts from Settings > Brand), `change_log`.

**Row rules for `own` scope:** Contractor sees their own `signatures` row and `print_kits` where `customer_id` is null. Customer sees `designs`, `print_kits` and `signatures` where `customer_id` is theirs, plus the business's kit items shared to their kind.

**Anchor kinds:**

- `design:<id>` on every gallery card and the editor
- `slide:<design>:<n>` on each slide in the strip and preview
- `field:design:<id>.slides.<slide key>.<field key>` for each text field
- `template:<key>`, `render:<id>`, `printkit:<id>`, `signature:<user id>`

**Config knobs:** `fields.templates` (which template keys are on), `fields.sizes` (default `9x16`, `4x5`, `1x1`, `16x9`, `og`), `fields.brand` (read from Settings > Brand: colors, fonts, logo; Studio never stores its own copy), `fields.watermark` (off by default), `fields.print` (on or off, default on for businesses with locations). **Sample:** `designs` (8 designs across post, carousel and video templates using sample Library media, one print kit with 2 posters and a counter card, signatures for 3 sample team members at `.example` addresses and 555-01xx phones).

## Agent actions

| Action | Tool | Verb | Gated | Writes to `change_log` | Undo |
|---|---|---|---|---|---|
| Read designs, templates, renders | `query_db`, `get_record` | view | no | nothing | n/a |
| Build a design from one sentence: pick template, write fields, pick a real photo | `build_design` | create | no | insert `designs` | soft delete |
| Swap a photo, re-crop, change text on a slide | `update_design` | edit | no | update `designs.slides` | restore |
| Add or remove slides | `update_design` | edit | no | update | restore |
| Render to PNG, JPG, MP4, WebM or GIF into the Library | `render_design` | export | no (consent check runs) | insert `renders`, Library `media` | soft delete the render |
| Build a print PDF and kit zip | `build_print_kit` | create, export | no | insert `print_kits`, `files` | soft delete |
| Build or refresh email signatures | `build_signatures` | create, edit | no (over 5 people: asks) | insert or update `signatures` | restore |
| Refresh the press kit zip | `build_press_kit` | edit, export | no | update `press_kit` | restore |
| Hand a design to Social as a draft post | `hand_off` to Social | create in Social | no | insert Social `posts` (draft) | soft delete the draft |
| Point at things | `navigate`, `highlight` | none | no | nothing | n/a |

**Rules the tools enforce:**

1. `build_design` picks photos through Library's `use_media`, so uncleared media never lands in a design. With `real_assets_only` on in Social, the agent does not generate people or fake product shots.
2. Text that overflows a frame fails validation; the agent shortens it and shows the before and after.
3. Brand values always come from Settings > Brand at render time. Changing the brand re-renders nothing silently; it marks affected designs "brand changed" for a person to re-render.
4. Renders are frame-exact: the same design and size always produce the same file.

**Background jobs:**

| Job | Trigger | Produces |
|---|---|---|
| Render worker | Each `renders` row | The file in Library, progress events, cost logged |
| OG cards | `content.published` | An `og-article` render for the post, linked in the article's SEO |
| Quote cards | A review approved for Social in Reviews | A `post-quote` design and a Social draft |
| Signature refresh | Team member added or changed | Updated signature, a notification to that person |

## Integrations

- **Rails:** none of its own. Uses the database and object storage through Library, and hosting for the worker.
- **Compute:** a render worker with a headless browser and a video encoder. Same contract as Library's worker queue. Video renders can be heavy; run them on a worker, never on the request path.
- **Platform APIs:** none. Social posts what Studio renders.
- **Webhooks in:** none. **Out:** `studio.rendered` (Library and Social listen).
- **Fonts:** self-hosted font files only, loaded from storage, so renders never depend on a third-party font CDN.
- **Secrets by name:** `RENDER_WORKER_TOKEN`.

## SaaS replaced

From `shared/saas.md`:

| Product | Risk | Migration |
|---|---|---|
| Canva (Design) | Easy | **Export:** brand kit (colors, fonts, logo) and the 5 to 10 templates actually used, as PDFs or PNGs. **Import:** brand into Settings > Brand; the agent rebuilds each used template as a Studio template; exported finished designs go to Library. **Parallel run:** two weeks; new posts built in Studio, Canva kept for reference. **Cutover:** Social pulls only from Studio and Library. **Cancel:** at the next renewal. |
| Loom (Video messaging) | Easy | **Export:** download the videos still linked anywhere public. **Import:** into Library as video. **Parallel run:** none needed. **Cutover:** new short videos record and render in Studio; replace public Loom links. **Cancel:** once public links are replaced. |
| Figma (Design) | Plan it | **Export:** only marketing templates and brand assets, not product design files. **Import:** marketing templates rebuilt in Studio; brand into Settings > Brand. **Parallel run:** keep Figma for any product or UI design team. **Cutover:** marketing design moves to Studio. **Cancel:** only if no one does product design in it; otherwise keep it. |

## Acceptance criteria

1. A user without `studio.view` never sees Studio in the nav, and a deep link shows the no-access page; a Contractor sees only Print kit and Signatures.
2. Every agent write (build a design, swap a photo, rewrite a slide, refresh signatures) appears in Log with before, after and a working Undo.
3. When the agent hands a design to Social, the Social draft waits for a human approval under Social's gate before posting; Studio itself shows nothing as published.
4. Every submit button (Save, Render, Build kit, Copy signature) shows a spinner and disables while it runs.
5. An Owner types "carousel: three tips for spring, warehouse photos" in chat; within 2 minutes a 3 to 5 slide carousel exists using Liked Library photos with cleared consent, and the chat cites `design:<id>`.
6. Changing `?size=4x5` in the URL re-lays out the same design at 4:5 with each photo at its 4:5 crop, and `&slide=2` opens slide 2.
7. A Staff user drags a photo inside its frame and pinches to zoom; the saved crop is what renders.
8. Rendering an MP4 shows progress on the record and lands a playable file in Library with `source: studio_render` and a link back to the design.
9. A design that includes a photo with uncleared consent cannot render; the button shows "Consent not cleared for 1 photo" and links to the item.
10. Text that overflows its frame is flagged on the slide with the field named, and the agent's fix shows before and after.
11. A Contractor opens Signatures, sees only their own signature, and copies it as HTML; the phone shows in 555-01xx format in the sample.
12. A buyer Customer in Portal Kit downloads a poster with their store name filled in and never sees the business's Designs or Templates.
13. Rendering the same design and size twice produces byte-identical PNG files.

## Open questions

1. **How many templates ship by default?** Recommended default: 10 (quote card, tip carousel, explainer video, before and after, proof stat, story, OG card, poster, counter card, signature), restyled from Settings > Brand on day one.
2. **Can Staff edit templates?** Recommended default: no. Templates are Configure. Staff ask the agent or the Owner.
3. **Where does the render worker run?** Recommended default: a queue worker on the app host for images; a separate worker for video when renders exceed 2 minutes.
4. **Generated imagery?** Recommended default: off for anything showing people or products; allowed for abstract backgrounds and textures only, labeled in the design's facts.
5. **Print sizes?** Recommended default: letter and A4 by business locale, plus 4x6in counter cards, 3mm bleed.
6. **Signature photos?** Recommended default: optional, pulled from the team member's avatar; off unless the person turns it on.
