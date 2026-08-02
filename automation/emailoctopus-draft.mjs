// Drives EmailOctopus's dashboard UI (no public create/send API exists, confirmed
// 2026-08-02) to build a campaign draft from a merged issue's HTML, then stops --
// it never touches the Send step. A human still reviews and presses Send.
//
// UI selectors below were captured live against the real dashboard on 2026-08-02.
// The Setup step is a plain server-rendered form (stable #ids). The Design/Content
// steps are a hashed-class SPA with no accessible names on the template thumbnail's
// hover-revealed icons, so those two clicks use measured bounding-box offsets --
// documented as the most likely thing to break if EmailOctopus reskins that page.
import { chromium } from 'playwright';
import { readFileSync } from 'node:fs';

const {
  EMAILOCTOPUS_EMAIL,
  EMAILOCTOPUS_PASSWORD,
  ISSUE_PATH,
  SUBJECT,
  FROM_NAME = 'FOWL AI',
  FROM_EMAIL = 'hello@fowl-ai.com',
} = process.env;

for (const [name, val] of Object.entries({ EMAILOCTOPUS_EMAIL, EMAILOCTOPUS_PASSWORD, ISSUE_PATH, SUBJECT })) {
  if (!val) throw new Error(`Missing required env var: ${name}`);
}

const html = readFileSync(ISSUE_PATH, 'utf8');
if (!html.includes('{{UnsubscribeURL}}')) {
  throw new Error(`${ISSUE_PATH} has no {{UnsubscribeURL}} merge tag -- EmailOctopus requires it. Refusing to create the draft.`);
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
await page.waitForURL('**/send**', { timeout: 15000 });
// Stop here. The campaign is already saved as a Draft as of the Setup step --
// never click anything on the Send step itself.

await browser.close();
console.log(`Draft created in EmailOctopus for: ${SUBJECT}`);
