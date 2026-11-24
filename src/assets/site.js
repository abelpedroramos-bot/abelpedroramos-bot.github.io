// Field Ready QHSE — small site behaviours (no tracking, no external calls)
(function () {
  document.documentElement.classList.add('js');
  // Mobile menu
  var btn = document.querySelector('.menu-btn');
  var nav = document.getElementById('site-nav');
  if (btn && nav) {
    btn.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }
  // Product gallery thumbnails
  var main = document.querySelector('.gallery .main');
  document.querySelectorAll('.thumbs button').forEach(function (b) {
    b.addEventListener('click', function () {
      if (!main) return;
      main.src = b.getAttribute('data-src');
      main.alt = b.getAttribute('data-alt') || main.alt;
      document.querySelectorAll('.thumbs button').forEach(function (o) { o.setAttribute('aria-pressed', 'false'); });
      b.setAttribute('aria-pressed', 'true');
    });
  });
  // Variant selector (Standard / Premium): show the matching price, contents and buy button
  var radios = document.querySelectorAll('input[name="variant"]');
  function showVariant(key) {
    document.querySelectorAll('.vpanel').forEach(function (p) { p.hidden = p.getAttribute('data-variant') !== key; });
  }
  radios.forEach(function (r) {
    r.addEventListener('change', function () { showVariant(r.value); });
  });
  var picked = document.querySelector('input[name="variant"]:checked');
  if (picked) {
    var wanted = (location.hash || '').replace('#', '');
    radios.forEach(function (r) { if (r.value === wanted) { r.checked = true; picked = r; } });
    showVariant(picked.value);
  }
})();
