# Content (admin, Make)

- **Module key:** `content` (stable, never renamed)
- **Tier:** common
- **Route:** `/admin/content`
- **Folder:** `admin/make/content/`

## Job

"Keep the blog full of real, useful posts that get us found, and never let a week go dark." Content holds every article, answer page and series episode the business publishes, puts them on a calendar, and gets them live on the public site (Site renders them at `/blog`).

The number: **published posts per week against `fields.cadence`**, shown as a streak ("6 of 6 this week, 14 weeks on cadence"). Secondary: days on the calendar with nothing scheduled in the next 14.

## Users and permissions

Starts from `shared/roles.md` section 4d. What differs or needs saying:

| Type | Scope | Notes |
|---|---|---|
| Owner | all | Approves publish by default. Can delegate publish approval to Admin. |
| Admin | all | Publishes directly. Approves Staff and Customer drafts. |
| Staff | all, V C E | Writes and edits drafts. Publish shows as **Send to review**. Cannot delete a published post. |
| Contractor | hidden | Nav item not rendered. |
| Customer (partner kind) | own, V C E | Writes contributions (expert answers) through Portal Listing. Never sees other contributors, the calendar or drafts. |
| Agent | as its role | V C E. Publish (`content.send`) is gated `*`. Delete gated `*`. |

- **Gated agent verbs:** `content.send` (publish, unpublish, change a live slug) and `content.delete`. The Owner can relax publish on Agents > Permissions with the limit "only after a person approved the draft" (`afterHumanApproval: true`) so an approved draft goes live at its scheduled time without a second yes. Relaxing without that limit is allowed but the switch warns "the agent will publish drafts nobody has read".
- **Never relaxable here:** approving a contribution (Approve is always human), changing the cadence or contributor settings (Configure).
- **Sensitive fields:** `contributions.contact_email` and `contributions.paste_attempts` are column grants (Owner, Admin). Staff see the contributor's display name and company only.

## Pages and states

Tabs in nav order. Each tab is a sub-route, so every view is a link.

| Tab | Route | What it shows |
|---|---|---|
| Posts | `/admin/content` | Every article: live, scheduled, draft, in review. Table with title, status chip, publish date, author, series, word count, last edit. |
| Schedule | `/admin/content/schedule` | Calendar, 6 weeks visible. Empty days render blank and red-tinted when they break cadence, so a gap is obvious. Drag a scheduled post to another day (Edit). |
| Contributors | `/admin/content/contributors` | Contributions from partner customers moving through submitted, drafting, sent for approval, approved, published, declined, withdrawn. Hidden when `fields.contributors` is off. |
| Series | `/admin/content/series` | Recurring formats (a weekly field note, an explainer series). Each series has a brief, a voice note and its episodes. |
| Settings | `/admin/content/settings` | Label, cadence, contributor switch, default author, categories. Hidden without K. |

**Record view.** Full route `/admin/content/[slug]/edit` (articles have tabs). Opens read-only: rendered preview on the left, facts on the right (status, publish date, slug, series, author, canonical URL, live check result). **Edit** switches to the editor. Record tabs: Preview, Edit, SEO (title, description, OG card preview, FAQ items), Activity, Files. Contributions open as a URL modal `?contribution=<id>`. Series open as a URL modal `?series=<id>` listing episodes.

**States, every page:**

- **Empty.** Posts: "No posts yet. Paste a rough draft or ask the agent for this week's post." with one button, **New post**. Schedule: blank calendar with "Nothing scheduled. Ask the agent to fill the next two weeks." Contributors: "No contributions yet. Partners write answers from their portal."
- **Loading.** Skeleton rows matching the table, skeleton calendar cells. No spinners over the whole page.
- **Error.** Inline banner over the list with the reason and **Retry**. A failed live check shows on the record as a bad-status chip "Not live: 404 at /blog/<slug>" with **Check again**.
- **Permission.** No V: nav hidden, deep link shows the no-access page with **Request access**. V without E: record opens read-only, no Edit button. Staff on a draft: the primary action reads **Send to review**, not Publish. Disabled with reason only for fixable states: "Add a title to schedule", "Waiting on Owner approval", "Publishing..." with spinner.

