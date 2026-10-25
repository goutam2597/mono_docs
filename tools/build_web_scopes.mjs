// Generates the scoped pages (vendor.html, admin.html) for the web doc and
// ensures index.html carries the scope tab bar.
// Usage: node tools/build_web_scopes.mjs   (from the docs/ folder)
import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const docsRoot = join(dirname(fileURLToPath(import.meta.url)), '..');
const webDir = join(docsRoot, 'web_doc');
const src = readFileSync(join(webDir, 'index.html'), 'utf8');

const ALL = [
  'introduction', 'architecture', 'installation', 'first-run', 'upgrading',
  'storefront-themes', 'catalog', 'cart-checkout', 'payments', 'customer-account', 'storefront-content', 'localization',
  'vendor-dashboard', 'vendor-catalog-finance',
  'admin-dashboard', 'admin-access', 'admin-orders', 'admin-catalog', 'admin-customers', 'admin-marketplace', 'admin-delivery', 'admin-messaging', 'admin-ai', 'admin-appearance', 'admin-settings', 'admin-platform',
  'api-overview', 'api-customer', 'api-vendor', 'database', 'services-jobs', 'deployment', 'troubleshooting',
];

const SCOPES = {
  web: {
    file: 'index.html',
    title: 'MONO Multi-Vendor Marketplace Operations & Engineering Dashboard',
    crumb: 'MONO WEB',
    active: 'web',
    keep: new Set([
      'introduction', 'architecture', 'installation', 'first-run', 'upgrading',
      'storefront-themes', 'catalog', 'cart-checkout', 'payments', 'customer-account', 'storefront-content', 'localization',
      'deployment', 'troubleshooting',
    ]),
  },
  vendor: {
    file: 'vendor.html',
    title: 'Mono Web — Vendor Portal Documentation Dashboard',
    crumb: 'MONO WEB · VENDOR PORTAL',
    active: 'vendor',
    keep: new Set([
      'introduction',
      'vendor-dashboard', 'vendor-catalog-finance', 'vendor-onboarding', 'vendor-modules',
    ]),
    banner: `
      <section class="executive-banner" aria-label="Executive Overview">
        <div class="banner-body">
          <div class="banner-badge-row">
            <span class="banner-kicker">MONO VENDOR PORTAL ENGINEERING CONSOLE</span>
            <span class="banner-tag">Seller Suite</span>
          </div>
          <h1 class="banner-title">Vendor Web Portal Operations &amp; Engineering Dashboard</h1>
          <p class="banner-desc">Field manual for the MONO vendor web portal: store branding and policies, the catalog and variant matrix with bulk CSV uploads, the order fulfillment pipeline, settlements and withdrawals, and store promotions.</p>
        </div>
      </section>`,
    kpis: `
      <section class="kpi-grid" aria-label="System Metrics">
<div class="kpi-card">
  <div class="kpi-card-header">
    <span class="kpi-code">SELLER / 01</span>
    <span class="kpi-pill kpi-pill-blue">Store</span>
  </div>
  <strong class="kpi-metric">Branding &amp; Policies</strong>
  <p class="kpi-label">Independent storefront workspace: banners, business info, and policies per vendor.</p>
</div>
<div class="kpi-card">
  <div class="kpi-card-header">
    <span class="kpi-code">SELLER / 02</span>
    <span class="kpi-pill kpi-pill-green">Catalog</span>
  </div>
  <strong class="kpi-metric">Variants + CSV Upload</strong>
  <p class="kpi-label">Multi-tier pricing, SKU tracking, low-stock alerts, and bulk import.</p>
</div>
<div class="kpi-card">
  <div class="kpi-card-header">
    <span class="kpi-code">SELLER / 03</span>
    <span class="kpi-pill kpi-pill-navy">Orders</span>
  </div>
  <strong class="kpi-metric">Fulfillment Pipeline</strong>
  <p class="kpi-label">Verification, packing slips, dispatch handover, and tracking updates.</p>
</div>
<div class="kpi-card">
  <div class="kpi-card-header">
    <span class="kpi-code">SELLER / 04</span>
    <span class="kpi-pill kpi-pill-amber">Money</span>
  </div>
  <strong class="kpi-metric">Settlements &amp; Wallet</strong>
  <p class="kpi-label">Commission breakdown per item and one-click withdrawal requests.</p>
</div>
      </section>`,
    hero: `
            <div class="ov" id="top" aria-labelledby="ov-title">
            <div class="ov-bar">
              <p class="ov-kicker"><span>Vendor portal documentation</span><span>Sell &middot; Manage &middot; Get paid</span></p>
              <span class="ov-signal"><i aria-hidden="true"></i>Web portal</span>
            </div>

            <div class="ov-head">
              <div class="ov-heading">
                <h1 id="ov-title">Mono.<em> Vendor Portal.</em></h1>
                <p class="ov-note"><span aria-hidden="true">&bull;</span> The seller web workspace, end to end.</p>
              </div>
              <div class="ov-side">
                <p class="ov-lede">The vendor web portal served at <code>/dashboard</code>: brand your store, build the catalog with variants and bulk CSV uploads, run the order fulfillment pipeline, and manage settlements, wallet, and withdrawals.</p>
                <div class="ov-actions">
                  <a href="https://monomarket.site/vendor" target="_blank" rel="noopener" class="action-button action-button--primary">Live Vendor Panel <span aria-hidden="true">&nearr;</span></a>
                  <a href="index.html#installation" class="action-button">Installation Guide <span aria-hidden="true">&darr;</span></a>
                </div>
              </div>
            </div>

            <div class="ov-kpis" aria-label="Vendor portal headline facts">
              <article class="ov-kpi"><span class="status-index">A / 01</span><p>Surface</p><strong>/dashboard portal</strong><span class="status-badge status-badge--blue">Vendor Portal</span></article>
              <article class="ov-kpi"><span class="status-index">A / 02</span><p>Catalog</p><strong>Variants + CSV uploads</strong><span class="status-badge status-badge--teal">Full control</span></article>
              <article class="ov-kpi"><span class="status-index">A / 03</span><p>Money</p><strong>Settlements &amp; withdrawals</strong><span class="status-badge status-badge--amber">Transparent</span></article>
            </div>
          </div>`,
  },
  admin: {
    file: 'admin.html',
    title: 'Mono Web — Admin Panel Documentation Dashboard',
    crumb: 'MONO WEB · ADMIN PANEL',
    active: 'admin',
    keep: new Set([
      'introduction',
      'admin-dashboard', 'admin-access', 'admin-orders', 'admin-catalog', 'admin-customers', 'admin-marketplace', 'admin-delivery', 'admin-messaging', 'admin-ai', 'admin-appearance', 'admin-settings', 'admin-platform',
    ]),
    banner: `
      <section class="executive-banner" aria-label="Executive Overview">
        <div class="banner-body">
          <div class="banner-badge-row">
            <span class="banner-kicker">MONO SUPER ADMIN ENGINEERING CONSOLE</span>
            <span class="banner-tag">Operations &amp; Governance</span>
          </div>
          <h1 class="banner-title">Super Admin Panel Operations &amp; Engineering Dashboard</h1>
          <p class="banner-desc">Super-admin field manual for the MONO Marketplace: vendor governance and KYC approvals, commissions and settlements, catalog and order operations, delivery, chat and push, AI tooling, themes, and every platform setting.</p>
        </div>
      </section>`,
    kpis: `
      <section class="kpi-grid" aria-label="System Metrics">
<div class="kpi-card">
  <div class="kpi-card-header">
    <span class="kpi-code">ADMIN / 01</span>
    <span class="kpi-pill kpi-pill-blue">Governance</span>
  </div>
  <strong class="kpi-metric">Vendors + KYC Approvals</strong>
  <p class="kpi-label">Multi-step registration, document verification, store approvals, and suspensions.</p>
</div>
<div class="kpi-card">
  <div class="kpi-card-header">
    <span class="kpi-code">ADMIN / 02</span>
    <span class="kpi-pill kpi-pill-green">Money</span>
  </div>
  <strong class="kpi-metric">Commissions &amp; Payouts</strong>
  <p class="kpi-label">Category-wise rates, automated settlement, and withdrawal control.</p>
</div>
<div class="kpi-card">
  <div class="kpi-card-header">
    <span class="kpi-code">ADMIN / 03</span>
    <span class="kpi-pill kpi-pill-navy">Catalog</span>
  </div>
  <strong class="kpi-metric">Orders, Refunds &amp; Invoices</strong>
  <p class="kpi-label">Catalog administration, order lifecycle, and refund operations end to end.</p>
</div>
<div class="kpi-card">
  <div class="kpi-card-header">
    <span class="kpi-code">ADMIN / 04</span>
    <span class="kpi-pill kpi-pill-amber">Access</span>
  </div>
  <strong class="kpi-metric">Roles + 32 Permissions</strong>
  <p class="kpi-label">Granular permission gates on every admin action.</p>
</div>
      </section>`,
    hero: `
            <div class="ov" id="top" aria-labelledby="ov-title">
            <div class="ov-bar">
              <p class="ov-kicker"><span>Super admin documentation</span><span>Operate &middot; Govern &middot; Scale</span></p>
              <span class="ov-signal"><i aria-hidden="true"></i>Laravel · /admin</span>
            </div>

            <div class="ov-head">
              <div class="ov-heading">
                <h1 id="ov-title">Mono.<em> Admin Panel.</em></h1>
                <p class="ov-note"><span aria-hidden="true">&bull;</span> Complete operations and governance guide.</p>
              </div>
              <div class="ov-side">
                <p class="ov-lede">The Laravel super-admin console behind the marketplace: govern vendors and KYC approvals, tune commissions and settlements, run catalog, order, delivery, chat, and AI operations, and control every platform setting from one place.</p>
                <div class="ov-actions">
                  <a href="https://monomarket.site/admin" target="_blank" rel="noopener" class="action-button action-button--primary">Live Admin Panel <span aria-hidden="true">&nearr;</span></a>
                  <a href="index.html#installation" class="action-button">Installation Guide <span aria-hidden="true">&darr;</span></a>
                </div>
              </div>
            </div>

            <div class="ov-kpis" aria-label="Super admin headline facts">
              <article class="ov-kpi"><span class="status-index">A / 01</span><p>Surface</p><strong>/admin console</strong><span class="status-badge status-badge--blue">Super Admin</span></article>
              <article class="ov-kpi"><span class="status-index">A / 02</span><p>Access control</p><strong>Roles + 32 permissions</strong><span class="status-badge status-badge--teal">Granular</span></article>
              <article class="ov-kpi"><span class="status-index">A / 03</span><p>Stack</p><strong>Laravel 13 / PHP 8.3</strong><span class="status-badge status-badge--amber">Self-hosted</span></article>
            </div>
          </div>`,
  },
};

