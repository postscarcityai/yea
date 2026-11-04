#!/usr/bin/env node
// YEA conformance checks. See README.md. Every data check runs in a transaction that rolls back.
import { execSync } from "node:child_process";
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join, relative } from "node:path";
import pg from "pg";

const arg = (name) => {
  const i = process.argv.indexOf(`--${name}`);
  return i > 0 ? process.argv[i + 1] : undefined;
};
const configPath = arg("config");
const appDir = arg("app") ?? process.cwd();
if (!configPath) {
  console.error("Usage: node check.mjs --config yea.conformance.json --app <dir> [--skip-deps]");
  process.exit(2);
}
const cfg = JSON.parse(readFileSync(configPath, "utf8"));

const results = [];
const check = (group, name, ok, detail = "") => results.push({ group, name, ok: !!ok, detail });

// Unexplained exemptions are the failure this kit exists to catch.
for (const key of ["publicRoutes", "auditExempt", "rowRuleExempt"]) {
  for (const [what, why] of Object.entries(cfg[key] ?? {})) check("Config", `${key}: ${what} has a reason`, typeof why === "string" && why.trim().length > 5);
}

function walk(dir, out = []) {
  for (const name of readdirSync(dir)) {
    if (name === "node_modules" || name.startsWith(".")) continue;
    const p = join(dir, name);
    if (statSync(p).isDirectory()) walk(p, out);
    else if (/\.(ts|tsx)$/.test(name)) out.push(p);
  }
  return out;
}