**Quick views (chips above Posts):** Needs review, Scheduled, Live, Drafts, Mine, Stale (live, not updated in 12 months). Filters behind the Filter button: status, series, author, category, date range.

**Badge count:** posts in review waiting on someone with Approve, plus contributions in "sent for approval". Same scope as the list.

## Data model

Owned by this module. Every table carries `id`, `org_id`, `owner_id`, `created_at`, `updated_at`, `deleted_at` per `shared/data-model.md`.

**`articles`**

| Column | Type | Notes |
|---|---|---|
| `slug` | text, unique per org | Stable once live. Changing a live slug is a gated publish action and writes a redirect. |
| `title` | text | |
| `excerpt` | text | 160 characters max |
| `body` | text | Markdown. Headings, lists, links, images by `files.id`. |
| `status` | text | Key from `fields.stages`. Default: `draft`, `in_review`, `scheduled`, `live`, `unpublished`. |
| `publish_at` | timestamptz | Scheduled time, business timezone |
| `published_at` | timestamptz | Set when the live check passes |
| `author_id` | fk `people` | Byline. Can differ from `owner_id` (who drafted it). |
| `assignee_id` | fk `users` | Who it is waiting on |
| `series_id` | fk `series`, null | |
| `category` | text | Key from `fields.kinds` |
| `seo` | jsonb | `{ title, description, og_file_id, faq: [{ key, q, a }] }`. FAQ items keyed by content hash. |
| `sources` | jsonb | `[{ key, url, title, accessed_at }]` for researched posts |
| `source_kind` | text | `typed`, `emailed_draft`, `agent_research`, `series`, `contribution` |
| `live_check` | jsonb | `{ url, status_code, checked_at }` |
| `redirect_from` | text[] | Old slugs |
| `custom` | jsonb | `fields.custom` |

**`article_schedule`**: `article_id`, `slot_date`, `slot_kind` (`cadence`, `extra`), `locked bool`. One row per calendar slot so empty cadence days exist as rows and can be counted.

**`contributions`**: `customer_id` (fk `people`), `company_id`, `topic`, `answers jsonb` (`[{ key, question, answer }]`), `status` (submitted, drafting, sent_for_approval, approved, published, declined, withdrawn), `article_id` (when published), `paste_attempts int`, `contact_email`, `notes`.

**`series`**: `name`, `brief`, `voice_note`, `cadence`, `next_episode_n`.

**`episodes`**: `series_id`, `n`, `prompt` (the plain sentence it came from), `article_id`.

