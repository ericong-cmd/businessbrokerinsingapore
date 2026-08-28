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

  /* ---------- Conversion tracking ----------
     Fires into Vercel Web Analytics when present; silently does nothing otherwise. */
  function track(name, data) {
    try {
      if (typeof window.va === 'function') window.va('event', { name: name, data: data || {} });
    } catch (e) { /* analytics must never break the page */ }
  }

  document.addEventListener('click', function (ev) {
    var el = ev.target.closest && ev.target.closest('[data-track], a[href*="wa.me"]');
    if (!el) return;
    track(el.getAttribute('data-track') || 'wa-click', { href: el.getAttribute('href') || '' });
  });

  /* Warm-lane capture: post to our own endpoint, which talks to Resend server-side.
     If the endpoint is not configured yet (503) the block falls back to WhatsApp,
     so this ships safely before the API key exists. */
  document.querySelectorAll('form[data-capture]').forEach(function (form) {
    var block = form.closest('.capture');
    var msg = block && block.querySelector('.capture-msg');
    var fallback = block && block.querySelector('.capture-fallback');
    var note = block && block.querySelector('.capture-note');
    var btn = form.querySelector('button[type="submit"]');

    function say(text, tone) {
      if (!msg) return;
      msg.textContent = text;
      msg.hidden = false;
      msg.setAttribute('data-tone', tone || 'info');
    }
    function toWhatsApp(text) {
      say(text, 'warn');
      form.hidden = true;
      if (note) note.hidden = true;
      if (fallback) fallback.hidden = false;
    }

    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var source = form.getAttribute('data-capture');
      var payload = {
        email: (form.querySelector('input[type="email"]') || {}).value || '',
        source: source,
        sector: (form.querySelector('[data-fill="sector"]') || {}).value || '',
        detail: (form.querySelector('[data-fill="detail"]') || {}).value || ''
      };

      if (btn) { btn.disabled = true; btn.textContent = 'Sending…'; }
      say('Sending…', 'info');

      fetch(form.getAttribute('action'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      }).then(function (r) {
        return r.json().catch(function () { return {}; }).then(function (d) {
          return { status: r.status, data: d };
        });
      }).then(function (res) {
        if (res.status === 200) {
          track('capture-' + source, { sector: payload.sector });
          form.hidden = true;
          if (note) note.hidden = true;
          say('Sent — it should arrive in a minute. Check spam if it doesn’t.', 'ok');
          return;
        }
        if (btn) { btn.disabled = false; btn.textContent = 'Email me the breakdown'; }
        if (res.status === 503) {
          toWhatsApp('Email delivery isn’t switched on yet — send it over WhatsApp instead and you’ll get the same breakdown.');
          return;
        }
        if (res.status === 400) { say(res.data.error || 'Please check that email address.', 'warn'); return; }
        toWhatsApp('That didn’t send. WhatsApp is the quickest route right now.');
      }).catch(function () {
        if (btn) { btn.disabled = false; btn.textContent = 'Email me the breakdown'; }
        toWhatsApp('That didn’t send — you may be offline. WhatsApp works too.');
      });
    });
  });

  function fillCapture(scope, sector, detail) {
    (scope || document).querySelectorAll('[data-fill="sector"]').forEach(function (i) { i.value = sector; });
    (scope || document).querySelectorAll('[data-fill="detail"]').forEach(function (i) { i.value = detail; });
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

      /* Owner-dependence positions the business WITHIN its published sector band —
         it never pushes the multiple above the band, so the estimator stays
         consistent with /singapore-sme-valuation-multiples/. */
      var m = MULTIPLES[industry] || MULTIPLES.other;
      var lo = m.lo, hi = m.hi, span = hi - lo;
      if (dependence === 'low') { lo = lo + span * 0.35; }
      if (dependence === 'high') { lo = lo * 0.85; hi = hi - span * 0.4; }
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

      fillCapture(result, m.label,
        'EBITDA ' + fmtSGD(ebitda) + ', range ' + fmtSGD(vLo) + '-' + fmtSGD(vHi) +
        ', dependence ' + dependence);
      track('estimator-run', { sector: industry, dependence: dependence });

      result.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'nearest' });
    });
  }

  /* ---------- Exit-readiness quiz ---------- */
  var AREAS = {
    owner: 'Owner-dependence', records: 'Financial records', customers: 'Customer concentration',
    transfer: 'Leases and licences', management: 'Management depth', growth: 'Growth trend',
    reason: 'Reason for selling', timeline: 'Timeline'
  };
  var GAP_ADVICE = {
    owner: 'Document processes and delegate decisions so the business runs without you — this is what converts an earn-out back into cash at completion.',
    records: 'Get three consistent years compiled cleanly and separate personal items from company accounts before a buyer ever looks.',
    customers: 'Reduce reliance on your largest customer by winning new accounts, or lock in longer contracts with the ones you have.',
    transfer: 'Review lease tenure and licence transferability now; renew short-dated leases before going to market, not during due diligence.',
    management: 'Build or hire a second tier who can run operations — buyers price the team that stays, not the owner who leaves.',
    growth: 'Stabilise the trend before marketing. A flat, profitable year beats a declining one; a declining year mid-process invites a re-trade.',
    reason: 'Plan the exit rather than reacting to an approach or to fatigue — a planned seller negotiates from strength.',
    timeline: 'Give yourself runway. Time is the cheapest thing you can spend on price; a forced timeline is the most expensive.'
  };
  var BANDS = [
    { min: 75, name: 'Ready now',
      verdict: 'Your business shows the characteristics buyers pay full value for. At this level the priority is running a competitive process rather than more preparation — the risk now is leaving money on the table by selling to the first buyer who asks.' },
    { min: 45, name: '6–12 months of preparation',
      verdict: 'A saleable business with specific, fixable gaps. Six to twelve months of focused work on the areas below would materially change both the price and the certainty of completion — and that work is almost always worth more than negotiating harder later.' },
    { min: 0, name: '1–2 years out',
      verdict: 'Selling now would mean accepting a discount for things that are fixable with time. That is not a reason to abandon the idea — it is a reason to start preparing deliberately, in the order below, while you still hold the leverage.' }
  ];

  var quizForm = document.getElementById('quiz-form');
  if (quizForm) {
    quizForm.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var errEl = document.getElementById('quiz-error');
      errEl.style.display = 'none';

      var total = 0, answered = 0, weak = [];
      var missing = null;
      Object.keys(AREAS).forEach(function (key) {
        var picked = quizForm.querySelector('input[name="q-' + key + '"]:checked');
        if (!picked) { if (!missing) missing = key; return; }
        var v = parseInt(picked.value, 10);
        total += v; answered++;
        if (v <= 40) weak.push(key);
      });

      if (answered < Object.keys(AREAS).length) {
        errEl.textContent = 'Please answer all eight questions — the one about ' +
          AREAS[missing].toLowerCase() + ' is still blank.';
        errEl.style.display = 'block';
        var el = quizForm.querySelector('[data-q="' + missing + '"]');
        if (el) el.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'center' });
        return;
      }

      var score = Math.round(total / answered);
      var band = BANDS.filter(function (b) { return score >= b.min; })[0];

      var result = document.getElementById('quiz-result');
      result.classList.add('show');
      requestAnimationFrame(function () {
        requestAnimationFrame(function () { result.classList.add('visible'); });
      });

      var numEl = document.getElementById('quiz-score-num');
      if (reduceMotion) { numEl.textContent = score; }
      else {
        var start = null;
        requestAnimationFrame(function step(ts) {
          if (!start) start = ts;
          var p = Math.min((ts - start) / 900, 1);
          numEl.textContent = Math.round(score * (1 - Math.pow(1 - p, 3)));
          if (p < 1) requestAnimationFrame(step); else numEl.textContent = score;
        });
      }
      document.getElementById('quiz-meter-fill').style.width = score + '%';
      document.getElementById('quiz-band').textContent = band.name;
      document.getElementById('quiz-verdict').textContent = band.verdict;

      var gaps = document.getElementById('quiz-gaps');
      if (weak.length) {
        gaps.innerHTML = '<h4>Where to start</h4><ul>' + weak.map(function (k) {
          return '<li><strong>' + AREAS[k] + '.</strong> ' + GAP_ADVICE[k] + '</li>';
        }).join('') + '</ul>';
      } else {
        gaps.innerHTML = '<h4>Where to start</h4><p>No individual area scored weak. The work now is process, not preparation — running enough buyer competition to price the business properly.</p>';
      }

      document.getElementById('quiz-wa').href = 'https://wa.me/' + WA_NUMBER + '?text=' +
        encodeURIComponent('Hi, I scored ' + score + '/100 on the exit-readiness quiz (' +
          band.name + '). I’d like to talk through what to fix first.');

      fillCapture(result, '', 'Score ' + score + '/100, band ' + band.name +
        (weak.length ? ', weak areas: ' + weak.map(function (k) { return AREAS[k]; }).join(', ') : ''));
      track('quiz-complete', { score: score, band: band.name, weak: weak.join(',') });

      result.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'nearest' });
    });
  }
})();
