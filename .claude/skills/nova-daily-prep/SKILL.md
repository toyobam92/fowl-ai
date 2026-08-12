---
name: nova-daily-prep
description: The day before each Nova video posts (Mon/Wed/Fri), propose 2-3 current AI-news hook candidates via Telegram, wait for a pick, draft the full script + pick a background/outfit look, and open a PR for a single combined APPROVE. Use when the recurring cloud routine fires, or the user asks to prep tomorrow's Nova video.
---

# Nova daily prep

Gets tomorrow's Nova video script + look through the same propose → pick → draft → PR → Telegram-approve pipeline every other piece of FOWL AI content goes through. Runs the evening before each of Nova's 3 weekly slots (Mon/Wed/Fri), so approval happens the night before and the video has all night + morning to render before it auto-publishes.

**This skill does not render video or publish anything.** Once a PR is merged, `telegram-approve.yml` kicks off the actual HeyGen render (`automation/render_nova_video.py`) synchronously on `APPROVE <PR#>`; a separate scheduled workflow (`render-check-nova.yml`) polls until it's done and hands the finished video off to `automation/social-state.json`; a daily cron (`auto-publish-nova.yml`) posts it automatically on its scheduled day. This skill's job is narrower: pick the topic, write the script, pick the look, get it approved.

**Content must be current-events/news style** — Nova reports things that just happened ("a new agent just launched," "OpenAI is going to IPO"), not evergreen career-trend explainers. **Every script ends with the exact sign-off:** "I'm Nova. Stay ahead — for more AI news, subscribe to the link in the bio." See project memory (`feedback_nova_video_format`) for the full rationale — this was corrected after the first batch of videos skipped both rules.

**Telegram is one-way into this skill.** Same as `weekly-issue`: `telegram-approve.yml` is the only thing that receives Telegram messages; it relays anything it doesn't recognize (`APPROVE`/`SCHEDULE`/`PUBLISH <PR#>`) verbatim into `automation/inbox.json`. To send a message, call `gh workflow run notify.yml -f text="..."` — never curl Telegram directly (no `TELEGRAM_BOT_TOKEN` in this routine's environment).

**Inbox entries for this skill are always prefixed `NOVA `** (`NOVA 1`, `NOVA 2`, `NOVA 3`, `NOVA MORE`) so they never collide with `weekly-issue`'s bare-digit picks or `monthly-test`'s `TEST N` picks, which share the same inbox file. Only ever consume entries matching that prefix; leave everything else untouched.

**No revision loop in v1.** Unlike `weekly-issue`, this skill doesn't re-open PRs on feedback — if the script or look needs a change before approving, edit `automation/nova-previews/<publish_date>.md` and `automation/nova-pipeline-state.json` directly on the PR branch via GitHub's UI, or close the PR (next cycle will propose fresh topics 2 days later). Keeps this first version bounded; add a revision step later if it's actually needed.

## 0. Check state and inbox first

Read `automation/nova-pipeline-state.json` (create `{"status": "idle", "last_proposed": null}` if missing) and `automation/inbox.json` (`[]` if missing/drained). Branch on `status`:

