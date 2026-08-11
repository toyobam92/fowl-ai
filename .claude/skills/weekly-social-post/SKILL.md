---
name: weekly-social-post
description: Take this week's finalized Nova video scripts (Facebook, Instagram, TikTok) from automation/social-state.json, open a PR with a readable preview for review, and — once approved and merged — hand off to the Telegram-gated PUBLISH step instead of posting anything automatically. Use when it's time to review/approve this week's social posts, the recurring cloud routine fires, or the user asks about the social posting pipeline.
---

# Weekly social post

Gets this week's Nova episode scripts (Facebook + Instagram + TikTok; Threads is deferred, see the TODO in step 1) through the same branch → PR → Telegram-approve pipeline every other piece of FOWL AI content already goes through, then stops — actually publishing to Facebook/Instagram or posting to TikTok is a separate, explicit step this skill never triggers itself.

**This skill does not write scripts, generate videos, or post anything.** Script drafting happens upstream (from the Nova hook backlog); video rendering is blocked on a HeyGen API key as of 2026-08-11 (`video_path` stays `null` in the state file until that's wired up — see project memory). This skill's job is narrower: turn already-finalized scripts+captions into a reviewable PR, and later, once merged, get out of the way so the human-gated publish step can run.

**Reuses the existing publish pipeline for the review/approve half.** `pr-notify.yml` already fires on any opened PR and pings Telegram with the diff stat — no changes needed there. `telegram-approve.yml` merges on `APPROVE <PR#>` the same way it does for every other PR in this repo, and separately handles a `PUBLISH <PR#>` reply (added specifically for this pipeline) that runs `automation/post_to_meta.py` for Facebook + Instagram and reminds the owner that TikTok needs an interactive browser session. This skill never calls Telegram directly and never runs `post_to_meta.py` itself — same "one receiver, two-step approve-then-act gate" shape as `SCHEDULE <PR#>` for the newsletter.

## 0. Check state first

Read `automation/social-state.json` (create `{"status": "idle", "last_drafted": null, "pr_number": null, "posts": []}` if missing). Branch on `status`:

- **`drafted`** (scripts+captions finalized, no PR yet) → proceed to step 1.
- **`pr_open`** (PR opened last cycle, awaiting merge) → check `gh pr view <pr_number> --json state,mergedAt`:
  - Merged → set `status: "merged"`; commit+push `automation/social-state.json` to `main`; exit. (Nothing more for this skill to do — actually posting requires the explicit `PUBLISH <PR#>` reply, handled entirely in `telegram-approve.yml`.)
  - Closed without merging → set `status: "drafted"`, `pr_number: null` (so the next cycle retries and reopens a PR); commit+push to `main`; exit.
  - Still open → exit quietly. Never open a second PR while one is outstanding.
- **`merged`** (PR merged, awaiting the human's `PUBLISH <PR#>` reply and/or manual TikTok posting) → check whether every post's `platforms_published` is now `{facebook: true, instagram: true, tiktok: true}`. If so, the cycle is complete: set `status: "idle"`, stamp `last_drafted` to today, clear `pr_number`; commit+push to `main`; exit. If not all done yet, exit quietly — this skill never chases the human for `PUBLISH` or posts to TikTok itself; it only waits.
- **`idle`** → nothing to do yet this cycle (next week's scripts land in this file the same way this week's did — upstream of this skill). Exit quietly.
- Anything else → treat as `drafted` if `posts` is non-empty, otherwise as `idle`.

## 1. Render the preview

(Reached only from step 0 with `status: "drafted"`.)

For each post in `posts`, render a readable Markdown preview so a reviewer can read the actual scripts/captions in the PR diff (JSON alone is not readable enough for a review-through-git-diff workflow). Write it to `automation/social-previews/<week_of>.md` (use today's date, `YYYY-MM-DD`, as `<week_of>` since this state file has no dedicated date field yet):

```markdown
# Social posts — week of <week_of>

## Monday — hook #3
**Video:** not yet rendered (HeyGen pending)  <!-- or the video_path URL, once set -->

**Script:**
> <script, verbatim>

**Caption:**
> <caption, verbatim>

---

## Wednesday — hook #4
...

## Friday — hook #5
...
```

<!-- TODO: Threads is deferred entirely for now (per project scope) -- no
     preview section, no publish step, nothing built for it here yet. -->

## 2. Branch, commit, and open a PR

```
git checkout -b update/social-<week_of>
git add automation/social-previews/<week_of>.md
git commit -m "Social posts for week of <week_of>: review preview"
git push -u origin update/social-<week_of>
gh pr create --title "Social posts — week of <week_of>" --body "<summary: which days/hooks, note that video rendering is still pending HeyGen access, so nothing publishes until video_path is filled in and PUBLISH <PR#> is sent after merge>"
```

Then update `automation/social-state.json` on `main` directly (separate commit, not on the branch): `status: "pr_open"`, `pr_number: <N>`.

```
git checkout main
git add automation/social-state.json
git commit -m "Mark social posts PR #<N> pending"
git push
```

Stop here. Do not merge, do not push the preview straight to `main`, and do not call the Meta Graph API or touch TikTok. `pr-notify.yml` pings Telegram automatically when the PR opens; `telegram-approve.yml` merges it (deploys nothing beyond the repo itself — this PR only records the approved content) on `APPROVE <PR#>`, and separately unlocks Facebook + Instagram publishing only on a later, explicit `PUBLISH <PR#>` reply once that PR is merged.

## 3. Report back

Summarize in chat (or, if run unattended by the cloud routine, this is the routine's entire output): which days/hooks were included, whether videos are rendered yet (`video_path` set) or still pending HeyGen, the PR link, and — once `status` reaches `merged` or later — how many of the 3×3 platform slots are published so far.