const TAB_BAR = (active) => `        <nav class="scope-tabs" aria-label="Documentation scope">
          <a href="index.html" class="scope-tab${active === 'web' ? ' is-active' : ''}">Web Storefront</a>
          <a href="vendor.html" class="scope-tab${active === 'vendor' ? ' is-active' : ''}">Vendor Portal</a>
          <a href="admin.html" class="scope-tab${active === 'admin' ? ' is-active' : ''}">Admin Panel</a>
        </nav>
`;

// Deterministically rebuild the tab bar with the given scope active.
const tabBar = (active) => {
  const line = (file, label, isActive) =>
    `          <a href="${file}" class="scope-tab${isActive ? ' is-active' : ''}">${label}</a>\n`;
  return `        <nav class="scope-tabs" aria-label="Documentation scope">\n` +
    line('index.html', 'Web Storefront', active === 'web') +
    line('vendor.html', 'Vendor Portal', active === 'vendor') +
    line('admin.html', 'Admin Panel', active === 'admin') +
    `        </nav>`;
};

// 1. Ensure the tab bar exists in the top navbar (idempotent).
let base = src;
if (!base.includes('class="scope-tabs"')) {
  const headerRe = /^( *)<\/header>/m;
  const m = base.match(headerRe);
  if (!m) throw new Error('top-navbar </header> not found');
  base = base.replace(headerRe, `${TAB_BAR('web')}${m[1]}</header>`);
}

