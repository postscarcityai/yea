# YEA module map

Part of the YEA docs. Revised 2026-10-31.


This file is the single source for: the admin left nav, the customer side, the repo folder tree, the module list, and the config knobs an onboarding agent sets. `shared/roles.md` owns the verb-level permission matrix; this file only says which user types see each module. Each folder holds one PRD.


---

## 1. The calls I made, and why

1. **Five groups, not six.** Grow, Sell, Make, Know, Run. The draft "Talk" group is gone:
   - **Inbox goes to the top of the nav, ungrouped, under Home.** Both left-nav apps in the inventories pin Dashboard then Inbox above every group. It is the second thing every operator checks.
   - **Chat is the right panel, not a page.** It lives on every screen, so it gets no nav item.
   - **Voice is a mode of the chat panel** (a Talk button in the panel header). What gets asked on a call lands on the Board, and the conversation record lands on the person it was about. One proven app ran voice as its own tab; with Board and People in place that tab has nothing left of its own.
2. **Group order is Grow, Sell, Make, Know, Run.** Nav order follows the operator's day: people waiting on you, then money waiting on you, then the work you make, then reading the numbers, then upkeep. Group order is a knob, so a shop that lives on orders puts Sell first.
3. **Nav items are modules. Pages inside a module are tabs.** One level of nesting (group, then item), never two. This keeps the nav short and matches all three left-nav apps. Tabs are sub-routes so every view is a link.
4. **Routes are flat, folders are grouped.** Route is `/admin/<module>`. Folder is `admin/<group>/<module>/`. Groups get renamed and reordered by config; a flat route means a rename never breaks a saved link.
5. **Campaigns stays in Grow** (it brings people back). **Reviews moves to Grow** (it brings new people in). **Promotions folds into Catalog.** **Data hygiene folds into Settings.** **Playbook goes to Know** (it is what the business knows about itself).
6. **The customer side keeps a top nav on public pages and gets the left-nav shell once signed in.** Every proven app uses a top nav for public pages; that is correct for marketing and paid traffic. The signed-in portal is a work surface, so it uses the same shell, nav and chat as admin. That is the "one eternal left nav" across both sides.
7. **One shell for every signed-in user.** Contractors (field reps, partners who work your book) get the admin shell filtered to their own records, not a separate portal. Customers get the portal shell. Same components, same chat, different nav items and data.
8. **Three modules are marked "not yet proven".** Bookings, Documents and Money. The SaaS research says businesses pay for them, the inventories show partial versions only. They stay in the map because the finale needs them for service businesses. Their PRDs start from the spec, not from code.

---

## 2. User types (short form)

Codes used in every module below. `shared/roles.md` owns the full matrix.

| Code | User type | Lands on |
|---|---|---|
| O | Owner | /admin |
| A | Admin | /admin |
| S | Staff | /admin |
| C | Contractor (reps, partners, freelancers). Sees own records only | /admin |
| Cu | Customer (kinds: shopper, buyer, member, partner, client) | /portal |
| Ag | Agent. Acts with the permissions of the role it runs as. Every write logged with undo | everywhere its role allows |

"Sees" in the module blocks means the module shows in that user type's nav. "Own" means filtered to records they own or are assigned.

---

## 3. The nav tree, exactly as it renders

### 3a. Admin (signed in as O, A, S, C)

Label first, then route, then the folder that holds its PRD. Badges show live counts (the queue that needs a person). A group with no enabled modules disappears. A collapsed group shows the sum of its badges.

```
Home                     /admin                    admin/home/
Inbox            (badge) /admin/inbox              admin/inbox/
Grow
  Leads          (badge) /admin/leads              admin/grow/leads/
  Pipeline       (badge) /admin/pipeline           admin/grow/pipeline/
  People                 /admin/people             admin/grow/people/
  Prospects              /admin/prospects          admin/grow/prospects/
  Outreach       (badge) /admin/outreach           admin/grow/outreach/
  Campaigns      (badge) /admin/campaigns          admin/grow/campaigns/
  Reviews        (badge) /admin/reviews            admin/grow/reviews/
  Programs               /admin/programs           admin/grow/programs/
  Reps                   /admin/reps               admin/grow/reps/
Sell
  Orders         (badge) /admin/orders             admin/sell/orders/
  Catalog                /admin/catalog            admin/sell/catalog/
  Bookings       (badge) /admin/bookings           admin/sell/bookings/
  Jobs           (badge) /admin/jobs               admin/sell/jobs/
  Marketplace    (badge) /admin/marketplace        admin/sell/marketplace/
  Documents              /admin/documents          admin/sell/documents/
  Money          (badge) /admin/money              admin/sell/money/
Make
  Content        (badge) /admin/content            admin/make/content/
  Social         (badge) /admin/social             admin/make/social/
  Library                /admin/library            admin/make/library/
  Studio                 /admin/studio             admin/make/studio/
Know
  Insights               /admin/insights           admin/know/insights/
  Search                 /admin/search             admin/know/search/
  Views                  /admin/views              admin/know/views/
  Goals                  /admin/goals              admin/know/goals/
  Costs                  /admin/costs              admin/know/costs/
  Playbook               /admin/playbook           admin/know/playbook/
  Calls                  /admin/calls              admin/know/calls/
Run
  Team                   /admin/team               admin/run/team/
  Agents                 /admin/agents             admin/run/agents/
  Board          (badge) /admin/board              admin/run/board/
  Log                    /admin/log                admin/run/log/
  Settings               /admin/settings           admin/run/settings/
---
[You]  menu: My profile /admin/me, Switch view (company + user type, demo only), View site /, Sign out
[Chat] right panel on every page, Cmd/Ctrl+J, not a nav item       shared/chat.md
```

Records open as a URL modal on the module route (`/admin/leads?lead=12`) or a full record route (`/admin/pipeline/[id]`) when the record has tabs. Each module block lists which.

### 3b. Customer side

Public pages use a top nav (no login, built for paid and organic traffic). Signed-in customers get the same left-nav shell as admin.

```
PUBLIC (top nav)
  Home                   /                         customer/site/
  [Industry pages]       /<slug>                   customer/site/        (services, about, results, locations, directory, stores)
  Blog                   /blog                     customer/site/        (rendered from Make > Content)
  Shop                   /shop                     customer/shop/
  Get started (CTA)      /start                    customer/intake/
  Sign in                /portal/login             customer/portal/
  Cart           (count) /cart                     customer/shop/
  Report (by link)       /r/[slug]                 customer/intake/      (private by unguessable link)

PORTAL (left nav, signed in as Cu)
  Home                   /portal                   customer/portal/home/
  Orders                 /portal/orders            customer/portal/orders/
  Reorder                /portal/reorder           customer/portal/reorder/
  Bookings               /portal/bookings          customer/portal/bookings/
  Documents              /portal/documents         customer/portal/documents/
  Invoices       (badge) /portal/invoices          customer/portal/invoices/
  Rewards                /portal/rewards           customer/portal/rewards/
  Leads          (badge) /portal/leads             customer/portal/leads/
  Listing                /portal/listing           customer/portal/listing/
  Posts                  /portal/posts             customer/portal/posts/
  Kit                    /portal/kit               customer/portal/kit/
  Account                /portal/account           customer/portal/account/
[Chat] right panel, customer permissions, same component
```