function exportedFunctions(src) {
  const out = [];
  const re = /^export async function (\w+)\s*\(/gm;
  const starts = [...src.matchAll(re)];
  starts.forEach((m, i) => {
    const end = starts[i + 1]?.index ?? src.length;
    out.push({ name: m[1], body: src.slice(m.index, end) });
  });
  return out;
}

function codeChecks() {
  const files = (cfg.appDirs ?? ["app"]).flatMap((d) => walk(join(appDir, d)));
  const guards = cfg.actionGuards ?? [];
  // A guard can be a local wrapper, as long as the wrapper itself calls a real guard.
  for (const file of files) {
    const src = readFileSync(file, "utf8");
    const rel = relative(appDir, file);
    if (/^\s*["']use server["']/m.test(src.split("\n").slice(0, 3).join("\n"))) {
      const wrappers = [...src.matchAll(/(?:const|function)\s+(\w+)[^\n]*(?:=>|\{)\s*\n?[^\n]*?(\w+)\(/g)].filter((m) => guards.includes(m[2])).map((m) => m[1]);
      const allowed = [...guards, ...wrappers];
      for (const fn of exportedFunctions(src)) {
        check("Code", `action ${rel}: ${fn.name} is guarded`, allowed.some((g) => fn.body.includes(`${g}(`)));
      }
    }
    if (/\/route\.ts$/.test(rel)) {
      const isPublic = !!cfg.publicRoutes?.[rel];
      const hasAuth = (cfg.routeAuthMarkers ?? []).some((m) => src.includes(m));
      check("Code", `route ${rel} checks auth`, isPublic || hasAuth, isPublic ? `public: ${cfg.publicRoutes[rel]}` : "");
      for (const banned of cfg.noRouteImports ?? []) {
        const imports = src.split("\n").filter((l) => /^\s*(import|export)\b.*from\s|require\(|import\(/.test(l));
        check("Code", `route ${rel} can't reach ${banned}`, !imports.some((l) => l.includes(banned)));
      }
    }
  }
}

async function dbChecks(adminUrl, appUrl) {
  const admin = new pg.Client({ connectionString: adminUrl });
  const app = new pg.Client({ connectionString: appUrl });
  await admin.connect();
  await app.connect();
  try {
    const { rows: [me] } = await app.query("select current_user as name");
    const { rows: [role] } = await admin.query("select rolsuper, rolbypassrls, rolcreaterole, rolcreatedb from pg_roles where rolname = $1", [me.name]);
    check("Database login", "not a superuser", !role.rolsuper);
    check("Database login", "can't bypass row rules", !role.rolbypassrls);
    check("Database login", "can't create roles or databases", !role.rolcreaterole && !role.rolcreatedb);
    const { rows: owned } = await admin.query("select tablename from pg_tables where schemaname = 'public' and tableowner = $1", [me.name]);
    check("Database login", "owns no tables", owned.length === 0, owned.map((t) => t.tablename).join(", "));

    const { rows: tables } = await admin.query(`
      select c.relname as name, c.relrowsecurity as rls,
             exists (select 1 from pg_policy p where p.polrelid = c.oid) as has_policy,
             exists (select 1 from pg_trigger t join pg_proc f on f.oid = t.tgfoid where t.tgrelid = c.oid and not t.tgisinternal and f.proname = 'log_change') as audited
        from pg_class c join pg_namespace n on n.oid = c.relnamespace
       where n.nspname = 'public' and c.relkind = 'r' order by 1`);
    for (const t of tables) {
      if (!cfg.rowRuleExempt?.[t.name]) check("Row rules", `${t.name} has row rules`, t.rls && t.has_policy);
      if (!cfg.auditExempt?.[t.name] && t.name !== cfg.logTable) check("Audit", `${t.name} is audited`, t.audited);
    }

    const log = cfg.logTable ?? "change_log";
    const denied = async (name, sql) => {
      await app.query("savepoint s");
      try {
        await app.query(sql);
        check("Log integrity", name, false, "the statement ran");
      } catch (e) {
        check("Log integrity", name, /permission denied|row-level security/.test(e.message), e.message);
      }
      await app.query("rollback to savepoint s");
    };
    await app.query("begin");
    await denied("app login can't insert into the log", `insert into ${log} (actor_kind, actor_label, subject_kind, op) values ('system', 'x', 'x', 'insert')`);
    await denied("app login can't rewrite the log", `update ${log} set actor_label = 'x'`);
    await denied("app login can't delete the log", `delete from ${log}`);
    await denied("app login can't truncate the log", `truncate ${log}`);
    await app.query("rollback");

    if (cfg.probe) {
      const set = (v) => app.query(`select set_config($1, $2, true)`, [cfg.tenantSetting, v]);
      await app.query("begin");
      await set(cfg.tenantSlug);
      const { rows: [row] } = await app.query(cfg.probe.insert, [cfg.tenantSlug]);
      const { rows: logged } = await app.query(`select before, after, actor_kind, actor_label, fields from ${log} where subject_kind = $1 and subject_id = $2`, [cfg.probe.table, String(row.id)]);
      check("Behavior", "a write lands in the change log", logged.length === 1 && logged[0].after && logged[0].fields.length > 0);
      check("Behavior", "the change log says who", !!logged[0]?.actor_kind && !!logged[0]?.actor_label);
      const { rows: seen } = await app.query(`select id from ${cfg.probe.table} where id = $1`, [row.id]);
      check("Behavior", "the right tenant sees its row", seen.length === 1);

      await set("no-such-tenant");
      const { rows: other } = await app.query(`select id from ${cfg.probe.table} where id = $1`, [row.id]);
      check("Behavior", "a wrong tenant sees nothing", other.length === 0);
      await app.query("savepoint w");
      try {
        await app.query(cfg.probe.insert, [cfg.tenantSlug]);
        check("Behavior", "a wrong tenant can't write", false, "the insert ran");
      } catch (e) {
        check("Behavior", "a wrong tenant can't write", /row-level security|null value/.test(e.message), e.message);
      }
      await app.query("rollback to savepoint w");

      await set("");
      const { rows: none } = await app.query(`select id from ${cfg.probe.table} where id = $1`, [row.id]);
      check("Behavior", "no tenant sees nothing", none.length === 0);
      await app.query("rollback");
    }

    const { rows: grants } = await admin.query("select role, module, verb, gated from role_grants");
    const agent = cfg.agentRole ?? "agent";
    for (const mod of cfg.modules ?? []) {
      const roles = grants.filter((g) => g.module === mod || g.module === "*");
      check("Grants", `${mod} has grants`, roles.length > 0);
    }
    const bad = grants.filter((g) => g.role === agent && ["approve", "configure", "*"].includes(g.verb));
    check("Grants", "agent can't approve or configure", bad.length === 0, bad.map((g) => `${g.module}.${g.verb}`).join(", "));
    const open = grants.filter((g) => g.role === agent && (cfg.gatedVerbs ?? ["send"]).includes(g.verb) && !g.gated);
    check("Grants", "agent's sends wait for a person", open.length === 0, open.map((g) => g.module).join(", "));
    const owners = grants.filter((g) => g.role === "owner");
    check("Grants", "an owner exists in the matrix", owners.length > 0);
  } finally {
    await app.end();
    await admin.end();
  }
}

function dependencyCheck() {
  if (!cfg.dependencyAudit || process.argv.includes("--skip-deps")) return;
  let out = "";
  try {
    out = execSync(cfg.dependencyAudit, { cwd: appDir, encoding: "utf8", stdio: ["ignore", "pipe", "ignore"] });
  } catch (e) {
    out = e.stdout ?? ""; // audit tools exit non-zero when they find something
  }
  let counts = null;
  try {
    counts = JSON.parse(out).metadata?.vulnerabilities;
  } catch {
    check("Dependencies", "audit ran", false, "no readable output");
    return;
  }
  const high = (counts?.critical ?? 0) + (counts?.high ?? 0);
  check("Dependencies", "no critical or high advisories", high === 0, `${counts?.critical ?? 0} critical, ${counts?.high ?? 0} high`);
}

codeChecks();
dependencyCheck();
const { YEA_ADMIN_URL, YEA_APP_URL } = process.env;
if (YEA_ADMIN_URL && YEA_APP_URL) await dbChecks(YEA_ADMIN_URL, YEA_APP_URL);
else check("Database login", "connections given", false, "set YEA_ADMIN_URL and YEA_APP_URL");

let failed = 0;
const groups = [...new Set(results.map((r) => r.group))];
for (const g of groups) {
  const rows = results.filter((r) => r.group === g);
  const bad = rows.filter((r) => !r.ok);
  console.log(`${bad.length ? "FAIL" : "PASS"}  ${g} (${rows.length - bad.length}/${rows.length})`);
  for (const r of bad) console.log(`      x ${r.name}${r.detail ? `: ${r.detail}` : ""}`);
  failed += bad.length;
}
console.log(failed ? `\n${failed} failed.` : `\nAll ${results.length} checks passed.`);
process.exit(failed ? 1 : 0);
