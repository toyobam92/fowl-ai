# FOWL AI dashboards — where to find them

Two live dashboards get refreshed every cycle by the `weekly-analytics-review` skill. Neither has a stable public URL, so pin this file instead of a link.

## Site snapshot
GA4 traffic snapshot — pages, sources, geography, bounce-rate callouts.

- **Open it:** Cowork sidebar → Artifacts panel → **"Fowlai Site Snapshot"**
- **Local file:** `~/Claude/Artifacts/fowlai-site-snapshot/index.html` (double-click in Finder, or drag into a browser tab)
- **Source in repo:** `analytics/dashboards/site-snapshot.html`

## Phase 1 roadmap
"AI destination" roadmap tracker — status badges sourced from `analytics/roadmap.md`.

- **Open it:** Cowork sidebar → Artifacts panel → **"Fowlai Phase1 Roadmap"**
- **Local file:** `~/Claude/Artifacts/fowlai-phase1-roadmap/index.html`
- **Source in repo:** `analytics/dashboards/phase1-roadmap.html`

## Notes
- Both dashboards were originally published from a different environment (old `claude.ai/code/artifact/...` links in `dashboards.json`) that this Cowork session can't reach or update. They were re-published here as Cowork artifacts instead — that's the current source of truth going forward.
- `dashboards.json` in this folder is the machine-readable version of the above (used by the weekly review skill to know what to republish and where).
