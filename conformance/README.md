# Conformance kit

Runnable checks for the rules a YEA app must keep. Your app has no upstream and its code will drift, so this tests behavior, not code. It works on any stack whose database is Postgres, and the static checks read TypeScript. Port them if you build in something else.

Status: running against one production app. Not yet run against an app built from scratch by an outside agent.

## Run it

```bash
cd conformance && npm install
YEA_ADMIN_URL=<owner connection> YEA_APP_URL=<the app's connection> \
  node check.mjs --config /path/to/your-app/yea.conformance.json --app /path/to/your-app
```

It writes nothing that stays. Every data check runs in a transaction and rolls back, so it is safe against production, though a test copy is better. It exits non-zero on any failure, so put it in CI. A new table with no audit trigger or row rule then fails the build.

## What it checks

| Group | Check |
|---|---|
| Database login | The app's login is not a superuser, can't bypass row rules, can't create roles and owns no tables |
| Row rules | Every table holding tenant data has row rules on |
| Audit | Every table has a change log trigger, or a written reason it doesn't |
| Log integrity | The app's login can't insert, rewrite, delete or truncate `change_log` |
| Behavior | A write produces a change log row with before, after and who. A wrong or missing tenant sees nothing and can't write |
| Grants | Every module has grants. An agent has no approve or configure grant, and its sends wait for a person |
| Code | Every server action calls a guard. Every route checks auth or has a written reason it is public. No route imports the send path |
| Dependencies | No known critical or high advisories in production dependencies |

## Config

See `example.conformance.json`. Every exemption needs a reason, because the reason is what gets reviewed.
