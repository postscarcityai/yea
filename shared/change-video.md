# Change videos

Part of the YEA docs. Written 2026-11-03. This is how a change gets approved. Nobody reads pull requests. The agent makes a short video of what changed, the owner watches it, and says yes or no. Not yet proven as a gate: the kit has made real plan films, and we have not yet run the gate on a live app.

---

## 1. When

| Change | Video? |
|---|---|
| Content and data: a show date, a blog post, a price the owner asked for | No. It ships, and it lands in Log with Undo |
| A bug fix the owner can't see | No. Conformance passes, and it ships |
| A new page, a new flow, or anything that changes how a screen works | **Yes** |
| A plan for work not built yet | **Yes**, before the work |
| Roles, agent permissions, payment or email rails, a migration that deletes data | **Yes**, and the owner's yes is required every time |

When unsure, make the video. Two minutes of watching beats a surprise.

---

## 2. The steps

The agent does all of this. Add it to the agent's standing instructions, so it runs on every qualifying change.

1. **Build on a branch,** and deploy a preview.
2. **Run the checks.** Tests, the PRD's acceptance criteria, `conformance/`. No passing checks, no video.
3. **Capture the real thing.** Take screenshots of the preview doing the new work, on desktop and phone. Use made-up data if the video will leave the company.
4. **Write the script,** using section 3.
5. **Build it** with `change-video/`, then watch the contact sheet. Check every scene against what actually shipped.
6. **Post it** on the Board card, and send the owner the video with one question.
7. **Yes ships it.** Merge, confirm the new version is live, and put the live link on the card. **No,** or any note, goes back as changes, and the agent re-cuts.

The video and the yes stay on the card, so Log can show what was approved and when.

---

## 3. The script

Keep it under three minutes. Use this order and cut any part that adds nothing:

1. **What changed,** in one sentence, in the owner's words.
2. **Before and after.** Show the screens.
3. **What the owner will notice** tomorrow morning.
4. **What it costs,** if anything changed.
5. **What you didn't test.** Say it out loud.
6. **The question.** One decision, on the dark closing scene.

Rules:

- **Say what's real.** Every scene's footer gives its status: Running, Preview, or Proposed, not built. Solid lines are running or fact. Dashed lines are planned.
- **Plain words.** No commit, deploy, branch or schema. Say what the business sees.
- **Print the words on the spoken word.** Nothing slides or fades in.
- **Facts come from the code,** checked that day. A confident video that's wrong is worse than none.
- **Client data stays private.** Send the video to the owner only.

---

## 4. Make it yours

`change-video/` is the framework. Give it your fonts, colors, logo and art through a theme file, and every video reads as your brand.
