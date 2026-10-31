# Prospects (admin, Grow)

- **Module key:** `prospects`
- **Tier:** industry (B2B selling at volume)
- **Route:** `/admin/prospects`
- **Folder:** `admin/grow/prospects/`

## Job

"The whole market in one list, ranked by fit, ready for outreach." Every business that could buy from us, placed in a market, scored against our best customers with plain reasons, with the right person found and every field traced to its source.

The number: **fit precision**, the share of prospects scored High that become a qualified lead within 90 days of first outreach. Second number: share of the market covered (prospects found versus estimated total in each market).

## Users and permissions

Starts from `shared/roles.md` section 4b. Differences only:

| User type | Prospects |
|---|---|
| Owner, Admin | all |
| Staff | V C E. No D, X, K. Can override a fit score with a note |
| Contractor | hidden. Prospects reach a rep only once enrolled or converted into their book |
| Customer | own: V E on their own listing, when `fields.directory` is public and they claimed it (Portal Listing) |
| Agent | V C E |

- **Gated agent verbs:** none inside Prospects (it never sends). Sending happens in Outreach, gated there. Bulk edits over 5 records still ask.
- **Rebuild ideal customer profile** and **edit fit rules** are Configure: Owner and Admin only, never the agent.
- **Sensitive fields:** personal emails and mobile numbers found for prospect people (`prospect_people.personal_email`, `mobile`) are a column grant, off for Staff by default. Licence numbers are not sensitive (public record).

## Pages and states

Tabs in nav order:

| Tab | Route | What it shows |
|---|---|---|
| All | `/admin/prospects` | Every prospect: name, market, kind, fit band with top reason, outreach status, claimed or not, last checked. 50 per page, server paged |
| Fit scores | `/admin/prospects/fit` | Open prospects ranked by fit, reasons inline, Override band with a note |
| Ideal customer | `/admin/prospects/icp` | The profile built from real customers: weights, signals, summary, team notes. Rebuild button (K) |
| Markets | `/admin/prospects/markets` | Market by kind coverage grid: found, contacted, customers, with gaps highlighted |
| People found | `/admin/prospects/people` | Every person found across prospects, role, source, confidence, cross-checks (on two listings, missing licence) |
| Review queue | `/admin/prospects/review` | Uncertain matches (licence, registration, duplicate business) with Attach or Not a match |
| Ad intel | `/admin/prospects/ads` | Who runs ads, on which platforms, which tracking and booking tools their site uses |
| Settings | `/admin/prospects/settings` | Fit rules, markets, directory on or off, kinds. Hidden without K |

**Record view:** full route `/admin/prospects/[id]`. Header: name, market, fit band chip, outreach status, primary action (Enroll in sequence, or Open in Pipeline once converted). Tabs: **Overview** (facts, fit reasons, notes), **People** (found contacts with role and confidence), **Intel** (ads, site tools, reviews count), **Field sources** (every field with where it came from and when).

**Quick views:** High fit not contacted, Ready to invite, Engaged, Claimed, Needs review, Runs ads. Filters: market, kind, fit band, status, claimed, has email, has phone.

**States:**

- **Empty:** "Your market goes here. Import a list or ask the agent to build one for a market." Buttons: Import CSV, Build a market.
- **Loading:** table skeleton; Markets grid shows the axes first.
- **Error:** "Prospects didn't load. Try again." with Retry. A failed enrichment shows on the record as "Couldn't reach their site on <date>", not as a page error.
- **Permission:** hidden for Contractor and Customer in admin; deep link shows no-access. Without K the Rebuild and Settings controls are not rendered. Override shows only with E.
- **Disabled with reason:** Enroll shows "No email found yet" when no contact is reachable; "On do-not-contact".

**Badge:** none by default. The Review queue count shows as a tab count.

## Data model

| Table | Columns |
|---|---|
| `prospects` | `id`, `org_id`, `company_id` (fk `companies`), `market_id`, `kind`, `status` (`found`, `ready`, `invited`, `engaged`, `claimed`, `customer`, `not_now`, `removed`), `priority` int, `claimed_at`, `listing_public` bool, `last_checked_at`, `custom` jsonb, `owner_id`, `created_at`, `updated_at`, `deleted_at` |
| `fit_scores` | `id`, `prospect_id`, `band` (`high`, `mid`, `low`), `score` int, `reasons` jsonb, `icp_version`, `override_band`, `override_note`, `override_by`, `scored_at` |
| `icp_profiles` | `id`, `org_id`, `version` int, `weights` jsonb, `signals` jsonb, `summary` text, `team_notes` text, `built_from_count` int, `built_at` |
| `markets` | `id`, `org_id`, `name`, `geo` jsonb (states, metros, ZIPs), `kinds` text[], `estimated_total` int |
| `prospect_people` | `id`, `prospect_id`, `person_id` (fk `people`, once promoted), `name`, `role`, `work_email`, `personal_email` (sensitive), `mobile` (sensitive), `source`, `confidence` |
| `field_sources` | `id`, `subject_kind`, `subject_id`, `field`, `value`, `source` (public record, website, directory, person), `source_url`, `fetched_at` |
| `match_reviews` | `id`, `prospect_id`, `kind` (`licence`, `registration`, `duplicate`), `candidate` jsonb, `confidence`, `decided` (`attach`, `not_a_match`), `decided_by`, `decided_at` |
| `ad_intel` | `id`, `prospect_id`, `platform`, `running` bool, `site_tools` text[], `checked_at`, `evidence_url` |

