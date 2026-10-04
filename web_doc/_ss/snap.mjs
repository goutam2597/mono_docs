// CDP screenshot tool for the MONO web doc.
// Usage: node snap.mjs [shotName ...]   (no args = every shot)
// Requires a headless Chrome it launches itself; the app must be reachable at BASE.
import { spawn } from 'node:child_process';
import { writeFileSync, rmSync, mkdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { tmpdir } from 'node:os';

const __dirname = dirname(fileURLToPath(import.meta.url));
const BASE = 'http://localhost/mono/mono_market';
const PORT = 9778;
const CHROME = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const ASSETS = join(__dirname, '..', 'assets');
const DEBUG_PORT_URL = `http://127.0.0.1:${PORT}`;

const sleep = ms => new Promise(r => setTimeout(r, ms));

// JS snippets evaluated in the page to reach overlay states.
const ACT = {
  openSearch: "document.querySelector('[data-open-search]')?.click()",
  openMenu: "document.querySelector('[data-open-menu]')?.click()",
  openVariation: "document.querySelector('button[data-variation-modal]')?.click()",
  pickLastVariations: `(() => {
    const groups = {};
    document.querySelectorAll('#varmodal-groups input[type="radio"][data-variation-radio]').forEach(r => {
      if (r.disabled) return;
      (groups[r.dataset.attrId] ??= []).push(r);
    });
    Object.values(groups).forEach(list => list[list.length - 1].click());
    return Object.keys(groups).length + ' groups';
  })()`,
};

const THEMES = ['mono', 'beauty', 'electronics', 'fashion', 'fullwidth', 'grocery', 'home', 'petshop', 'sports'];
const PRODUCT = '/products/tailored-heavyweight-wool-overcoat';

const SHOTS = {};
for (const t of THEMES) {
  SHOTS[`theme-${t}`] = { url: '/', w: 1440, h: 900, dsf: 1, mobile: false,
    out: join(ASSETS, 'themes', `theme-${t}.jpg`), settle: 2600 };
}
SHOTS['home-desktop'] = { url: '/', w: 1440, h: 900, dsf: 1, out: join(ASSETS, 'storefront', 'storefront-home-desktop.jpg') };
SHOTS['home-mobile'] = { url: '/', w: 390, h: 844, dsf: 2, mobile: true, out: join(ASSETS, 'storefront', 'storefront-home-mobile.jpg') };
SHOTS['shop-desktop'] = { url: '/shop', w: 1440, h: 900, dsf: 1, out: join(ASSETS, 'storefront', 'storefront-shop-desktop.jpg') };
SHOTS['shop-mobile'] = { url: '/shop', w: 390, h: 844, dsf: 2, mobile: true, out: join(ASSETS, 'storefront', 'storefront-shop-mobile.jpg') };
SHOTS['product-desktop'] = { url: PRODUCT, w: 1440, h: 900, dsf: 1, out: join(ASSETS, 'storefront', 'storefront-product-desktop.jpg') };
SHOTS['variation-modal'] = { url: '/shop', w: 1440, h: 900, dsf: 1, actions: [ACT.openVariation], settle: 1200,
  out: join(ASSETS, 'storefront', 'storefront-variation-modal.jpg') };
SHOTS['variation-selected'] = { url: '/shop', w: 1440, h: 900, dsf: 1, actions: [ACT.openVariation, ACT.pickLastVariations], settle: 1200,
  out: join(ASSETS, 'storefront', 'storefront-variation-selected.jpg') };
SHOTS['mobile-search'] = { url: '/', w: 390, h: 844, dsf: 2, mobile: true, actions: [ACT.openSearch], settle: 900,
  out: join(ASSETS, 'storefront', 'storefront-mobile-search.jpg') };
SHOTS['mobile-menu'] = { url: '/', w: 390, h: 844, dsf: 2, mobile: true, actions: [ACT.openMenu], settle: 900,
  out: join(ASSETS, 'storefront', 'storefront-mobile-menu.jpg') };
SHOTS['login-desktop'] = { url: '/login', w: 1440, h: 900, dsf: 1, out: join(ASSETS, 'storefront', 'storefront-login-desktop.jpg') };

// Marketing popup hides the page behind a backdrop — dismiss and remove it on every capture.
// Also drop the cookie banner and small floating widgets (chat/WhatsApp launcher) that
// overlap the bottom-right corner of the viewport.
const DISMISS_POPUP = `(() => {
  document.querySelectorAll('[data-promo-close]').forEach(el => el.click());
  document.getElementById('promo-popup')?.remove();
  document.getElementById('cookie-consent')?.remove();
  document.querySelectorAll('.mono-wa-float, .mono-stt').forEach(el => el.remove());
  for (const el of document.querySelectorAll('body *')) {
    const s = getComputedStyle(el);
    if (s.position !== 'fixed') continue;
    const r = el.getBoundingClientRect();
    if (r.width >= 24 && r.width <= 100 && r.height >= 24 && r.height <= 100
        && r.top > innerHeight - 260 && r.left > innerWidth - 260) el.remove();
  }
  return true;
})()`;

class Cdp {
  constructor(ws) { this.ws = ws; this.id = 0; this.pending = new Map(); this.listeners = new Map();
    ws.addEventListener('message', ev => {
      const msg = JSON.parse(ev.data);
      if (msg.id && this.pending.has(msg.id)) { const { resolve, reject } = this.pending.get(msg.id);
        this.pending.delete(msg.id); msg.error ? reject(new Error(msg.error.message)) : resolve(msg.result); }
      else if (msg.method && this.listeners.has(msg.method)) this.listeners.get(msg.method).forEach(fn => fn(msg.params));
    }); }
  send(method, params = {}) { const id = ++this.id; this.ws.send(JSON.stringify({ id, method, params }));
    return new Promise((resolve, reject) => this.pending.set(id, { resolve, reject })); }
  once(method, fn) { if (!this.listeners.has(method)) this.listeners.set(method, []);
    this.listeners.get(method).push(fn); }
}

async function waitEvent(cdp, method, timeoutMs) {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error(`timeout waiting ${method}`)), timeoutMs);
    cdp.once(method, p => { clearTimeout(timer); resolve(p); });
  });
}

