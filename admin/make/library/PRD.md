# Library (admin, Make)

- **Module key:** `library` (stable, never renamed)
- **Tier:** common
- **Route:** `/admin/library`
- **Folder:** `admin/make/library/`

## Job

"Every photo and video we have, in one place. I type 'red truck at the warehouse' and it is there, already cropped for every post size, and I know whether I am allowed to use it." Library is the media source for Social, Studio, Content, Site and Catalog.

The number: **share of media with a cleared consent status that was used in a post or design in the last 90 days**. Secondary: median seconds from typing a search to opening a result.

## Users and permissions

Starts from `shared/roles.md` section 4d. What differs or needs saying:

| Type | Scope | Notes |
|---|---|---|
| Owner | all | Hard delete only by emptying Trash. |
| Admin | all | Sets consent status. Exports originals. |
| Staff | all, V C E, D own uploads | Uploads, tags, likes, crops. Deletes only what they uploaded. Can mark consent "needs check", not "cleared". |
| Contractor | hidden | |
| Customer | own, C | Uploads only, through the flows that ask for them (photos for a report, store photos, customer content for Programs). Never browses the Library. Their uploads land here tagged with source and `customer_id`. |
| Agent | as its role | V C E. Delete gated `*`. Download or export of media with people in it and no cleared consent: always asks. |

- **Gated agent verbs:** `library.delete`, `library.export` on any media with `media_people` rows (personal data). The Owner can relax delete with a daily cap (default 20) for near-duplicate cleanup.
- **Consent is a human call.** Setting `consent_status` to `cleared` is treated like Approve: a person with Edit plus the `consent` field grant does it, never the agent. The agent can attach evidence (a signed release in Documents, a message where the person said yes) and propose.
- **Sensitive fields:** `media_people` (names of people in a photo), `consents.evidence`, original EXIF location. Column grants: Owner and Admin. Staff see "2 people, consent cleared" without names unless granted.

## Pages and states

Tabs in nav order, each a sub-route.

| Tab | Route | What it shows |
|---|---|---|
| All | `/admin/library` | True-aspect mosaic of every item, newest first. Never cropped in the grid. Search bar on top: plain words. |
| Liked | `/admin/library/liked` | Items with a thumbs up. The agent picks from here first. |
| Needs consent | `/admin/library/consent` | Items with people in them and no cleared consent, plus items whose consent expires within 30 days. |
| Uploads | `/admin/library/uploads` | Upload sessions in progress and recent, by person and source (phone, portal, import), with progress and any failed files. |
| Jobs | `/admin/library/jobs` | Background work: tagging, transcodes, renders landing from Studio, imports. Status, duration, error. |
| Settings | `/admin/library/settings` | Consent rules, post sizes, tag vocabulary, storage use. Hidden without K. |

**Record view.** URL modal `?item=<id>`, full-screen viewer. Left and right arrows step through the current result set; Esc closes. Panel on the right, read-only until **Edit**: kind, size, duration, source, uploaded by, tags (auto and manual), people (if granted), consent status with evidence, credit, notes, where it is used (posts, designs, articles, products). Below: the crop editor, one draggable box per post size in `fields.sizes`, pre-set by the agent, each adjustable. Buttons: Like, Unlike, More like this, Use in Studio, Download (original or a size).

**Upload.** A modal from the **Upload** button (and `?upload=1`). Pick files or drop them, add an optional note. Uploads two at a time in chunks; resumes after a dropped connection or a locked phone; keeps the phone awake while running; closing the modal never stops an upload; a count badge on the Upload button shows files in flight. Photos are downscaled for preview and stripped of GPS in the browser and again on the server; the original is kept privately only when `fields.keep_originals` is on.

**States:**

- **Empty.** "No media yet. Upload from your phone or drag a folder here." with **Upload**. Search with no hits: "Nothing matches 'blue van'. Try fewer words, or ask the agent."
- **Loading.** Grey blocks at each item's true aspect (the aspect is known from the row, so the mosaic never jumps). Video shows its poster frame, plays on hover on desktop, on tap on mobile.
- **Error.** A failed upload stays on Uploads with the file name, reason and **Retry**. A failed tag job shows on the item as "Not tagged yet" with **Tag now**.
- **Permission.** No V: nav hidden, deep link shows no-access. Staff without the consent grant: the consent field shows status only, Edit renders it as plain text. Disabled for fixable states: "Consent not cleared for 2 people. Add a release to download", "Uploading 3 of 12..." with spinner.

**Quick views (chips above All):** Photos, Videos, Liked, Needs consent, People, No people, From customers, Unused, Duplicates. Filters behind Filter: kind, shape (portrait, square, landscape), scene tag, uploaded by, source, date range, consent status, used in.

**Badge count:** none in the nav by default (the module map lists Library without a badge). Needs consent shows its count on its tab.

## Data model

Every table carries `id`, `org_id`, `owner_id`, `created_at`, `updated_at`, `deleted_at`.

**`media`**

