// Drives EmailOctopus's dashboard UI (no public create/send API exists, confirmed
// 2026-08-02) to build a campaign draft AND schedule it. Only ever invoked by the
// explicit "SCHEDULE <PR#>" Telegram command (see .github/workflows/telegram-approve.yml
// and send-issue.yml) -- never runs unattended off a mere site-merge approval.
//
// Verified live end-to-end on 2026-08-02 against the real account (create -> fill ->
// schedule -> confirm -> cancel -> delete), so the flow below is proven, not guessed --
// except that this script drives it unattended instead of a person clicking through.
//
// UI selectors: the Setup and Send/Review steps are plain server-rendered forms with
// stable #ids -- .fill() on those is reliable. The Design/Content steps are a
// hashed-class SPA with no accessible names on the template thumbnail's hover-revealed
// icons, so those two clicks use measured bounding-box offsets -- documented as the
// most likely thing to break if EmailOctopus reskins that specific page.
import { chromium } from 'playwright';
import { readFileSync } from 'node:fs';

const {
  EMAILOCTOPUS_EMAIL,
  EMAILOCTOPUS_PASSWORD,
  ISSUE_PATH,
  SUBJECT,
  SCHEDULE_DATE, // 'YYYY-MM-DD'
  SCHEDULE_TIME, // e.g. '7:45 AM' -- interpreted in the account's own timezone (Eastern)
  FROM_NAME = 'FOWL AI',
  FROM_EMAIL = 'hello@fowl-ai.com',
} = process.env;

for (const [name, val] of Object.entries({
  EMAILOCTOPUS_EMAIL, EMAILOCTOPUS_PASSWORD, ISSUE_PATH, SUBJECT, SCHEDULE_DATE, SCHEDULE_TIME,
})) {
  if (!val) throw new Error(`Missing required env var: ${name}`);
}

const html = readFileSync(ISSUE_PATH, 'utf8');
for (const tag of ['{{UnsubscribeURL}}', '{{SenderInfoLine}}']) {
  if (!html.includes(tag)) {
    throw new Error(`${ISSUE_PATH} is missing the ${tag} merge tag -- EmailOctopus requires it. Refusing to create the draft.`);
  }
}

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

async function ensureLoggedIn() {
  await page.goto('https://dashboard.emailoctopus.com/campaigns', { waitUntil: 'domcontentloaded' });
  const emailField = page.locator('input[type="email"]').first();
  const isLoginPage = await emailField.isVisible({ timeout: 8000 }).catch(() => false);
  if (!isLoginPage) return;

  await emailField.fill(EMAILOCTOPUS_EMAIL);
  await page.locator('input[type="password"]').first().fill(EMAILOCTOPUS_PASSWORD);
  await Promise.all([
    page.waitForURL('**/campaigns**', { timeout: 20000 }),
    page.getByRole('button', { name: /log.?in|sign.?in/i }).click(),
  ]);
}

// Click at a fraction of an element's own bounding box -- used for the two
// hover-revealed icons on the template thumbnail, which have no accessible name.
async function clickWithinBox(locator, fx, fy) {
  const box = await locator.boundingBox();
  if (!box) throw new Error('Target element has no bounding box (not visible?).');
  await page.mouse.click(box.x + box.width * fx, box.y + box.height * fy);
}

await ensureLoggedIn();

await page.getByRole('button', { name: 'Create', exact: true }).click();
await page.waitForURL('**/campaigns/setup**', { timeout: 15000 });

await page.locator('#campaign_setup_fromName').fill(FROM_NAME);
await page.locator('#campaign_setup_fromEmailAddress').fill(FROM_EMAIL);
await page.locator('#campaign_setup_subject').fill(SUBJECT);
await page.locator('#campaign_setup_previewText').fill(SUBJECT);
await page.getByRole('button', { name: 'Save & next' }).click();
await page.waitForURL('**/template**', { timeout: 15000 });

await page.getByRole('button', { name: 'Code your own', exact: true }).click();
await page.waitForTimeout(500);

// The template list is now filtered to exactly this one card. Its live preview
// renders inside an iframe -- use that iframe's box as "the card" rather than
// text-matching, since the caption text is ambiguous with the sidebar button.
const thumbnail = page.locator('iframe').first();
await thumbnail.waitFor({ state: 'visible', timeout: 10000 });

let onDesignStep = false;
for (let attempt = 0; attempt < 3 && !onDesignStep; attempt++) {
  await clickWithinBox(thumbnail, 0.5, 0.35); // select/focus the card, reveals hover icons
  await page.waitForTimeout(600);
  await clickWithinBox(thumbnail, 0.82, 0.82); // the code (</>) icon, bottom-right of the thumbnail
  onDesignStep = await page
    .waitForURL('**/design**', { timeout: 6000 })
    .then(() => true)
    .catch(() => false);
}
if (!onDesignStep) {
  throw new Error('Could not open the "Code your own" editor after 3 attempts -- EmailOctopus\'s template UI may have changed.');
}

const editor = page.locator('.cm-content');
await editor.click();
await page.keyboard.press('ControlOrMeta+A');
await page.keyboard.insertText(html); // insertText, not type() -- type() fires per-key autoclose and duplicates closing tags

const mirrored = await page.locator('.body-html').inputValue();
if (mirrored.trim() !== html.trim()) {
  throw new Error('Editor content does not match the source HTML after paste -- refusing to save a possibly-corrupted draft.');
}

await page.getByRole('button', { name: 'Save & next' }).click();
await page.waitForURL('**/review**', { timeout: 15000 });

// --- Schedule step. Everything from here on stages a real send to the full ---
// --- list -- only reached because this script was explicitly invoked by a  ---
// --- human's "SCHEDULE <PR#>" reply, not automatically after a site merge. ---

await page.locator('#campaign_review_delaySend_1').check();
// Plain <input> fields underneath the calendar/spinner popovers -- .fill() sets
// the real value directly, verified live to be respected by the form on submit.
await page.locator('#campaign_review_delayedSendAt_date').fill(SCHEDULE_DATE);
await page.keyboard.press('Escape');
await page.locator('#campaign_review_delayedSendAt_time').fill(SCHEDULE_TIME);
await page.keyboard.press('Escape');

await page.getByRole('button', { name: 'Schedule', exact: true }).click();

// EmailOctopus's own "Just checking..." confirmation states the recipient count
// and date/time in plain English -- verify it before confirming, as a second,
// independent check that the fields above actually took.
const confirmHeading = page.getByText('Just checking', { exact: false });
await confirmHeading.waitFor({ timeout: 8000 });
const confirmText = (await page.getByText('Ready to schedule a send', { exact: false }).textContent()) || '';
const [, expectedYear] = SCHEDULE_DATE.match(/^(\d{4})-\d{2}-\d{2}$/) || [];
const expectedHourMinute = SCHEDULE_TIME.replace(/^0/, ''); // EmailOctopus displays "7:45 AM", not "07:45 AM"
if (!confirmText.includes(expectedYear) || !confirmText.includes(expectedHourMinute)) {
  throw new Error(`Confirmation dialog text ("${confirmText}") doesn't match the intended schedule (${SCHEDULE_DATE} ${SCHEDULE_TIME}) -- aborting without confirming.`);
}

await page.getByRole('button', { name: 'Schedule', exact: true }).last().click();
await page.getByText('Your campaign is scheduled', { exact: false }).waitFor({ timeout: 10000 });

await browser.close();
console.log(`Scheduled in EmailOctopus for ${SCHEDULE_DATE} ${SCHEDULE_TIME}: ${SUBJECT}`);
