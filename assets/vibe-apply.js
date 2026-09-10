// Progressive enhancement: the complete native Google Forms POST works without JS.
const form = document.querySelector('form');
const sections = [...form.querySelectorAll('.form-section')];
const button = form.querySelector('button[type="submit"]');
const previous = form.querySelector('.previous-button');
const status = document.querySelector('#submit-status');
const privacy = form.querySelector('.privacy-note');
const labels = ['About you', 'Your starting point', 'Your Saturday'];
let step = 0, recovery;
const submissionFrame = document.createElement('iframe');
submissionFrame.name = 'submission-frame';
submissionFrame.title = 'Form submission';
submissionFrame.hidden = true;
document.body.appendChild(submissionFrame);
form.target = 'submission-frame';
let submitted = false;
form.noValidate = true;
document.body.classList.add('enhanced');
document.querySelector('.form-progress').hidden = false;
function render(focus = false) {
 sections.forEach((section, i) => { section.hidden = i !== step; });
 previous.hidden = step === 0;
 privacy.hidden = step !== 2;
 document.querySelector('#step-label').textContent = `Step ${step + 1} of 3 · ${labels[step]}`;
 document.querySelector('#step-percent').textContent = `${Math.round((step + 1) / 3 * 100)}%`;
 document.querySelector('#progress-fill').style.width = `${(step + 1) / 3 * 100}%`;
 button.disabled = false;
 button.innerHTML = step === 2 ? 'Apply for the first session <span aria-hidden="true">↗</span>' : 'Continue <span aria-hidden="true">→</span>';
 status.textContent = step === 2 ? 'Free to attend. No coding background required.' : 'Free to attend. No coding background required.';
 if (focus) { const heading = sections[step].querySelector('h3'); heading.tabIndex = -1; heading.focus(); }
}
function valid(section) {
 for (const input of section.querySelectorAll('input,textarea')) {
  if (!input.checkValidity()) { input.reportValidity(); return false; }
 }
 return true;
}
function showSuccess() {
 if (!submitted) return;
 submitted = false;
 clearTimeout(recovery);
 form.hidden = true;
 document.querySelector('.form-progress').hidden = true;
 const panel = document.createElement('div');
 panel.className = 'success-panel';
 panel.innerHTML = '<div class="success-mark" aria-hidden="true">✓</div><p class="eyebrow">YOU’RE ON THE LIST</p><h3>We’ll see you in the room.</h3><p>Your application is in. We’ll email you when the first date, venue, and setup details are ready.</p><a href="/vibe-code-saturdays/">Back to Vibe Code Saturdays <span aria-hidden="true">↗</span></a>';
 form.parentNode.insertBefore(panel, form);
}
submissionFrame.addEventListener('load', showSuccess);
previous.addEventListener('click', () => { step--; render(true); });
form.addEventListener('submit', event => {
 if (!valid(sections[step])) { event.preventDefault(); return; }
 if (step < 2) { event.preventDefault(); step++; render(true); return; }
 for (let i = 0; i < sections.length; i++) {
  const invalid = [...sections[i].querySelectorAll('input,textarea')].find(input => !input.checkValidity());
  if (invalid) { event.preventDefault(); step = i; render(); invalid.reportValidity(); return; }
 }
 button.disabled = true;
 previous.disabled = true;
 submitted = true;
 button.textContent = 'Sending your application…';
 status.textContent = 'Opening your confirmation. Please keep this page open.';
 recovery = setTimeout(() => {
  showSuccess();
 }, 4000);
});
window.addEventListener('pageshow', () => { clearTimeout(recovery); previous.disabled = false; render(); });
render();
