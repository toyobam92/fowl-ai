---
name: schedule-issue
description: Schedule a merged FOWL AI issue's email in EmailOctopus by driving the owner's real logged-in browser via claude-in-chrome — duplicate the latest campaign, paste the issue HTML, and schedule for the next Monday 7:45am ET. Use when the user says "schedule issue <N>", replies to the schedule-watchdog Telegram nudge, or otherwise asks to send/schedule an already-merged issue in EmailOctopus.
---

# Schedule issue

Turns the interactive EmailOctopus step into one pass instead of ad hoc trial-and-error. **This can only run interactively in Claude Code** — EmailOctopus's dashboard sits behind Cloudflare bot-protection that blocks headless automation outright (confirmed dead end, see `automation/emailoctopus-draft.mjs` and the `SCHEDULE <PR#>` handler in `.github/workflows/telegram-approve.yml`, which deliberately no-ops and just points here instead of dispatching a doomed headless run). `schedule-watchdog.yml` nudges the owner on Telegram every 6h when a merged issue is still unscheduled — that nudge, or the owner typing "schedule issue N" directly, are the two ways into this skill.

**Never run this without an explicit ask in the current conversation.** Scheduling reaches the real ~205-subscriber Audience list. This skill is itself the distinct, deliberate authorization channel for that (same shape as `SCHEDULE <PR#>` elsewhere in this repo) — don't infer it from a merge or an `APPROVE`.

## 0. Identify the issue and confirm it's ready

If the user gave a number, use it. Otherwise: `git -C <repo> pull --ff-only` if the local checkout is behind, then find the highest-numbered `issues/<date>/` folder (grep `Issue N` out of its `<title>`) and confirm with the user that's the one they mean if it's ambiguous.

Check the issue is actually merged to `main` (it will be, if you can see its folder after a fresh pull — the PR flow never puts unpublished content on `main` directly). If you can't find the folder after pulling, stop and tell the user — don't try to draft or guess content.

## 1. Derive subject and preview text from the HTML

Pull from the issue's own `<head>`:
- `og:title` meta content is `FOWL AI · Issue N · <hook>` — the email subject is `Issue N: <hook>` (same "Issue N:" prefix pattern as every past campaign — check `list_posts`-equivalent, i.e. an existing sent campaign's subject line, if unsure of the exact separator).
- `description`/`og:description` meta content is a good source for preview text — write one short sentence (under ~140 chars) that teases the piece; doesn't need to be a verbatim copy of the meta description.

## 2. Copy the HTML to the clipboard

```
pbcopy < issues/<date>/index.html
```

Real OS clipboard, not a variable — the paste step later depends on this being the last thing copied.

## 3. Duplicate the most recent campaign in EmailOctopus

Load `claude-in-chrome` tools (tabs_context_mcp, navigate, computer, read_page, tabs_create_mcp, find, javascript_tool at minimum). Get tab context, open a new tab, navigate to `https://dashboard.emailoctopus.com/campaigns`. The owner's session is already logged in — no auth step needed.

The top row is the most recently sent issue. Use `find` for its three-dot menu button, click it, click **Duplicate** (NOT the "Create" button — duplicating carries over the sender name/email and the "Code your own" design/template; starting fresh leaves those blank and re-picking the template means fumbling the hashed-class SPA thumbnail icons again).

This lands on the Setup step of a new campaign titled "Issue N-1 (copy)".

## 4. Fill in Setup

- Click the title text at the top (pencil icon next to it), `cmd+a`, type `Issue <N>`.
- Subject field: triple-click to select all, type the derived subject from step 1.
- Preview text field: triple-click to select all, type the derived preview text.
- Leave "Sending to: All subscribers" and the sender name/email as inherited from the duplicate.
- Click **Save & next** (top right).

## 5. Paste the content

This lands on Content (the Design step is skipped since it was inherited). Click into the code editor, `cmd+a`, `cmd+v` — **a real OS paste, never typed**. Typing HTML char-by-char triggers the CodeMirror editor's auto-close and duplicates closing tags; synthetic clipboard events are silently ignored by CodeMirror 6. `cmd+v` after a real `pbcopy` is the only reliable path.

EmailOctopus may show a banner: *"It looks like you removed your preview text from the HTML. We've re-added it, but please check your email looks OK before proceeding."* — expected and harmless (it auto-injects a hidden preview-text span the fresh paste didn't carry); confirmed via `Preview & test` that it doesn't visibly break anything.

**Verify the paste**, don't just trust it landed:
```js
const ta = document.querySelector('.body-html') || document.querySelector('textarea');
const val = ta.value;
({length: val.length, start: val.slice(0,80), end: val.slice(-80)})
```
Compare `start`/`end` against the source file's actual first/last ~80 chars (`Read` the file or `head -c`/`tail -c`). They should match exactly. The `length` may be a few characters higher than the source file's Python/byte-oriented character count if the HTML contains astral-plane emoji (anything above U+FFFF) — JS `.length` counts UTF-16 code units (2 per astral emoji) where most other tools count code points (1 each); a small, emoji-count-sized delta is expected and NOT a paste error. Any other mismatch — wrong start/end, or a large unexplained length gap — means the paste failed; retry `cmd+a`/`cmd+v` before proceeding.

Open **Preview & test** (top right) and glance at the rendered issue for anything visibly broken, then close it.

Click **Save & next**.

## 6. Schedule

This lands on Send. Click **Send at a specific time** (not "Send immediately").

**Date**: click the date field to open the calendar popover, then click the target day cell directly. Typing a `YYYY-MM-DD` string into the input does not reliably commit — always use the calendar click. Compute the target as **the next Monday from today** (if today is Monday, that's today) unless the user specified a different date.

**Time**: click the time field to open the segmented hour/minute/AM-PM spinner (hour segment auto-selects). Type the two-digit hour, click the minute segment and type the two-digit minute, then click the AM/PM segment and either press the `a`/`p` key or click that segment's down-caret to toggle it — **typing the literal text "AM"/"PM" does not work**, it's a stepper control, not free text. Target **07:45 AM**, matching every past send (all prior EmailOctopus sends have gone out 7:45-7:46am ET). Confirm the timezone reads "(UTC-04:00) Eastern Time (US and Canada)" — it should already, inherited from the duplicate.

Scroll down and re-read the To/From/Subject/Content summary one more time before scheduling.

Click **Schedule** (top right). A **"Just checking..."** confirmation modal appears stating the recipient count and date/time in plain English — read it and verify it matches the intended send (e.g. "Ready to schedule a send to 205 subscribers for Mon Aug 17 2026 at 7:45 AM?"). Only click the modal's own **Schedule** button once it matches; if it doesn't, cancel and go back rather than clicking through.

## 7. Confirm success

The page should now read **"Your campaign is scheduled"** with a **"Cancel scheduled send"** button. Report the scheduled date/time and recipient count back to the user. Nothing further to do — `schedule-watchdog.yml` will stop nudging once it sees the campaign's status flip to `preparing`.
