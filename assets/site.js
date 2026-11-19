(function () {
  'use strict';
  function track(name, data) {
    if (typeof window.gtag === 'function') window.gtag('event', name, data);
  }
  var header = document.querySelector('.site-header');
  if (header) {
    var toggle = header.querySelector('.site-menu-toggle');
    var more = header.querySelector('.site-more');
    function closeMenu(returnFocus) {
      header.dataset.menuOpen = 'false';
      toggle.setAttribute('aria-expanded', 'false');
      toggle.setAttribute('aria-label', 'Open navigation');
      if (more) more.open = false;
      if (returnFocus) toggle.focus();
    }
    header.dataset.menuReady = 'true';
    toggle.addEventListener('click', function () {
      var open = toggle.getAttribute('aria-expanded') !== 'true';
      header.dataset.menuOpen = String(open);
      toggle.setAttribute('aria-expanded', String(open));
      toggle.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
    });
    header.querySelectorAll('a').forEach(function (link) {
      if (new URL(link.href).pathname === window.location.pathname && !link.hash) link.setAttribute('aria-current', 'page');
      link.addEventListener('click', function () { closeMenu(false); });
    });
    document.addEventListener('keydown', function (event) {
      if (event.key !== 'Escape') return;
      if (more && more.open) { more.open = false; more.querySelector('summary').focus(); }
      else if (header.dataset.menuOpen === 'true') closeMenu(true);
    });
    document.addEventListener('click', function (event) {
      if (!header.contains(event.target)) closeMenu(false);
    });
    header.addEventListener('focusout', function () {
      window.setTimeout(function () {
        if (!header.contains(document.activeElement)) closeMenu(false);
      }, 0);
    });
    window.matchMedia('(min-width: 801px)').addEventListener('change', function () { closeMenu(false); });
  }

  document.querySelectorAll('a[data-conversion]').forEach(function (link) {
    link.addEventListener('click', function () {
      track(link.dataset.conversion === 'newsletter' ? 'subscribe_click' : link.dataset.conversion === 'vibe-code-apply' ? 'vibe_code_apply_click' : 'vibe_code_click', {
        link_location: link.dataset.linkLocation || 'unspecified',
        link_url: link.href
      });
      if (link.hash === '#signup' && new URL(link.href).pathname === window.location.pathname) {
        var field = document.querySelector('#signup input');
        if (field) window.setTimeout(function () { field.focus({ preventScroll: true }); }, 0);
      }
    });
  });

  // The newsletter boxes post to tools.fowl-ai.com/newsletter (Nov 18 2026). The server checks the sign-up
  // came from this page and wasn't sent instantly (fg.js stamps the times), then writes it to the owner's
  // Google Form. Until then the boxes posted to a public Google Form, and a script fed it about 1,700 rows
  // of other people's addresses in nine days. The server sends people on to /subscribed/.
  var badSignup = new URLSearchParams(window.location.search).get('signup') === 'error';
  document.querySelectorAll('.newsletter-form').forEach(function (form) {
    var button = form.querySelector('button');
    var input = form.querySelector('input[type=email]');
    var response = document.getElementById(form.dataset.response);
    var started = false;
    input.addEventListener('input', function () {
      if (started) return;
      started = true;
      track('subscribe_start', { form_id: form.id });
    });
    form.addEventListener('submit', function () {
      button.disabled = true;
      button.textContent = 'Sending…';
    });
    if (badSignup && form.id === 'fowlSignupForm' && response) {
      response.textContent = 'That email address did not look right. Please check it and try again.';
      response.hidden = false;
    }
  });
})();
