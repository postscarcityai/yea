# Portal: Listing (customer, portal)

- **Module key:** `portal.listing` (stable, never renamed)
- **Tier:** follows Prospects (`prospects`, industry, B2B selling at volume) with a public directory on (`fields.directory = public`). Shows only then.
- **Route:** `/portal/listing`
- **Folder:** `customer/portal/listing/`

## Job

Let a firm claim and keep its own listing in the business's public directory, and contribute expert answers, so the directory stays accurate without staff typing and the firm earns visibility. The number that tells you it is working: **share of invited firms that claim their listing**, and **share of claimed listings that are complete** (every checklist item done).

## Users and permissions

- Customer kind `partner` only: View and Edit their own listing (`shared/roles.md` 4g), and Create contributions (Content: own contributions).
- Any member of the firm can edit the listing; every edit is logged with who made it.
- Claiming: a firm claims by a claim invite link (`/portal/claim/[token]`) or by signing in with an email on the firm's domain and asking; the second path lands as a request for staff to approve.
- Some fields publish on save (bio, phone, website, hours, photos). Fields that carry trust (licence or registration numbers, the firm name) go to a review queue in admin Prospects before they change on the public page.
- Agent (as the partner): View, Edit listing fields, draft a bio, draft an expert answer for the partner to edit. **Gated (customer's yes):** publishing an edit that changes the public page, and submitting an expert answer. The agent never submits an answer as the partner's own words without the partner editing and pressing Submit (see Content rules below).
- Sensitive fields: staff notes, fit score, outreach status, ad intel, field sources. Never rendered.

## Pages and states

Tabs:

| Tab | Route | Shows |
|---|---|---|
| Listing | `/portal/listing` | The listing as it appears publicly, read-only with Edit. Fields: name, logo, city, service area, phone, website, email, hours, bio, photos, people (name, role, bio, licence number where the business asks for one) |
| Checklist | `/portal/listing/checklist` | What is missing for the listing to be complete and indexed (logo, bio over 40 words, one person, licence verified), each with a Fix button |
| Answers | `/portal/listing/answers` | Expert questions offered to this firm by topic; answer, save draft, submit; status per answer (draft, submitted, in review, published) |
| Preview | `/portal/listing/preview` | The public page exactly as it will render, with a link to the live page |

- **Claim** `/portal/claim/[token]`: "Claim Example Services Co." with one button. Claiming signs the person in and marks the listing claimed. A claimed listing becomes indexable once the checklist is complete; unclaimed listings stay greyed and noindex on the Site.
- **Answers** rule: answers must be in the firm's own words. Paste into the answer box is blocked and the attempt is counted on the contribution; the agent's draft appears beside the box as a reference the partner retypes or adapts, never inserted.
- **States:** empty Answers says "No questions for your area yet." Loading skeletons. Error with Retry. A field in review shows "In review" with the submitted value under the live one.
- **Disabled with reason:** Submit answer disabled until the answer is at least 60 words: "Write at least 60 words (now 42)".
- Badge: none. Home shows checklist items missing.

## Data model

- Owns no tables. Reads and writes `prospects` (the listing row, public fields only), `prospect_people` (people on the listing), `field_sources` (every portal edit stores source `portal` and the editor's user id), `match_reviews` (trust fields waiting for review) from Prospects; `contributions` from Content; `files` for logo and photos.
- Claim state lives on `prospects.custom.claimed_at` and `claimed_by`.
- Every public-field change writes `change_log` and pings the search rail through the Site's index sync so the page is recrawled.
- Anchors: `prospect:<id>` (own), `field:prospect:<id>.<field>`, `prospect_person:<id>`, `contribution:<id>`, `checklist_item:<key>`.
- Knobs (on Prospects and Content): `fields.directory` (public or not), `fields.contributors` (on or off). Portal knobs: `fields.listing.review_fields` (default name and licence numbers), `fields.listing.min_answer_words` (default 60). Sample: `prospect_list`.

## Agent actions

| Action | Tool | Verb | Gated | Writes to `change_log` | Undo |
|---|---|---|---|---|---|
| What is missing on my listing | `query_db`, `highlight` | V | No | Nothing | n/a |
| Update phone, hours, website | `update_record` on `prospects` | E | Yes (public change) | field before and after, `field_sources` row | Yes |
| Draft a bio from my website | `draft_listing_bio` | C | No (draft only) | draft stored on the listing, not published | Yes |
| Add a person to the listing | `update_record` on `prospect_people` | C | Yes (public change) | row insert | Yes |
| Draft a reference answer | `draft_answer_reference` | C | No | reference text on the contribution, never in the answer field | Yes |
| Submit my answer | none | C | Only the partner, by pressing Submit | n/a | n/a |
| Ask for lead opt-in or other help | `file_request` | C | No | Board card | Yes while New |

Background jobs: weekly "complete your listing" nudge to claimed firms with checklist items missing (system message to a claimed customer, stops when complete); trust-field review queue in admin Prospects.

## Integrations

- **Hosting:** public directory pages rebuild on change.
- **Search engines:** the Site's index sync submits changed URLs; only claimed, complete listings are indexed.
- **Email delivery:** claim invites (sent from admin Outreach), nudges, "your answer is live".
- Webhooks: none. Secrets: none of its own (index sync key belongs to Site).

## SaaS replaced

None from `shared/saas.md`. Directory and listing software is not priced in the explorer yet; see admin Prospects for what the inventories saw.

## Acceptance criteria

1. A non-partner customer never sees Listing in the nav, and a deep link to `/portal/listing/answers` shows the not-found page.
2. Every agent write on Listing appears in Log with before, after and a working Undo, and in admin Prospects field sources with source `portal`.
3. Asked to change the phone number, the agent shows "Change public phone from 555-0142 to 555-0188 on your listing" with one Approve button and changes nothing until approved.
4. Every submit button on Listing shows a spinner and disables while it runs.
5. A firm opens a claim link, presses Claim, lands on Listing signed in, and the admin record shows claimed with the time and person.
6. A partner edits the licence number; the public page keeps the old value with the new one shown as In review until staff approve it.
7. Pasting into the answer box does nothing and increments the paste count on that contribution.
8. A listing with every checklist item done becomes indexable; the public page drops noindex on the next build.
9. Two members of the same firm edit the bio; both edits appear in the record history with each person's name.

## Open questions

1. **Which fields need staff review?** Default: firm name and licence or registration numbers; everything else publishes on save.
2. **Allow unclaimed firms to request removal from the portal?** Default: removal stays on the public Site's remove page, no sign-in needed.
3. **Minimum answer length?** Default: 60 words.