Which portal items show is driven by the customer kind and the admin modules that are on: Orders and Reorder need Sell > Orders; Bookings needs Sell > Bookings; Documents needs Sell > Documents or Make > Content reports; Invoices needs Sell > Money; Rewards needs Grow > Programs; Leads needs Sell > Marketplace; Listing needs Grow > Prospects with a public directory; Posts and Kit need Make > Studio. Account always shows.

### 3c. Repo folder tree

This is the repo tree. One PRD.md per leaf.

```
README.md
shared/      roles.md  chat.md  data-model.md  design-system.md  saas.md  modules.md (this map, stripped)
admin/
  home/  inbox/
  grow/  leads/ pipeline/ people/ prospects/ outreach/ campaigns/ reviews/ programs/ reps/
  sell/  orders/ catalog/ bookings/ jobs/ marketplace/ documents/ money/
  make/  content/ social/ library/ studio/
  know/  insights/ search/ views/ goals/ costs/ playbook/ calls/
  run/   team/ agents/ board/ log/ settings/
customer/
  site/  shop/  intake/
  portal/  home/ orders/ reorder/ bookings/ documents/ invoices/ rewards/ leads/ listing/ posts/ kit/ account/
```

38 module folders (34 admin, 4 customer) plus 12 portal page folders.

---

## 4. Tiers

| Tier | Meaning | Modules |
|---|---|---|
| core | Every business gets it, on by default, cannot be switched off (only relabeled) | Home, Inbox, Leads, People, Views, Goals, Team, Agents, Board, Log, Settings, Site, Intake, Portal (Home, Account) |
| common | Most businesses want it; on or off by config | Pipeline, Outreach, Campaigns, Reviews, Orders, Catalog, Bookings, Documents, Money, Content, Social, Library, Studio, Insights, Search, Costs, Playbook, Calls, Shop |
| industry | Switched on for a business model; usually relabeled | Prospects (B2B selling at volume), Programs (consumer brands), Reps (field sales teams), Jobs (service, case and project work), Marketplace (businesses that route or resell leads, bookings or work) |

Count: 14 core, 19 common, 5 industry.

---

## 5. Knobs every module supports

The finale (PSAI-33) and the fictional companies (PSAI-25) configure an app by writing one config object. Every module takes the same four knobs; some add their own (listed per module).

```ts
type ModuleConfig = {
  key: string;            // stable, never changes: "leads"
  enabled: boolean;       // core modules ignore false
  label: string;          // nav label: "Leads" -> "Inquiries"
  group?: GroupKey;       // move to another group (rare)
  fields: {               // module-specific shape
    stages?: string[];    // ordered statuses
    kinds?: string[];     // record kinds
    custom?: { key: string; label: string; type: "text"|"number"|"money"|"date"|"select"|"bool"; options?: string[] }[];
    tabs?: string[];      // subset and order of the module's tabs
    [k: string]: unknown; // module extras below
  };
  sample: SampleType;     // which seed generator fills it for a demo
};

type AppConfig = {
  company: { name: string; industry: string; url?: string; colors: { brand: string; accent: string } };
  groups: { key: "grow"|"sell"|"make"|"know"|"run"; label: string }[]; // order = nav order
  modules: ModuleConfig[];
  customer: { kinds: ("shopper"|"buyer"|"member"|"partner"|"client")[]; intake: IntakeKind[]; shop: boolean };
  roles: { key: string; label: string }[];  // the six types, relabelable ("Staff" -> "Associates")
};
```

Sample data types (one generator each, PSAI-25 builds them): `contacts`, `companies`, `inbound_leads`, `deals`, `prospect_list`, `sequences`, `campaigns`, `reviews`, `rewards`, `reps`, `orders`, `products`, `appointments`, `jobs`, `lead_buyers`, `documents`, `invoices`, `articles`, `posts`, `media`, `designs`, `traffic`, `keywords`, `chart_tiles`, `goals`, `costs`, `playbook`, `team`, `agents`, `cards`, `changes`, `settings`, `messages`, `site_pages`, `intake_runs`.

---

## 6. The modules

Format per module: key and tier, job, admin tabs in nav order, record route, customer pages, who sees it, data objects, anchor kinds for the chat, agent actions, rails, SaaS it replaces, module knobs. Rails are keep-list only (hosting, database, email delivery, SMS, payments, domains, banking, payroll tax, DNS, passwords). Where a module needs a platform's own API (a social network, a search engine, an ad platform) it says "platform API": those are the channels themselves, not SaaS we replace.

"Replaces" uses the products in yea-saas.json, grouped by the new module key. Where the JSON has no entry, the line says "not priced" and names what the inventories saw businesses paying for, for PSAI-30 to price if wanted.

### Home `home` · core
- **Job:** what needs a person right now, then how the business is doing.
- **Admin tabs:** Today (act-now queue: Now, Today, Soon, Whenever), Numbers (KPI tiles with sparklines, funnel), Feed (latest changes).
- **Record route:** none. Every tile links into its module.
- **Customer:** Portal Home (`/portal`): their open items, last order or booking, balance, next step.
- **Sees:** O A S C(own) Cu(own, portal) Ag.
- **Data:** reads from every module; stores only `home_tiles` (which tiles, order, per role).
- **Anchors:** `tile:<key>`, `queue_item:<module>:<id>`.
- **Agent:** writes the morning summary (also emailed at a set hour), explains any tile ("why is this red"), opens the record behind a queue item, pins a chat chart to Home.
- **Rails:** email delivery (daily summary).
- **Replaces:** not priced. Dashboard tools and reporting automations (Databox, Zapier reporting zaps).
- **Knobs:** `fields.tiles` (which KPIs), `fields.summary_hour`. Sample: `chart_tiles`.

