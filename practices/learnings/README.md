# Learnings inbox

Lessons sent back by real builds, one file per build, waiting for a maintainer to fold them into `practices/traps.md`, the README or a PRD. Once folded, the file is removed and the `CHANGELOG.md` entry says where it went.

How to send one, and what must never be in it: [`CONTRIBUTING.md`](../../CONTRIBUTING.md).

## Template

Copy this into `practices/learnings/<YYYY-MM-DD>-<short-topic>.md`.

```markdown
# Learnings: <short topic>

- **Stack:** <framework, database, host, model router>
- **Spec commit built from:** <sha from yea.lock.json>
- **Owner said yes to sharing:** yes

## <One-sentence learning, in bold in traps.md style>

- **What happened:** <the symptom, paraphrased, no logs>
- **Why:** <the cause>
- **The fix:** <what worked>
- **The reference should say:** <the sentence> in <file and section>
```

Repeat the `##` block for each learning. Five good ones beat twenty thin ones.
