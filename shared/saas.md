# YEA SaaS explorer: what you can drop, what you keep

Part of the YEA docs. Prices checked 2026-10-31 on each vendor's own pricing page. Machine-readable copy: `shared/saas.json`. Prices change; recheck before you quote one.

**86 products, 33 categories. 70 drop, 16 keep.**

## The rule

YEA replaces the apps. It does not replace the rails. If a product is software a business uses to do its work, YEA can absorb it. If a product is infrastructure, a license, or a regulated rail that moves money, mail, messages or tax filings, YEA plugs into it and keeps it.

## What makes something high risk

Four things push a product to high. Any one is enough.

1. **Money.** It moves cash or holds the record of it. Books, invoices, checkout, payroll. A mistake here is a missed payment, a double charge, or a bad tax return.
2. **Compliance.** A regulator or a court relies on the record. Tax filings, signed contracts and audit trails, SMS consent under TCPA, unsubscribe lists under CAN-SPAM, PCI for cards.
3. **Deliverability.** It depends on reputation built over years. Sending IPs, domain authentication, carrier registration. You cannot rebuild trust with Gmail or AT&T on a weekend.
4. **Data you can't lose.** Years of email, deal history, order history, the database itself. If the export misses something, it is gone.

High does not always mean keep. QuickBooks Online and Gmail are high risk to replace, but YEA can replace them. They move last, with a full parallel run (one complete month-end close for the books, one full mail cycle with MX cutover for Gmail). The keep list is the set where replacing the vendor is the wrong goal.

## Risk scale

- **none (No brainer)**: Nothing at stake. Swap it this week.
- **low (Easy)**: Data moves cleanly. Small rebuild, no money or compliance attached.
- **mid (Plan it)**: Live revenue, contracts, consent records or history the business runs on. Needs a migration plan and a parallel run.
- **high (Careful)**: Money, compliance, deliverability, or data you cannot lose. Move last with a full parallel run, or keep it.

## You still need these (keep)