async function newTab() {
  const res = await fetch(`${DEBUG_PORT_URL}/json/new?about:blank`, { method: 'PUT' });
  return res.json();
}

async function shoot(name, cfg) {
  const tab = await newTab();
  const ws = new WebSocket(tab.webSocketDebuggerUrl);
  await new Promise((res, rej) => { ws.addEventListener('open', res); ws.addEventListener('error', rej); });
  const cdp = new Cdp(ws);
  await cdp.send('Page.enable');
  await cdp.send('Emulation.setDeviceMetricsOverride',
    { width: cfg.w, height: cfg.h, deviceScaleFactor: cfg.dsf ?? 1, mobile: !!cfg.mobile,
      screenWidth: cfg.w, screenHeight: cfg.h });
  const loaded = waitEvent(cdp, 'Page.loadEventFired', 20000).catch(() => {});
  await cdp.send('Page.navigate', { url: BASE + cfg.url });
  await loaded;
  await sleep(cfg.settle ?? 1800);
  await cdp.send('Runtime.evaluate', { expression: 'window.scrollTo(0,0)' });
  await cdp.send('Runtime.evaluate', { expression: DISMISS_POPUP });
  await sleep(250);
  for (const expr of cfg.actions ?? []) {
    await cdp.send('Runtime.evaluate', { expression: expr, returnByValue: true });
    await sleep(700);
  }
  // The chat float and friends are lazy-injected; sweep again immediately before capture.
  await cdp.send('Runtime.evaluate', { expression: DISMISS_POPUP });
  await sleep(200);
  const shot = await cdp.send('Page.captureScreenshot', { format: 'jpeg', quality: 90 });
  mkdirSync(dirname(cfg.out), { recursive: true });
  writeFileSync(cfg.out, Buffer.from(shot.data, 'base64'));
  await cdp.send('Page.close').catch(() => {});
  ws.close();
  console.log('saved', cfg.out);
}

const chrome = spawn(CHROME, [
  '--headless=new', `--remote-debugging-port=${PORT}`, `--user-data-dir=${join(tmpdir(), 'mono-ss-profile')}`,
  '--no-first-run', '--no-default-browser-check', '--hide-scrollbars', '--disable-gpu',
  '--window-size=1500,1000', 'about:blank', '--silent-debugger-extension-api',
], { stdio: 'ignore' });

try {
  let up = false;
  for (let i = 0; i < 60 && !up; i++) { await sleep(250);
    up = await fetch(`${DEBUG_PORT_URL}/json/version`).then(r => r.ok).catch(() => false); }
  if (!up) throw new Error('chrome debug port never came up');

  const wanted = process.argv.slice(2);
  const names = wanted.length ? wanted : Object.keys(SHOTS);
  for (const name of names) {
    const cfg = SHOTS[name];
    if (!cfg) { console.error('unknown shot:', name); continue; }
    try { await shoot(name, cfg); }
    catch (e) { console.error('FAILED', name, e.message); }
  }
} finally {
  chrome.kill();
  try { rmSync(join(tmpdir(), 'mono-ss-profile'), { recursive: true, force: true, maxRetries: 5, retryDelay: 400 }); }
  catch { /* chrome may still hold the profile for a moment; harmless */ }
}
