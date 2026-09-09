# FOWL AI newsletter identity

`newsletter.html` is the canonical template for new issues from September 2026 onward. Use it instead of copying the appearance of a past issue. `newsletter.txt` is the matching plain-text skeleton. The outer project's `issues/template/index.html` mirrors the HTML for the manual workflow.

The website and email now share a light canvas, forest-green accents, native sans-serif typography, and a restrained FOWL AI wordmark. The email uses a 640 px reading column, 16 px body copy, inline styles, and presentation tables. Content and calls to action remain legible without images or external fonts. Mobile styles are progressive enhancements; the essential layout and colors are inline.

## Authoring

1. Replace every `[UPPERCASE_PLACEHOLDER]` with this issue's researched copy or an absolute URL. Keep the class names used for editorial checks: `mast-title`, `mast-sub`, `tldr-text`, `nova-quote`, `nova-call`, and `intro-text`.
2. Keep EmailOctopus's case-sensitive merge tags intact: `{{UnsubscribeURL}}`, `{{SenderInfoLine}}`, `{{RewardsURL}}`, `{{WebVersionURL}}`, and `{{ShareURL}}`. These are provider tags, not issue placeholders. Unsubscribe must remain a text hyperlink. The sender address comes from the configured account.
3. Set `[READ_TIME]` from the finished copy, rather than always claiming five minutes. Set a concise `[PREHEADER]`, issue date, and edition label.
4. Save the email source as `issues/<date>/email.html`. Generate `index.html` from the same filled content for the website; add canonical, description, and Article metadata only to the web copy. Never copy analytics scripts, JavaScript buttons, or unresolved footer tags from a web page back into email.
5. Update the text version with the same content and links. Check HTML byte size; keep the final email compact (target below 95 KB).

## Editorial structure

Masthead and provenance → main takeaway → Nova's perspective and short intro → five sourced developments → signals → community context → prediction → three actions → career radar → platform opportunities and jobs → closing and reply → Vibe Code Saturdays → share and footer.

The established front-of-issue word budgets and source checks still apply. Each opening block has a separate purpose. Source links belong with the relevant claims. A community report must be identified as reported experience. Keep forecasts explicit and give them a review date.

Brand Brain, Launch Lab, and Guides & Resources promotions are paused. Do not carry them forward from old issues. Vibe Code Saturdays stays as one compact recurring block after the reply prompt. Its first date and venue are still unannounced; update only when confirmed.

## Before any actual send

Check the filled issue in EmailOctopus Preview & test and in actual inboxes, especially mobile Gmail, Apple Mail, and Outlook. Browser rendering and static validation cannot establish email-client compatibility. Verify the configured sender address, merge tags, destinations, and preheader. Scheduling or sending requires the user's existing explicit authorization; preparing a template does not send it.

The implementation follows EmailOctopus's guidance to keep custom-email CSS inline and simple: [custom HTML guidance](https://help.emailoctopus.com/article/253-what-can-i-code-into-emailoctopus). Provider tag names and behavior are documented in the [customisation cheat sheet](https://help.emailoctopus.com/article/74-customisation-cheat-sheet) and [unsubscribe-link instructions](https://help.emailoctopus.com/article/71-how-to-insert-an-unsubscribe-link).
