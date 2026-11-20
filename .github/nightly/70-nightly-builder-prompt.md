# FOWL nightly builder activation payload

Status: activation unverified. Target: toyobam92/fowl-ai. Proposed once daily at 00:10 America/New_York, one task, 40-minute maximum. Verify the account timezone and avoid other FOWL builds before enabling. No new paid API or subscription.

Read the repository's Night queue issue and .github/nightly/70-actions-migration.md. Pick the first unchecked eligible migration item; verify prerequisites against the canonical Brand Brain register and its PR/test receipts. Claim nightly/<task-id> once, reconcile existing claims, work in an isolated checkout, and implement exactly one task. Read applicable repository instructions. Test with mocks/disposable data; no live customer sends, paid renders, DNS cutover or production migrations. Never merge or deploy from the builder. Push a PR with exact checks, source SHA, missing live verification and rollback notes. Mark the issue item built/review with the PR link, not deployed. Record failure once for the consolidated daily summary. If no eligible work remains, exit silently. No separate email.

Activation receipt must include consumer/trigger ID, enabled state, target repo, timezone, next run and a dry-run selection result. Do not create another trigger if one already owns this queue.
