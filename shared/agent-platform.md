# The agent platform

Part of the YEA docs. How agents connect to a YEA app, where they run, what they may do alone, and who owns what. Written 2026-11-03 from the founder's decisions. This is direction: unless a line says it runs in production, treat it as not yet proven and test harder. `shared/roles.md` owns permissions and `shared/chat.md` owns the panel.

---

## 1. The calls we made

1. **The business app is the product. Agents are workers inside it.** The app holds the data, the rules and the screens. An agent can be swapped. The app stays.
2. **Three pieces, one repo.** A marketing site, a back office and an agent. They ship together so the agent's tools never drift from the app (section 8).
3. **Incubate, then hand off.** PostScarcity stands the app up on its own accounts, pays for compute during incubation and trains the agent. Then the business takes over and owns its own copy on its own compute (section 3).
4. **MCP is the door.** Every outside agent connects the same way (section 4).
5. **Native by default, Hermes as the swap.** Most people should never have to think about which agent they run (section 5).
6. **A ladder for compute.** Vercel, then Beam, then a Mac mini. Most businesses stay on the first rung (section 6).
7. **One relax switch: YOLO.** There is no super YOLO. Nothing reaches outside the organization without a person's yes (section 7).
8. **Quiet by default.** Errors go to a backlog, not into chat (section 7).

---

## 2. Who can reach the app

| Surface | How it connects | Status |
|---|---|---|
| The chat panel | Native. Runs as the signed-in user, sees the page. `shared/chat.md` | Runs in production |
| Claude Code, Codex and other coding agents | MCP | Planned |
| Grok, Meta Muse and other assistants | MCP, where the surface supports it. Confirm each one before promising it | Planned, unchecked |
| Hermes | The back-office contract: the app relays a question to the business's own Hermes and shows the answer. The contract ships as a template | Runs in production at PostScarcity |
| Phone agent apps such as Yui | MCP, like any other client. Yui is a separate PostScarcity product and is not part of YEA | Yui is paused |

Every surface obeys one rule: **an agent's access never goes above the signed-in user's role.** A connection made by a Contractor sees that Contractor's book, and nothing more.

---

## 3. Incubation and hand-off

- **During incubation** PostScarcity carries the setup, the training and the compute bill for hosting and API usage.
- **At hand-off** every account moves to the business: repo, hosting, database, model keys, domain. If you are the vendor, put everything in their name from day one, so hand-off is a change of who pays and who drives.
- **After hand-off** the business runs its own compute and its own model account. PostScarcity can stay on under a service contract, but the business can leave with everything.

**Open: when does hand-off happen?** The founder said about day 60. The PostScarcity site sells the first 90 days and treats what follows as a managed run. Pick one number before this goes in a contract.

---

## 4. MCP, the general door

The app ships its own MCP server, so any capable outside agent can use the same tools as the chat panel.

- **One tool list.** The panel and the MCP server read the same definitions, in `packages/tools`. A module adds a tool once and both surfaces get it. This is how it stays in sync as the app changes.
- **Same checks.** Each MCP call goes through `can()`, row rules and `change_log`, exactly like a chat tool. Gated verbs still wait for a person.
- **Sign-in.** The connection authenticates as a real user of the app, never as a shared key with its own powers.
- **Change over time.** Version the tool list. Adding a tool is safe. Renaming or removing one is a breaking change, and it goes in the release notes with its replacement.

Not yet proven: hosting the MCP endpoint on the same Vercel deployment as the app. Test it before relying on it.

---

## 5. The agent

### The native agent

The default. It lives in the app and needs nothing but an API key.

- **Reads and proposes.** On day one it reads what the signed-in user can read and proposes changes. Writes follow `shared/roles.md` section 5.
- **Connectors are the value.** An agent that can't reach the business's tools isn't worth much. Preconfigure what works with no setup, then add connectors in the order the owner needs them.
- **It files what it can't do.** Inside a Vercel function it can't change the software, so it files a Board card (`shared/chat.md` section 6). When a person says "do these three," that work runs on the next rung up.

### Hermes as the swap

A business that wants a long-lived agent with its own memory, schedules and machine can run Hermes and connect it through the back-office contract and MCP. The app does not change.

### Model access

- **Native agent and anything PostScarcity hosts: API keys only.** Anthropic's terms bar third parties from offering Claude login in their own apps, from routing requests through plan credentials, and from paying for a user's Claude usage. Products built on the Agent SDK should use API keys. So YEA does not offer "log in with your Claude subscription" on a cloud server.
- **OpenAI** offers Sign in with ChatGPT for other apps, with an interest form for paid or remotely hosted ones. Check the current terms before building on it.
- **Keep the provider a config value** behind one `callModel()` (`admin/run/agents/`).

Read each vendor's current terms before relying on any of this. This is a reading of them, not legal advice.

### Open: how a fresh agent learns

