# GitHub Actions migration: nightly build and test plan

Owner requested November 20, 2026. Build and test incrementally; keep GitHub for source/review, use T9 releases and server runtime jobs first, retain Actions as a manual fallback only after a successful drill.

Canonical dependency/state register: https://github.com/toyobam92/brandbrain-cloud/blob/main/docs/plans/70-actions-migration-queue.json

## Execution contract

- One bounded task per slot, using an isolated checkout and existing project instructions. Preserve the existing backlog. Do not start a second scheduler to work around an unverified first one.
- Read the register and dependency receipts first. Only tasks whose prerequisites are merged with passing tests are eligible. Live-readiness dependencies additionally require deployment/observation receipts. A PR, BUILT message or successful process exit is not live evidence.
- Claim once by branch/task ID. If a prior claim exists, reconcile it rather than silently skipping it forever or deleting it. A blocked retry gets an explicit new attempt linked to the original receipt.
- Run relevant unit/integration checks, then the project's required build/typecheck/security gates. Use disposable data and provider stubs. Save exact commands, exit codes, commit, resource use and untested cases.
- Push a reviewable PR. No unattended production merge/deploy, production migration, live DNS switch, credential/access expansion, paid-service reactivation or purchases under this build task. Prepare and test those steps; the reviewed release process performs cutovers only after gates pass. Never send or schedule newsletter/social content without approval of that exact content and destination.
- No new server/subscription/API budget. Do not copy desktop login tokens to a server. Stop resource-intensive phases below 1 GiB free; below 5 GiB avoid heavy builds. Never delete or steal another worker's lock.
- Preserve tests, secret scanning, authorization, customer isolation, pause flags, models and native binaries. No fallback bypassing a failed test or migration gate.
- Reuse the consolidated daily summary and persistent-outage policy. Do not introduce per-task failure emails. A queued automation is not an approved send.

## Advancement and release gates

After each morning review, reconcile PR state into the canonical register and source queue. Populate test_receipt and merged_sha before marking done. Promote only dependents whose receipts exist; copy the corresponding eligible items into the CitySignal/FOWL Night queue. Held items must NOT appear as unchecked tasks in a consumer that ignores dependencies. The first scheduler task q70a must wire this reconciliation into the existing review flow, or explicitly report the remaining manual promotion requirement.

For Brand Brain the plan number is 70 and the task ID identifies the subsection below. Review status is not completion. For cross-repository dependencies, use the remote main register; do not trust stale local copies.

Initial execution status: Brand Brain and CitySignal consumers have recent run evidence. FOWL builder activation is UNVERIFIED: q70a must confirm or register it using the supplied prompt and save a read-back receipt. Local duplicate Brand Brain slots remain disabled. Do not describe FOWL as scheduled merely because this plan exists.

## Task definitions

### f70a: Newsletter and Nova workflow disposition

Dependencies: none. Initial state: queued.

Inventory all workflow files and stale registered workflows. Classify keep/move/retire; verify the source folder. Assess HeyGen-dependent steps against cancellation; inspect pending render/publication receipts before retiring anything.

**Done when:** Map every workflow and trigger, provider, approval, state file and secret label. No paid render, token rotation, publishing, newsletter send or deletion.

### f70b: Durable newsletter job state and idempotency

Dependencies: f70a. Initial state: hold.

Move runtime JSON-state writes out of Git into a durable store accessible to primary and recovery workers. Retain immutable content history in Git; design import/export and rollback without importing secrets.

**Done when:** Duplicate messages, crash before/after provider acceptance, lease expiry, restart and concurrent workers; unknown result requires reconciliation, not blind retry.

### f70c: Telegram approval to server queue

Dependencies: f70b. Initial state: hold.

Adapt the existing webhook to enqueue allowlisted commands instead of dispatching Actions. Pin approval to content revision, destination and time. APPROVE site content remains separate from SCHEDULE newsletter.

**Done when:** Unauthorized chat rejected; duplicate webhook coalesced; changed asset invalidates approval; webhook retries cannot cause duplicate send. Test provider is a stub.

### f70d: Pending-only render checks and lightweight timers

Dependencies: f70b. Initial state: hold.

Replace every-15-minute no-op render polling with checks only for active renders and a bounded deadline; move signup sync, token health and watchdog to server timers. Retire obsolete HeyGen routines only after outstanding work is reconciled.

**Done when:** Idle queue causes zero provider calls; pending render backs off; retry stops at cap; expired token produces one incident; repeated ticks never publish twice.

### f70e: Newsletter scheduling worker rehearsal

Dependencies: f70c, f70d. Initial state: hold.

Reuse existing EmailOctopus automation initially; verify current supported integrations before proposing replacement. Keep scheduling approval, recipient/list, exact subject, revision, Eastern time and campaign receipt.

**Done when:** Mock then a non-sending draft rehearsal; reject duplicate campaign and changed approval, handle DST and uncertain submission. Real campaign scheduling/sending requires its own exact content approval.

### f70f: Static site release and hosting candidate

Dependencies: none. Initial state: queued.

Package the FOWL static site and compare an existing-host candidate with GitHub Pages. Check newsletter archives, signup forms, redirects, HTTPS and DNS rollback; choose capacity without new subscriptions.

**Done when:** Local/candidate link and asset checks, form test doubles, headers, domain/redirect manifest and rollback plan. Do not change live DNS or send signup campaigns.

### f70g: Manual fallback and quiet reporting

Dependencies: f70d, f70e, f70f, q70f, q70g. Initial state: hold.

Create manual-only recovery wrappers calling the same scripts and durable state. Integrate the daily summary; separate informational notices from approval requests. Keep GitHub Pages fallback until hosting cutover is verified.

**Done when:** Primary/fallback exclusivity, job receipt lookup, no repeated email/Telegram alerts, recovery from worker outage with explicit approval still enforced.

### f70h: FOWL cutover readiness and seven-day observation

Dependencies: f70g. Initial state: hold.

Prepare a phased job/hosting ownership switch, DNS rollback and evidence report. Track one approved newsletter cycle separately from technical tests. Re-enable neither retired paid integrations nor duplicate schedulers.

**Done when:** Verify approved cycle receipt when one is authorized, static site comparison, seven actual days of receipts and recovery drill. Report unperformed live tests explicitly.