### Inbox `inbox` · core
- **Job:** every message to the business in one shared inbox, threaded, with a reply drafted.
- **Admin tabs:** Inbox, Assigned to me, Archived, Spam, Rules. Two panes: list left, thread right.
- **Record route:** `/admin/inbox/[thread]`, compose at `/admin/inbox/new`.
- **Customer:** messages they send from Site, Intake, Portal, email, DMs and SMS all land here. Customers see their own thread history in Portal Account.
- **Sees:** O A S C(assigned) Ag.
- **Data:** `threads`, `messages`, `attachments`, `inbox_rules`, `aliases`, `suppressions`.
- **Anchors:** `thread:<id>`, `message:<id>`.
- **Agent:** threads and filters spam, links a thread to its person or company, drafts the reply in the business's voice, routes to a person, turns a thread into a lead, flags requests (for example a partner asking for a feature) onto the Board, runs DM and comment auto-replies that qualify and hand off. Sends only where Settings allows; default is a person presses Send.
- **Rails:** email delivery (send and inbound parse), SMS.
- **Replaces:** Zendesk, Freshdesk, Help Scout, Gorgias (Helpdesk); Intercom, Tidio, LiveChat, Crisp (Chat widget, as a web chat channel); Google Workspace Gmail (Careful, moves last with a full mail cycle and MX cutover); Slack (team threads, Plan it).
- **Knobs:** `fields.channels` (email, sms, web_chat, dm), `fields.aliases`, `fields.auto_send` (off by default). Sample: `messages`.

### Leads `leads` · core
- **Job:** everyone who raised a hand, in one queue, scored and answered fast.
- **Admin tabs:** Queue (quick views: Needs reply, Assigned to me, Stuck), Applied (applications to approve), Map, Sources.
- **Record route:** `/admin/leads/[id]`: answers, photos and files, attribution (source, campaign, click id, landing page), consent record, notes, timeline.
- **Customer:** fed by Intake (forms, funnels, applications, waitlist). Customer sees their own submission and report.
- **Sees:** O A S C(own) Ag.
- **Data:** `leads`, `lead_answers`, `lead_files`, `consents`, `attribution`, `activities`.
- **Anchors:** `lead:<id>`, `field:lead:<id>.<field>`.
- **Agent:** classifies and scores each lead with plain reasons, vets applications (domain, phone, website, repeat match) to "looks legit, check, red flags", drafts the first reply, routes to a person or a buyer, creates a lead from a photo of a business card or badge, converts a lead to a deal, job or customer, nudges on stale leads.
- **Rails:** email delivery, SMS.
- **Replaces:** not priced as its own line (CRM intake is part of the CRM entries under Pipeline). Inventories saw legal intake CRMs and form-plus-alert stacks.
- **Knobs:** `fields.stages` (default New, Contacted, Qualified, Won, Lost), `fields.kinds` (inquiry, application, consult, waitlist), `fields.custom`, `fields.routing` (owner, round robin, marketplace). Sample: `inbound_leads`.

### Pipeline `pipeline` · common
- **Job:** the companies and deals you are working, by stage, with the next step on every row.
- **Admin tabs:** Board, List, Map, Follow-ups due, Hot.
- **Record route:** `/admin/pipeline/[id]`: Conversations, Orders or Jobs, Timeline, People, Details.
- **Customer:** none.
- **Sees:** O A S C(own book) Ag.
- **Data:** `companies`, `deals`, `deal_stage_history`, `activities`, `next_steps`, `owners`.
- **Anchors:** `company:<id>`, `deal:<id>`.
- **Agent:** opens every record with the next email already drafted, logs calls, visits and notes, moves stage with a reason, starts a sequence, flags accounts that stopped buying and why ("win-back"), computes stage from behaviour when set to auto.
- **Rails:** email delivery.
- **Replaces:** HubSpot Sales Hub Starter, Salesforce Starter Suite, Pipedrive, Zoho CRM, Close (CRM); ActiveCampaign (CRM half).
- **Knobs:** `label` (Pipeline, Accounts, Sponsors, Partners, Deals), `fields.stages`, `fields.kinds` (customer, partner, sponsor, vendor, press), `fields.stage_mode` (manual or from behaviour). Sample: `deals`.

### People `people` · core
- **Job:** every human the business has touched, in one list, with one timeline each.
- **Admin tabs:** Everyone, Customers, Subscribers, Press, Merge duplicates.
- **Record route:** `/admin/people/[id]`: profile, companies, leads, orders, jobs, messages, consent, rewards.
- **Customer:** Portal Account shows their own profile and email preferences.
- **Sees:** O A S C(own) Ag.
- **Data:** `people`, `company_people`, `subscribers`, `consents`, `email_prefs`, `profile_answers`, `do_not_contact`.
- **Anchors:** `person:<id>`.
- **Agent:** merges duplicates (asks first), fills blanks from public sources, tags people by kind, builds a list from a sentence ("everyone who bought twice and never reviewed"), exports.
- **Rails:** email delivery (preferences, unsubscribe).
- **Replaces:** CRM contact lists (see Pipeline); signup forms and waitlist tools (Mailchimp forms) count under Campaigns.
- **Knobs:** `label` (People, Contacts, Clients, Members, Waitlist), `fields.kinds`, `fields.custom`. Sample: `contacts`.

### Prospects `prospects` · industry (B2B selling at volume)
- **Job:** the whole market in one list, ranked by fit, ready for outreach.
- **Admin tabs:** All, Fit scores, Ideal customer, Markets, People found, Review queue, Ad intel.
- **Record route:** `/admin/prospects/[id]` with Overview, People, Intel, Field sources.
- **Customer:** optional public directory on the Site (only claimed listings indexed) and Portal Listing for claimed businesses.
- **Sees:** O A S Ag.
- **Data:** `prospects`, `fit_scores`, `icp_profiles`, `markets`, `prospect_people`, `field_sources`, `match_reviews`, `ad_intel`.
- **Anchors:** `prospect:<id>`, `market:<id>`.
- **Agent:** rebuilds the ideal customer profile from real customers, scores fit with reasons (person can override, the note trains the next version), enriches from public records and websites, finds the right person, matches licences or registrations, checks who runs ads, places prospects in markets.
- **Rails:** none.
- **Replaces:** not priced. Inventories saw ZoomInfo, Apollo data, Clay, Hunter, Clearbit, BuiltWith and directory software.
- **Knobs:** `label` (Prospects, Market, Firms, Stores), `fields.fit_rules`, `fields.markets`, `fields.directory` (public or not). Sample: `prospect_list`.

