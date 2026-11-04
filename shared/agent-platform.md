# The agent platform

Part of the YEA docs. How agents connect to a YEA app, where they run, what they may do alone, and who owns what. Written 2026-11-03 from the founder's decisions. This is direction: unless a line says it runs in production, treat it as not yet proven and test harder. `shared/roles.md` owns permissions and `shared/chat.md` owns the panel.

---

## 1. The calls we made

1. **The business app is the product. Agents are workers inside it.** The app holds the data, the rules and the screens. An agent can be swapped. The app stays.
2. **Three pieces, one repo.** A marketing site, a back office and an agent. They ship together so the agent's tools never drift from the app (section 8).
3. **Stand it up, then hand it over.** The vendor builds the app, trains the agent and hands everything to the business on day 90 (section 3).
4. **The back office is how Hermes connects.** The app asks the business's own Hermes and shows the answer. MCP is being tested read-only, and is not a commitment yet (section 4).
5. **The agent in the app, plus Hermes when you want one.** The agent on Vercel covers everyday work. Hermes is the main way in for a business that runs its own (section 5).
6. **Vercel plus Beam is all most businesses need.** A Mac mini sits on top and serves its own purpose (section 6).
7. **One relax switch: YOLO.** There is no super YOLO. Nothing reaches outside the organization without a person's yes (section 7).
8. **Quiet by default.** Errors go to a backlog, not into chat (section 7).

---

## 2. Who can reach the app

| Surface | How it connects | Status |
|---|---|---|
| The chat panel | Native. Runs as the signed-in user, sees the page. `shared/chat.md` | Runs in production |
| Hermes | The back office: the app relays a question to the business's own Hermes and shows the answer. This is the main way in. The contract ships as a template | Runs in production at PostScarcity |
| Claude Code, Codex and other outside agents | MCP, if the test in section 4 earns it | Being tested, read-only |
| Yui | Yui is its own agent and a separate PostScarcity product. One day it may become the agent layer. It is not part of this work | Paused |

Every surface obeys one rule: **an agent's access never goes above the signed-in user's role.** A connection made by a Contractor sees that Contractor's book, and nothing more.

---

## 3. Stand it up, then hand it over

- **While it's being built** the vendor carries the setup and the training.
- **On day 90** everything belongs to the business: repo, hosting, database, model keys, domain. If you are the vendor, put everything in their name from day one, so hand-over is only a change of who drives.
- **After that** the business runs its own compute and its own model account. The vendor can stay on under a service contract, but the business can leave with everything.

**Open: who pays compute during the ninety days?** The business, in its own accounts, is the simplest answer. If the vendor carries it, that cost has to go in the price.

---

## 4. The back office and MCP

Both are one party asking and the other answering. The difference is who starts.

| | Who starts | What it's for |
|---|---|---|
| **Back office** | The app asks Hermes | Someone in the app, or on a call, gets an answer from the business's own agent |
| **MCP** | The agent calls the app | The agent looks up records, or uses the app's tools, while it works |

The back office doesn't give Hermes a way to look things up in the app. Without some path in, an agent running on its own machine knows only what it was told. The other options are a database login, which walks around the role check, or a hand-built endpoint for each job.

**So MCP has to earn its place.** The test: the same Hermes answers the same real questions with and without read-only MCP tools. If the answers aren't better, stay with the back office.

If it does earn its place:
- **One tool list.** The panel and the MCP server read the same definitions, in `packages/tools`.
- **Same checks.** Each call goes through `can()`, row rules and `change_log`, like a chat tool. Gated verbs still wait for a person.
- **Sign-in.** The connection authenticates as a real user of the app, never as a shared key with its own powers.
- **Change over time.** Adding a tool is safe. Renaming or removing one is a breaking change, and it goes in the release notes with its replacement.

Read-only comes first. Writes need `can()` and `change_log` in place before an outside agent gets them.

---

## 5. The agent

### The agent in the app

The default. It runs on Vercel, lives in the app and needs nothing but an API key.

- **Reads and proposes.** On day one it reads what the signed-in user can read and proposes changes. Writes follow `shared/roles.md` section 5.
- **Connectors are the value.** An agent that can't reach the business's tools isn't worth much. Preconfigure what works with no setup, then add connectors in the order the owner needs them.
- **It files what it can't do.** Inside a Vercel function it can't change the software, so it files a Board card (`shared/chat.md` section 6). When a person says "do these three," that work runs on the next rung up.

### Hermes

A business that wants a long-lived agent with its own memory, schedules and machine runs Hermes and connects it through the back office. The app does not change.

### Watching Cloudflare

