# Portal: Posts (customer, portal)

- **Module key:** `portal.posts` (stable, never renamed)
- **Tier:** follows Studio and Social (`studio`, `social`, common). Shows only when Studio is enabled.
- **Route:** `/portal/posts`
- **Folder:** `customer/portal/posts/`

## Job

Let a business customer (a store that stocks the brand) make on-brand posts for its own social channels from one sentence, using the brand's templates and real product photos, so the brand gets shelf-level promotion without a design request. The number that tells you it is working: **posts downloaded or shared per active store per month**, and **orders attributed to store posts** where links carry the store's code.

## Users and permissions

- Customer kind `buyer` only: View, Create, Edit, Send/Publish (to the store's own channels) and Export (download) on their own posts (`shared/roles.md` 4g).
- Posts belong to the store; every member of the store sees them.
- Templates, fonts, colors and logo lock to the brand's settings in Studio. A store can add its own name, logo and a photo of its shelf; it cannot change the brand's marks.
- Agent (as the buyer): View, Create and Edit drafts, render. **Gated (customer's yes):** publishing to a connected channel. Downloads are not gated (the customer asked for the file).
- Each generation costs money (model calls and renders). Usage counts against the store's monthly allowance (`fields.posts.monthly_renders`), logged on admin Costs.
- Sensitive fields: none of the brand's internal posts, metrics, or other stores' posts.

## Pages and states

- **Tabs:** Make (`/portal/posts`), My posts (`/portal/posts/mine`), Channels (`/portal/posts/channels`, only when publishing is on).
- **Make:** one prompt box ("New flavor in stock this weekend"), a size picker (square, portrait, story), an optional photo upload (the store's shelf or window), and Generate. The result shows a preview, the caption, hashtags kept to three or fewer, and actions: Edit caption, Swap photo, Try another template, Add motion (short MP4), Download, Copy caption, Share.
- **Record:** URL modal `?post=<id>` with the render per size, caption, history of edits, Download and Share.
- **Share:** on phones uses the device share sheet with the image and caption; on desktop, Download plus Copy caption.
- **Publish** (only when Channels is on and the store connected an account): pick channel and time, then Publish or Schedule.
- **States:** empty My posts says "Make your first post from one sentence." Loading shows a render progress bar (renders take seconds, never a blank screen). Error: "That render failed. Try again." with the prompt kept.
- **Disabled with reason:** Generate disabled with "You've used this month's 40 posts. More on Dec 1." at the allowance; Publish disabled with "Connect a channel first".
- Badge: none.

## Data model

- Owns no tables. Writes Social's `posts` with `customer_id` = the store's company and `kind = customer`, `post_variants` (one per size), and Studio's `designs` and `renders`; uploads go to `files` (Library) tagged source `portal`.
- Product photos come only from the brand's Library items marked cleared for customer use (`consents` on each media item); the agent never uses an uncleared photo.
- Store channel connections, when on, are rows in Social's `channels` with `customer_id`; tokens are stored encrypted, by reference only.
- Every generation writes `model_calls` with cost and the store id, so Costs can show spend per store.
- Anchors: `post:<id>`, `design:<id>`, `slide:<design>:<n>`, `media:<id>` (cleared brand photos only).
- Knobs (on Studio and Social): `fields.templates`, `fields.sizes`, `fields.real_assets_only` (default true). Portal knobs: `fields.posts.monthly_renders` (default 40 per store), `fields.posts.publishing` (default off: download and share only). Sample: `posts` plus `designs`.

## Agent actions

| Action | Tool | Verb | Gated | Writes to `change_log` | Undo |
|---|---|---|---|---|---|
| Make a post from a sentence | `make_customer_post` | C | No | `posts`, `designs`, `renders` inserts; `model_calls` | Yes (soft delete) |
| Change caption, swap photo, change template | `update_record`, `swap_photo` | E | No | before and after | Yes |
| Add motion | `render_motion` | C | No | `renders` insert | Yes |
| Point at a post or a slide | `highlight`, `navigate` | none | No | Nothing | n/a |
| Publish or schedule to the store's channel | `publish_post` | P | Yes | `post_publishes` insert | Yes until it goes out; after, delete is on the platform |

Background jobs: none required. If publishing is on, scheduled posts go out at their slot through Social's publisher.

## Integrations

- **Platform APIs** (only when publishing is on): each social network's posting API through the store's own connected account.
- **Rendering:** the Studio renderer (images and short MP4) and the business's model provider for captions, both metered on Costs.
- **Object storage:** renders served by signed URL; Download gives the full-size file.
- Secrets: per-store channel tokens (stored encrypted, by reference); the renderer and model keys belong to Studio.

## SaaS replaced

| Product | Risk | Migration |
|---|---|---|
| Canva (shared brand templates sent to stockists) | Easy | Export the brand kit and the templates stores use. Rebuild them as Studio templates. Parallel run one month with both links in the stockist email. Cut over by replacing the template links with the portal. Cancel the extra seats or shared team. |
| Buffer (when the brand schedules for stores) | No brainer | Only if publishing is on. Stores connect their own channels in Channels; the brand stops posting on their behalf; cancel. |

## Acceptance criteria

1. A shopper, member, partner or client never sees Posts in the nav, and a deep link to `/portal/posts?post=12` shows the not-found page.
2. Every agent write on Posts (make, edit, swap, publish) appears in Log with before, after and a working Undo where the PRD allows it.
3. Asked to post it to the store's account, the agent shows "Publish to @cornerstore.example on Instagram, Sat 10:00 AM, square image and caption" with one Approve button and publishes nothing until approved.
4. Every submit button on Posts, including Generate, shows a spinner and disables while it runs.
5. A buyer types "new flavor in stock this weekend" and gets a branded square post with a cleared product photo and a caption in under 30 seconds.
6. A buyer uploads a shelf photo and swaps it in; the brand logo and colors stay locked.
7. At the monthly allowance, Generate is disabled with the reset date, and admin Costs shows the store's spend for the month.
8. On a phone, Share opens the share sheet with the image and the caption.
9. A post from store A is never visible to store B, even by URL.

## Open questions

1. **Turn on direct publishing to store channels?** Default: off; download and share cover it without holding the store's tokens.
2. **Monthly allowance per store?** Default: 40 renders, raised per store from admin.
3. **Let stores pick from all brand photos or only a curated set?** Default: only photos marked cleared for customer use.