### Outreach `outreach` · common
- **Job:** multi-step sequences that stop on a reply, with every step drafted.
- **Admin tabs:** Today (steps due), Sequences, Waves, Templates, Replies.
- **Record route:** `/admin/outreach/sequences/[id]`.
- **Customer:** one-click unsubscribe and takedown pages on the Site.
- **Sees:** O A S C(own) Ag.
- **Data:** `sequences`, `sequence_steps`, `enrollments`, `tasks`, `templates`, `send_events`, `suppressions`.
- **Anchors:** `sequence:<id>`, `step:<id>`, `enrollment:<id>`.
- **Agent:** drafts each step for the specific company, sends inside business hours only when auto-send is on, stops on reply, order, application, bounce or do-not-contact, reads every reply and drafts the answer in-thread, compares waves (who opened, engaged, converted), caps daily sends.
- **Rails:** email delivery (send and event webhooks), SMS.
- **Replaces:** not priced. Inventories saw Outreach.io, Apollo sequences, Lemlist, Instantly.
- **Knobs:** `fields.step_kinds` (email, call, visit, text, dm, mail), `fields.daily_cap`, `fields.auto_send` (off by default). Sample: `sequences`.

### Campaigns `campaigns` · common
- **Job:** email and text campaigns to your own list, built by the agent, approved by the owner.
- **Admin tabs:** Campaigns, Automatic (flows and system emails), Audiences, Templates, Reports.
- **Record route:** `/admin/campaigns/[id]` (editor), `/admin/campaigns/[id]/report`.
- **Customer:** email preferences and one-click unsubscribe; newsletter signup on the Site.
- **Sees:** O A S(draft) Ag(draft, never approve).
- **Data:** `campaigns`, `campaign_sends`, `email_events`, `audiences`, `flows`, `email_templates`, `suppressions`, `sender_settings`.
- **Anchors:** `campaign:<id>`, `audience:<id>`, `flow:<id>`.
- **Agent:** proposes campaigns weekly, builds audiences from rules with live counts and a sample of who matched, writes the email with its rationale, sends a test to the team, submits for approval. Cannot approve or send. Send confirms the exact count, blocks without a mailing address, drops unsubscribed and bounced.
- **Rails:** email delivery, SMS.
- **Replaces:** Mailchimp, Klaviyo, Constant Contact, Kit, beehiiv (Email marketing); ActiveCampaign (email half); SimpleTexting (SMS, over the SMS rail).
- **Knobs:** `fields.channels` (email, sms), `fields.approval` (owner, admin), `fields.starters` (template set). Sample: `campaigns`.

### Reviews `reviews` · common
- **Job:** ask every happy customer for a review, answer every review, reuse the best ones.
- **Admin tabs:** To moderate, Published, Requests, Quote cards.
- **Record route:** URL modal `?review=<id>`.
- **Customer:** review page by private link (`/review/[token]`), reviews shown on product and Site pages.
- **Sees:** O A S Ag.
- **Data:** `reviews`, `review_requests`, `review_replies`.
- **Anchors:** `review:<id>`.
- **Agent:** sends review requests after delivery or a finished job, drafts replies, turns approved reviews into quote cards for Social.
- **Rails:** email delivery, SMS. Platform API for public review sites.
- **Replaces:** not priced. Inventories saw Judge.me, Yotpo, Birdeye, Podium.
- **Knobs:** `fields.request_delay_days`, `fields.sources` (own, public listing). Sample: `reviews`.

### Programs `programs` · industry (consumer brands)
- **Job:** the programs that make customers come back and bring friends.
- **Admin tabs:** Rewards, Referrals, Influencers, Giveaways, Offers, Customer content.
- **Record route:** `/admin/programs/giveaways/[id]`, `/admin/programs/influencers/[id]`.
- **Customer:** Portal Rewards (points balance, claim offers, referral link, influencer hub), public giveaway and claim pages.
- **Sees:** O A S Ag. Cu(own, portal).
- **Data:** `points_ledger`, `offers`, `offer_claims`, `referrals`, `influencers`, `influencer_payouts`, `giveaways`, `giveaway_entries`, `winners`, `draw_log`, `ugc_posts`.
- **Anchors:** `giveaway:<id>`, `influencer:<id>`, `offer:<id>`, `ugc:<id>`.
- **Agent:** drafts official giveaway rules (owner approves), runs the draw with an audit trail, drafts launch, last call and winner posts, reviews customer photos for approval, pays out influencer commission statements for approval.
- **Rails:** payments (payouts), email delivery.
- **Replaces:** not priced. Inventories saw Smile.io, LoyaltyLion, ReferralCandy, Refersion, UpPromote, Gleam, ViralSweep, Foursixty.
- **Knobs:** `label` (Programs, Loyalty, Members), `fields.tabs`, `fields.points_name` (points, stars, any brand word). Sample: `rewards`.

### Reps `reps` · industry (field sales teams)
- **Job:** a scorecard for every rep, their goal and their book.
- **Admin tabs:** Leaderboard, Goals, Activity, Territories.
- **Record route:** `/admin/reps/[id]`.
- **Customer:** none. Reps are Contractors: they see the admin shell filtered to their own book, plus Leaderboard and their Commission in Money.
- **Sees:** O A S C(leaderboard, own scorecard) Ag.
- **Data:** `reps`, `rep_goals`, `territories`, `activities`.
- **Anchors:** `rep:<id>`.
- **Agent:** tells each rep who to call and what to offer from customer behaviour, flags cold accounts, writes a weekly scorecard note.
- **Rails:** none.
- **Replaces:** not priced. Inventories saw sales performance and commission tools (Spiff, CaptivateIQ).
- **Knobs:** `label` (Reps, Agents, Ambassadors), `fields.goal_metric`. Sample: `reps`.

### Orders `orders` · common
- **Job:** every order from every channel in one queue, through to shipped.
- **Admin tabs:** Orders, Pack queue, New order.
- **Record route:** `/admin/orders/[number]`: lines, ship-to, emails sent, history, status.
- **Customer:** Shop checkout, order status page by private link, Portal Orders and Reorder.
- **Sees:** O A S C(own clients, placed as pending) Ag. Cu(own, portal).
- **Data:** `orders`, `order_lines`, `shipments`, `refunds`, `order_emails`.
- **Anchors:** `order:<number>`, `order_line:<id>`.
- **Agent:** answers "where is my order", flags address problems and emails the customer, drafts refunds for approval, finds orders stuck in a status, places reorders a business customer asked for in chat.
- **Rails:** payments, email delivery. Carrier label API where shipping is on.
- **Replaces:** Shopify, BigCommerce (order half, Plan it). Inventories also saw ShipStation.
- **Knobs:** `fields.stages` (Placed, Approved, Packed, Shipped, Delivered), `fields.shipping` (on or off; off hides Pack queue), `fields.channels` (retail, wholesale). Sample: `orders`.

