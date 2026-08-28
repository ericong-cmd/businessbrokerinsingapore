/* Business Broker In Singapore — site runtime (no dependencies) */
(function () {
  'use strict';

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* Hero entrance */
  document.body.classList.add('loaded');

  /* Sticky header condense */
  var header = document.querySelector('.site-header');
  var sentinel = document.getElementById('top-sentinel');
  if (header && sentinel && 'IntersectionObserver' in window) {
    new IntersectionObserver(function (entries) {
      header.classList.toggle('condensed', !entries[0].isIntersecting);
    }).observe(sentinel);
  }

  /* Mobile menu */
  var menuBtn = document.querySelector('.menu-btn');
  var mobileNav = document.querySelector('.mobile-nav');
  if (menuBtn && mobileNav) {
    menuBtn.addEventListener('click', function () {
      var open = mobileNav.classList.toggle('open');
      menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  /* Animated counters (final value already in HTML for no-JS/SEO) */
  function runCounter(el) {
    if (reduceMotion) return;
    var target = parseFloat(el.dataset.count);
    var prefix = el.dataset.prefix || '';
    var suffix = el.dataset.suffix || '';
    var decimals = parseInt(el.dataset.decimals || '0', 10);
    var dur = 1200;
    var start = null;
    function frame(ts) {
      if (!start) start = ts;
      var p = Math.min((ts - start) / dur, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      var val = target * eased;
      el.textContent = prefix + val.toFixed(decimals) + suffix;
      if (p < 1) requestAnimationFrame(frame);
      else el.textContent = prefix + target.toFixed(decimals) + suffix;
    }
    requestAnimationFrame(frame);
  }

  /* Scroll reveals */
  if ('IntersectionObserver' in window && !reduceMotion) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        e.target.classList.add('in-view');
        if (e.target.dataset.count) runCounter(e.target);
        io.unobserve(e.target);
      });
    }, { threshold: 0.15, rootMargin: '0px 0px -10% 0px' });
    document.querySelectorAll('.reveal, .timeline, [data-count]').forEach(function (el) { io.observe(el); });
  } else {
    document.querySelectorAll('.reveal, .timeline').forEach(function (el) { el.classList.add('in-view'); });
  }

  /* FAQ accordion */
  document.querySelectorAll('.faq-q').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var item = btn.closest('.faq-item');
      var open = item.classList.toggle('open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  });

  /* Open the FAQ a deep link points at (#question-slug), on load and on hash change */
  function openHashedFaq() {
    if (!location.hash) return;
    var item;
    try { item = document.querySelector(location.hash); } catch (e) { return; }
    if (!item || !item.classList.contains('faq-item')) return;
    item.classList.add('open');
    var btn = item.querySelector('.faq-q');
    if (btn) btn.setAttribute('aria-expanded', 'true');
    item.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'center' });
  }
  openHashedFaq();
  window.addEventListener('hashchange', openHashedFaq);

  /* WhatsApp nudge (one-time, delayed) */
  var waFloat = document.querySelector('.wa-float');
  if (waFloat && !reduceMotion) {
    setTimeout(function () { waFloat.classList.add('nudge'); }, 2200);
  }

  /* ---------- Valuation estimator ---------- */
  var WA_NUMBER = '6589518821';
  var MULTIPLES = {
    fnb:           { label: 'F&B / restaurant / food manufacturing', lo: 2.5, hi: 5 },
    manufacturing: { label: 'Manufacturing / engineering', lo: 3, hi: 6 },
    distribution:  { label: 'Distribution / wholesale trade', lo: 2.5, hi: 5 },
    services:      { label: 'Professional / B2B services', lo: 3, hi: 6 },
    logistics:     { label: 'Logistics / transport', lo: 3, hi: 5.5 },
    construction:  { label: 'Construction / M&E', lo: 2, hi: 4 },
    retail:        { label: 'Retail / consumer', lo: 2, hi: 4 },
    ecommerce:     { label: 'E-commerce / online', lo: 2.5, hi: 5.5 },
    healthcare:    { label: 'Healthcare / education', lo: 4, hi: 7 },
    tech:          { label: 'Software / technology', lo: 4, hi: 9 },
    other:         { label: 'Other', lo: 2.5, hi: 5 }
  };

  function fmtSGD(n) {
    if (n >= 1e6) return 'S$' + (n / 1e6).toFixed(n >= 1e7 ? 0 : 1) + 'M';
    return 'S$' + Math.round(n / 1e3) + 'k';
  }

  function animateRange(el, lo, hi) {
    if (reduceMotion) { el.textContent = fmtSGD(lo) + ' – ' + fmtSGD(hi); return; }
    var dur = 1100, start = null;
    function frame(ts) {
      if (!start) start = ts;
      var p = Math.min((ts - start) / dur, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = fmtSGD(lo * eased) + ' – ' + fmtSGD(hi * eased);
      if (p < 1) requestAnimationFrame(frame);
      else el.textContent = fmtSGD(lo) + ' – ' + fmtSGD(hi);
    }
    requestAnimationFrame(frame);
  }

  var calcForm = document.getElementById('calc-form');
  if (calcForm) {
    calcForm.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var industry = document.getElementById('calc-industry').value;
      var revenue = parseFloat(document.getElementById('calc-revenue').value);
      var ebitda = parseFloat(document.getElementById('calc-ebitda').value);
      var dependence = document.getElementById('calc-dependence').value;
      var errEl = document.getElementById('calc-error');
      errEl.style.display = 'none';

      if (!industry || isNaN(revenue) || isNaN(ebitda) || ebitda <= 0) {
        errEl.textContent = !industry ? 'Please choose your industry.' :
          (isNaN(revenue) ? 'Please enter your annual revenue.' :
          'Please enter a positive annual profit (adjusted EBITDA). For loss-making businesses, message us directly — valuation works differently.');
        errEl.style.display = 'block';
        return;
      }

      var m = MULTIPLES[industry] || MULTIPLES.other;
      var lo = m.lo, hi = m.hi;
      if (dependence === 'high') { lo *= 0.8; hi *= 0.85; }
      if (dependence === 'low') { hi *= 1.1; }
      var vLo = Math.round(ebitda * lo / 10000) * 10000;
      var vHi = Math.round(ebitda * hi / 10000) * 10000;

      var result = document.getElementById('calc-result');
      result.classList.add('show');
      requestAnimationFrame(function () {
        requestAnimationFrame(function () { result.classList.add('visible'); });
      });
      animateRange(document.getElementById('calc-range'), vLo, vHi);
      document.getElementById('calc-basis').textContent =
        'Based on ' + m.label.toLowerCase() + ' businesses typically transacting at ' +
        lo.toFixed(1) + '×–' + hi.toFixed(1) + '× adjusted EBITDA of ' + fmtSGD(ebitda) + '.';

      var msg = 'Hi, I used the valuation estimator on businessbrokerinsingapore.com.\n' +
        'Industry: ' + m.label + '\n' +
        'Annual revenue: ' + fmtSGD(revenue) + '\n' +
        'Adjusted EBITDA: ' + fmtSGD(ebitda) + '\n' +
        'Indicative range shown: ' + fmtSGD(vLo) + ' – ' + fmtSGD(vHi) + '\n' +
        'I’d like a confidential assessment of what my business could actually sell for.';
      document.getElementById('calc-wa').href =
        'https://wa.me/' + WA_NUMBER + '?text=' + encodeURIComponent(msg);

      result.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'nearest' });
    });
  }
})();
