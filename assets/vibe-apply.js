// Progressive enhancement: the complete native Google Forms POST works without JS.
const form = document.querySelector('form');
const sections = [...form.querySelectorAll('.form-section')];
const button = form.querySelector('button[type="submit"]');
const previous = form.querySelector('.previous-button');
const status = document.querySelector('#submit-status');
const privacy = form.querySelector('.privacy-note');
const labels = ['About you', 'Your starting point', 'Your Saturday'];
let step = 0;
// Show the actual Google Forms response; an iframe load cannot prove acceptance.
form.target = '_self';
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
 button.innerHTML = step === 2 ? 'Send application <span aria-hidden="true">↗</span>' : 'Continue <span aria-hidden="true">→</span>';
 status.textContent = step === 2 ? 'Google Forms will show whether your application was received.' : 'Free to attend. No coding background required.';
 if (focus) { const heading = sections[step].querySelector('h3'); heading.tabIndex = -1; heading.focus(); }
}
function valid(section) {
 for (const input of section.querySelectorAll('input,textarea')) {
  if (!input.checkValidity()) { input.reportValidity(); return false; }
 }
 return true;
}
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
 button.textContent = 'Sending your application…';
 status.textContent = 'Opening your confirmation. Please keep this page open.';
});
window.addEventListener('pageshow', () => { previous.disabled = false; render(); });
render();
