# Data model: the shared spine

Part of the YEA docs. Revised 2026-10-31.

Every module owns its own tables (its PRD lists them). This file holds the tables every module shares and the rules every table follows. Build these first. Default store is Postgres; any relational database with row-level rules works.

## Rules for every table

1. **Ids.** `id` is a UUID or bigint, assigned by the database. Never reuse an id. Anchors in the chat (`lead:123`) use it, so it must be stable for the life of the record.
2. **Tenant.** Every row carries `org_id`. One database can hold one business or many. Row rules filter on it first.
3. **Ownership.** Every record table has `owner_id` (the user who owns it) and, where work is assigned, `assignee_id`. Customer-visible tables add `customer_id`. These three columns are what `own` scope in `shared/roles.md` checks.
4. **Timestamps.** `created_at`, `updated_at`, and `deleted_at` (soft delete). Hard delete is a never-relaxable verb and runs as a separate job.
5. **No silent writes.** Every insert, update and delete made through the app writes a `change_log` row in the same transaction. That includes the agent and background jobs.
6. **Money** is stored in integer cents with a `currency` column. Never floats.
7. **Status fields** hold a key from the module's `fields.stages`, not free text, so a relabel never breaks a query.
8. **Custom fields** from config live in a `custom jsonb` column on the record, validated against the module's `fields.custom` list.
9. **JSON list items** that the chat can point at get a content-hash key, never a list position.

## Shared tables

### Identity and access

| Table | Holds | Key columns |
|---|---|---|
| `orgs` | The business | `id`, `name`, `industry`, `url`, `config jsonb` (the AppConfig from `shared/modules.md` section 5) |
| `users` | Every person who signs in, staff and customers | `id`, `org_id`, `email`, `name`, `phone`, `avatar_url`, `last_seen_at` |
| `roles` | The six types and named presets | `key`, `type`, `label`, `customer_kind` |
| `user_roles` | Who has which role | `user_id`, `role_key` (one admin-side type per user; customer kinds can stack) |
| `role_grants` | The permission matrix as rows | `role`, `module`, `verb`, `scope`, `gated`, `limit jsonb`, `fields text[]` |
| `agent_permissions` | What the agent runs as, and per-module relax | `agent_id`, `runs_as_role`, `module`, `verb`, `relaxed`, `limit jsonb` |
| `sessions`, `auth_log` | Sign-in sessions and every sign-in attempt | magic link or passkey; no passwords stored by default |

### People and companies

| Table | Holds | Key columns |
|---|---|---|
| `people` | Every human the business deals with: leads, customers, contacts, vendors | `id`, `org_id`, `name`, `email`, `phone`, `company_id`, `kind`, `owner_id`, `consent jsonb` |
| `companies` | Accounts, prospects, partners | `id`, `org_id`, `name`, `domain`, `kind`, `stage`, `owner_id` |
| `activities` | The timeline on any record: notes, calls, emails, meetings | `id`, `subject_kind`, `subject_id`, `kind`, `body`, `actor_id`, `at` |
| `tags`, `taggings` | Labels on any record | polymorphic `subject_kind` + `subject_id` |

`people` is one table on purpose. A lead who becomes a customer is the same row with a new `kind` and a new `user_id` once they sign in. History never splits.

### Work and messages

| Table | Holds | Key columns |
|---|---|---|
| `threads`, `messages` | Every message in and out, any channel | `channel` (email, sms, web_chat, dm), `direction`, `person_id`, `status` |
| `files` | Every upload and generated asset | `id`, `storage_key`, `mime`, `bytes`, `subject_kind`, `subject_id`, `alt` |
| `cards` | The Board: requests, tasks, bugs, ideas | `id`, `title`, `body`, `status`, `assignee_id`, `source` (chat, inbox, call, person) |
| `approvals` | Gated actions waiting for a human yes | `id`, `module`, `verb`, `payload jsonb`, `preview text`, `requested_by`, `decided_by`, `decided_at`, `outcome` |
| `notifications` | What each user needs to see | `user_id`, `kind`, `subject_kind`, `subject_id`, `read_at` |

### The agent

| Table | Holds | Key columns |
|---|---|---|
| `agents` | Each agent the business runs | `id`, `name`, `runs_as_role`, `prompt_key`, `monthly_cap_cents` |
| `chat_threads`, `chat_messages` | Chat panel history per user | `user_id`, `page_context jsonb`, `chips jsonb`, `tool_calls jsonb` |
| `agent_runs` | Every background job and its result | `agent_id`, `trigger`, `status`, `started_at`, `ended_at`, `summary` |
| `model_calls` | Every model call with its real cost | `agent_run_id` or `chat_message_id`, `model`, `tokens_in`, `tokens_out`, `cost_cents` |

### The audit spine

| Table | Holds | Key columns |
|---|---|---|
| `change_log` | Every write, by anyone | `id`, `org_id`, `actor_kind` (person, agent, system), `actor_id`, `on_behalf_of`, `chat_message_id`, `subject_kind`, `subject_id`, `op` (insert, update, delete), `before jsonb`, `after jsonb`, `undone_by`, `at` |

Undo writes a new `change_log` row that restores `before`, and sets `undone_by` on the original. If a later change touched the same field, Undo shows both and asks. Log (Run > Log) is a view over this table.

## Sample data

Every table that a module owns has a seed generator named by the module's `sample` knob (`shared/modules.md` section 5). Demo data uses `.example` domains and 555-01xx phone numbers, never a real person or business.
