  (function(){
    var term = document.getElementById('vcsTerminal');
    if(!term || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    var lines = Array.prototype.slice.call(term.querySelectorAll('.term-line'));
    var cursor = document.getElementById('vcsCursor');
    var playing = false;

    function play(){
      if(playing) return;
      playing = true;
      // Snapshot typed spans' full text, then hide everything
      lines.forEach(function(line){
        line.style.visibility = 'hidden';
        line.querySelectorAll('[data-type]').forEach(function(span){
          if(span.dataset.full === undefined) span.dataset.full = span.textContent;
        });
      });
      cursor.style.display = 'none';
      var i = 0;

      function nextLine(){
        if(i >= lines.length){
          cursor.style.display = 'inline-block';
          playing = false;
          setTimeout(play, 7000); // pause, then replay like a looping GIF
          return;
        }
        var line = lines[i++];
        var typed = line.querySelector('[data-type]');
        line.style.visibility = 'visible';
        if(typed){
          var full = typed.dataset.full;
          typed.textContent = '';
          var c = 0;
          (function typeChar(){
            if(c < full.length){
              typed.textContent += full.charAt(c++);
              setTimeout(typeChar, 90);
            } else {
              setTimeout(nextLine, 350);
            }
          })();
        } else {
          var isMenu = line.classList.contains('term-menu');
          setTimeout(nextLine, isMenu ? 110 : 300);
        }
      }
      nextLine();
    }

    var obs = new IntersectionObserver(function(entries){
      entries.forEach(function(e){
        if(e.isIntersecting){ play(); obs.unobserve(term); }
      });
    }, {threshold:0.35});
    obs.observe(term);
  })();

