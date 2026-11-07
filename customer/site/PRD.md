# Site (customer, public)

- **Module key:** `site` (stable, never renamed)
- **Tier:** core
- **Route:** `/`, `/<slug>`, `/blog`, `/blog/[slug]`, plus the utility pages listed under Pages and states
- **Folder:** `customer/site/`

## Job

The public website. It tells a stranger what the business does, proves it, and sends them to one next step: Get started (Intake), Shop, Book, or Call. Every page is fast, indexable, and editable by asking the agent instead of opening a website builder.

The number that tells you it is working: **visitor to started intake rate** (sessions on `/` and `/<slug>` that reach `/start` step 1, last 30 days). Secondary: pages live with no broken links and no failed checks.

## Users and permissions

Starts from `shared/roles.md` section 4g. What differs or needs saying:

- **Public visitors** (anyone, signed in or not) read every published page. No chat panel on public pages unless the Owner turns on the web chat channel (`fields.web_chat`), which posts into Inbox as a `web_chat` thread.
- **Owner, Admin:** edit pages, nav, redirects and SEO fields from the admin preview (`/admin/site`, reached from Settings > Brand and from Make > Content), publish, roll back.
- **Staff:** create and edit page drafts. Publish shows as **Send to review**.
- **Contractor:** hidden.
- **Customer:** public pages only. Signed-in customers see their name and a Portal link in the top nav; nothing else changes.
- **Agent:** View and Edit on drafts. **Publish is gated (`P*`)**: the agent shows the page diff and the live URL it will change, then waits for a human yes. The Owner can relax publish to "Go ahead" with the limit `afterHumanApproval` (agent may publish copy a person already approved) or `hours: business`. Deleting a page (`D`) is gated and moves the page to Trash; its URL gets a 410 or a redirect, never a silent 404.
- **Sensitive fields:** none on public pages by design. Draft pages, unpublished prices and the redirect map are admin-only. Directory pages never show a person who asked to be removed.

## Pages and states

Public pages live in the **same repo** as the back office and deploy with it. They default to the **light theme**, with a dark mode switch in the footer saved in a cookie (`shared/design-system.md` section 7). Every page is tracked first party only: no Google Analytics.

Public pages use a **top nav** (`fields.nav`), not the left-nav shell. Default order: Home, the industry pages the business picked, Blog, Shop (if Shop is on), one CTA button (Get started, Book or Call, from `fields.cta`), Sign in, Cart (if Shop is on).

| Page | Route | Built from |
|---|---|---|
| Home | `/` | `site_pages` row with `path = '/'`: hero, proof strip, sections |
| Industry pages | `/<slug>` | `fields.pages`: services, about, results, locations, team, FAQ, pricing, stores, links |
| Location pages | `/<slug>` (for example `/riverside`) | one row per location, shared template |
| Blog | `/blog`, `/blog/[slug]`, `/blog/rss.xml` | published `articles` from Make > Content |
| Directory | `/directory`, `/directory/[region]`, `/directory/[region]/[company]` | Prospects or Pipeline when `fields.directory` is on |
| Store locator | `/stores` | companies with `on_locator = true` (map plus list) |
| Links page | `/links` | `site_pages` row of kind `links`, replaces a link-in-bio tool |
| Contact | `/contact` | short form that creates an Intake run of kind `form` |
| Policies | `/policies/[slug]` (privacy, terms, refunds, accessibility) | `site_pages` of kind `policy` |
| Unsubscribe and opt-out | `/unsubscribe/[token]`, `/privacy/opt-out` | Campaigns and Outreach suppression, Insights tracking opt-out |
| Removal | `/directory/remove/[id]` | anyone can remove a person from a public roster, no login |
| Not found, gone | 404, 410 | branded, with search and the CTA |

**Admin preview** (`/admin/site`, tabs as sub-routes): **Pages** (`/admin/site/pages`), **Nav** (`/admin/site/nav`), **Redirects** (`/admin/site/redirects`), **Checks** (`/admin/site/checks`), **Settings** (`/admin/site/settings`, last, needs K). It lives under Settings > Brand in the nav; Site has no left-nav item of its own.

- **Record view:** full route `/admin/site/pages/[id]` with tabs Preview (desktop and phone frames side by side), Copy (sections as editable blocks), SEO (title, description, OG image, canonical, noindex), History (every published version, each with Roll back).
- **Empty state:** a new business has Home and the policy pages generated from the interview. Pages list empty text: "No pages yet. Ask the agent to draft your services page." with one button, Draft a page.
- **Loading:** skeleton blocks the size of the final layout. Public pages are static or cached, so the public visitor never sees a loading state on first paint.
- **Error:** a failed publish leaves the live page untouched and shows the build error in one line with Retry. A public page whose data source fails renders the last good cached version.
- **Permission states:** Staff see Publish replaced by Send to review. Contractors get the no-access page on `/admin/site`. Customers deep-linking to `/admin/site` get a normal 404.
- **Quick views:** Drafts, Waiting on approval, Changed this week, Failing checks.
- **Badge:** pages waiting on approval (shown on Settings in the left nav, since Site has no item).

