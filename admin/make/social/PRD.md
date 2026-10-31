# Social (admin, Make)

- **Module key:** `social` (stable, never renamed)
- **Tier:** common
- **Route:** `/admin/social`
- **Folder:** `admin/make/social/`

## Job

"Next week's posts are drafted from our real stuff, I approve them from my phone in two minutes, and they go out at the right time without me touching a scheduler." The agent proposes a batch, the owner comments or approves, the agent posts the approved pick at the planned slot and reports what worked.

The number: **share of planned slots that went out on time with an approved post**, per week (target 100%). Secondary: median minutes from "ready for review" to the owner's decision.

## Users and permissions

Starts from `shared/roles.md` section 4d. What differs or needs saying:

| Type | Scope | Notes |
|---|---|---|
| Owner | all | Default approver (`fields.approval: owner`). Reviews from a phone. |
| Admin | all | Posts directly. Approves when `fields.approval` is `admin` or the Owner delegated it. |
| Staff | all, V C E | Uploads cuts, writes captions, comments. Post shows as **Submit for approval**. |
| Contractor | hidden | |
| Customer (buyer kind) | own, V C E P | Portal Posts: makes posts for their own channels from the business's kit (Studio) and posts them to their own connected accounts. Never sees the business's calendar, channels or metrics. |
| Agent | as its role | V C E. Post (`social.send`) gated `*`. |

