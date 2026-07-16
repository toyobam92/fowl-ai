/*
 * FOWL AI — sitewide engagement events (TICKET-6)
 *
 * Fires four GA4 custom events that were previously only captured on a
 * couple of pages, so bounce rate reflects real disengagement instead of
 * missing instrumentation:
 *   - scroll_75        fires once per page load, past 75% of document height
 *   - outbound_click    fires when a visitor clicks a link to another domain
 *   - subscribe_click   fires specifically for links to the newsletter
 *                        signup platform (fowlai.eo.page) — most pages link
 *                        out to subscribe.
 *   - subscribe_submit  fires when the embedded signup form (homepage hero,
 *                        class "signup-form", posts to a Google Form) is
 *                        submitted — that's the actual conversion the
 *                        "Embedded signup form + social proof" experiment
 *                        is testing, not a link click.
 * Mark subscribe_click AND subscribe_submit as GA4 Key Events in Admin —
 * together they're the real newsletter-conversion metric across every page.
 *
 * Loaded on every page right after the gtag() snippet. No dependencies.
 */
(function () {
  "use strict";

  if (typeof window.gtag !== "function") return;

  var SUBSCRIBE_HOST = "fowlai.eo.page";

  // --- scroll_75 -----------------------------------------------------
  var scrollFired = false;
  function checkScroll() {
    if (scrollFired) return;
    var doc = document.documentElement;
    var scrollableHeight = doc.scrollHeight - doc.clientHeight;
    if (scrollableHeight <= 0) return; // page shorter than viewport
    var pct = (window.scrollY || doc.scrollTop) / scrollableHeight;
    if (pct >= 0.75) {
      scrollFired = true;
      window.gtag("event", "scroll_75", {
        page_location: window.location.href
      });
      window.removeEventListener("scroll", checkScroll);
    }
  }
  window.addEventListener("scroll", checkScroll, { passive: true });
  // Handle pages already scrolled past 75% on load (e.g. hash navigation)
  checkScroll();

  // --- outbound_click / subscribe_click ------------------------------
  document.addEventListener(
    "click",
    function (e) {
      var link = e.target.closest ? e.target.closest("a[href]") : null;
      if (!link) return;

      var href = link.getAttribute("href") || "";
      var url;
      try {
        url = new URL(href, window.location.href);
      } catch (err) {
        return; // malformed href (mailto:, javascript:, etc. handled below)
      }

      if (url.hostname === window.location.hostname) return; // internal link

      var linkText = (link.textContent || "").trim().slice(0, 100);

      if (url.hostname.indexOf(SUBSCRIBE_HOST) !== -1) {
        window.gtag("event", "subscribe_click", {
          link_url: url.href,
          link_location: link.getAttribute("data-link-location") || "unspecified"
        });
      } else {
        window.gtag("event", "outbound_click", {
          link_url: url.href,
          link_text: linkText
        });
      }
    },
    true
  );

  // --- subscribe_submit (embedded hero signup form) -------------------
  document.addEventListener(
    "submit",
    function (e) {
      var form = e.target;
      if (!form || !form.classList || !form.classList.contains("signup-form")) return;
      window.gtag("event", "subscribe_submit", {
        form_id: form.id || "unspecified",
        page_location: window.location.href
      });
    },
    true
  );
})();