- **`idle`** → **one proposal per publish slot, not "every time this fires."** Check `last_proposed`. If set and fewer than **2 days** have passed, exit quietly. Otherwise check today's day of week: only proceed on **Sunday, Tuesday, or Thursday** (the evenings before Mon/Wed/Fri); any other day, exit quietly. If proceeding, go to step 1.
- **`awaiting_topic_pick`** → look in the inbox for an entry matching `^NOVA\s+(\d+|MORE)$` (case-insensitive). If none, exit. If found, remove it from the inbox (write back without it, commit as its own small commit — `git add automation/inbox.json && git commit -m "Drain inbox" && git push`), then go to step 2.
- **`pr_open`** → check `gh pr view <pr_number> --json state,mergedAt`. If merged: nothing further for *this* skill to do — `telegram-approve.yml` already kicked off the render synchronously on approve, and `render-check-nova.yml` owns everything from here. Exit quietly (don't touch state; that render pipeline updates `nova-pipeline-state.json` itself once done). If closed without merging: set `status: "idle"`, clear `pr_number`/`pr_branch` (leave `last_proposed` as-is so the 2-day guard still applies), commit+push, exit. If still open: exit quietly.
- **`rendering`** or anything else → exit quietly; this state belongs to the GitHub Actions render pipeline, not this skill.

## 1. Propose 2-3 topics

Compute `publish_date` = tomorrow's date (`YYYY-MM-DD`). Compute `tone` from `publish_date`'s weekday: Monday or Friday → `"casual-professional"`, Wednesday → `"professional"`.

Use `WebSearch` for a *light* pass — enough to find 2-3 genuinely current AI-news items from the last few days (a launch, a funding/IPO move, a new model/feature, a notable industry shift). Not evergreen trend pieces — see the content-style note above. For each: a one-line title and a one-sentence why-it-matters-to-a-knowledge-worker angle.

Write to `automation/nova-pipeline-state.json`:

```json
{
  "status": "awaiting_topic_pick",
  "last_proposed": "<today>",
  "publish_date": "<tomorrow>",
  "tone": "<casual-professional|professional>",
  "topics": [{"title": "...", "why": "..."}, ...],
  "rejected_titles": [],
  "picked_topic": null,
  "script": null,
  "caption": null,
  "picked_look": null,
  "look_alternates": [],
  "pr_number": null,
  "pr_branch": null,
  "video_id": null,
  "last_updated": "<now>"
}
```

Commit+push directly to `main`. Then notify:

```
Nova's next episode (<publish_date>) — pick a topic:
1. <title> — <why>
2. ...
3. ...

Reply "NOVA 1", "NOVA 2", "NOVA 3", or "NOVA MORE" for different options.
```

Stop here.

## 2. Act on the pick

(Reached only from step 0 with a matching inbox entry already removed.)

- **`NOVA MORE`** → move current `topics` titles into `rejected_titles`, find 2-3 new current-news angles that don't repeat any rejected title, update state (`topics` replaced, `status` stays `awaiting_topic_pick`), commit+push, re-notify with the new list. Stop here.
- **`NOVA <digit>`** → set `picked_topic` to that topic, continue in this same run to step 3.

## 3. Draft the script

Voice: Nova reports the news — direct, catchy, current-affairs framing (see examples in the content-style note above). Structure: a hook line, 2-3 sentences of substance with real sourced specifics (numbers, names, dates — same sourcing bar as the newsletter, don't invent stats), then the mandatory closing line **exactly**:

"I'm Nova. Stay ahead — for more AI news, subscribe to the link in the bio."

Target 100-160 words total (roughly 40-60 seconds spoken) so the rendered video stays short-form. Write a one-sentence `caption` too (for the Facebook/Instagram post text, with 3-5 relevant hashtags including `#FOWLAI`).

## 4. Pick the look

Fetch the Nova avatar group's looks: `GET https://api.heygen.com/v2/avatar_group/6eef573ef32844d8b881010bf917601f/avatars` with header `X-Api-Key: $HEYGEN_API_KEY` (available in this routine's environment). Each entry has `id`, `name`, `image_url`, `default_voice_id`.

Pick one look whose `name` reads as fitting today's `tone`:
- `casual-professional` → simple tops, sweaters, everyday pieces (avoid anything named "Blazer," "Collared," "Button-Up," "Vest" — those read more formal).
- `professional` → blazers, collared/button-up pieces, structured tops.

Avoid repeating whatever look was used for the immediately prior episode if you can tell from `automation/social-state.json`'s most recent post. Pick one primary look and 1-2 alternates in the same tone family for the preview message.

Set `picked_look` to `{"avatar_id": "<id>", "name": "<name>", "image_url": "<image_url>"}` and `look_alternates` to a list of the same shape.

## 5. Open the PR

Write `automation/nova-previews/<publish_date>.md`:

```markdown
# Nova — <publish_date> (<tone>)

**Topic:** <picked topic title>

**Script:**
> <script, verbatim, including the sign-off line>

**Caption:**
> <caption, verbatim>

**Look:** <name>
<image_url>

**Alternates considered:**
- <alt 1 name> — <alt 1 image_url>
- <alt 2 name> — <alt 2 image_url>
```

```
git checkout -b update/nova-<publish_date>
git add automation/nova-previews/<publish_date>.md
git commit -m "Nova script + look for <publish_date>: <topic title>"
git push -u origin update/nova-<publish_date>
gh pr create --title "Nova — <publish_date>: <topic title>" --body "<short summary>"
```

Then update `automation/nova-pipeline-state.json` on `main` directly (separate commit) with the full state accumulated since step 2 — `picked_topic`, `script`, `caption`, `picked_look`, `look_alternates` all filled in, plus `status: "pr_open"`, `pr_number: <N>`, `pr_branch: "update/nova-<publish_date>"`. This is the only copy of the script/look that `render_nova_video.py` reads later (in a fresh checkout, after merge) — nothing on the PR branch itself is read programmatically, the preview file is for human review only.

```
git checkout main
git add automation/nova-pipeline-state.json
git commit -m "Mark Nova PR #<N> pending for <publish_date>"
git push
```

Stop here. Do not merge, do not call HeyGen, do not touch `automation/social-state.json`. `pr-notify.yml` pings Telegram automatically when the PR opens; `telegram-approve.yml` merges it **and kicks off the render** on a single `APPROVE <PR#>` reply — there's no separate publish step to remember, that's handled by the daily auto-publish cron once the video finishes rendering.

## 6. Report back

Summarize in chat (or, if run unattended, this is the routine's entire output): publish date, topic picked, tone, look picked, PR link.