- **Gated agent verbs:** `social.send` (post to a channel, delete a live post, reply publicly to a comment). The usual relax: "Go ahead" with the limit `afterHumanApproval: true`, so a post a person approved goes out at its slot with no second yes. The Owner can add `hours: business` and a daily cap per channel.
- **Comment-to-DM keywords** are a send. They run only when relaxed, and only as a reply to the person who commented the keyword (`shared/roles.md` rule 6 treats it as a requested reply once relaxed; the switch is off by default).
- **Never relaxable here:** approving a post (Approve is always human, including the agent's own drafts), connecting or disconnecting a channel (Configure).
- **Sensitive fields:** `channels.token_ref` is never rendered to anyone. `post_metrics` paid fields (boost spend) are column grants for Owner and Admin.

## Pages and states

Tabs in nav order, each a sub-route.

| Tab | Route | What it shows |
|---|---|---|
| Review | `/admin/social` | The queue that needs a person: posts in review and changes requested, oldest first, as big phone-first cards with a thumbnail, the slot, the channel icons and one button. |
| Calendar | `/admin/social/calendar` | Week and month views. Each slot shows its planned format (from `fields.rotation`), the post in it, and its state. Empty planned slots show the format name in neutral. |
| Posts | `/admin/social/posts` | Every post in every state: table with thumbnail, caption start, status chip, channels, slot, owner. |
| Grid | `/admin/social/grid` | A 3-column preview of how the profile will look with scheduled posts placed ahead of live ones, per channel. Drag to reorder scheduled posts (Edit). |
| What worked | `/admin/social/what-worked` | Last 30 days: top posts by the metric each channel reports, with the agent's "why it worked" note on the top three. Charts first, sentences under. |
| Channels | `/admin/social/channels` | Connected accounts per network, health (token valid, last post), posting limits. Connect and disconnect need K. |
| Settings | `/admin/social/settings` | Approval mode, weekday rotation, best-time slots, real-assets-only, caption rules per network. Hidden without K. |

**Record view.** Full route `/admin/social/[id]`, phone-first. Header: status chip, slot, channels. Body: player for video (scrubbable, timecode visible) or swipeable carousel. Under it: timecoded comments, then per-platform variants (caption, hashtags, first comment, cover frame), then **Post** buttons per channel. Record tabs: Review, Variants, Activity, Files. On a phone, the primary action is pinned to the bottom: **Approve** for an approver on an in-review post, **Submit for approval** for a drafter.

**Timecoded comments.** Tap the player at any moment and type: the comment stores the time and shows as a dot on the scrubber. Tapping a comment seeks to it. A comment can be resolved. "Request changes" bundles open comments and sends the post back.

**States:**

- **Empty.** Review: "Nothing waiting on you. Next week's batch drafts Sunday at 18:00." Calendar: planned format names in every slot. Posts: "No posts yet. Upload a cut or ask the agent to draft next week from the Library." Channels: "Connect a channel to post. Drafts and review work without one."
- **Loading.** Skeleton cards with a grey 9:16 or 4:5 block at the post's real aspect. Video loads poster first, then streams.
- **Error.** Post failed at the network: the record shows a bad-status chip "Failed on <network>: <reason>" with **Retry** and the slot stays visible on Calendar in red. A disconnected channel shows on Channels with **Reconnect** and on every post scheduled to it.
- **Permission.** No V: nav hidden, deep link shows no-access. Staff: Post buttons read **Submit for approval**. Disabled only for fixable states: "Reconnect this channel to post", "Caption is 2,310 characters; this network allows 2,200", "Add a cover frame", "Posting..." with spinner.

**Quick views (chips above Posts):** Needs review, Changes requested, Approved, Scheduled, Posted, Failed, Mine. Filters: status, channel, format, date range, source (agent drafted, uploaded).

**Badge count:** posts in review where the signed-in user can approve, plus failed posts.

## Data model

Every table carries `id`, `org_id`, `owner_id`, `created_at`, `updated_at`, `deleted_at`.

**`posts`**

| Column | Type | Notes |
|---|---|---|
| `kind` | text | `video`, `carousel`, `image`, `story`, `text` (from `fields.kinds`) |
| `format` | text | Rotation format key (`myth`, `explainer`, `proof`, `quote`), from `fields.rotation` |
| `status` | text | `draft`, `in_review`, `changes_requested`, `approved`, `scheduled`, `posted`, `failed`, `archived` |
| `title` | text | Internal name |
| `media` | jsonb | `[{ key, file_id, order, cover_ms }]`, items keyed by content hash. Points at Library `media` and `files`. |
| `slot_at` | timestamptz | Planned time |
| `batch_id` | fk `post_batches`, null | |
| `source` | jsonb | `{ kind: "library"|"article"|"review"|"design"|"upload", id }`. With `real_assets_only` on, an agent draft must have a real source. |
| `approved_by`, `approved_at` | fk `users`, timestamptz | |
| `assignee_id` | fk `users` | |
| `customer_id` | fk `people`, null | Set on portal posts |
| `why_it_worked` | text | Agent note on top performers |
| `custom` | jsonb | |

**`post_variants`**: `post_id`, `channel_id`, `caption`, `hashtags text[]`, `first_comment`, `cover_file_id`, `crop` (from Library crops), `char_count`, `valid bool`, `errors text[]`.

**`post_comments`**: `post_id`, `author_kind` (person, agent), `author_id`, `body`, `timecode_ms int null`, `slide int null`, `resolved_at`, `resolved_by`.

**`post_publishes`**: `post_id`, `channel_id`, `status` (queued, sent, failed), `external_id`, `external_url`, `attempts`, `error`, `sent_at`. One row per channel per post.

**`post_metrics`**: `publish_id`, `captured_at`, `reach`, `views`, `likes`, `comments`, `shares`, `saves`, `clicks`, `watch_ms_avg`, `spend_cents`, `currency`. Captured at 1h, 24h, 7d.

**`channels`**: `network`, `handle`, `account_ref`, `token_ref` (secret name, never the token), `status` (ok, expired, revoked), `limits jsonb` (caption max, hashtag max, video max seconds, sizes), `best_times jsonb`, `customer_id` (null for the business's own).

**`post_batches`**: `week_of`, `status` (proposed, in_review, locked), `preview_sent_at`.

**`dm_keywords`**: `channel_id`, `keyword`, `reply_body`, `link`, `active bool`, `sent_count`.

**Foreign keys into shared tables:** `files` and Library `media` (assets), `people` (portal customers, commenters who become leads), `threads`/`messages` (DM replies and comment replies land in Inbox), `approvals`, `change_log`, `activities`.

**Row rules for `own` scope:** a Customer sees `posts` and `channels` where `customer_id` is theirs. Staff "Mine" matches `owner_id` or `assignee_id`.

**Anchor kinds:**

- `post:<id>` on every card, row, calendar slot and grid tile
- `comment:<id>`, plus `field:post:<id>.slot_at` and `field:post:<id>.status`
- `variant:<post>:<channel>` and `field:variant:<post>:<channel>.caption`
- `slot:<iso datetime>` for an empty planned slot
- `channel:<id>`, `batch:<id>`

**Config knobs:** `fields.channels` (which networks are on), `fields.approval` (`owner`, `admin`, `none`; `none` still needs a person unless the agent is relaxed), `fields.rotation` (weekday to format map, default Mon tip, Tue video, Wed explainer, Thu carousel, Fri proof, Sat video, Sun off), `fields.real_assets_only` (default true: agent drafts must use Library media or Studio designs built from Library media, never generated people), `fields.slots_per_day` (default 1), `fields.preview_hour` (default 05:00). **Sample:** `posts` (a locked week of 7 posts across 3 formats, 2 in review with timecoded comments, 10 posted with metrics, 2 sample channels on `.example` handles).

## Agent actions

| Action | Tool | Verb | Gated | Writes to `change_log` | Undo |
|---|---|---|---|---|---|
| Read queue, calendar, metrics | `query_db`, `get_record`, `social_summary` | view | no | nothing | n/a |
| Propose next week's batch from real content into best-time slots | `propose_batch` | create | no (it is drafts) | insert `post_batches`, `posts`, `post_variants` | Undo the batch removes every draft in it |
| Write captions per network within limits | `write_variants` | edit | no | update `post_variants` | restore |
| Swap the asset or cover frame | `update_record` | edit | no | update `posts.media` or `cover_file_id` | restore |
| Reply to a timecoded comment, fix and resubmit | `resolve_comment`, `request_review` | edit | no | update comment, status, insert `approvals` | restore |
| Move a post to another slot | `move_slot` | edit | no (over 5 posts: asks) | update `slot_at` | restore |
| Send the morning preview to the approver | `send_preview` | none (system message to the user who asked for it) | no | insert `notifications` | n/a |
| Post an approved pick at its slot | `publish_post` | send | `*` | insert `post_publishes`, update status | Delete the live post on the network (itself a gated send) |
| Reply publicly to a comment | `reply_comment` | send | `*` | insert `messages` | Delete the reply (gated) |
| Comment-to-DM keyword reply | `dm_keyword_reply` | send | `*`, off by default | insert `messages`, increment `sent_count` | n/a, logged |
| Write "why it worked" for the top three | `explain_top` | edit | no | update `why_it_worked` | restore |
| Point at things | `navigate`, `highlight`, `show_chart` | none | no | nothing | n/a |

**Rules the tools enforce:**

1. With `real_assets_only` on, `propose_batch` only drafts from Library media, published Content, approved Reviews or Studio designs. It never invents a testimonial, a result or a person.
2. A variant that breaks a network limit is saved with `valid = false` and the reason; it never posts.
3. `publish_post` re-checks at send time: still approved, channel healthy, slot not in the past by more than 30 minutes. Otherwise it fails the slot and files a Board card.
4. The agent never approves, including its own drafts. It can say "ready for you" and send the preview.

**Background jobs:**

| Job | Trigger | Produces |
|---|---|---|
| Weekly batch | Sunday 18:00 | Next week's drafts in every rotation slot, a batch in review, a Home > Today row |
| Morning preview | Daily at `fields.preview_hour` | A notification and email to the approver with today's pick, thumbnail, caption and one Approve link that opens the record |
| Publisher | Every 5 minutes | Posts approved items whose slot has arrived (when relaxed), or queues an approval card at the slot (when gated) |
| Metrics pull | 1h, 24h, 7d after each post | `post_metrics` rows |
| What worked | Monday 07:00 | `why_it_worked` on the last week's top three, a Feed item |
| Channel health | Daily | Token checks; an expiring token files a Board card 7 days before |

## Integrations

- **Rails:** email delivery (morning preview), SMS optional for the preview link. Object storage through Library for media.
- **Platform APIs:** each network's own publishing and insights API, one adapter per network behind one contract: `publish(post, variant) -> { external_id, url }`, `delete(external_id)`, `metrics(external_id) -> {...}`, `comments(since)`, `send_dm(user, body)`, `limits()`. Networks are on per `fields.channels`. Posting rides the network's official API only; no scraping, no unofficial clients.
- **Webhooks in:** network comment and DM webhooks (land in Inbox as threads tagged `social`, and feed comment-to-DM keywords). Token revoked or expired events. **Out:** `social.posted` and `social.failed` events for Home and Insights.
- **Reads from:** Content (`content.published` becomes a post draft), Reviews (approved reviews become quote cards via Studio), Library (media and crops), Studio (designs and renders).
- **Secrets by name:** one per connected channel, stored as `SOCIAL_<NETWORK>_<CHANNEL_ID>_TOKEN` in the secrets store; app config holds only the name. `SOCIAL_WEBHOOK_SECRET`.

## SaaS replaced

From `shared/saas.md`:

| Product | Risk | Migration |
|---|---|---|
| Buffer | No brainer | **Export:** none needed beyond the current queue list. **Import:** re-create queued posts as drafts in YEA (the agent can do it from a CSV or screenshots). **Parallel run:** not needed. **Cutover:** connect each channel in Channels, pause the Buffer queue. **Cancel:** same week. |
| Hootsuite | No brainer | **Export:** scheduled post list and any saved replies. **Import:** queued posts as drafts, saved replies as `dm_keywords` or Inbox snippets. **Parallel run:** one week, YEA drafts, Hootsuite posts. **Cutover:** YEA posts from the next Monday; empty the Hootsuite schedule. **Cancel:** after the first full week posts from YEA. |
| Later | No brainer | **Export:** download the media library. **Import:** media into Library (tagged on upload), scheduled posts as drafts. **Parallel run:** none. **Cutover:** reschedule in YEA, clear Later. **Cancel:** same week. |
| Sprout Social (scheduling half; analytics half moves to Insights) | Easy | **Export:** reporting history as CSV, the only thing worth keeping. **Import:** history into `post_metrics` as archived rows so What worked has a baseline. **Parallel run:** one month of reports side by side. **Cutover:** connect channels, post from YEA. **Cancel:** after the month's numbers match within the network's own reporting. |

## Acceptance criteria

1. A user without `social.view` (a Contractor) never sees Social in the nav, and `/admin/social` shows the no-access page.
2. Every agent write (propose a batch, rewrite a caption, move a slot) appears in Log with before, after and a working Undo; Undo on a batch removes every draft it created.
3. With `social.send` gated, at a post's slot the agent shows an approval card ("Post to 2 channels at 12:30: carousel, 6 slides, caption 182 characters") with one button, Approve, and nothing reaches a network until a person approves.
4. Every submit button (Approve, Request changes, Submit for approval, Post, Retry) shows a spinner and disables while it runs.
5. An Owner on a 390px-wide phone opens the morning preview link, lands on the record, taps the player at 0:07 and leaves a comment; the comment shows a dot at 0:07 on the scrubber and tapping it seeks there.
6. An Owner taps **Request changes**; the post moves to Changes requested, the open comments travel with it, and it leaves the Owner's Review queue.
7. A Staff user's primary action on a draft is **Submit for approval**; they never see a Post button.
8. With `real_assets_only` on, every post in a proposed batch links a real source (Library media, article, review or design), and the batch view shows the source on each card.
9. A caption over a network's limit shows the count and limit under the field and blocks that channel's Post button with the reason.
10. When a network rejects a post, the record shows the failure reason with Retry, the Calendar slot turns red, and a Board card exists.
11. With the Owner's relax set to "Go ahead, only after a person approved", an approved post goes out at its slot with no second approval, and Log shows "Agent, scheduled, as Admin" with the external URL.
12. Grid shows scheduled posts ahead of live ones in the order they will post, and dragging one changes its slot after a confirm.
13. A buyer Customer in Portal Posts sees only their own posts and channels; none of the business's calendar, channels or metrics appear, and the agent's answers in their chat never mention them.
14. The agent never shows an Approve button on its own draft, in chat or on Home > Today.

## Open questions

1. **Which networks ship first?** Recommended default: the two the business already posts to most (ask in the interview); build the adapter contract so a third is one file.
2. **Default approver?** Recommended default: Owner (`fields.approval: owner`), delegable to Admin or a Reviewer named role.
3. **Relax posting on day one?** Recommended default: no. Run one week fully gated so the owner sees the agent's batches, then offer "Go ahead, only after a person approved".
4. **Comment-to-DM keywords?** Recommended default: off. Turn on per keyword once the owner has written the reply and the link.
5. **Video hosting for review cuts?** Recommended default: Library object storage with streaming; files over 500 MB transcode to a review proxy first.
6. **Metric for What worked?** Recommended default: saves plus shares per reach for images and carousels, average watch time for video. Show the network's own numbers, never a blended score.
7. **Stories and ephemeral formats?** Recommended default: supported as a `kind`, excluded from What worked since metrics vanish in 24 hours.
