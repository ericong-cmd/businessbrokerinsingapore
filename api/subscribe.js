/**
 * Warm-lane capture endpoint.
 *
 * Receives an email from the valuation estimator or the exit-readiness quiz,
 * stores the contact in a Resend audience (tagged by source), and sends the
 * requested breakdown immediately.
 *
 * Environment variables (set in Vercel project settings):
 *   RESEND_API_KEY      required — server-side only, never exposed to the browser
 *   RESEND_AUDIENCE_ID  optional — if set, contacts are added to this audience
 *   CAPTURE_FROM        optional — verified sender, defaults to the address below
 *   CAPTURE_BCC         optional — copies each capture to the broker
 *
 * Until RESEND_API_KEY exists the endpoint answers 503 {configured:false} and the
 * page falls back to the WhatsApp lane, so nothing is broken while it is unset.
 */

const RESEND = 'https://api.resend.com';
const DEFAULT_FROM = 'Business Broker In Singapore <hello@businessbrokerinsingapore.com>';
const REPLY_TO = 'businessbrokerinsingapore@thefundingassembly.com';
const WA = 'https://wa.me/6589518821';

const SOURCES = {
  estimator: {
    subject: 'Your valuation range — what drives the number',
    lead: 'Thanks for using the valuation estimator. Here is the context behind the range you saw, and what would move it.',
    points: [
      'The range applies your sector’s adjusted-EBITDA multiple to the profit figure you entered, then positions the business within that band according to how dependent it is on you.',
      'What moves it up: reducing owner-dependence, diversifying customers beyond any single account above 30% of revenue, converting project work into contracted or recurring revenue, and three consistent years of clean accounts.',
      'What moves it down: customer concentration, a short-dated lease or non-transferable licence, earnings that swing year to year, and records that force a buyer to guess.',
      'What the estimator cannot see: growth trend, contract quality, margin stability and deal structure. Those routinely move a final price by 30% in either direction.',
    ],
    next: 'The published multiples table is at https://www.businessbrokerinsingapore.com/singapore-sme-valuation-multiples/ if you want to check the band for your sector.',
  },
  quiz: {
    subject: 'Your exit-readiness score — where to start',
    lead: 'Thanks for completing the exit-readiness quiz. Here is what your score means and the order worth tackling it in.',
    points: [
      'The score weighs the eight things a buyer’s advisors examine first: owner-dependence, financial records, customer concentration, transferability of leases and licences, management depth, growth trend, your reason for selling and your timeline.',
      'Owner-dependence and financial records are almost always the highest-return fixes: the first decides whether you are paid in cash or in an earn-out, the second decides whether the deal survives due diligence at all.',
      'Customer concentration takes longest to fix, so start it earliest if a single account is above 30% of revenue.',
      'Leases and licences are the cheapest to check and the most expensive to discover late — review tenure and transferability before going to market, not during due diligence.',
    ],
    next: 'The seven-stage process is at https://www.businessbrokerinsingapore.com/how-it-works/ if you want to see how a sale actually runs.',
  },
};

function esc(s) {
  return String(s).replace(/[&<>"]/g, function (c) {
    return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
  });
}

function buildEmail(kind, detail) {
  const t = SOURCES[kind] || SOURCES.estimator;
  const items = t.points.map(function (p) {
    return '<li style="margin:0 0 12px">' + esc(p) + '</li>';
  }).join('');
  const yours = detail
    ? '<p style="margin:0 0 18px;color:#475569"><strong>What you entered:</strong> ' + esc(detail) + '</p>'
    : '';
  const html =
    '<div style="font-family:Helvetica,Arial,sans-serif;font-size:16px;line-height:1.6;color:#0F172A;max-width:620px">' +
      '<p style="margin:0 0 18px">' + esc(t.lead) + '</p>' +
      yours +
      '<ul style="padding-left:20px;margin:0 0 18px">' + items + '</ul>' +
      '<p style="margin:0 0 18px">' + esc(t.next) + '</p>' +
      '<p style="margin:0 0 18px">If it would help to talk any of this through, reply to this email or message us on WhatsApp at ' +
        '<a href="' + WA + '" style="color:#B45309">+65 8951 8821</a>. Confidential, no fee, no obligation.</p>' +
      '<hr style="border:0;border-top:1px solid #CBD5E1;margin:26px 0">' +
      '<p style="margin:0;font-size:13px;color:#64748B">' +
        'Business Broker In Singapore is operated by The Funding Assembly Pte. Ltd. (UEN 202443830Z), ' +
        '2 Leng Kee Road, #02-06 Thye Hong Centre, Singapore 159086.<br>' +
        'Indicative guidance only — not a valuation of your business and not financial advice.' +
      '</p>' +
    '</div>';
  return { subject: t.subject, html: html };
}

async function resend(path, key, body) {
  const r = await fetch(RESEND + path, {
    method: 'POST',
    headers: { Authorization: 'Bearer ' + key, 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error('Resend ' + path + ' -> ' + r.status + ' ' + (await r.text()).slice(0, 300));
  return r.json();
}

module.exports = async function handler(req, res) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const key = process.env.RESEND_API_KEY;
  if (!key) {
    // Not wired yet — the page falls back to the WhatsApp lane on this response.
    return res.status(503).json({ configured: false });
  }

  let body = req.body;
  if (typeof body === 'string') {
    try { body = JSON.parse(body); } catch (e) { body = {}; }
  }
  body = body || {};

  const email = String(body.email || '').trim();
  const source = SOURCES[body.source] ? body.source : 'estimator';
  const sector = String(body.sector || '').slice(0, 120);
  const detail = String(body.detail || '').slice(0, 300);

  if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email) || email.length > 200) {
    return res.status(400).json({ error: 'Please enter a valid email address.' });
  }

  const from = process.env.CAPTURE_FROM || DEFAULT_FROM;
  const audience = process.env.RESEND_AUDIENCE_ID;
  const mail = buildEmail(source, detail);

  try {
    if (audience) {
      // Storing the contact must not block the email the person actually asked for.
      try {
        await resend('/audiences/' + audience + '/contacts', key, {
          email: email,
          unsubscribed: false,
          first_name: source === 'quiz' ? 'Quiz' : 'Estimator',
          last_name: sector || 'Unknown sector',
        });
      } catch (e) {
        console.error('audience add failed:', e.message);
      }
    }

    const payload = {
      from: from,
      to: [email],
      reply_to: REPLY_TO,
      subject: mail.subject,
      html: mail.html,
      tags: [
        { name: 'source', value: source },
        { name: 'sector', value: (sector || 'unknown').toLowerCase().replace(/[^a-z0-9_-]/g, '-').slice(0, 40) || 'unknown' },
      ],
    };
    if (process.env.CAPTURE_BCC) payload.bcc = [process.env.CAPTURE_BCC];

    await resend('/emails', key, payload);
    return res.status(200).json({ ok: true });
  } catch (err) {
    console.error('capture failed:', err.message);
    return res.status(502).json({ error: 'We could not send that just now.' });
  }
};