Not decided. A preloaded agent starts with months of context, and a new YEA agent starts with `docs/interview.md`, the config and whatever is in the app. How it accrues context and gets better is the biggest open question on this page.

---

## 6. The compute ladder

| Rung | What runs there | Who it fits | What moves a business up |
|---|---|---|---|
| **1. The app on Vercel** | The native agent, chat, MCP tool calls, CRUD | Almost everyone, and every new client. Very little uptime to worry about | Work that outlasts a function call, or needs a shell |
| **2. Beam, on demand** | Long-running shells, virtual desktops, pull-request workers, model endpoints | A business with heavy jobs now and then. Scales to zero, so idle costs little | A need for an always-on agent, private data, or local models |
| **3. Their own Mac mini** | An always-on agent on hardware the business owns, and local models | A business that wants a machine and a private slice of its data | |

**Beam jobs worth building:**
- A pull-request worker that wakes, works the Board's requests, tests, opens a PR and shuts down.
- A browser desktop for testing.
- Model endpoints.

Virtual desktops are the priority. Beam's default images are Linux, so a Mac desktop means real Mac hardware.

**Other clouds.** Offer them only after the integrations are validated: Fly.io, Render, DigitalOcean, AWS. A full Cloudflare agent stack is an experimental track, and for now it's a theory.

### The Mac mini tier

- **It's the client's purchase and the client's machine.** PostScarcity sets it up, trains it and carries responsibility during incubation under a service contract, on site or hosted, then hands it over.
- **The label can be fun.** "Adopt a lobster" or "lobster in a tank" can be button text at selection time. The name is not settled.
- **Who signs in.** If it runs Claude, the client signs in to unmodified Claude Code themselves, and PostScarcity never holds that login. Otherwise use API keys or local models.
- **Owning the box is not the same as keeping data private.** A Mac mini running Claude still sends prompts to Anthropic. Only a local model keeps data in the building. The honest line is: route the small sensitive slice to a local model.

**Open: the pitch.** The founder saw subscription pricing as the big saving on this tier. The recommendation is not to sell it on that, because a rule change would break it and "ordinary, individual usage" is unclear for a business agent running all day. Get written clarity first. Sell it on ownership and on the private slice.

---

## 7. What the agent does alone, and when it speaks

### YOLO

`shared/roles.md` section 5 is the base. The default is "Ask me first." The Owner can relax one module and verb at a time, or turn on **YOLO**, which sets every relaxable verb to "Go ahead" for one agent.

Even in YOLO:
- **Never-relaxable actions stay gated** (`shared/roles.md` section 5, rule 7).
- **Nothing reaches outside the organization without a person's yes.** No text, email, post or call to anyone outside the business.
- **Every write is still logged** with Undo where Undo is possible.

There is no second, stronger mode. Super YOLO was considered and dropped.

### Quiet mode

- **Routine errors stay out of chat.** They go on a backlog. Another agent reads the backlog on a schedule and escalates only what needs a person.
- **A short urgent list can interrupt**, set by the Owner. Example: a critical payment failure.
- **Agent notices go to a staff-only home channel**, never to a client by default.
- **Clients never get unsolicited messages from the agent.**

---

## 8. Where the code lives

One repo by default. It's what keeps the agent, the tools and the app in step, and it makes hand-off one thing to transfer.

```
apps/web         the marketing site and back office. A Vercel project with its Root Directory set to this folder
apps/agent       anything that outlives a request. Deploys to Beam, Fly or another host, scoped to this folder
packages/tools   the one tool list the panel and the MCP server both read
```

One repo with several deploy targets is a normal setup. It runs today in production at a PostScarcity project deploying to Vercel, Beam and Fly.

**Watch these:**
- **Vercel skips unchanged projects** only if the repo is on GitHub and uses workspaces with unique package names and declared dependencies. A change outside the workspace rebuilds everything.
- **Vercel still downloads the whole repo.** Tracked media slowed one of our builds to 8.8 minutes. Keep media in blob storage.
- **Set path filters** so a change in one app doesn't redeploy the other.
- **The two apps can deploy out of step,** so changes to shared contracts have to stay backward compatible.
- **Beam from a subfolder** works by hand. It's untested from a GitHub Action.

Split the repo only if the agent becomes its own product with its own release cycle, or a client must not see its code. PostScarcity's own split between its site and admin is an exception, not the pattern.

---

## 9. The first thing to prove

The first connection to prove in ninety days is the marketing content workflow, end to end. Start with the website and blog, because search takes time to build and brand voice should be set early. Then move to social and broader content. Every later asset, from sales enablement to investor decks, reads from that voice.

---

## Open questions

1. Hand-off at day 60 or day 90?
2. How does a fresh agent learn?
3. Does the Mac mini tier drop subscription savings from its pitch? Recommended: yes.
4. What is the Mac mini tier called, and what does the service contract cost?
5. Which outside surfaces actually support MCP today?