| Column | Type | Notes |
|---|---|---|
| `file_id` | fk `files` | The stored object |
| `kind` | text | `photo`, `video`, `render`, `audio`, `doc` |
| `width`, `height` | int | Drives true-aspect layout |
| `duration_ms` | int, null | |
| `shape` | text | `portrait`, `square`, `landscape`, derived |
| `scene` | text | Main scene tag |
| `like` | smallint | 1, 0, -1 |
| `auto_tags` | text[] | From the tagger |
| `tags` | text[] | Manual |
| `embedding` | vector | Image or frame embedding for plain-word search and "more like this" |
| `dup_group` | uuid, null | Near-duplicate stack |
| `consent_status` | text | `not_needed`, `needs_check`, `cleared`, `refused`, `expired` |
| `credit` | text | Photographer or source |
| `source` | text | `phone_upload`, `portal`, `import`, `studio_render`, `intake` |
| `customer_id` | fk `people`, null | Customer uploads |
| `subject_kind`, `subject_id` | text, id, null | What it was uploaded for (an intake run, a job, a product) |
| `notes` | text | |
| `custom` | jsonb | |

**`media_tags`**: `media_id`, `tag`, `source` (auto, person, agent), `confidence`. One row per tag for filtering and counts.

**`media_people`**: `media_id`, `person_id` (fk `people`, null when unknown), `box jsonb` (normalized x, y, w, h), `label` (when not a known person).

**`consents`**: `person_id`, `scope` (all media, one shoot, one item), `media_ids uuid[] null`, `granted_at`, `expires_at`, `evidence_file_id` (fk `files`, often a signed release from Documents), `evidence_message_id` (fk `messages`), `recorded_by`.

**`crops`**: `media_id`, `size_key` (from `fields.sizes`: `9x16`, `4x5`, `1x1`, `16x9`, `og`), `box jsonb`, `set_by` (agent, person), `locked bool`.

**`upload_sessions`**: `user_id` or `customer_id`, `source`, `file_count`, `done_count`, `bytes`, `note`, `status` (open, done, failed), `resume_token`.

**`media_jobs`**: `kind` (tag, transcode, dedupe, import, render_landing), `media_id` or `batch jsonb`, `status`, `started_at`, `ended_at`, `error`, `cost_cents`.

**Foreign keys into shared tables:** `files` (every object), `people` (people in photos, customer uploaders), `messages` and Sell > Documents (consent evidence), `change_log`, `agent_runs` (tag jobs).

**Row rules for `own` scope:** Staff delete matches `owner_id = user`. Customer rows: a customer can read back only media where `customer_id` is theirs, and only through the flow they uploaded in (their report, their store), never through `/admin/library`.

**Anchor kinds:**

- `media:<id>` on every tile and the viewer
- `field:media:<id>.consent_status`, `field:media:<id>.tags`, `field:media:<id>.credit`
- `crop:<media>:<size>`
- `dupgroup:<id>` for a near-duplicate stack
- `upload:<session id>`

**Config knobs:** `fields.consent_required` (default true: media with people needs `cleared` before use in Social, Studio exports or Site), `fields.sizes` (default `9x16`, `4x5`, `1x1`, `16x9`, `og`), `fields.vocabulary` (scene and tag words for the business, set from the interview), `fields.keep_originals` (default true), `fields.kinds`. **Sample:** `media` (60 generated stock-style photos and 6 short clips of objects, places and products with no real people, across 5 scenes; 4 items marked as containing people with consent in mixed states; 2 near-duplicate stacks).

## Agent actions

| Action | Tool | Verb | Gated | Writes to `change_log` | Undo |
|---|---|---|---|---|---|
| Search in plain words, find more like this | `search_media`, `similar_media` | view | no | nothing | n/a |
| Tag on upload (scene, objects, people boxes) | `tag_media` | edit | no | update `media`, insert `media_tags`, `media_people` | restore tags |
| Group near-duplicates | `group_duplicates` | edit | no | update `dup_group` | restore |
| Set people-centred crops for each post size | `set_crops` | edit | no | insert or update `crops` (unlocked only) | restore |
| Rename and file phone uploads with the uploader's note | `file_upload` | edit | no | update `files` name, `media.notes`, `subject_*` | restore |
| Like, unlike, retag, edit credit | `update_record` | edit | no (over 5 items: asks) | update | restore |
| Propose consent cleared, with evidence | `propose_consent` | create | no | insert `approvals` with evidence | cancel |
| Warn before use of uncleared media | built into `use_media` | view | no | nothing; returns a block with the reason | n/a |
| Delete a near-duplicate or a refused item | `delete_record` | delete | `*` | soft delete | restore from Trash |
| Export originals of media with people | `export_media` | export | `*` | insert `change_log` export row | n/a, logged on Log > Exports |
| Point at things | `navigate`, `highlight` | none | no | nothing | n/a |

**Rules the tools enforce:**