Public page rules: one H1 per page, server-rendered, structured data per page kind (Organization and LocalBusiness on Home, Article and FAQ on posts, Product on shop pages, BreadcrumbList everywhere), generated OG card per page, sitemap and robots from the published set, no text animating in, images sized and lazy below the fold, AA contrast.

## Data model

Owned by Site:

| Table | Columns |
|---|---|
| `site_pages` | `id`, `org_id`, `path text unique per org`, `kind` (home, page, location, links, policy, landing), `title`, `status` (draft, review, live, archived, from `fields.stages`), `sections jsonb` (ordered blocks, each with a content-hash `key`), `seo jsonb` (title, description, og_file_id, canonical, noindex), `published_version_id`, `owner_id`, `custom jsonb`, `created_at`, `updated_at`, `deleted_at` |
| `site_page_versions` | `id`, `page_id`, `sections jsonb`, `seo jsonb`, `published_by` (user or agent id), `published_at`, `change_id` (FK `change_log`) |
| `site_nav` | `id`, `org_id`, `items jsonb` (label, href, kind: link or cta), `updated_at` |
| `redirects` | `id`, `org_id`, `from_path`, `to_path`, `code` (301, 308, 410), `hits int`, `last_hit_at` |
| `site_checks` | `id`, `org_id`, `run_at`, `path`, `check` (status, links, title, description, h1, structured_data, image_alt, speed), `result` (pass, warn, fail), `detail text` |
| `page_views` | `id`, `org_id`, `path`, `session_id`, `person_id null`, `referrer`, `utm jsonb`, `at` (first-party, honors opt-out; Insights reads it) |

Foreign keys into shared tables: `files` for every image and OG card, `people` for directory people and for a `page_views.person_id` once a visitor identifies, `companies` for directory and store locator entries, `change_log` for every draft edit and publish, `approvals` for gated publishes.

Reads from other modules (never writes): Content (`articles`), Catalog (`products` for featured items), Reviews (published reviews), Prospects and Pipeline (directory and stores, claimed and public only).

Row rules: public reads only `status = 'live'` and `deleted_at is null`. Staff `own` scope applies to drafts they created. Directory rows obey `people.consent` and removal requests.

Anchor kinds (admin preview only, public pages render none): `page:<path>`, `section:<page_id>.<key>`, `field:page:<id>.<field>` (for example `field:page:12.seo.title`), `redirect:<id>`, `check:<id>`.

Config knobs: `fields.pages` (which page kinds exist and their slugs), `fields.nav` (top nav items and order), `fields.cta` (get_started, book, call, shop), `fields.directory` (on or off), `fields.locator` (on or off), `fields.web_chat` (off by default), `fields.stages` (draft, review, live, archived). Sample type: `site_pages` (Home, three service pages, About, one location, policies, a links page, all `.example` content, 555-01xx phones).

## Agent actions

| Action | Tool | Verb | Gated | Writes to `change_log` | Undo |
|---|---|---|---|---|---|
| Draft or rewrite a page or section | `update_record` on `site_pages` | E | No (draft only) | `site_pages` update, before and after `sections` | Restores the prior draft |
| Create a new page | `create_page` | C | Yes. The default matrix gives the agent V E on Site, not C, so a new page waits for a yes unless the Owner grants C | `site_pages` insert as a draft | Deletes the draft |
| Publish a page | `publish_page` | P | **Yes**, shows the diff and the live URL; relaxable with `afterHumanApproval` | `site_page_versions` insert, `site_pages.published_version_id` update | Roll back to the previous version, then verify live |
| Edit nav | `update_record` on `site_nav` | E | Yes when the page is live (changes every page) | before and after `items` | Restores prior nav |
| Add or change a redirect | `upsert_redirect` | E | No | `redirects` insert or update | Removes or restores |
| Delete a page | `delete_page` | D | **Yes** | soft delete plus a 301 or 410 row in `redirects` | Restores page and drops the redirect |
| Write SEO fields from the page copy | `update_record` | E | No (draft) | `seo` before and after | Restores |
| Verify a URL is live | `check_url` | read | No | none | n/a |
| Point at a page or section | `navigate`, `highlight` | UI | No | none | n/a |

Background jobs:

- **Post-publish verify** (on every publish): fetches the live URL, confirms a 200, the new copy is present and the canonical is right, then posts "Live at <url>" in the chat or on the approval row. A failed verify rolls back automatically and files a Board card.
- **Daily checks** (06:00 business time): crawls every live page for status, broken links, missing titles or descriptions, duplicate H1s, missing alt text, structured data errors. Results land in `site_checks`; failures file one Board card per page, not one per check.
- **Search ping** (on publish and hourly sweep): tells search engines which URLs changed (an IndexNow-style ping) and refreshes the sitemap.
- **Weekly site note** (Mondays): one paragraph in the Owner's morning summary on which pages gained or lost traffic and which page to improve next, with a draft ready to approve.

## Integrations

- **Rails:** hosting (default Vercel; contract: a git push or deploy hook builds and serves the site, preview URLs per draft), domains (registrar holds the domain; the business keeps it), DNS (apex and `www` records point at hosting; never touch MX or SPF records when editing), database (Postgres for pages and versions).
- **Platform APIs:** search engine site-verification and change-ping endpoints; Search reads search console data for the same site.
- **Webhooks out:** deploy hook on publish. **Webhooks in:** deploy status callback (ready or failed), which drives the post-publish verify.
- **Secrets (names only):** `DEPLOY_HOOK_URL`, `HOSTING_API_TOKEN`, `INDEXNOW_KEY`, `SITE_URL`.

## SaaS replaced

| Product | Risk | Migration |
|---|---|---|
| Squarespace | Easy | Export pages and blog, import into `site_pages` and Content, build the full redirect map from the old sitemap, run both for one week on a preview URL, cut DNS, confirm every old URL resolves, cancel |
| Wix | Easy | Same as Squarespace. The redirect map is the work |
| Webflow | Easy | Export CMS collections to CSV, import, redirect old URLs, parallel run on preview, cut DNS, cancel |
| WordPress.com | Easy | Export XML, import posts to Content and pages to `site_pages`, check plugins that held data (forms, galleries), redirect, cut DNS, cancel |
| Framer | Easy | Rebuild marketing pages from the live site, redirect old URLs, cut DNS, cancel |
| Linktree | No brainer | Rebuild as `/links`, change the URL in each social bio, cancel |
| Beacons | No brainer | Same as Linktree. Move any products it sold into Shop first |

## Acceptance criteria

1. A Contractor never sees Site under Settings, and opening `/admin/site` shows "You don't have access to Site. Ask the Owner." with Request access.
2. Every agent write (draft edit, publish, redirect, nav change) appears in Log with before, after and a working Undo; Undo on a publish restores the previous live version and the public URL shows the old copy after verify.
3. When the agent is asked to publish, the chat shows an approval card with the page path, a side-by-side diff and the live URL, and nothing changes on the public site until an Owner or Admin taps Approve.
4. Every submit button (Save draft, Publish, Send to review, Roll back, Add redirect) shows a spinner and disables while it runs.
5. A Staff user editing a page sees Send to review instead of Publish; after sending, the page shows a "Waiting on approval" chip and the Owner sees the row on Home > Today.
6. A public visitor loading `/` gets a server-rendered page with one H1, the business name in the title, valid Organization structured data, and the CTA button from `fields.cta` in the top nav.
7. A page deleted by the Owner returns a 301 to the chosen target (or 410 if none) within one minute, and the old URL never returns a 404.
8. After any publish, the post-publish verify posts "Live at <url>" with a 200 status, or rolls the page back and files a Board card if the check fails.
9. The daily checks job writes a `site_checks` row per live page, and a page with a broken link shows a red "fail" chip on Checks with the broken URL in one line.
10. An Admin pins a section on the preview into the chat, asks "make this shorter", and the draft changes in place with the section ring flashing and an Undo in the Changes tab.
11. A visitor who submits `/directory/remove/[id]` disappears from the public page on the next render, and the request lands in Inbox.
12. With `fields.web_chat` off, no chat button renders on any public page.

## Open questions

1. **Page editor: blocks or free layout?** Default: ordered blocks from a fixed set (hero, proof strip, text, image, list, FAQ, CTA, gallery, map). The agent edits copy inside blocks; layout changes are a build task.
2. **Does publishing need a code deploy or a data change?** Default: data change. Pages render from `site_pages` and revalidate on publish, so copy ships in seconds without a build. Template changes are code and go through the normal deploy.
3. **Web chat on public pages?** Default: off. Turn it on only when Inbox has a person or a relaxed agent covering replies during business hours.
4. **Who can relax agent publishing?** Default: Owner only, with `afterHumanApproval` as the only relax offered in the first month.
5. **Analytics on public pages?** Default: first-party `page_views` only (own cookie, own middleware, no Google Analytics), with the opt-out page live. Add a third-party tag only if the business runs paid ads that need conversion events.
6. **Directory on by default?** Default: off. Turn on for businesses that list partners, stores or members; only claimed listings are indexed, unclaimed ones show greyed and noindex.