### Catalog `catalog` · common
- **Job:** what you sell, what it costs, what is in stock, what is on sale.
- **Admin tabs:** Products, Pricing, Inventory, Promotions.
- **Record route:** `/admin/catalog/[slug]`.
- **Customer:** Shop product pages, Portal Reorder at the customer's tier price.
- **Sees:** O A S(inventory) C(read) Ag.
- **Data:** `products`, `variants`, `price_tiers`, `tier_prices`, `price_changes`, `inventory`, `promotions`, `promo_codes`.
- **Anchors:** `product:<slug>`, `variant:<sku>`.
- **Agent:** adjusts stock, schedules price changes (asks first, rolls back), sets up a timed promotion, flags low stock.
- **Rails:** none.
- **Replaces:** Shopify, BigCommerce, Gumroad (catalog half).
- **Knobs:** `label` (Catalog, Products, Menu, Services), `fields.tiers` (retail, wholesale, distributor), `fields.inventory` (on or off). Sample: `products`.

### Bookings `bookings` · common · not yet proven
- **Job:** let customers book time, and keep every date that matters on one calendar.
- **Admin tabs:** Calendar, Bookings, Availability, Booking pages.
- **Record route:** URL modal `?booking=<id>`.
- **Customer:** public booking page on the Site, Portal Bookings (reschedule, cancel).
- **Sees:** O A S C(own) Ag. Cu(own, portal).
- **Data:** `bookings`, `availability`, `booking_types`, `calendar_events`.
- **Anchors:** `booking:<id>`, `event:<id>`.
- **Agent:** books, moves and confirms appointments, sends reminders, fills cancellations from a waitlist, adds deadlines from Jobs to the calendar and emails a daily reminder.
- **Rails:** email delivery, SMS, payments (deposits).
- **Replaces:** Calendly, Acuity Scheduling, Cal.com (Scheduling); calendar half of Google Workspace.
- **Knobs:** `label` (Bookings, Appointments, Sessions, Reservations), `fields.booking_types`, `fields.deposit`. Sample: `appointments`.

### Jobs `jobs` · industry (service, case and project work)
- **Job:** the work you deliver after the sale: one file per job, with parties, dates, tasks and documents.
- **Admin tabs:** Open, Calendar, Tasks, All.
- **Record route:** `/admin/jobs/[id]`: header, parties, dates, tasks, documents, notes, each block saving on its own.
- **Customer:** Portal Documents and Bookings for their job; a client view is optional.
- **Sees:** O A S C(assigned) Ag. Cu(own, if client view on).
- **Data:** `jobs`, `job_parties`, `job_events`, `job_tasks`, `job_documents`.
- **Anchors:** `job:<id>`, `job_task:<id>`, `job_event:<id>`.
- **Agent:** turns a won lead into a job, tracks deadlines and sends a reminder digest, drafts status updates to the client, files incoming documents to the right job.
- **Rails:** email delivery.
- **Replaces:** not priced. Inventories saw practice management tools (Clio Manage, MyCase, PracticePanther).
- **Knobs:** `label` (Jobs, Matters, Cases, Projects, Engagements), `fields.stages`, `fields.party_roles`, `fields.event_kinds`. Sample: `jobs`.

### Marketplace `marketplace` · industry (businesses that route or resell leads or work)
- **Job:** route each lead to the right buyer by rules, price it, bill it from a prepaid balance.
- **Admin tabs:** Buyers, Pricing, Routing, Ledger, Stuck.
- **Record route:** `/admin/marketplace/buyers/[id]`: criteria, ledger, delivered leads.
- **Customer:** Portal Leads (purchased leads with the full file), Portal Account balance, optional white-label intake on the buyer's own brand.
- **Sees:** O A Ag. Cu(partner kind, own).
- **Data:** `buyers`, `buyer_criteria`, `lead_prices`, `lead_types`, `assignments`, `ledger_entries`, `white_label_sites`.
- **Anchors:** `buyer:<id>`, `assignment:<id>`.
- **Agent:** splits one request into every trade it implies, scores whether it qualifies, matches criteria, checks balance, debits, pings the buyer, retries stuck routes hourly, warns when a buyer will run dry.
- **Rails:** payments (deposits), email delivery.
- **Replaces:** not priced. Inventories saw lead distribution software (Boberdoo, LeadsPedia, Phonexa).
- **Knobs:** `label` (Marketplace, Referrals, Lead buyers), `fields.lead_types`, `fields.price_matrix`, `fields.white_label` (on or off). Sample: `lead_buyers`.

### Documents `documents` · common · not yet proven
- **Job:** every document the business sends or signs: reports, quotes, agreements, signed copies.
- **Admin tabs:** All, Templates, Out for signature, Signed.
- **Record route:** `/admin/documents/[id]`.
- **Customer:** Portal Documents (download, sign), report pages by private link.
- **Sees:** O A S C(own) Ag. Cu(own).
- **Data:** `documents`, `document_templates`, `signatures`, `signature_events`.
- **Anchors:** `document:<id>`.
- **Agent:** fills a template from a record, renders the PDF, sends for signature, files the signed copy to the person and job, reads uploaded documents and extracts fields without guessing numbers.
- **Rails:** email delivery.
- **Replaces:** DocuSign eSignature, Dropbox Sign (E-signature); PandaDoc (Sign and docs).
- **Knobs:** `fields.templates`, `fields.signing` (on or off). Sample: `documents`.

### Money `money` · common · not yet proven end to end
- **Job:** what you are owed, what you were paid, what you owe out.
- **Admin tabs:** Invoices, Payments, Aging, Payouts, Books export.
- **Record route:** `/admin/money/invoices/[number]`.
- **Customer:** Portal Invoices (view, pay).
- **Sees:** O A Ag(read, draft). C(own payouts).
- **Data:** `invoices`, `payments`, `payouts`, `commission_statements`, `tax_rates`, `books_sync`.
- **Anchors:** `invoice:<number>`, `payment:<id>`, `payout:<id>`.
- **Agent:** sends invoice reminders, records payments for approval, builds monthly commission and payout statements, exports to the books. Moves money only through the payments rail and only with approval.
- **Rails:** payments, banking, payroll tax.
- **Replaces:** QuickBooks Online, Xero (Careful, moves last after one full parallel month-end close); FreshBooks, Wave (Careful).
- **Knobs:** `label` (Money, Billing, Finance), `fields.tabs`, `fields.books` (keep current books or run in YEA). Sample: `invoices`.