**Foreign keys into shared tables:** `people` (author, contributor), `companies` (contributor's firm), `files` (images, OG cards, attachments), `change_log` (every write), `approvals` (publish requests), `cards` (emailed drafts become Board cards first), `activities` (record timeline).

**Row rules for `own` scope:** a Customer sees `contributions` where `customer_id` is their person row, and the `articles` row linked to their published contribution (read-only). Staff `own` (for Mine) matches `owner_id`, `author_id` or `assignee_id`.

**Anchor kinds:**

- `article:<slug>` on every row, card and calendar cell
- `field:article:<slug>.<field>` for title, excerpt, publish_at, status, seo.description
- `faq:<slug>:<hash>` for each FAQ item
- `contribution:<id>`, `series:<id>`, `episode:<series>:<n>`
- `slot:<date>` for an empty calendar day (so "fill this" works)

**Config knobs:** `label` (Content, Blog, Journal, Insights), `fields.cadence` (posts per week and which weekdays, default `{ per_week: 3, days: ["mon","wed","fri"] }`), `fields.contributors` (default off), `fields.stages`, `fields.kinds` (categories), `fields.custom`, `fields.tabs`. **Sample:** `articles` (12 live posts across 3 categories, 4 scheduled, 2 drafts, one series with 5 episodes, 3 contributions in different states, authors at `.example` addresses).

## Agent actions

| Action | Tool | Verb | Gated | Writes to `change_log` | Undo |
|---|---|---|---|---|---|
| Read posts, calendar, contributions | `query_db`, `get_record`, `content_summary` | view | no | nothing | n/a |
| Turn an emailed rough draft into a formatted post: headings, hook, excerpt, meta, images. Substance stays verbatim. | `format_draft` | create | no | insert `articles` (draft) | soft delete the draft |
| Research and write a sourced post on a topic | `write_post` | create | no | insert `articles` with `sources` | soft delete |
| Write the next episode of a series from a plain sentence | `write_episode` | create | no | insert `articles`, insert `episodes` | soft delete both |
| Edit a field (title, excerpt, body section, SEO) | `update_record` | edit | no (bulk over 5: asks) | update with before and after | restore before |
| Fill empty cadence slots with drafts | `fill_schedule` | create, edit | asks first when over 5 slots | inserts `articles`, updates `article_schedule` | one Undo per slot |
| Move a scheduled post to another day | `move_schedule` | edit | no | update `publish_at` | restore |
| Submit a draft for review | `request_review` | edit | no | update status to `in_review`, insert `approvals` | restore status, cancel approval |
| Publish or schedule live | `publish_article` | send | `*` | update status, `published_at`, `live_check` | Unpublish (writes a new row; the page goes offline) |
| Change a live slug | `change_slug` | send | `*` | update `slug`, append `redirect_from` | restore slug, redirect stays |
| Draft a contribution into a post | `draft_from_contribution` | create | no | insert `articles`, update `contributions.status` | restore both |
| Delete a draft | `delete_record` | delete | `*` | soft delete | restore from Trash |
| Point at things | `navigate`, `highlight` | none | no | nothing | n/a |

**Rules the tools enforce:**

1. A post is never reported live until the live check returns 200 at the public URL. If it fails, the agent says so and files a Board card.
2. Before writing, the agent checks for an existing post on the same topic (title and body similarity) and refuses to make a duplicate. It offers to update the existing post instead.
3. Formatting an emailed draft never changes claims, numbers or advice. The diff view shows only structure added.
4. Every researched claim with a number or date has a source in `sources`. No source, no claim.

**Background jobs:**

| Job | Trigger | Produces |
|---|---|---|
| Inbound draft watcher | Email to the content address (Inbox thread tagged `content`) | A Board card plus a formatted draft, linked |
| Cadence keeper | Daily, 06:00 business time | Drafts for any empty cadence slot in the next 7 days, each sent to review. A Home > Today row "3 posts waiting on you". |
| Publisher | Every 5 minutes | Publishes approved posts whose `publish_at` has passed, runs the live check, writes `published_at` |
| Live check | After publish, and weekly for every live post | Updates `live_check`; a failing page files a Board card |
| Contribution nudger | Weekly | Reminds partner contributors with a stalled draft (system message to the contributor, not a send) |

## Integrations

- **Rails:** hosting (publish). The contract: `revalidate(paths[])` rebuilds `/blog`, `/blog/[slug]`, the RSS feed, the sitemap and any category page, then returns once the new content is served. Default: the app's own host with on-demand revalidation. Email delivery for the "you're published" note to contributors (a system message) and for the inbound draft address.
- **Platform APIs:** search engine indexing ping on publish (IndexNow where supported; a sitemap ping otherwise). Optional, read through Search.
- **Webhooks in:** inbound email for drafts (arrives through Inbox). **Out:** `content.published` event other modules subscribe to (Social builds posts from it, Campaigns can include it in a newsletter).
- **Outputs on the public side:** Article, FAQ and Breadcrumb structured data per post, a generated OG card per post (rendered by Studio, stored in Library), RSS at `/blog/rss.xml`.
- **Secrets by name:** `INDEXNOW_KEY`, `CONTENT_INBOUND_ADDRESS`, `REVALIDATE_SECRET`.

## SaaS replaced

From `shared/saas.md`:

| Product | Risk | Migration |
|---|---|---|
| WordPress.com (blog half; the page half moves with Site) | Easy | **Export:** WordPress XML export of posts, pages and media. **Import:** importer maps posts to `articles` (slug, title, body as Markdown, date, author, categories), media to Library, comments dropped with a note. **Parallel run:** new posts publish in YEA at the same slugs; old site stays up one week. **Cutover:** Site serves `/blog/*`; every old URL that changes gets a 301 in `redirect_from`; resubmit the sitemap. **Cancel:** after a week of zero 404s in Search. |

Inventories also saw editorial calendar plugins and AI writing subscriptions. They are not in `shared/saas.md`, so they are not priced here.

## Acceptance criteria

1. A user without `content.view` (a Contractor) never sees Content in the nav, and `/admin/content` shows the no-access page with Request access.
2. Every agent write (format a draft, edit a title, fill a slot) appears in Log with before, after and a working Undo; clicking Undo restores the before state and the post list re-renders.
3. When the agent tries to publish while `content.send` is gated, it shows an approval card ("Publish 'Five signs your roof needs work' to /blog/five-signs, Tuesday 09:00, OG card attached") with one button, Approve, and nothing goes live until a person with Send on Content clicks it.
4. Every submit button (Save, Send to review, Publish, Approve) shows a spinner and disables while it runs, then re-enables with an inline result.
5. A Staff user opening a draft sees **Send to review** as the primary action, never Publish; clicking it moves the post to In review and it appears on the Owner's Home > Today.
6. An Owner pastes a rough draft by email to the content address; within 10 minutes a Board card and a formatted draft exist, and the draft's diff shows only structure added (headings, excerpt, meta), no changed sentences.
7. An Owner opens Schedule; every cadence day with no post in the next 14 days renders blank with a red tint, and the count of empty days matches the Settings cadence.
8. After the publisher runs, a post is marked Live only when its public URL returns 200; if it returns 404, the record shows "Not live" with the status code and a Board card exists.
9. An Admin changes a live slug; the old URL returns a 301 to the new one, and `redirect_from` holds the old slug.
10. A partner Customer writes a contribution in the portal; it shows on Contributors as Submitted, the customer sees only their own contributions, and pasted text is blocked with the attempt counted.
11. A Staff user does not see contributor email addresses in the Contributors list or record, and the agent's query results for that user omit the column.
12. The agent refuses to draft a post whose topic matches an existing live post and offers to update that post instead.
13. With the sample loaded, Posts shows 12 live posts, 4 scheduled, 2 drafts, and every author email ends in `.example`.

## Open questions

1. **Editor format: Markdown or rich text?** Recommended default: Markdown stored, with a toolbar editor that writes Markdown. It diffs cleanly in Log and survives export.
2. **Who approves publish by default?** Recommended default: Owner, delegable to Admin. Matches `fields.approval` in Social so one switch can cover both later.
3. **Should the agent keep the calendar full without being asked?** Recommended default: yes for drafts (Cadence keeper on), never for publishing. Every drafted slot waits for review.
4. **Comments on public posts?** Recommended default: off. Questions route to Inbox through the site's web chat or contact form.
5. **Where do OG cards come from?** Recommended default: Studio template `og-article` renders one per post on save, stored in Library. The owner can swap the photo.
6. **Multiple authors and bylines?** Recommended default: byline is any `people` row with kind `staff` or `partner`; default author set in Settings.
7. **Contributor paste blocking: required?** Recommended default: on when `fields.contributors` is on. It keeps answers in the contributor's own words, which is the point of the feature.
