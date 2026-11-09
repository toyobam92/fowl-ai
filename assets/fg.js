// Stamps when this page loaded (fg_t) and when a form was sent (fg_s) on every form that posts to
// tools.fowl-ai.com. A person takes a few seconds to fill a form; a script sends it instantly, so the
// server holds posts sent too fast. Both times come from the visitor's own clock, so skew doesn't matter.
(function () {
  var loaded = String(Date.now());
  document.querySelectorAll('form[action^="https://tools.fowl-ai.com/"]').forEach(function (form) {
    function put(name, value) {
      var input = form.querySelector('input[name="' + name + '"]');
      if (!input) { input = document.createElement('input'); input.type = 'hidden'; input.name = name; form.appendChild(input); }
      input.value = value;
    }
    put('fg_t', loaded);
    form.addEventListener('submit', function () { put('fg_s', String(Date.now())); }, true);
  });
})();
