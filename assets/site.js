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

  document.querySelectorAll('.newsletter-form').forEach(function (form) {
    var button = form.querySelector('button');
    var input = form.querySelector('input[type=email]');
    var response = document.getElementById(form.dataset.response);
    var frame = document.querySelector('iframe[name="' + form.target + '"]');
    var label = button.innerHTML;
    var pending = false;
    var timeout;
    var started = false;
    input.addEventListener('input', function () {
      if (started) return;
      started = true;
      track('subscribe_start', { form_id: form.id });
    });
    function showMessage(text) {
      response.replaceChildren(document.createTextNode(text + ' '));
      var link = document.createElement('a');
      link.href = 'https://fowlai.eo.page/vmk69';
      link.textContent = 'Open the signup page';
      response.appendChild(link);
      response.hidden = false;
    }
    function reset() {
      pending = false;
      window.clearTimeout(timeout);
      button.disabled = false;
      button.innerHTML = label;
      form.removeAttribute('aria-busy');
    }
    form.addEventListener('submit', function (event) {
      if (pending) { event.preventDefault(); return; }
      pending = true;
      response.hidden = true;
      button.disabled = true;
      button.textContent = 'Sending…';
      form.setAttribute('aria-busy', 'true');
      timeout = window.setTimeout(function () {
        reset();
        showMessage('We could not confirm your request. You can finish subscribing on our signup page.');
      }, 18000);
    });
    // The existing Google Forms integration has no cross-origin confirmation API.
    // A frame load is a returned request, never proof of a completed subscription.
    frame.addEventListener('load', function () {
      if (!pending) return;
      reset();
      showMessage('Thanks for your interest. Look out for FOWL AI in your inbox. If nothing arrives, finish subscribing here.');
      track('subscribe_request_returned', { form_id: form.id, method: 'embedded_form' });
    });
    frame.addEventListener('error', function () {
      if (!pending) return;
      reset();
      showMessage('Something interrupted your request. Please use our signup page to finish subscribing.');
    });
  });
})();