1. `use_media` (called by Social, Studio, Content, Site) refuses media with `consent_status` of `needs_check`, `refused` or `expired` when `fields.consent_required` is on, and returns the reason for the UI to show.
2. The agent never sets `consent_status` to `cleared`.
3. Tagging and embeddings run on open-weight models, on the business's own compute where possible; cost per job is logged to `model_calls`.
4. Crops a person locked are never moved by the agent.

**Background jobs:**

| Job | Trigger | Produces |
|---|---|---|
| Tagger | Every upload, and nightly for anything untagged | Tags, embedding, people boxes, shape, scene |
| Crop setter | After tagging | A crop per size, centred on people when present, else on the main subject |
| Dedupe | Nightly | `dup_group` stacks; a Feed item "Found 6 near-duplicate stacks" |
| Consent watch | Daily | Moves expired consents to `expired`, lists items on Needs consent, files a Board card for any expired item scheduled in Social in the next 7 days |
| Transcode | Video upload | Streaming rendition and poster frame |
| Upload filer | Upload session done | Names and files each item, notes it in the Feed with the uploader's note |

## Integrations

- **Rails:** database, with object storage for files (the `files` table holds the key). Contract: `put(stream, key, mime) -> key`, `signed_url(key, ttl)`, resumable chunked upload with a resume token, private by default, public only through a signed or published path. Default: the database provider's object storage or any S3-compatible bucket.
- **Platform APIs:** none required. Optional imports from a cloud drive the business already uses (read-only connector, one-time import).
- **Webhooks in:** none. **Out:** `library.uploaded` and `library.tagged` events (Social and Studio listen for new liked media).
- **Compute:** a worker for tagging, embeddings, transcodes and crops. Runs as a queue consumer; can be the app host or a separate machine.
- **Egress:** watch storage egress on plans with a monthly cap. Grid thumbnails are small renditions, never originals; video plays from a streaming rendition.
- **Secrets by name:** `STORAGE_BUCKET`, `STORAGE_ACCESS_KEY_ID`, `STORAGE_SECRET_ACCESS_KEY`, `MEDIA_WORKER_TOKEN`.

## SaaS replaced

From `shared/saas.md`:

| Product | Risk | Migration |
|---|---|---|
| Dropbox (Files) | Easy | **Export:** download the media folders, or connect read-only for a one-time pull. **Import:** every file into Library through the import job; folder names become tags; the tagger runs on all of it. **Parallel run:** two weeks; new uploads go to YEA, Dropbox stays read-only. **Cutover:** replace every public shared link (on the site, in emails, in bios) with YEA links, since shared links break. **Cancel:** once the import count matches the folder count and no public link points at Dropbox. |

Inventories also saw digital asset managers and video review tools. They are not in `shared/saas.md`, so they are not priced here.

## Acceptance criteria

1. A user without `library.view` (a Contractor, a Customer) never sees Library in the nav, and `/admin/library` shows the no-access page (staff side) or not found (customer).
2. Every agent write (tags, crops, duplicate groups, renames) appears in Log with before, after and a working Undo.
3. When the agent tries to delete media while `library.delete` is gated, it shows an approval card ("Move 6 near-duplicates to Trash, keep the liked one in each stack") with thumbnails and one button, Approve; nothing moves until a person approves.
4. Every submit button (Upload, Save, Approve, Retry) shows a spinner and disables while it runs.
5. A Staff user types "boxes on a pallet" in search and sees matching photos ranked first, though no item has that tag text.
6. The mosaic shows each item at its true aspect; no tile is cropped, and the layout does not shift as images load.
7. An Owner uploads 12 photos from a phone, locks the screen mid-upload, unlocks, and the upload resumes and finishes without re-picking files.
8. Opening an item shows a crop box per configured size; with people in the photo, every box contains the people.
9. A photo with people and consent `needs_check` cannot be used in a Studio export or a Social post; the attempt shows "Consent not cleared for 2 people" with a link to the item.
10. The agent can propose consent with evidence attached, but only a person can set it to Cleared; the agent has no button or tool for it.
11. A Staff user without the people grant sees "2 people" on an item but no names, and the agent's search results for that user omit names.
12. A Customer's portal upload appears on Uploads tagged with its source and the customer, and that customer can see it back only inside the flow they used.
13. A photo uploaded from a phone has no GPS data in the stored copy served to the app.

## Open questions

1. **Keep originals or only web renditions?** Recommended default: keep originals in private storage, serve renditions. Print and video work need the original.
2. **Consent required for every photo with a person?** Recommended default: yes (`fields.consent_required: true`). Turn off only for businesses with no people in their media.
3. **Where does tagging run?** Recommended default: an open-weight image model on a worker the business controls; fall back to a hosted open-weight endpoint with cost logged.
4. **Face recognition to name people?** Recommended default: off. Detect people for crops and consent prompts; naming a person is a manual tag.
5. **Storage cap and alerts?** Recommended default: alert on Costs at 80% of the storage plan and on any day egress exceeds 3x the 30-day average.
6. **Video review proxies?** Recommended default: transcode to a 1080p streaming rendition on upload; keep the original for export.