// 2. Build a scoped variant.
function buildScope(key) {
  const cfg = SCOPES[key];
  let out = base;

  // 2a. Drop out-of-scope sections (no nested <section> inside doc-sections).
  out = out.replace(/<section class="doc-section dashboard-card[^"]*" id="([a-z-]+)" data-section-title="[^"]*">[\s\S]*?<\/section>\n?/g, (block, id) => (cfg.keep.has(id) ? block : ''));

  // 2b. Drop orphaned section comments left behind.
  out = out.replace(/<!-- Section: ([a-z-]+) -->\n/g, (c, id) => (cfg.keep.has(id) ? c : ''));

  // 2c. Filter sidebar links, then drop empty groups.
  out = out.replace(/<div class="sidebar-group-label">[^<]+<\/div>\n<div class="sidebar-group-items">[\s\S]*?<\/div>\n(?=<div class="sidebar-group-label">|    <\/nav>)/g, (group) => {
    const links = group.match(/<a href="#[a-z-]+" class="sidebar-nav-link" data-nav-id="[a-z-]+">[\s\S]*?<\/a>/g) || [];
    const kept = links.filter((l) => cfg.keep.has(l.match(/data-nav-id="([a-z-]+)"/)[1]));
    if (!kept.length) return '';
    const head = group.match(/^[\s\S]*?<div class="sidebar-group-items">/)[0];
    return head + '\n' + kept.join('\n') + '\n' + group.match(/<div class="sidebar-group-items">[\s\S]*?(<\/div>\n)$/)[1];
  });

  // 2d. Rewrite internal anchors pointing at removed sections to the full doc.
  out = out.replace(/href="#([a-z-]+)"/g, (m, id) => (!cfg.keep.has(id) && ALL.includes(id) ? `href="index.html#${id}"` : m));

  // 2e. Page identity.
  out = out.replace(/<title>[\s\S]*?<\/title>/, `<title>${cfg.title}</title>`);
  out = out.replace(/(<span class="crumb-section">)[^<]*(<\/span>)/, `$1${cfg.crumb}$2`);

  // 2f. Active tab — rebuild the whole tab bar for this scope.
  out = out.replace(/        <nav class="scope-tabs"[\s\S]*?<\/nav>/, tabBar(cfg.active));

  // 2g. Scoped banner, KPI grid, and hero (when the scope defines them).
  if (cfg.banner) out = out.replace(/<section class="executive-banner" aria-label="Executive Overview">[\s\S]*?<\/section>/, cfg.banner);
  if (cfg.kpis) out = out.replace(/<section class="kpi-grid" aria-label="System Metrics">[\s\S]*?<\/section>/, cfg.kpis);
  if (cfg.hero) out = out.replace(/<div class="ov" id="top" aria-labelledby="ov-title">[\s\S]*?(?=\n\s*<p class="section-kicker">01 \/ Overview<\/p>)/, cfg.hero);

  return out;
}

// index.html = the full manual, web tab active.
const idx = base.replace(/        <nav class="scope-tabs"[\s\S]*?<\/nav>/, tabBar('web'));
writeFileSync(join(webDir, 'index.html'), idx);
writeFileSync(join(webDir, 'vendor.html'), buildScope('vendor'));
writeFileSync(join(webDir, 'admin.html'), buildScope('admin'));

// Report
for (const key of Object.keys(SCOPES)) {
  const cfg = SCOPES[key];
  const out = readFileSync(join(webDir, cfg.file), 'utf8');
  const secs = (out.match(/<section class="doc-section/g) || []).length;
  const links = (out.match(/sidebar-nav-link/g) || []).length;
  console.log(`${cfg.file}: ${secs} sections, ${links} sidebar links, title="${cfg.title}"`);
}