### Content `content` · common
- **Job:** the articles, answers and pages that get the business found, on a calendar.
- **Admin tabs:** Posts, Schedule, Contributors, Series.
- **Record route:** `/admin/content/[slug]/edit`.
- **Customer:** Site blog, topic and answer pages, RSS. Portal Listing lets partners contribute answers.
- **Sees:** O A S Ag. Cu(partner kind, own contributions).
- **Data:** `articles`, `article_schedule`, `contributions`, `series`, `episodes`.
- **Anchors:** `article:<slug>`, `contribution:<id>`.
- **Agent:** turns an emailed rough draft into a formatted post (substance stays verbatim), researches and writes a sourced weekly post, writes the next episode of a series from a plain sentence, keeps the calendar full, verifies the page is live before reporting.
- **Rails:** hosting (publish).
- **Replaces:** WordPress.com (Site, see Site); inventories also saw editorial calendar plugins and AI writers.
- **Knobs:** `label` (Content, Blog, Journal, Insights), `fields.cadence`, `fields.contributors` (on or off). Sample: `articles`.

### Social `social` · common
- **Job:** next week's posts drafted, reviewed on a phone, posted at the planned slot.
- **Admin tabs:** Review, Calendar, Posts, Grid, What worked, Channels.
- **Record route:** `/admin/social/[id]`: player or carousel, timecoded comments, per-platform variants, post buttons.
- **Customer:** Portal Posts (a business customer makes posts for its own channels).
- **Sees:** O A S Ag. Cu(buyer kind, own posts).
- **Data:** `posts`, `post_variants`, `post_comments`, `post_publishes`, `post_metrics`, `channels`, `post_batches`.
- **Anchors:** `post:<id>`, `comment:<id>`.
- **Agent:** proposes next week's batch from real content into best-time slots, writes captions per platform within limits, sends the morning preview, takes comments and approvals from the owner's phone, posts the approved pick, writes "why it worked" for the top three, runs comment-to-DM keywords.
- **Rails:** none (platform APIs for each network).
- **Replaces:** Hootsuite, Buffer, Later (Social scheduling); Sprout Social (scheduling and analytics).
- **Knobs:** `fields.channels`, `fields.approval` (owner, admin, none), `fields.rotation` (weekday formats), `fields.real_assets_only` (default true). Sample: `posts`.

### Library `library` · common
- **Job:** every photo and video in one place, searchable in plain words, with consent on each.
- **Admin tabs:** All, Liked, Needs consent, Uploads, Jobs.
- **Record route:** URL modal `?item=<id>` (full-screen viewer).
- **Customer:** customer uploads (photos for a report, store photos, customer content) land here tagged by source.
- **Sees:** O A S Ag.
- **Data:** `media`, `media_tags`, `media_people`, `consents`, `crops`, `upload_sessions`, `media_jobs`.
- **Anchors:** `media:<id>`.
- **Agent:** tags everything on upload, groups near-duplicates, finds "more like this", sets people-centred crops for each post size, warns before using anything not cleared, renames and files phone uploads.
- **Rails:** database (object storage).
- **Replaces:** Dropbox (File storage). Inventories also saw digital asset managers (Air, Canto, Frame.io).
- **Knobs:** `fields.consent_required` (default true), `fields.sizes`. Sample: `media`.

### Studio `studio` · common
- **Job:** on-brand designs, carousels and short videos from templates and your own photos.
- **Admin tabs:** Designs, Templates, Print kit, Signatures, Press kit.
- **Record route:** `/admin/studio/[design]?size=9x16&slide=2`.
- **Customer:** Portal Kit (posters, counter cards, signature), Portal Posts (prompt to post).
- **Sees:** O A S C(kit, signature) Ag. Cu(buyer kind, kit and posts).
- **Data:** `designs`, `templates`, `renders`, `print_kits`.
- **Anchors:** `design:<id>`, `slide:<design>:<n>`.
- **Agent:** builds a post from one sentence with the right template and a real photo, swaps photos, renders PNG, MP4 or GIF into the Library, builds print PDFs and email signatures.
- **Rails:** none.
- **Replaces:** Canva (Design); Figma (Plan it); Loom (Video messaging, low).
- **Knobs:** `fields.templates`, `fields.sizes`, `fields.brand` (colors, fonts, logo from Settings). Sample: `designs`.