- **Shared:** `companies` (a prospect is a company of kind prospect until it buys), `people`, `do_not_contact`, `activities`, `change_log`.
- **Row rules:** Customer reads and edits only the `prospects` and `companies` row they claimed (`customer_id`), and only listing columns.
- **Anchor kinds:** `prospect:<id>`, `market:<id>`, `field:prospect:<id>.<field>`, `review:match:<id>`.
- **Config knobs:** `label` (Prospects, Market, Firms, Stores), `fields.fit_rules`, `fields.markets`, `fields.directory` (`public` or `private`, only claimed listings indexed when public), `fields.kinds`, `fields.enrich_budget_cents`.
- **Sample type:** `prospect_list`. Seeds 2 markets, 400 prospects, 60 with people, 8 in Review queue, fictional names on `.example` domains.

## Agent actions

| Action | Tool | Verb | Gated | Writes to `change_log` | Undo |
|---|---|---|---|---|---|
| Rebuild the ideal customer profile from real customers | `rebuild_icp` | K (draft only) | Agent drafts, Owner or Admin applies | New `icp_profiles` version on apply | Revert to prior version |
| Score fit with reasons | `score_fit` | E | No | `fit_scores` row | Restores prior score |
| Enrich from public records and websites | `enrich_prospect` | E | No (budget capped) | Each field plus a `field_sources` row | Clears filled fields |
| Find the right person | `find_people` | C | No | `prospect_people` rows | Removes them |
| Match a licence or registration | `match_record` | E | Uncertain matches go to Review queue | `match_reviews` or attached field | Detaches |
| Check who runs ads | `scan_ad_intel` | E | No | `ad_intel` row | Removes it |
| Place prospects in markets | `place_in_market` | E | Over 5 asks | `market_id` | Restores |
| Hand a list to Outreach | `enroll_in_sequence` | C | No; steps gated in Outreach | `enrollments` | Unenrolls |

**Background jobs:**

- **Weekly public record import:** new and changed licences or registrations per market; certain matches attach, uncertain ones go to Review queue.
- **Weekly site recrawl:** public business emails and phones from prospect websites, polite rate, robots respected.
- **Nightly re-score:** up to a set number of prospects whose facts changed, logged with cost.
- **Monthly ICP rebuild proposal:** drafts a new version when 10 or more new customers landed; the Owner applies it.

## Integrations

- **Database** (default Neon Postgres). Large tables: page on the server, index `market_id`, `status`, `band`.
- **Platform APIs:** a search engine API for finding sites and people, ad platforms' public ad libraries for ad intel, a places API for address and category, public record download endpoints for licences or registrations. All budget capped in Costs.
- **Webhooks:** none.
- **Secrets by name:** `SEARCH_API_KEY`, `PLACES_API_KEY`, `CRAWL_API_KEY` (optional).
- No email delivery: Prospects never sends.

## SaaS replaced

None priced in `shared/saas.md`. Prospect data and enrichment tools are not in the explorer yet, so no product is listed here. When the explorer adds a prospecting category, add the rows with their risk label; expected risk is Easy (lists export to CSV, no money or consent attached).

Migration pattern for any list tool a business pays for: export the list with source columns, import into `prospects` with `field_sources` set to the tool's name, re-score, cancel at the end of the paid term.

## Acceptance criteria

1. A Contractor never sees Prospects in the nav, and a deep link shows the no-access page.
2. Every agent write (score, enrich, match, place) appears in Log with before, after and a working Undo.
3. When the agent drafts a new ideal customer profile, the Owner sees the weight changes side by side with the current version and one Apply button; the agent cannot apply it.
4. Every submit button (Override, Attach, Rebuild, Import) shows a spinner and disables while it runs.
5. A Staff user opens Fit scores and every High prospect shows at least two plain reasons tied to the profile.
6. A Staff user overrides a band with a note; the note appears in Ideal customer team notes and the next rebuild proposal cites it.
7. On any prospect record, the Field sources tab shows a source and date for every non-empty field.
8. An uncertain licence match lands in Review queue; Attach writes the licence to the record, Not a match removes it from the queue and it never returns for that prospect.
9. With `fields.directory = public`, an unclaimed prospect's public page renders greyed and noindex; after the business claims it, the page is indexed and the business can edit it in Portal Listing.
10. An Admin selects 30 High fit prospects and clicks Enroll; they appear in Outreach with step 1 drafted and waiting.
11. Enrichment stops when `fields.enrich_budget_cents` is reached for the month and a Board card asks the Owner for more.

## Open questions

1. **Public directory on by default?** Recommended: off. Turn on only for businesses whose model is a directory or a partner network.
2. **Re-score volume per night?** Recommended: 25 prospects, raised once Costs shows the per-score cost.
3. **Personal emails and mobiles: collect at all?** Recommended: no by default. Work contacts only; turn on per market with a written reason.
4. **Who can rebuild the profile?** Recommended: Owner and Admin only, with a minimum of 10 real customers behind it.
5. **When does a prospect leave Prospects?** Recommended: when it converts to a lead or account it stays as `status = customer`, read-only, and Pipeline owns it from there.
