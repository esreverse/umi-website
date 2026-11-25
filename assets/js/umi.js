// UMI Stuttgart – kleines Skript: Menü auf dem Handy, Platzhalter-Knöpfe
(function () {
  var t = document.querySelector('.menu-toggle');
  var n = document.getElementById('hauptmenue');
  if (t && n) {
    t.addEventListener('click', function () {
      var open = n.classList.toggle('open');
      t.setAttribute('aria-expanded', open ? 'true' : 'false');
      t.closest('.site-header').classList.toggle('menu-open', open);
    });
  }
  // Aufgeklapptes Menü: Höhe bis zum unteren Bildschirmrand, damit die Buttons sichtbar haften
  if (n) {
    var fit = function () {
      var kopf = n.closest('.site-header').getBoundingClientRect().bottom;
      n.style.setProperty('--nav-max', (window.innerHeight - kopf) + 'px');
    };
    fit();
    window.addEventListener('scroll', fit, { passive: true });
    window.addEventListener('resize', fit);
  }
  // Kopfzeile der Startseite: über dem Hero durchsichtig, beim Scrollen hell
  var h = document.querySelector('.site-header');
  if (h) {
    var onScroll = function () { h.classList.toggle('scrolled', window.scrollY > 60); };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }
  // Ausklappmenüs: Klick öffnet/schließt (Handy, Touch, Tastatur)
  document.querySelectorAll('.dd-btn').forEach(function (b) {
    b.addEventListener('click', function () {
      var dd = b.parentNode, open = !dd.classList.contains('open');
      document.querySelectorAll('.dd.open').forEach(function (o) { o.classList.remove('open'); o.firstChild.setAttribute('aria-expanded', 'false'); });
      if (open) { dd.classList.add('open'); b.setAttribute('aria-expanded', 'true'); }
    });
  });
  document.addEventListener('click', function (e) {
    if (!e.target.closest('.dd')) document.querySelectorAll('.dd.open').forEach(function (o) { o.classList.remove('open'); o.firstChild.setAttribute('aria-expanded', 'false'); });
  });
  // Knöpfe, deren Ziel noch fehlt (z. B. Gutschein-Shop), lösen nichts aus
  document.querySelectorAll('a[aria-disabled="true"]').forEach(function (a) {
    a.addEventListener('click', function (e) { e.preventDefault(); });
  });
})();