Cloudflare's agent tools suit an agent in the app: each agent gets its own small database, schedules and sub-agents, and isn't billed for run time while asleep. It's early, and it's on watch, not in the plan. Its containers aren't a home for Hermes: they stop when idle, and their disks go with them.

### Model access

- **Native agent and anything PostScarcity hosts: API keys only.** Anthropic's terms bar third parties from offering Claude login in their own apps, from routing requests through plan credentials, and from paying for a user's Claude usage. Products built on the Agent SDK should use API keys. So YEA does not offer "log in with your Claude subscription" on a cloud server.
- **OpenAI** offers Sign in with ChatGPT for other apps, with an interest form for paid or remotely hosted ones. Check the current terms before building on it.
- **Keep the provider a config value** behind one `callModel()` (`admin/run/agents/`).

Read each vendor's current terms before relying on any of this. This is a reading of them, not legal advice.

### Open: how a fresh agent learns

Not decided. A preloaded agent starts with months of context, and a new YEA agent starts with `docs/interview.md`, the config and whatever is in the app. How it accrues context and gets better is the biggest open question on this page.

---

## 6. Compute

Most businesses need two things. A Mac mini sits on top for a business that wants one.

| | What runs there | Who it fits |
|---|---|---|
| **The app on Vercel** | The agent in the app, chat, CRUD | Everyone |
| **Beam** | Long-running shells, virtual desktops, pull-request workers, model endpoints, and an always-on Hermes | A business with heavier jobs, or one that wants its own agent |
| **Their own Mac mini** | An always-on agent on hardware the business owns, and local models | A business that wants a machine and a private slice of its data. Its own purpose, not a next step up |

### An agent instance

An instance is one thing: the Hermes Docker image, a persistent disk, a model key, and a connection to the app. Any host that can run that can hold an agent. **Start on Beam.**

Other hosts are options for later, and untested by us: a plain Linux VM such as a DigitalOcean Droplet is cheaper when always on, and Render works with a disk but one instance only. Avoid hosts with no persistent disk, because Hermes would lose its memory.

Never put a database login on the machine.

**Beam jobs worth building:**
- A pull-request worker that wakes, works the Board's requests, tests, opens a PR and shuts down.
- A browser desktop for testing.
- Model endpoints.

Virtual desktops are the priority. Beam's default images are Linux, so a Mac desktop means real Mac hardware.

### The Mac mini tier

- **It's the client's purchase and the client's machine.** The vendor sets it up at the client's site, trains it and carries responsibility until day 90 under a service contract, then hands it over.
- **The label can be fun.** "Your own machine" in agent mode, "Adopt a lobster" in lobster mode.
- **Who signs in.** If it runs Claude, the client signs in to unmodified Claude Code themselves, and PostScarcity never holds that login. Otherwise use API keys or local models.
- **Owning the box is not the same as keeping data private.** A Mac mini running Claude still sends prompts to Anthropic. Only a local model keeps data in the building. The honest line is: route the small sensitive slice to a local model.

**The pitch.** Sell it on ownership and on the private slice, not on subscription savings. A rule change would break that, and "ordinary, individual usage" is unclear for a business agent running all day.

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

One repo with several deploy targets is a normal setup. We tested it from GitHub Actions: a change to the web app deployed only the web app, a change to the agent deployed only the agent, and a change to the shared package deployed both.

**Watch these:**
- **Vercel skips unchanged projects** only if the repo is on GitHub and uses workspaces with unique package names and declared dependencies. A change outside the workspace rebuilds everything.
- **Vercel still downloads the whole repo.** Tracked media slowed one of our builds to 8.8 minutes. Keep media in blob storage.
- **Set path filters** so a change in one app doesn't redeploy the other.
- **The two apps can deploy out of step,** so changes to shared contracts have to stay backward compatible.
- **Beam from a subfolder** works in CI, but the build context defaults to the Dockerfile's folder. A shared package needs `--context-dir`.
- **Beam apps are public by default,** and old versions keep serving at their own URLs. Lock them down and clean them up.
- **Vercel's skip has an edge.** Files at the repo root, such as the README or `.github`, still build the web app.

Split the repo only if the agent becomes its own product with its own release cycle, or a client must not see its code. PostScarcity's own split between its site and admin is an exception, not the pattern.

---

## 9. The first thing to prove

The first connection to prove in ninety days is the marketing content workflow, end to end. Start with the website and blog, because search takes time to build and brand voice should be set early. Then move to social and broader content. Every later asset, from sales enablement to investor decks, reads from that voice.

---

## Open questions

1. Does MCP earn its place? The test in section 4 decides.
2. Who pays compute during the ninety days?
3. How does a fresh agent learn?
4. Does the agent in the app stay on Vercel, or move somewhere like Cloudflare?