### Insights `insights` · common
- **Job:** where customers come from and what happens to them, in sentences first, then charts.
- **Admin tabs:** Sources, Traffic, Funnel, What worked, Ads.
- **Record route:** `/admin/insights/visitors/[id]` (one visitor's timeline).
- **Customer:** first-party tracking with an opt-out page on the Site.
- **Sees:** O A S(read) Ag.
- **Data:** `page_views`, `visitors`, `touches`, `attribution`, `funnel_snapshots`, `ad_reports`.
- **Anchors:** `source:<key>`, `visitor:<id>`, `funnel_step:<key>`.
- **Agent:** answers "is this working" in plain sentences, ties each lead to its true source and ad click, explains where ad money leaks, flags a funnel step that dropped.
- **Rails:** none (platform APIs for ad accounts).
- **Replaces:** Hotjar, Mixpanel, Plausible Analytics (Analytics); analytics half of Sprout Social.
- **Knobs:** `fields.tabs`, `fields.ads` (on or off). Sample: `traffic`.

### Search `search` · common
- **Job:** are we found on search and in AI answers, and what to fix.
- **Admin tabs:** Overview, Rankings, Keywords, Competitors, Links, Audit, Pages, Indexing, AI crawlers.
- **Record route:** URL modal `?keyword=<id>`.
- **Customer:** none (it measures the Site).
- **Sees:** O A S(read) Ag.
- **Data:** `keywords`, `rank_snapshots`, `keyword_ideas`, `serp_results`, `competitors`, `backlinks`, `audit_runs`, `audit_issues`, `url_inspections`, `crawler_hits`.
- **Anchors:** `keyword:<id>`, `page:<path>`, `issue:<id>`.
- **Agent:** harvests keyword ideas from real search queries, scores difficulty, tracks ranks daily, runs a weekly site audit, pings search engines when pages change, writes the monthly search report.
- **Rails:** hosting (crawler log at the edge).
- **Replaces:** not priced. Inventories saw Semrush and Ahrefs seats.
- **Knobs:** `fields.keywords` (seed list), `fields.competitors`. Sample: `keywords`.

### Views `views` · core
- **Job:** your own dashboards, built by asking the chat a question and saving the answer.
- **Admin tabs:** My views, Shared.
- **Record route:** `/admin/views/[id]`.
- **Customer:** none.
- **Sees:** O A S C(own) Ag.
- **Data:** `views`, `view_tiles` (each tile stores its read-only query).
- **Anchors:** `view:<id>`, `tile:<id>`.
- **Agent:** turns any chart in the chat into a tile, re-runs tiles on open, explains a tile.
- **Rails:** database (read-only role).
- **Replaces:** Airtable (Data views). Inventories also saw Looker Studio, Databox, Metabase.
- **Knobs:** `fields.default_views`. Sample: `chart_tiles`.

### Goals `goals` · core
- **Job:** what the business is working toward, with a live number and a checklist.
- **Admin tabs:** Goals, Done.
- **Record route:** URL modal `?goal=<id>`.
- **Customer:** none.
- **Sees:** O A S C(own) Ag.
- **Data:** `goals`, `goal_steps`, `goal_metrics`.
- **Anchors:** `goal:<id>`, `goal_step:<id>`.
- **Agent:** sets up a goal from a sentence, wires its live number to a query, ticks steps it completed, warns when a goal is behind.
- **Rails:** none.
- **Replaces:** Asana, monday.com goals views (see Board). Not priced separately.
- **Knobs:** `fields.metrics` (which live numbers can drive a goal). Sample: `goals`.

### Costs `costs` · common
- **Job:** what each lead, order or job really cost, including every agent call.
- **Admin tabs:** Per lead, Agent spend, Ad spend, Fixed costs, Caps, Budget.
- **Record route:** none.
- **Customer:** none.
- **Sees:** O A Ag(read).
- **Data:** `agent_calls` (real cost per call), `ad_spend`, `fixed_costs`, `cost_caps`, `budgets`.
- **Anchors:** `cost_line:<id>`, `cap:<key>`.
- **Agent:** logs the real cost of every model call it makes, allocates ad and fixed cost per lead, shows unattributed spend on its own line, stops itself at a monthly cap.
- **Rails:** banking (spend import).
- **Replaces:** not priced. Inventories saw BI dashboards and a separate budget spreadsheet.
- **Knobs:** `fields.unit` (lead, order, job), `fields.caps`. Sample: `costs`.

### Playbook `playbook` · common
- **Job:** how the business works, written down and live: flows, messages, assets, competitors.
- **Admin tabs:** Flows, Messaging, Assets, Competitors, Docs.
- **Record route:** `/admin/playbook/[flow]`.
- **Customer:** none.
- **Sees:** O A S(read) C(read) Ag.
- **Data:** `flows` (diagram plus live step counts), `messaging`, `assets` (every email and key page), `competitors`, `docs`.
- **Anchors:** `flow:<key>`, `asset:<key>`, `competitor:<id>`.
- **Agent:** keeps flow diagrams in step with the code, sends a test of any email, writes a cited SWOT per competitor, answers "how do we handle X" from the docs.
- **Rails:** email delivery (test sends).
- **Replaces:** Notion, Confluence, Coda (Docs and wiki); docs half of ClickUp.
- **Knobs:** `fields.tabs`. Sample: `playbook`.

### Calls `calls` · common
- **Job:** send the agent into a Zoom, Meet or Teams call: it listens, checks what is said against the business's data, shows live cards and the next question, answers the host's questions through the back-office agent, and writes the report.
- **Admin tabs:** Calls, Lenses, Settings.
- **Record route:** `/admin/calls/[id]` (Live, Transcript, Cards, Report, Follow-ups).
- **Customer:** none (a customer on a call sees the agent as a named participant).
- **Sees:** O A S(own) C(own) Ag(own).
- **Data:** `calls`, `call_participants`, `call_lines`, `call_cards`, `call_lenses`, `call_reports`.
- **Anchors:** `call:<id>`, `call_line:<id>`, `call_card:<id>`.
- **Agent:** joins on a person's say-so, triages every turn through the call's lens, checks claims against the linked record, suggests the next question, forwards questions to the back office, speaks only when voice is on and it is asked by our side.
- **Rails:** live worker (long-running, Fly.io), meeting bot vendor (Recall.ai), text to speech (voice only), calendar (read-only).
- **Replaces:** Otter, Fireflies, Fathom (note takers); Gong, Chorus (call intelligence).
- **Knobs:** `fields.calls.agent_name`, `fields.calls.lenses`, `fields.calls.default_lens_by_record`. Sample: `calls`.

### Team `team` · core
- **Job:** who works here, what they can do, and how they sign in.
- **Admin tabs:** People, Roles, Invites, Sessions.
- **Record route:** URL modal `?member=<id>`.
- **Customer:** none (customer logins live on People and Portal).
- **Sees:** O. A(read).
- **Data:** `users`, `roles`, `role_permissions`, `invites`, `sessions`, `login_links`.
- **Anchors:** `member:<id>`, `role:<key>`.
- **Agent:** none by default. Can draft an invite for the owner to send. Cannot change permissions.
- **Rails:** email delivery (sign-in links), passwords vault for shared credentials.
- **Replaces:** not priced. Inventories saw seat management in auth tools.
- **Knobs:** `fields.roles` (relabel the six types). Sample: `team`.

### Agents `agents` · core
- **Job:** the agents that work here, what each may do, when they run, what they cost.
- **Admin tabs:** Agents, Schedules, Permissions, Hand-offs.
- **Record route:** `/admin/agents/[key]`.
- **Customer:** none.
- **Sees:** O A(read).
- **Data:** `agents`, `agent_schedules`, `agent_permissions`, `agent_runs`, `handoffs`.
- **Anchors:** `agent:<key>`, `run:<id>`, `schedule:<id>`.
- **Agent:** reports what it ran and what it changed, pauses a schedule on request, hands outside work (shipping, books, research) to a person as a Board card.
- **Rails:** none.
- **Replaces:** Zapier, Make (Automation).
- **Knobs:** `fields.agents` (name, role it runs as, schedules), `fields.voice` (Talk button on or off). Sample: `agents`.

### Board `board` · core
- **Job:** everything someone asked for, from chat, voice, email or the team, tracked to done.
- **Admin tabs:** Board, Requests, Mine.
- **Record route:** URL modal `?card=<id>`.
- **Customer:** feature requests and service requests from Portal land here.
- **Sees:** O A S C(own) Ag.
- **Data:** `cards`, `card_comments`, `card_votes`.
- **Anchors:** `card:<id>`.
- **Agent:** files a card from any request in chat or on a voice call with urgency, moves cards, posts what it did, closes with proof.
- **Rails:** none.
- **Replaces:** Asana, monday.com, Trello, Basecamp (Project management); ClickUp.
- **Knobs:** `label` (Board, Requests, Tasks), `fields.stages`. Sample: `cards`.

### Log `log` · core
- **Job:** every change, by whom (person or agent), with before and after, and Undo.
- **Admin tabs:** Changes, Sign-ins, Exports.
- **Record route:** URL modal `?change=<id>`.
- **Customer:** none.
- **Sees:** O A. S(own). Ag(own, for undo).
- **Data:** `change_log` (actor kind, thread, message, before, after), `auth_log`.
- **Anchors:** `change:<id>`.
- **Agent:** reports every change with its number, undoes a change on request.
- **Rails:** database.
- **Replaces:** not priced. Inventories saw audit logs sold on enterprise tiers.
- **Knobs:** `fields.retention_days` (default 365). Sample: `changes`.

### Settings `settings` · core
- **Job:** the business, the brand and the switches.
- **Admin tabs:** Business, Brand, Modules, Channels, Email, Checkout, Data.
- **Record route:** none.
- **Customer:** none.
- **Sees:** O. A(all but Modules).
- **Data:** `tenant`, `brand`, `module_config` (this file's ModuleConfig), `channels`, `sender_settings`, `tax_rates`, `shipping_rules`, `do_not_contact`, `merges`.
- **Anchors:** `setting:<key>`.
- **Agent:** reads settings to answer questions; changes them only with the owner's yes.
- **Rails:** domains, DNS, email delivery, payments, SMS (connection settings for each rail).
- **Replaces:** none.
- **Knobs:** none (it holds everyone else's). Sample: `settings`.

### Site `site` · core (customer)
- **Job:** the public website: pages, blog, directory, locations, results.
- **Pages:** Home, industry pages from `fields.pages`, Blog (from Content), Directory and Stores (from Prospects and Pipeline when public), Policies, Unsubscribe and opt-out.
- **Admin side:** edited through Content, Catalog and Settings; no separate admin module.
- **Sees:** public. Ag (publishes).
- **Data:** `site_pages`, plus reads from Content, Catalog, Reviews, Prospects.
- **Anchors:** none for the public; admin previews use `page:<path>`.
- **Agent:** ships copy and page changes on request and verifies the URL is live.
- **Rails:** hosting, domains, DNS.
- **Replaces:** Squarespace, Wix, Webflow, WordPress.com, Framer (Website builder); Linktree, Beacons (Link in bio).
- **Knobs:** `fields.pages`, `fields.nav` (top nav items), `fields.directory` (on or off). Sample: `site_pages`.

### Intake `intake` · core (customer)
- **Job:** turn a visitor into a lead with the least typing, and give them something useful back.
- **Pages:** `/start` and its steps, `/r/[slug]` report, `/resume/[token]`, white-label `/e/[slug]` when Marketplace is on.
- **Kinds (`fields.kind`):** `form` (multi-step form), `application` (vetted), `waitlist` (join a list), `photo_report` (photos plus adaptive interview, then a cited report and a deterministic estimate), `booking` (hands off to Bookings).
- **Admin side:** lands in Leads.
- **Sees:** public. Cu (resume and report).
- **Data:** `intake_runs`, `intake_answers`, `intake_photos`, `reports`, `consents`.
- **Anchors:** `report:<slug>`.
- **Agent:** plans the interview from the photos, cites the photo behind each observation, never writes a price (pricing comes from rules), reads uploaded documents, sends the report and a resume link.
- **Rails:** email delivery, SMS, payments (deposits on booking).
- **Replaces:** Typeform, Jotform, Tally, SurveyMonkey (Forms and surveys).
- **Knobs:** `fields.kind`, `fields.steps`, `fields.questions`, `fields.price_table` (photo_report only). Sample: `intake_runs`.

### Shop `shop` · common (customer)
- **Job:** a storefront with cart and checkout, retail and business pricing in one.
- **Pages:** `/shop`, `/products/[slug]`, `/cart`, `/order/[number]`.
- **Admin side:** Catalog and Orders.
- **Sees:** public. Cu (business pricing when signed in as buyer).
- **Data:** reads Catalog, writes Orders.
- **Anchors:** `product:<slug>` (portal chat only).
- **Agent:** answers product questions in the customer chat, applies offers.
- **Rails:** payments, email delivery.
- **Replaces:** Shopify, BigCommerce (Plan it); Gumroad; Kajabi, Teachable (Plan it, digital products and members only; courses are not a proven module).
- **Knobs:** `fields.guest_checkout`, `fields.business_pricing`. Sample: `products`.

### Portal `portal` · core (customer)
- **Job:** the signed-in customer's own app: same shell, same chat, only their records.
- **Pages:** see the Portal tree in 3b. Home and Account are core; the rest follow the admin modules that feed them.
- **Sees:** Cu.
- **Data:** reads each module filtered to the customer; writes reorders, bookings, documents signed, listing edits, contributions, posts.
- **Anchors:** the same kinds as the feeding modules, filtered to own records.
- **Agent:** the chat on the right answers about their orders, invoices, bookings and documents, and files requests to the Board. Customer permissions only.
- **Rails:** email delivery (sign-in links), payments.
- **Replaces:** customer portal add-ons inside the CRM and storefront tools above.
- **Knobs:** `customer.kinds`, `fields.pages`. Sample: per feeding module.

---

## 7. yea-saas.json, re-keyed to these modules

PSAI-30 should rewrite the `yea_module` field with these keys.

| yea-saas.json yea_module | Module key(s) |
|---|---|
| Campaigns | campaigns |
| Campaigns + CRM | campaigns, pipeline |
| Campaigns (SMS over Twilio) | campaigns |
| CRM | pipeline, people |
| Storefront | shop, catalog, orders |
| Courses + Storefront | shop, portal |
| Bookings | bookings |
| Forms | intake |
| Inbox | inbox |
| Chat, Chat + Inbox | inbox |
| Projects | board |
| Projects + Docs | board, playbook |
| Docs | playbook |
| Data views | views |
| Studio | studio |
| Social | social |
| Social + Analytics | social, insights |
| Site, Site (links page) | site |
| Analytics | insights |
| Agents | agents |
| Team chat | inbox |
| Files | library |
| Sign, Sign + Docs | documents |
| Ledger, Ledger + Invoices | money |
| Inbox + Calendar | inbox, bookings |
| None (keep list) | rails, no module |

---

## 8. Notes for the cards that build on this

- **PSAI-22 roles:** visibility codes above are the floor. Contractor always means "own records". Agent always runs as a named role and every write goes to Log.
- **PSAI-23 repo:** create the tree in 3c exactly. `shared/modules.md` is this file without the appendix (yea-module-map.repo.md).
- **PSAI-24 PRDs:** one PRD per folder. Each PRD lists its tabs in the order above, its anchor kinds, its agent actions, its knobs and its sample type. Start Leads from the existing reference module in the Open Sky shell.
- **PSAI-25 companies:** pick modules per company by tier: all core, the common ones that fit, at most two industry modules. Use the sample types in section 5.
- **PSAI-28 and PSAI-31 screen and dashboard:** render the nav from AppConfig. The shell never changes; nav items, labels and data do.
- **PSAI-33 finale:** the config object in section 5 is the whole output. Toggle `enabled`, set `label`, pick `fields.stages` and `fields.kinds`, set colors, pick `sample`.