| Product | Category | What it does | Starts at | Why it stays | Source |
|---|---|---|---|---|---|
| Vercel | Hosting | Hosts and deploys web apps | $20/mo | YEA itself runs here. Global edge, preview deploys and scaling that would cost a team to rebuild. | [pricing](https://vercel.com/pricing) |
| Netlify | Hosting | Hosts and deploys web sites | $9/mo | Same role as Vercel. If a business is already here, YEA can run here too. | [pricing](https://www.netlify.com/pricing/) |
| Neon | Database | Serverless Postgres database | $0.106 per compute hour, $0.35 per GB-month storage | The data you cannot lose. Backups, branching and point in time restore are a vendor job, not ours. | [pricing](https://neon.com/pricing) |
| Cloudflare | DNS and security | DNS, CDN and DDoS protection | $20/mo | DNS and attack protection. One bad record takes email and the site down together. | [pricing](https://www.cloudflare.com/plans/) (snippet) |
| Twilio SendGrid | Email delivery | Sends transactional and bulk email | $19.95/mo | Deliverability is IP reputation, authentication and inbox provider relationships built over years. YEA writes the email, SendGrid lands it in the inbox. | [pricing](https://www.twilio.com/en-us/products/email-api/pricing) |
| Postmark | Email delivery | Fast transactional email delivery | $15/mo | Same as SendGrid. Receipts and password resets have to arrive. | [pricing](https://postmarkapp.com/pricing) |
| Resend | Email delivery | Developer email sending API | $20/mo | Same as SendGrid, for teams that prefer it. | [pricing](https://resend.com/pricing) |
| Twilio | SMS and voice | Carrier SMS and voice rail | $0.0083 per SMS segment plus carrier fees | Carrier access, 10DLC registration and phone numbers. Regulated rail, nobody rebuilds it. | [pricing](https://www.twilio.com/en-us/sms/pricing/us) |
| Stripe | Payments | Card payments and subscriptions | 2.9% + 30c per domestic card charge | Moving money means PCI compliance, fraud control and bank licenses. YEA calls Stripe, it never touches a card number. | [pricing](https://stripe.com/pricing) |
| Square | Payments | In person and online payments | 3.3% + 30c per online card payment | Card readers and point of sale. Same reasons as Stripe. | [pricing](https://squareup.com/us/en/payments/our-fees) |
| PayPal | Payments | PayPal and card checkout | 3.49% + 49c per transaction | Buyers expect the button. Licensed money transmitter. | [pricing](https://www.paypal.com/us/business/paypal-business-fees) |
| Namecheap | Domains | Domain registration and renewal | $18.48 per year renewal, $19.98 from 2026-11-01, plus 20c ICANN fee | An ICANN accredited registrar owns the legal record of your domain. Lose the domain, lose everything on it. | [pricing](https://www.namecheap.com/domains/registration/gtld/com/) (snippet) |
| Mercury | Banking | Business bank accounts and cards | $0/mo | Banks hold deposits under a charter and FDIC insurance through partner banks. YEA reads balances, it never holds money. | [pricing](https://mercury.com/pricing) |
| Gusto | Payroll | Payroll, tax filing and benefits | $49/mo, plus $6 per person per month | Payroll tax filing in every state and IRS liability. A filing error costs penalties. Keep the rail, YEA shows the data. | [pricing](https://gusto.com/product/pricing) (snippet) |
| Rippling | Payroll | Payroll, HR and IT platform | $8/mo | Same as Gusto: payroll tax and benefits are regulated work. | [pricing](https://www.rippling.com/pricing) |
| 1Password | Security | Team password and secrets vault | $24.95/mo | Credentials and secrets for every system, including YEA. Security tooling stays with a specialist. | [pricing](https://1password.com/pricing/business) |

## You can drop these, by risk

### No brainer: risk none (22)

| Product | Category | What it does | Starts at | Why this risk | Working label | Source |
|---|---|---|---|---|---|---|
| Hotjar (Contentsquare) | Analytics | Heatmaps and session recordings | $39/mo | Recordings are disposable. YEA tracks its own sessions. | Analytics | [pricing](https://contentsquare.com/pricing/) |
| Plausible Analytics | Analytics | Privacy friendly website analytics | $9/mo | Pageview counts. YEA logs its own traffic. | Analytics | [pricing](https://plausible.io/#pricing) |
| Crisp | Chat widget | Shared inbox and site chat | $45/mo | Swap the embed and forward the inbox. | Chat + Inbox | [pricing](https://crisp.chat/en/pricing/) |
| LiveChat | Chat widget | Live chat for websites | $19/mo | Swap the embed. Done. | Chat | [pricing](https://www.livechat.com/pricing/) |
| Tidio | Chat widget | Live chat and chatbot | $24.17/mo | A widget and a few canned replies. Nothing to lose. | Chat | [pricing](https://www.tidio.com/pricing/) |
| Constant Contact | Email marketing | Small business email newsletters | $12/mo | Simple newsletter sends. Nothing a list export and the Campaigns module cannot carry. | Campaigns | [pricing](https://www.constantcontact.com/pricing) (snippet) |
| Mailchimp | Email marketing | Sends newsletters and email campaigns | $13/mo | Lists, templates and sends move in an afternoon. Bring the unsubscribe list so suppression carries over. | Campaigns | [pricing](https://mailchimp.com/landers/pricing/essentials/) |
| SurveyMonkey | Forms and surveys | Surveys and response analysis | $39/mo | Surveys and results export. The agent writes the analysis. | Forms | [pricing](https://www.surveymonkey.com/pricing/individual/) |
| Tally | Forms and surveys | Simple no-code forms | $24/mo | Plain forms. Nothing to lose. | Forms | [pricing](https://tally.so/pricing) |
| Typeform | Forms and surveys | Conversational forms and surveys | $28/mo | Forms are the first thing YEA builds. Old responses export to CSV. | Forms | [pricing](https://www.typeform.com/pricing) |
| Beacons | Link in bio | Creator link page and store | $8.33/mo, 9% transaction fee | One page of links and a few products. | Site (links page) | [pricing](https://beacons.ai/i/plans) |
| Linktree | Link in bio | Link in bio landing page | $6/mo, 9% on digital product sales | One page of links. Change the URL in your bio. | Site (links page) | [pricing](https://linktr.ee/s/pricing) (snippet) |
| Asana | Project management | Tasks, projects and timelines | $10.99/mo | Tasks and projects export. Internal only, no customer data at stake. | Projects | [pricing](https://asana.com/pricing) |
| Basecamp | Project management | Projects, messages and files | $29/mo | Messages and files export. Internal only. | Projects | [pricing](https://basecamp.com/pricing) |
| ClickUp | Project management | Tasks, docs and goals | $9/mo | Tasks and docs export. Internal only. | Projects + Docs | [pricing](https://clickup.com/pricing) |
| Trello | Project management | Kanban boards for tasks | $5/mo | Cards and lists. YEA ships a board. | Projects | [pricing](https://trello.com/pricing) |
| monday.com | Project management | Work boards and workflows | $9/mo | Boards export. Real floor is $27 a month. | Projects | [pricing](https://monday.com/pricing) |
| Cal.com | Scheduling | Open scheduling infrastructure | $12/mo | Booking links and availability rules. Nothing at stake. | Bookings | [pricing](https://cal.com/pricing) |
| Calendly | Scheduling | Book meetings from links | $10/mo | Booking links and calendar sync. Rebuilt in a day. | Bookings | [pricing](https://calendly.com/pricing) |
| Buffer | Social scheduling | Queue and publish social posts | $5/mo | Queue and publish. Nothing to lose. | Social | [pricing](https://buffer.com/pricing) |
| Hootsuite | Social scheduling | Schedule and monitor social posts | $99/mo | A calendar and a publish button. YEA posts through each network's API. | Social | [pricing](https://www.hootsuite.com/plans) |
| Later | Social scheduling | Visual social media planner | $18.75/mo | Media library downloads. Posts reschedule in YEA. | Social | [pricing](https://later.com/pricing/) |

### Easy: risk low (30)

| Product | Category | What it does | Starts at | Why this risk | Working label | Source |
|---|---|---|---|---|---|---|
| Mixpanel | Analytics | Product event analytics | $0/mo | Historical events take a backfill if you want the trend lines. | Analytics | [pricing](https://mixpanel.com/pricing/) |
| Make | Automation | Visual workflow automation builder | $9/mo | Same as Zapier. The agent runs the workflow. | Agents | [pricing](https://www.make.com/en/pricing) (snippet) |
| Zapier | Automation | Connect apps with workflows | $19.99/mo | Once the apps live in one place there is little left to glue. Audit each zap before you turn it off. | Agents | [pricing](https://zapier.com/pricing) |
| Close | CRM | Calling and email sales CRM | $9/mo | Leads and activity export cleanly. Calling rides on Twilio either way. | CRM | [pricing](https://www.close.com/pricing) |
| Pipedrive | CRM | Visual sales pipeline tracking | $14/mo | Deals and stages map one to one. Clean CSV export. | CRM | [pricing](https://www.pipedrive.com/en/pricing) (snippet) |
| Zoho CRM | CRM | Contact and deal management | $14/mo | Standard objects export cleanly. Watch custom fields. | CRM | [pricing](https://www.zoho.com/crm/zohocrm-pricing.html) (snippet) |
| Intercom | Chat widget | Website chat and support | $19/mo, AI resolutions billed extra | The site chat becomes the YEA agent. Conversation history exports. | Chat | [pricing](https://www.intercom.com/pricing) |
| Canva | Design | Drag and drop graphic design | $12/mo | Brand kit and templates move into YEA. The agent renders on-brand assets. | Studio | [pricing](https://www.canva.com/pricing/) (snippet) |
| Airtable | Docs and wiki | Spreadsheet database for teams | $20/mo | Bases are tables. They become real tables in the YEA database. | Data views | [pricing](https://www.airtable.com/pricing) |
| Coda | Docs and wiki | Docs that act like apps | $12/mo | Doc formulas become YEA views and agent actions. | Docs | [pricing](https://coda.io/pricing) (snippet) |
| Confluence | Docs and wiki | Team wiki and documentation | $5.78/mo | Pages export. Teams on Jira may want to keep both together. | Docs | [pricing](https://www.atlassian.com/software/confluence/pricing) (recheck) |
| Notion | Docs and wiki | Docs, wikis and databases | $10/mo | Exports to markdown. Linked databases need a little rebuild. | Docs | [pricing](https://www.notion.com/pricing) |
| Gumroad | Ecommerce | Sell digital products simply | 10% + 50c per sale | A product page and a Stripe checkout. Cheaper on every sale once moved. | Storefront | [pricing](https://gumroad.com/pricing) |
| ActiveCampaign | Email marketing | Email automation with light CRM | $15/mo | Automations are rebuilt as agent workflows. Contact history exports cleanly. | Campaigns + CRM | [pricing](https://www.activecampaign.com/pricing) (recheck) |
| Kit (ConvertKit) | Email marketing | Creator newsletters and sequences | $33/mo | Sequences and tags need a careful map, but no money or regulated data rides on them. | Campaigns | [pricing](https://kit.com/pricing) |
| beehiiv | Email marketing | Newsletter publishing and growth | $49/mo | Paid newsletter subscriptions need their Stripe link moved. The rest is content. | Campaigns | [pricing](https://www.beehiiv.com/pricing) |
| Dropbox | File storage | Cloud file storage and sharing | $9.99/mo | Files copy over. Shared links break, so update anything public. | Files | [pricing](https://www.dropbox.com/plans) |
| Jotform | Forms and surveys | Online forms and data collection | $34/mo | Check for forms that collect payments or health data before moving. | Forms | [pricing](https://www.jotform.com/pricing/) |
| Freshdesk | Helpdesk | Support tickets and knowledge base | $19/mo | Tickets and help articles export cleanly. | Inbox | [pricing](https://www.freshworks.com/freshdesk/pricing/) |
| Gorgias | Helpdesk | Ecommerce support helpdesk | $10/mo | Tied to the store, so it moves when the store moves. | Inbox | [pricing](https://www.gorgias.com/pricing) |
| Help Scout | Helpdesk | Shared inbox for support | $25/mo | A shared inbox on top of email. Keep the support address pointed at YEA. | Inbox | [pricing](https://www.helpscout.com/pricing/) |
| Zendesk | Helpdesk | Customer support ticketing | $19/mo | Ticket history exports. Macros become agent playbooks. | Inbox | [pricing](https://www.zendesk.com/pricing/) |
| Acuity Scheduling | Scheduling | Client appointment booking | $16/mo | Intake forms and paid deposits need a careful map. Future appointments move first. | Bookings | [pricing](https://acuityscheduling.com/pricing) |
| Sprout Social | Social scheduling | Social publishing and listening | $79/mo | Reporting history is the only thing worth exporting. | Social + Analytics | [pricing](https://sproutsocial.com/pricing/) |
| Loom | Video messaging | Record and share screen videos | $18/mo | Old videos download. New ones record inside YEA. | Studio | [pricing](https://www.loom.com/pricing) |
| Framer | Website builder | Design-led website builder | $10/mo | Marketing pages rebuild fast. Redirect old URLs. | Site | [pricing](https://www.framer.com/pricing) |
| Squarespace | Website builder | Website templates and hosting | $19/mo, 2% store fee on Basic | Pages and blog move, but redirect every old URL or you lose search rank. | Site | [pricing](https://www.squarespace.com/pricing) |
| Webflow | Website builder | Visual site builder and CMS | $15/mo | CMS collections export to CSV. Redirect old URLs. | Site | [pricing](https://webflow.com/pricing) (snippet) |
| Wix | Website builder | Drag and drop website builder | $17.77/mo | Same as Squarespace. The redirect map is the work. | Site | [pricing](https://www.wix.com/plans) |
| WordPress.com | Website builder | Hosted blogs and websites | $4/mo, 8% on payments on Personal | Posts export to XML. Plugins with data need a check. | Site | [pricing](https://wordpress.com/pricing/) |

### Plan it: risk mid (13)

| Product | Category | What it does | Starts at | Why this risk | Working label | Source |
|---|---|---|---|---|---|---|
| HubSpot Sales Hub Starter | CRM | Contacts, deals and pipeline | $7/mo | Years of deal history, emails and attribution. Lose the history and sales loses its memory. | CRM | [pricing](https://www.hubspot.com/pricing/sales) |
| Salesforce Starter Suite | CRM | Sales, service and marketing CRM | $25/mo | Custom objects and reports take real mapping. Fine at small business scale, plan the export. | CRM | [pricing](https://www.salesforce.com/small-business/pricing/) |
| Kajabi | Courses and memberships | Courses, memberships and community | $143/mo, 2.9% + 30c with Kajabi Payments | Active subscriptions must migrate without double charging or dropping members. | Courses + Storefront | [pricing](https://kajabi.com/pricing) |
| Teachable | Courses and memberships | Host and sell online courses | $29/mo, 7.5% transaction fee on Starter | Student progress and recurring payments need a clean handoff. | Courses + Storefront | [pricing](https://www.teachable.com/pricing) |
| Figma | Design | Interface design and prototyping | $16/mo | Product teams with years of design files and a component library should move last, or keep it. | Studio | [pricing](https://www.figma.com/pricing/) |
| DocuSign eSignature | E-signature | Send documents for signature | $11/mo | Signed agreements need an audit trail that holds up. Keep the completed archive and certificates. | Sign | [pricing](https://ecom.docusign.com/plans-and-pricing/esignature) |
| Dropbox Sign | E-signature | Simple e-signature workflows | $10.05/mo | Same as DocuSign: export the signed archive and audit trails first. | Sign | [pricing](https://sign.dropbox.com/products/dropbox-sign/pricing) |
| PandaDoc | E-signature | Proposals, quotes and e-signature | $19/mo | Proposal templates rebuild easily. Signed contracts and audit trails must be archived. | Sign + Docs | [pricing](https://www.pandadoc.com/pricing/) |
| BigCommerce | Ecommerce | Online store and catalog | $29/mo, card processing from 2.89% + 29c | Same as Shopify: live checkout, catalog and SEO URLs move together. | Storefront | [pricing](https://www.bigcommerce.com/essentials/pricing/) |
| Shopify | Ecommerce | Online store and checkout | $29/mo, 2.9% + 30c online card rate | Live revenue, product catalog, SEO URLs and order history. Money keeps flowing through Stripe, but the move needs redirects and a parallel run. | Storefront | [pricing](https://www.shopify.com/pricing) |
| Klaviyo | Email marketing | Ecommerce email and SMS flows | $20/mo | Revenue-driving abandoned cart and post-purchase flows must be rebuilt and proven before cutover. | Campaigns | [pricing](https://www.klaviyo.com/pricing) (recheck) |
| SimpleTexting | SMS marketing | Bulk text message campaigns | $39/mo | Opt-in records and 10DLC registration carry TCPA exposure. Port the number and consent log together. | Campaigns (SMS over Twilio) | [pricing](https://simpletexting.com/pricing/) |
| Slack | Team chat | Team messaging and channels | $7.25/mo | Habit is the risk, not data. Message history may matter for legal hold. Export before you cancel. | Team chat | [pricing](https://slack.com/pricing) |

### Careful: risk high (5)

| Product | Category | What it does | Starts at | Why this risk | Working label | Source |
|---|---|---|---|---|---|---|
| FreshBooks | Accounting | Invoicing and small business accounting | $23/mo | Open invoices, client payment history and tax records. A missed invoice is missed cash. | Ledger + Invoices | [pricing](https://www.freshbooks.com/pricing) |
| QuickBooks Online | Accounting | Books, invoicing and tax prep | $38/mo | The books are the record your CPA, lender and the IRS rely on. Bank feeds, reconciliations and tax categories cannot break. Move last, run both in parallel through a full close. | Ledger | [pricing](https://quickbooks.intuit.com/pricing/) |
| Wave | Accounting | Free accounting and invoicing | $19/mo, Starter is free, cards 2.9% + 60c | Still the books. Same rules as QuickBooks. | Ledger + Invoices | [pricing](https://www.waveapps.com/pricing) |
| Xero | Accounting | Cloud accounting for small business | $27/mo | Same as QuickBooks. Money and tax records, parallel run through a close. | Ledger | [pricing](https://www.xero.com/us/pricing-plans/) |
| Google Workspace (Gmail) | Email and workspace | Business email, calendar and docs | $7/mo | Your domain email is your identity, your login recovery and your sender reputation. MX records, years of mail, calendar invites and every vendor password reset ride on it. Move last, or keep it. | Inbox + Calendar | [pricing](https://workspace.google.com/pricing) |

## Which module replaces what

The `yea_module` field in `shared/saas.json` uses working labels. This table maps each label to the module keys in `shared/modules.md`.

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

## Price notes

- "Starts at" is the cheapest paid plan. Where the vendor shows both, the annual-billed per-month number is listed and the monthly number is in the JSON `basis` field. Most prices scale with contacts, seats, or volume.
- **(snippet)**: the vendor page blocked a direct fetch. The number came from the vendor's own page via search. Constant Contact, Pipedrive, Zoho CRM, Webflow, Linktree, Coda, Canva, Make, Cloudflare, Namecheap, Gusto.
- **(recheck)**: the vendor page did not render the number. The figure came from third-party trackers and needs a human look before it goes public. Klaviyo ($20), ActiveCampaign ($15), Confluence ($5.78, Atlassian raised cloud seat prices on 2026-10-15).
- Promos to avoid quoting as list: HubSpot Starter shows $7 with $20 crossed out. QuickBooks shows $19 for 3 months, list $38. Xero 90% off ends 2026-11-02. Google Workspace has a new-customer promo running 2026-11-14 to 2027-02-14.
- Price changes inside the window: Namecheap .com renewal goes from $18.48 to $19.98 on 2026-11-01. Webflow moves legacy sites to new pricing by 2026-11-16.
- Conflicts seen on vendor pages: Typeform plan card ($28) vs its own comparison table ($25). Freshdesk page ($19) vs its meta description ($15). Mercury table ($29.90) vs its FAQ ($35).

## Categories covered

Accounting, Analytics, Automation, Banking, CRM, Chat widget, Courses and memberships, DNS and security, Database, Design, Docs and wiki, Domains, E-signature, Ecommerce, Email and workspace, Email delivery, Email marketing, File storage, Forms and surveys, Helpdesk, Hosting, Link in bio, Payments, Payroll, Project management, SMS and voice, SMS marketing, Scheduling, Security, Social scheduling, Team chat, Video messaging, Website builder.
