# FOWL AI — Phase 1 roadmap status

Source of truth for `analytics/dashboards/phase1-roadmap.html`. Status values: `live` · `in_progress` · `planned` · `later` (deliberately deferred to Phase 2/3).

When `weekly-analytics-review` runs, it checks `git log` since the last review against the **match hints** for every `planned`/`in_progress` item below (judgment call, not exact string match — a commit doesn't have to use these exact words). On a match: flip status, fill in `shipped`, regenerate the badges in `phase1-roadmap.html`, and add an `EXPERIMENTS.md` entry per the usual convention (a new page is also a change worth measuring).

| Item | Category | Status | Shipped | Match hints |
|---|---|---|---|---|
| Weekly AI Issues | Core Content | live | pre-dates tracking | — |
| AI Jobs Board | Discovery | live | pre-dates tracking | — |
| AI Platforms Directory | Discovery | live | pre-dates tracking | — |
| Launch Lab (separate business) | — | live | pre-dates tracking | — |
| AI Glossary | Core Content | in_progress | started, pre-dates tracking | glossary, LLM/MCP/agents/skills definitions page |
| AI Newsletter Archive | Core Content | planned | — | archive page, best of 2026, most popular issues |
| AI Books & Resources | Core Content | planned | — | books, resources, reading list, courses, podcasts |
| AI Company Tracker | Discovery | planned | — | company tracker, OpenAI/Anthropic/Google/Microsoft/Meta/Apple/Amazon page |
| AI Intelligence Dashboard | Discovery | planned | — | intelligence dashboard, weekly AI stats page |
| AI Career Hub | Career | planned | — | career hub, resume tips, interview prep, career roadmap |
| AI Salary Hub | Career | planned | — | salary hub, salary guide, prompt engineer/ML engineer/AI PM salary |
| AI Interview Hub | Career | planned | — | interview hub, interview questions, take-home |
| AI Learning Paths | Career | planned | — | learning path, beginner to enterprise AI path |
| Weekly Trending | Community | planned | — | trending page, most read, most shared |
| AI Events | Community | planned | — | events page, conferences, webinars, hackathons |
| "AI This Week in 5 Minutes" (signature) | Signature | planned | — | this week in 5 minutes, weekly digest page |

## Deliberately later (Phase 2/3)

User accounts, AI chatbot, premium membership, paid reports, resume builder, AI resume reviewer, subscription products. Don't flip these even if a related commit appears — confirm with the user first, since these were explicitly called premature.
