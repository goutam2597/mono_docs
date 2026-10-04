# -*- coding: utf-8 -*-
"""Content source for the MONO Marketplace documentation site.

build_design.py reads SECTIONS and renders index.html using the dark
dashboard design shared with the customer and vendor app docs.

Every section needs: id, group, title, html.
The order of SECTIONS is the order the sections appear in the document,
and it must also be the order of the navigation links.
"""

SECTIONS = [

# =============================================================== OVERVIEW
dict(
    id='introduction', group='Overview',
    title='One codebase, three front doors',
    html="""
<p>MONO Marketplace is a multi-vendor commerce platform. A single Laravel
application serves three completely separate front doors, and they all share
one database, one permission system, and one theme engine.</p>

<div class="service-grid">
  <article class="service-card"><span>STOREFRONT</span><h3>Customer website</h3>
  <ul><li>Themeable catalog with nine shipped storefront themes.</li>
  <li>Cart, coupons, vouchers, wishlist, loyalty, and wallet.</li>
  <li>Fourteen payment methods including cash on delivery and bank transfer.</li>
  <li>Digital goods, bundles, and vendor chat with realtime delivery.</li></ul></article>

  <article class="service-card service-card--teal"><span>VENDOR PANEL</span><h3>Seller dashboard</h3>
  <ul><li>Applications, product, bundle, and taxonomy management.</li>
  <li>Order fulfilment with per-item digital delivery.</li>
  <li>Settlements, withdrawal requests, subscription packages.</li>
  <li>AI suite with metered text, translation, and image quotas.</li></ul></article>

  <article class="service-card service-card--amber"><span>ADMIN PANEL</span><h3>Platform control</h3>
  <ul><li>Orders, invoices, refunds, and a full finance ledger.</li>
  <li>Vendor approvals, subscriptions, payouts, and delivery operations.</li>
  <li>Roles, permissions, languages, media, and site settings.</li>
  <li>Push broadcasting, newsletters, and an AI administration toolset.</li></ul></article>
</div>

<h3 class="heading-2">What ships in the package</h3>
<div class="callout-grid">
  <div class="callout"><strong>Storefront themes</strong><p>Nine themes on disk: <code>mono</code> (built in), plus <code>beauty</code>, <code>electronics</code>, <code>fashion</code>, <code>fullwidth</code>, <code>grocery</code>, <code>home</code>, <code>petshop</code>, and <code>sports</code>. Each is a self-contained package with its own views, assets, palette, and optional database tables.</p></div>
  <div class="callout"><strong>Mobile applications</strong><p>Two Flutter clients ship alongside: the customer app and the vendor app. Both talk to the same versioned API described in this document.</p></div>
  <div class="callout"><strong>Web installer</strong><p><code>public/install.php</code> is a self-contained wizard that creates the database, writes the environment file, creates the first administrator, and activates a theme. No Composer, Node, or shell access is required on the host.</p></div>
</div>

<h3 class="heading-2">The storefront, at a glance</h3>
<div class="screenshot-grid">
  <figure class="shot shot--wide"><button class="shot-button" type="button" data-lightbox="assets/storefront/storefront-home-desktop.jpg" data-caption="Storefront home page, desktop viewport"><img src="assets/storefront/storefront-home-desktop.jpg" alt="Storefront home page on a desktop viewport: announcement bar, category strip, hero slider and trust badges." loading="lazy"><span>Open capture</span></button><figcaption>Home / desktop</figcaption></figure>
  <figure class="shot"><button class="shot-button" type="button" data-lightbox="assets/storefront/storefront-home-mobile.jpg" data-caption="Storefront home page, mobile viewport"><img src="assets/storefront/storefront-home-mobile.jpg" alt="The same storefront home page on a mobile viewport." loading="lazy"><span>Open capture</span></button><figcaption>Home / mobile</figcaption></figure>
</div>

<h3 class="heading-2">Who this documentation is for</h3>
<p>This guide covers the web product: the storefront, the vendor panel, the
admin panel, and the backend services that support them. The two Flutter
applications have their own companion documents. Everything here is written
against the shipped source, so route names, table names, and permission keys
match what you will find in the package.</p>

<div class="api-url"><span>API PREFIX</span><code>https://your-domain.com/api/v1</code></div>
"""),

dict(
    id='architecture', group='Overview',
    title='Stack, panels, and how a request flows',
    html="""
<h3 class="heading-2">Technology stack</h3>
<table class="data-table">
<thead><tr><th>Layer</th><th>Choice</th><th>Notes</th></tr></thead>
<tbody>
<tr><td>Language</td><td>PHP <code>^8.3</code></td><td>Platform is pinned to <code>8.3.30</code>.</td></tr>
<tr><td>Framework</td><td>Laravel <code>^13.8</code></td><td>Blade templates, no SPA build step.</td></tr>
<tr><td>API auth</td><td>Laravel Sanctum <code>^4.3</code></td><td>Bearer personal access tokens.</td></tr>
<tr><td>Realtime chat</td><td>Ably <code>^1.1</code></td><td>Server-minted short-lived client tokens.</td></tr>
<tr><td>PDF invoices</td><td>dompdf <code>^3.1</code></td><td>Renders and emails invoice documents.</td></tr>
<tr><td>Machine translation</td><td>google-translate-php <code>^5.3</code></td><td>Backs the admin AI translation tools.</td></tr>
<tr><td>CSS</td><td>Tailwind CSS <code>^4.3</code></td><td>CSS-first config via an <code>@theme</code> block. No Vite, no bundler.</td></tr>
<tr><td>Databases</td><td>MySQL or SQLite</td><td>Both drivers are supported; MySQL is the production target.</td></tr>
</tbody></table>

<div class="callout callout--warn"><strong>There is no Vite pipeline.</strong>
<p>Assets are plain Blade, plain CSS compiled by the Tailwind CLI, and plain
JavaScript served from <code>public/js</code>. If you add a JavaScript entry
point, add the file to <code>public/js</code> and reference it directly; do
not look for <code>vite.config.js</code> or an <code>npm run dev</code> asset
server.</p></div>

<h3 class="heading-2">The three panels</h3>
<div class="workflow-columns">
  <article><h3>Storefront</h3><ul>
    <li>Public routes in <code>routes/web.php</code>.</li>
    <li>Views resolve through <code>ThemeServiceProvider</code>, which
        prepends the active theme's view path so theme templates win over the
        default ones.</li>
    <li>A theme that does not supply a view falls back to
        <code>resources/views</code> automatically.</li>
    <li>Uploaded media resolves through <code>PublicMedia::url()</code>.</li>
  </ul></article>
  <article><h3>Vendor panel</h3><ul>
    <li>Routes under <code>prefix('dashboard')</code> with
        <code>auth:vendor</code>, <code>vendor.verified</code>, and
        <code>vendor.approved</code>.</li>
    <li>Layout is <code>layouts/dashboard.blade.php</code>.</li>
    <li>Signed app-bridge routes let the Flutter vendor app open specific
        panel pages.</li>
  </ul></article>
  <article><h3>Admin panel</h3><ul>
    <li>Routes under <code>prefix('admin')</code> with <code>auth:admin</code>.</li>
    <li>Layout is <code>layouts/admin.blade.php</code> and owns the entire
        sidebar navigation map.</li>
    <li>Every page is additionally guarded by a
        <code>permission:</code> middleware key.</li>
  </ul></article>
</div>

<h3 class="heading-2">Request lifecycle</h3>
<p>The API stack prepends <code>ForceJsonResponse</code> and
<code>SetApiLocale</code>; the web stack appends <code>SetLocale</code>.
Successful API responses use a <code>{ success, data, meta }</code> envelope.
Errors are rendered by <code>App\\Support\\ApiException</code> into
<code>{ success: false, error: { message, code, fields } }</code>, so the
mobile clients only ever parse one shape.</p>

<p>Guest redirects are area aware: an unauthenticated <code>admin/*</code>
request lands on <code>admin.login</code>, a <code>vendor</code> or
<code>dashboard</code> request lands on <code>vendor.login</code>, and
everything else lands on the customer <code>login</code> route.</p>

<h3 class="heading-2">Custom middleware</h3>
<table class="data-table">
<thead><tr><th>Alias</th><th>Class</th><th>What it enforces</th></tr></thead>
<tbody>
<tr><td><code>permission</code></td><td><code>HasPermission</code></td><td>Admin permission check. Pipe-separated values mean "any of".</td></tr>
<tr><td><code>auth.optional</code></td><td><code>OptionalSanctumAuth</code></td><td>Resolves the user when a token is present but never rejects, so public catalog routes can resolve wishlist flags.</td></tr>
<tr><td><code>vendor.verified</code></td><td><code>EnsureVendorEmailVerified</code></td><td>Vendor email must be verified.</td></tr>
<tr><td><code>vendor.approved</code></td><td><code>EnsureVendorApproved</code></td><td>Vendor registration must be approved.</td></tr>
<tr><td><code>guest.checkout</code></td><td><code>EnsureGuestCheckoutAllowed</code></td><td>Honours the guest-checkout setting.</td></tr>
</tbody></table>
"""),

dict(
    id='installation', group='Overview',
    title='Installation on shared hosting and on a dev machine',
    html="""
<p>MONO installs two ways. The web installer is the supported path for shared
hosting, where you have a control panel but no shell. The Artisan path is for
developers and CI. The walkthrough below was captured on a cPanel account;
other control panels follow the same shape.</p>

<div class="callout"><strong>Before you start</strong>
<p>You need the release archive <code>mono-marketplace-installer.zip</code>
(built on your machine with <code>python tools/build_release.py</code> — it
already contains <code>vendor/</code>, the compiled CSS, and the public tree,
so the host needs no Composer, Node, or shell access), a cPanel or similar
hosting account with MySQL, and PHP 8.3 or newer. Every screenshot below is
clickable for a full-size view.</p></div>

<h3 class="heading-2">Part 1 — Create the database in cPanel</h3>
<ol class="walkthrough">
  <li><strong>Open the database manager.</strong>
    <p>In cPanel, scroll to the <strong>Databases</strong> section and open
    <strong>Manage My Databases</strong>.</p>
    <figure class="doc-figure">
      <button class="doc-shot-btn" type="button" data-lightbox="assets/installer/open-database-manager.png" data-caption="cPanel — Databases → Manage My Databases"><img class="doc-shot" src="assets/installer/open-database-manager.png" alt="cPanel home with the Databases section open and Manage My Databases highlighted." loading="lazy"></button>
      <figcaption>cPanel → Databases → Manage My Databases</figcaption>
    </figure></li>

  <li><strong>Create the database.</strong>
    <p>Under <strong>Create New Database</strong>, type a name after your
    account prefix and click <strong>Create Database</strong>. cPanel prepends
    the account prefix — <code>mono</code> becomes something like
    <code>clotcode_mono</code>. Note the full name; the installer will ask for
    it exactly.</p>
    <figure class="doc-figure">
      <button class="doc-shot-btn" type="button" data-lightbox="assets/installer/create-database.png" data-caption="Manage My Databases — Create New Database"><img class="doc-shot" src="assets/installer/create-database.png" alt="Create New Database form with a name entered after the account prefix and the Create Database button highlighted." loading="lazy"></button>
      <figcaption>Create New Database — note the prefixed name</figcaption>
    </figure></li>

  <li><strong>Create the database user.</strong>
    <p>Scroll to <strong>Database Users → Add New User</strong>, pick a
    username, and generate a strong password. Note the username and password
    too, then click <strong>Create User</strong>.</p>
    <figure class="doc-figure">
      <button class="doc-shot-btn" type="button" data-lightbox="assets/installer/create-database-user.png" data-caption="Database Users — Add New User"><img class="doc-shot" src="assets/installer/create-database-user.png" alt="Add New User form with username and password fields filled in and the Create User button highlighted." loading="lazy"></button>
      <figcaption>Database Users → Add New User → Create User</figcaption>
    </figure></li>

  <li><strong>Attach the user to the database.</strong>
    <p>In <strong>Add User To Database</strong>, select the user and the
    database you just created, and click <strong>Add</strong>.</p>
    <figure class="doc-figure">
      <button class="doc-shot-btn" type="button" data-lightbox="assets/installer/add-user-to-database.png" data-caption="Add User To Database — select both, then Add"><img class="doc-shot" src="assets/installer/add-user-to-database.png" alt="Add User To Database section with the new user and database selected in the dropdowns and the Add button highlighted." loading="lazy"></button>
      <figcaption>Add User To Database → Add</figcaption>
    </figure></li>

  <li><strong>Grant all privileges.</strong>
    <p>cPanel opens the privilege screen for that user/database pair. Tick
    <strong>ALL PRIVILEGES</strong>, then click <strong>Make Changes</strong>
    to save. The installer migrates and seeds through this user, so it needs
    full rights on this database.</p>
    <figure class="doc-figure">
      <button class="doc-shot-btn" type="button" data-lightbox="assets/installer/database-privileges.png" data-caption="Manage User Privileges — ALL PRIVILEGES → Make Changes"><img class="doc-shot" src="assets/installer/database-privileges.png" alt="Manage User Privileges screen with ALL PRIVILEGES ticked and the Make Changes button highlighted." loading="lazy"></button>
      <figcaption>ALL PRIVILEGES → Make Changes</figcaption>
    </figure></li>
</ol>

<h3 class="heading-2">Part 2 — Upload and extract the installer</h3>
<ol class="walkthrough">
  <li><strong>Open File Manager.</strong>
    <p>In cPanel, open <strong>Files → File Manager</strong> and enter the
    document root of the domain you are installing on — <code>public_html</code>
    for the primary domain, or the subfolder the domain points at.</p>
    <figure class="doc-figure">
      <button class="doc-shot-btn" type="button" data-lightbox="assets/installer/open-file-manager.png" data-caption="cPanel — Files → File Manager"><img class="doc-shot" src="assets/installer/open-file-manager.png" alt="cPanel home with the Files section open and File Manager highlighted." loading="lazy"></button>
      <figcaption>cPanel → Files → File Manager → public_html</figcaption>
    </figure></li>

  <li><strong>Upload the archive.</strong>
    <p>Click <strong>Upload</strong> and select
    <code>mono-marketplace-installer.zip</code>. Stay on the page until the
    progress bar reaches 100%.</p>
    <figure class="doc-figure">
      <button class="doc-shot-btn" type="button" data-lightbox="assets/installer/upload-installer-zip.png" data-caption="File Upload — mono-marketplace-installer.zip"><img class="doc-shot" src="assets/installer/upload-installer-zip.png" alt="cPanel File Upload page showing mono-marketplace-installer.zip uploading into public_html." loading="lazy"></button>
      <figcaption>Upload mono-marketplace-installer.zip</figcaption>
    </figure></li>

  <li><strong>Extract it in place.</strong>
    <p>Back in File Manager, select the zip, click <strong>Extract</strong>,
    keep the destination path <code>/public_html</code>, and click
    <strong>Extract Files</strong>. The archive expands into the application
    tree; delete the zip afterwards to reclaim the space.</p>
    <figure class="doc-figure">
      <button class="doc-shot-btn" type="button" data-lightbox="assets/installer/extract-installer-zip.png" data-caption="File Manager — Extract into /public_html"><img class="doc-shot" src="assets/installer/extract-installer-zip.png" alt="cPanel File Manager with the Extract dialog open, the destination path set to /public_html, and the Extract Files button highlighted." loading="lazy"></button>
      <figcaption>Extract into /public_html</figcaption>
    </figure></li>
</ol>

<h3 class="heading-2">Part 3 — Run the installer wizard</h3>
<p>Visit <code>https://your-domain.com/install.php</code>. If
<code>.env</code> is still missing, <code>public/index.php</code> also
redirects the storefront's first request there automatically. The wizard is
five steps and takes about a minute.</p>
<ol class="walkthrough">
  <li><strong>Welcome — server requirements.</strong>
    <p>The installer checks PHP 8.3+, every required extension, the presence
    of <code>vendor/</code>, and that <code>storage/</code>,
    <code>bootstrap/cache/</code>, and <code>.env</code> are writable. When
    each row reads Ready, continue to the database step.</p>
    <figure class="doc-figure">
      <button class="doc-shot-btn" type="button" data-lightbox="assets/installer/installer-welcome.png" data-caption="install.php — step 1 of 5, server requirements"><img class="doc-shot" src="assets/installer/installer-welcome.png" alt="MONO installer step 1 of 5, Welcome, listing the server requirements, each marked Ready, with the Continue to Database button highlighted." loading="lazy"></button>
      <figcaption>install.php — step 1 / 5 — server requirements</figcaption>
    </figure></li>

  <li><strong>Database connection.</strong>
    <p>Keep the type on <strong>MySQL / MariaDB</strong>, leave the host on
    <code>localhost</code> and the port on <code>3306</code> unless your host
    says otherwise, and enter the database name, username, and password from
    Part 1. <strong>Test connection &amp; create tables</strong> verifies the
    login, writes <code>.env</code>, and runs the migrations. SQLite is also
    accepted for small or staging installs.</p>
    <figure class="doc-figure">
      <button class="doc-shot-btn" type="button" data-lightbox="assets/installer/installer-database.png" data-caption="install.php — step 2 of 5, database connection"><img class="doc-shot" src="assets/installer/installer-database.png" alt="MONO installer step 2 of 5, Database, with MySQL selected and host, port, database name, username, and password filled in." loading="lazy"></button>
      <figcaption>Step 2 / 5 — database connection &amp; tables</figcaption>
    </figure></li>

  <li><strong>Site &amp; admin account.</strong>
    <p>The site URL is auto-detected — change it only if the store will be
    served from another address or a subfolder. Set the store name and
    tagline, then create the first administrator; the account is attached to
    the <code>super_admin</code> role automatically. Leave <em>Install the
    current catalog demo</em> ticked if you want starter products, categories,
    brands, vendors, and bundles to explore.</p>
    <figure class="doc-figure">
      <button class="doc-shot-btn" type="button" data-lightbox="assets/installer/installer-admin-account.png" data-caption="install.php — step 3 of 5, site & admin account"><img class="doc-shot" src="assets/installer/installer-admin-account.png" alt="MONO installer step 3 of 5, Site and Admin, with site URL, store name, tagline, admin name, email, password fields, and the demo catalog checkbox." loading="lazy"></button>
      <figcaption>Step 3 / 5 — site &amp; admin account</figcaption>
    </figure></li>

  <li><strong>Pick a theme.</strong>
    <p>Choose one of the nine storefront themes. The installer runs that
    theme's migrations and copies its assets. You can switch or add themes
    later in the admin panel under <strong>Appearance → Themes</strong>.</p>
    <figure class="doc-figure">
      <button class="doc-shot-btn" type="button" data-lightbox="assets/installer/installer-theme.png" data-caption="install.php — step 4 of 5, pick a theme"><img class="doc-shot" src="assets/installer/installer-theme.png" alt="MONO installer step 4 of 5, Theme, showing a grid of nine storefront themes with MONO selected." loading="lazy"></button>
      <figcaption>Step 4 / 5 — pick a theme</figcaption>
    </figure></li>

  <li><strong>Finish.</strong>
    <p>The installer writes <code>storage/app/installed.lock</code> and shows
    your admin login and URLs. <strong>Log in to the Admin Panel →</strong>
    signs you in with a one-time token that deletes itself on first use.</p>
    <figure class="doc-figure">
      <button class="doc-shot-btn" type="button" data-lightbox="assets/installer/installer-finish.png" data-caption="install.php — step 5 of 5, installation complete"><img class="doc-shot" src="assets/installer/installer-finish.png" alt="MONO installer step 5 of 5, Finish, showing Installation complete with the admin login, admin and storefront URLs, and the log in to the Admin Panel button." loading="lazy"></button>
      <figcaption>Step 5 / 5 — installation complete</figcaption>
    </figure></li>
</ol>

<div class="callout callout--warn"><strong>Two last things.</strong>
<p>Delete <code>public/install.php</code> from the server via File Manager —
until you do, anyone who can reach the URL can re-run configuration. And add
the scheduler to cron so background tasks (order and SMS queues, SMS-gateway
recovery) keep running: in cPanel open <strong>Cron Jobs</strong> and add a
job that runs every minute:</p>
<pre><code>* * * * * php /path/to/artisan schedule:run &gt;&gt; /dev/null 2&gt;&amp;1</code></pre>
</div>

<h3 class="heading-2">Host requirements</h3>
<div class="callout-grid">
  <div class="callout"><strong>Required extensions</strong><p><code>pdo_mysql</code> or <code>pdo_sqlite</code>, <code>mbstring</code>, <code>openssl</code>, <code>tokenizer</code>, <code>xml</code>, <code>ctype</code>, <code>json</code>, <code>fileinfo</code>.</p></div>
  <div class="callout"><strong>Not required</strong><p>Composer, Node, npm, and shell access are all unnecessary on the host. Everything the runtime needs is already in the release archive.</p></div>
  <div class="callout"><strong>Writable paths</strong><p><code>storage/</code>, <code>bootstrap/cache/</code>, and <code>public/storage</code> must be writable. <code>public/storage</code> is a symlink to <code>storage/app/public</code>, which is where every upload lands.</p></div>
</div>

<h3 class="heading-2">Developer install</h3>
<div class="build-commands">
  <div><span>01 / Install</span><code>composer install</code></div>
  <div><span>02 / Key</span><code>php artisan key:generate</code></div>
  <div><span>03 / Schema</span><code>php artisan migrate --seed</code></div>
  <div><span>04 / Storage link</span><code>php artisan storage:link</code></div>
  <div><span>05 / Serve</span><code>php artisan serve</code></div>
  <div><span>06 / CSS</span><code>npm run build:css</code></div>
</div>

<p>After <code>migrate --seed</code> the demo data creates an administrator at
<code>admin@mono.test</code> with the password <code>password</code>, a
customer at <code>jordan@example.com</code>, and eight vendors whose passwords
are also <code>password</code>. Change or remove all of these before the site
is reachable by anyone but you.</p>
"""),

dict(
    id='upgrading', group='Overview',
    title='Updates, scheduled jobs, and the queue worker',
    html="""
<h3 class="heading-2">Applying an update</h3>
<ol class="walkthrough">
  <li><strong>Back up first.</strong><p>Copy the database and the
  <code>storage/</code> directory. Uploads and the environment file both live
  outside version control.</p></li>
  <li><strong>Replace the code.</strong><p>Upload the new release archive and
  extract it over the existing files. Do not delete
  <code>storage/</code>, <code>.env</code>, or <code>public/storage</code>
  during extraction.</p></li>
  <li><strong>Migrate.</strong><p>Run <code>php artisan migrate</code>. Theme
  migrations are registered automatically by
  <code>ThemeServiceProvider</code>, so <code>migrate</code> picks up tables
  declared by the active theme.</p></li>
  <li><strong>Rebuild CSS if you customised it.</strong><p>Run
  <code>npm run build:css</code> only if you edited
  <code>resources/css/app.css</code> or a theme stylesheet.</p></li>
  <li><strong>Clear caches.</strong><p><code>php artisan config:clear</code>,
  <code>php artisan cache:clear</code>, and <code>php artisan view:clear</code>
  are enough after a migration run.</p></li>
</ol>

<div class="callout callout--warn"><strong>There is no in-app updater.</strong>
<p>MONO is updated by replacing files and migrating. It deliberately does not
phone home or self-modify, which is what makes it safe to run on a locked-down
shared host.</p></div>

<h3 class="heading-2">Scheduled jobs</h3>
<p>Background work is data-driven rather than hard-coded in
<code>routes/console.php</code>. The <code>scheduled_jobs</code> table holds
each job's key, Artisan command, frequency, and enabled flag, and
<code>ScheduledJobService</code> registers them with Laravel's scheduler at
boot. Admins edit the table at
<code>/admin/settings/scheduled-jobs</code> and can run any job on demand.</p>

<table class="data-table">
<thead><tr><th>Frequency</th><th>Seeded jobs</th></tr></thead>
<tbody>
<tr><td>Every minute</td><td><code>orders:cancel-expired</code>, <code>ai-credits:cancel-expired</code></td></tr>
<tr><td>Every five minutes</td><td><code>featured:expire</code></td></tr>
<tr><td>Daily</td><td><code>vendor-packages:notify-expiry</code>, <code>loyalty:expire-points</code>, <code>badges:expire-new</code></td></tr>
</tbody></table>

<p>For these to run, the host's cron must hit
<code>/&lt;path&gt;/artisan schedule:run</code> every minute. On shared hosting
that is usually a cron entry in the control panel rather than a real crontab.</p>

<div class="build-commands">
  <div><span>EVERY MINUTE</span><code>* * * * * cd /path/to/mono &amp;&amp; php artisan schedule:run &gt;&gt; /dev/null 2&gt;&amp;1</code></div>
</div>

<h3 class="heading-2">Queue worker</h3>
<p>Three jobs send mail or push notifications: newsletter campaigns, customer
push, and vendor push. A long newsletter campaign sets
<code>timeout = 1800</code> precisely because it chunks through subscribers in
a single worker run. If you leave notifications and newsletters enabled, run a
worker.</p>

<div class="build-commands">
  <div><span>QUEUE</span><code>php artisan queue:work --tries=2</code></div>
  <div><span>WINDOWS</span><code>queue-worker.bat</code></div>
</div>

<p>Without a worker the jobs simply sit in the <code>jobs</code> table. Orders,
payments, and the admin panel all continue to work; only asynchronous email
and push are delayed.</p>
"""),

# ============================================================== STOREFRONT
dict(
    id='storefront-themes', group='Storefront',
    title='Themes and the theme engine',
    html="""
<p>A theme is a folder under <code>themes/</code> that contains a
<code>theme.json</code> manifest. The filesystem is the source of truth: a
theme exists because its folder exists, and removing the folder removes it
from the admin panel.</p>

<p>Every theme below was activated live and captured from its home page at a
desktop viewport, so what you see is what each theme actually ships — hero,
palette, typography, and storefront sections.</p>

<div class="screenshot-grid themes-grid">
  <figure class="shot"><button class="shot-button" type="button" data-lightbox="assets/themes/theme-mono.jpg" data-caption="MONO theme — the built-in default storefront"><img src="assets/themes/theme-mono.jpg" alt="MONO theme storefront home page with a minimal black-and-white hero, category strip and featured products." loading="lazy"><span>Open capture</span></button><figcaption>MONO — built-in default</figcaption></figure>
  <figure class="shot"><button class="shot-button" type="button" data-lightbox="assets/themes/theme-beauty.jpg" data-caption="Beauty &amp; Wellness theme storefront"><img src="assets/themes/theme-beauty.jpg" alt="Beauty and Wellness theme home page with a rose-pink palette, serif display type and a soft hero." loading="lazy"><span>Open capture</span></button><figcaption>Beauty &amp; Wellness</figcaption></figure>
  <figure class="shot"><button class="shot-button" type="button" data-lightbox="assets/themes/theme-electronics.jpg" data-caption="Electronics theme storefront"><img src="assets/themes/theme-electronics.jpg" alt="Electronics theme home page with a blue tech palette and gadget-focused hero." loading="lazy"><span>Open capture</span></button><figcaption>Electronics</figcaption></figure>
  <figure class="shot"><button class="shot-button" type="button" data-lightbox="assets/themes/theme-fashion.jpg" data-caption="Fashion theme storefront"><img src="assets/themes/theme-fashion.jpg" alt="Fashion theme home page with an editorial boutique layout and arch-shaped category tiles." loading="lazy"><span>Open capture</span></button><figcaption>Fashion</figcaption></figure>
  <figure class="shot"><button class="shot-button" type="button" data-lightbox="assets/themes/theme-fullwidth.jpg" data-caption="Mono Edge theme storefront"><img src="assets/themes/theme-fullwidth.jpg" alt="Mono Edge theme home page with a full-width marketplace layout, hero slider and dense product grid." loading="lazy"><span>Open capture</span></button><figcaption>Mono Edge (fullwidth)</figcaption></figure>
  <figure class="shot"><button class="shot-button" type="button" data-lightbox="assets/themes/theme-grocery.jpg" data-caption="Grocery theme storefront"><img src="assets/themes/theme-grocery.jpg" alt="Grocery theme home page with a fresh green palette and pantry-focused categories." loading="lazy"><span>Open capture</span></button><figcaption>Grocery</figcaption></figure>
  <figure class="shot"><button class="shot-button" type="button" data-lightbox="assets/themes/theme-home.jpg" data-caption="Home &amp; Living theme storefront"><img src="assets/themes/theme-home.jpg" alt="Home and Living theme home page with warm amber tones and furniture categories." loading="lazy"><span>Open capture</span></button><figcaption>Home &amp; Living</figcaption></figure>
  <figure class="shot"><button class="shot-button" type="button" data-lightbox="assets/themes/theme-petshop.jpg" data-caption="Pet Shop theme storefront"><img src="assets/themes/theme-petshop.jpg" alt="Pet Shop theme home page with an orange palette and pet supply categories." loading="lazy"><span>Open capture</span></button><figcaption>Pet Shop</figcaption></figure>
  <figure class="shot"><button class="shot-button" type="button" data-lightbox="assets/themes/theme-sports.jpg" data-caption="Sports theme storefront"><img src="assets/themes/theme-sports.jpg" alt="Sports theme home page with a bold red palette and athletic gear hero." loading="lazy"><span>Open capture</span></button><figcaption>Sports</figcaption></figure>
</div>

<p>Switching themes is instant and reversible — the admin panel activates a
theme by writing one setting; no rebuild, no downtime. Captures above were
taken by activating each theme in turn on the same demo catalog.</p>

<table class="data-table">
<thead><tr><th>Slug</th><th>Name</th><th>Own tables</th></tr></thead>
<tbody>
<tr><td><code>mono</code></td><td>Mono (built in)</td><td>None. The manifest lives at <code>resources/theme/mono.json</code>, outside the removable tree.</td></tr>
<tr><td><code>beauty</code></td><td>Beauty &amp; Wellness</td><td>No extra tables.</td></tr>
<tr><td><code>electronics</code></td><td>Electronics</td><td>Yes, <code>electronics_features</code>.</td></tr>
<tr><td><code>fashion</code></td><td>Fashion</td><td>Yes, <code>fashion_looks</code>.</td></tr>
<tr><td><code>fullwidth</code></td><td>Mono Edge</td><td>No extra tables.</td></tr>
<tr><td><code>grocery</code></td><td>Grocery</td><td>Yes, <code>grocery_promos</code>.</td></tr>
<tr><td><code>home</code></td><td>Home &amp; Living</td><td>No extra tables.</td></tr>
<tr><td><code>petshop</code></td><td>Pet Shop</td><td>Yes, <code>petshop_banners</code>.</td></tr>
<tr><td><code>sports</code></td><td>Sports</td><td>Yes, <code>sports_banners</code>.</td></tr>
</tbody></table>

<div class="callout callout--warn"><strong><code>config/themes.php</code> is stale.</strong>
<p>That file still lists the original eight and omits <code>fullwidth</code>.
<code>ThemeManager</code> is the real source of truth; trust the
<code>themes/</code> directory, not the config file.</p></div>

<h3 class="heading-2">How view resolution works</h3>
<p><code>ThemeServiceProvider</code> registers
<code>resources/views/core</code> under the <code>core::</code> namespace and
calls <code>prependLocation()</code> with the active theme's views path. That
single call is what makes theming work: a theme view shadows the default view
of the same name, and anything the theme does not provide falls through to
the core views. The provider also registers the active theme's
<code>migrations/</code> path with the migrator.</p>

<h3 class="heading-2">Theme manifests</h3>
<p>Each <code>theme.json</code> declares the slug, name, description, version,
owned <code>tables[]</code>, a full <code>palette</code>, and an
<code>assets</code> block (CSS path, Google Fonts URL, body class). The palette
carries per-colour labels, defaults, and CSS variable names, shape radii, an
<code>isDark</code> flag, status colours for the seven order statuses, and logo
and invoice accents.</p>

<div class="callout callout--warn"><strong>Uninstalling deletes data.</strong>
<p>Removing a theme drops every table declared in its manifest. Take a
database backup first. This is why <code>mono</code> is deliberately kept
outside <code>themes/</code>: it cannot be uninstalled out from under the
site.</p></div>

<h3 class="heading-2">App themes are a separate axis</h3>
<p><code>AppThemeRegistry</code> controls the <em>mobile app's</em> visual
system, not the website. It offers <code>standard</code>,
<code>marketplace</code>, <code>aurora</code>, and <code>nova</code>, with
<code>fresh-market</code> as the default. The registry keeps an integer
version stamp in <code>active_app_theme_version</code> that devices diff
against so the apps know when to re-fetch. Colours always come from the
active storefront palette, so the app and the site stay visually consistent.</p>
"""),

dict(
    id='catalog', group='Storefront',
    title='Products, variations, and taxonomy',
    html="""
<h3 class="heading-2">Product model</h3>
<table class="data-table">
<thead><tr><th>Concern</th><th>Fields</th></tr></thead>
<tbody>
<tr><td>Identity</td><td><code>vendor_id</code>, <code>category_id</code>, <code>brand_id</code>, <code>name</code>, <code>slug</code></td></tr>
<tr><td>Pricing</td><td><code>price</code>, <code>old_price</code></td></tr>
<tr><td>Merchandising</td><td><code>badge</code> (new / sale / bestseller), <code>rating</code>, <code>reviews_count</code>, <code>is_featured</code>, <code>featured_until</code></td></tr>
<tr><td>Inventory</td><td><code>stock</code>, released on fulfilment by <code>OrderInventoryService</code></td></tr>
<tr><td>Digital goods</td><td><code>is_digital</code>, <code>digital_delivery_window</code>, plus assets, licence keys, and entitlements</td></tr>
<tr><td>Content</td><td><code>description</code>, <code>long_description</code>, <code>return_days</code>, <code>delivery_method</code></td></tr>
<tr><td>SEO and i18n</td><td><code>seo_title</code>, <code>seo_meta</code>, <code>translations</code>, <code>seo_translations</code></td></tr>
</tbody></table>

<h3 class="heading-2">Variations</h3>
<p>Variable products carry <code>product_variations</code> rows. Buyers pick
attributes on the storefront and the variation modal resolves the matching row:
it opens from any product card, lists one group per attribute, disables
unavailable combinations, and enables <em>Add to bag</em> only when the chosen
combination is in stock.</p>

<div class="screenshot-grid">
  <figure class="shot"><button class="shot-button" type="button" data-lightbox="assets/storefront/storefront-variation-modal.jpg" data-caption="Variation picker opened from a product card"><img src="assets/storefront/storefront-variation-modal.jpg" alt="Variation picker modal open over the shop grid, with the size group and quantity stepper." loading="lazy"><span>Open capture</span></button><figcaption>Variation picker</figcaption></figure>
  <figure class="shot"><button class="shot-button" type="button" data-lightbox="assets/storefront/storefront-variation-selected.jpg" data-caption="Variation selected — Add to bag enabled"><img src="assets/storefront/storefront-variation-selected.jpg" alt="Variation modal with the M size chip selected and the Add to bag button enabled." loading="lazy"><span>Open capture</span></button><figcaption>Variation selected</figcaption></figure>
</div>

<h3 class="heading-2">Shared taxonomy</h3>
<p>Categories, brands, and attributes are shared platform-wide but can also be
vendor-owned. Each carries <code>vendor_id</code> and an <code>is_global</code>
flag: vendors create their own, and an administrator can promote an entry to
global with the "make global" action. Categories are a tree via
<code>parent_id</code> and can require approval before they appear.</p>

<p>Attributes carry values in <code>attribute_values</code>. The seeded demo
set includes Size, Color, Storage, and Capacity.</p>

<h3 class="heading-2">Bundles</h3>
<p><code>ProductBundleService</code> validates and replaces a bundle's ordered
item list. Variable children can be pinned to a specific variation rather than
left open, and cancellation restocks every bundle line through
<code>OrderInventoryService</code>.</p>

<div class="callout"><strong>Digital products are first class.</strong>
<p>A digital product owns <code>digital_assets</code>, optional
<code>digital_license_keys</code>, and per-purchase
<code>digital_entitlements</code>. <code>DigitalDeliveryService</code> owns the
lifecycle: an entitlement starts <code>pending</code> on order,
becomes <code>active</code> on delivery, and is <code>revoked</code> on
cancellation or refund. Download limits and expiry windows are enforced
server-side.</p></div>
"""),

dict(
    id='cart-checkout', group='Storefront',
    title='Cart, coupons, tax, shipping, and order placement',
    html="""
<h3 class="heading-2">Cart</h3>
<p>Carts live in <code>carts</code> and <code>cart_items</code> and are shared
between the website and the mobile apps. <code>ShippingMeter</code> produces
the product-aware free-shipping progress data the cart drawer renders, and
<code>OrderInventoryService</code> is the only place stock is decremented or
restored.</p>

<h3 class="heading-2">Discounts</h3>
<table class="data-table">
<thead><tr><th>Table</th><th>Role</th></tr></thead>
<tbody>
<tr><td><code>coupons</code></td><td>Discount rules: type, value, minimum spend, maximum discount, usage limit and count, expiry, free-shipping flag, and scope.</td></tr>
<tr><td><code>coupon_customer</code></td><td>Per-customer redemption limits.</td></tr>
<tr><td><code>customer_vouchers</code></td><td>Vouchers issued to customers, including loyalty tier redemptions.</td></tr>
<tr><td><code>loyalty_redemption_tiers</code></td><td>Tier definitions: name, points cost, voucher value, minimum spend.</td></tr>
</tbody></table>
<p><code>VoucherService</code> decides which coupons are publishable as
vouchers and serialises the voucher cards the apps display.</p>

<h3 class="heading-2">Tax and shipping</h3>
<p><code>TaxService</code> is a country-and-state aware tax engine with tax
classes, rates, and priorities, so it behaves the way a WooCommerce store does.
Shipping is configured per method with a flat rate, a free-shipping threshold,
and a free-shipping zone. Both are managed from
<code>/admin/settings/shipping</code> and <code>/admin/settings/taxes</code>.</p>

<h3 class="heading-2">Order placement</h3>
<p><code>OrderPlacementService</code> is the single canonical path for placing
an order, used by both the website and the API. It revalidates, server-side,
everything the client submitted: order ownership, gateway availability, stock,
coupon validity, shipping cost, and tax. Totals are always recomputed on the
server; the client total is never trusted.</p>

<div class="callout callout--warn"><strong>Never trust a client total.</strong>
<p>That is the entire point of this service. If you add a checkout entry point,
route it through <code>OrderPlacementService</code> rather than writing
totals by hand.</p></div>

<p>Orders carry a human-readable <code>code</code> such as
<code>MN-98412</code>, a denormalised customer name and email for display, and
snapshot shipping details so historical invoices stay accurate after a customer
edits their address book.</p>

<figure class="doc-figure">
  <button class="doc-shot-btn" type="button" data-lightbox="assets/storefront/storefront-shop-desktop.jpg" data-caption="Shop — category filters and product grid, desktop"><img class="doc-shot" src="assets/storefront/storefront-shop-desktop.jpg" alt="Storefront shop page with a category filter sidebar, sorting controls and a product grid." loading="lazy"></button>
  <figcaption>Shop — filters and product grid, desktop</figcaption>
</figure>

<figure class="doc-figure">
  <button class="doc-shot-btn" type="button" data-lightbox="assets/storefront/storefront-product-desktop.jpg" data-caption="Product detail page, desktop"><img class="doc-shot" src="assets/storefront/storefront-product-desktop.jpg" alt="Storefront product detail page with a photo gallery, price, size picker and add to bag." loading="lazy"></button>
  <figcaption>Product detail — gallery, price, size picker</figcaption>
</figure>

<p>The same experience on a phone: the shop grid, the search overlay, and the
navigation drawer are all first-class mobile surfaces.</p>

<div class="screenshot-grid">
  <figure class="shot"><button class="shot-button" type="button" data-lightbox="assets/storefront/storefront-shop-mobile.jpg" data-caption="Shop page on a mobile viewport"><img src="assets/storefront/storefront-shop-mobile.jpg" alt="Shop page on a mobile viewport with a product grid and category chips." loading="lazy"><span>Open capture</span></button><figcaption>Shop / mobile</figcaption></figure>
  <figure class="shot"><button class="shot-button" type="button" data-lightbox="assets/storefront/storefront-mobile-search.jpg" data-caption="Search overlay open on mobile"><img src="assets/storefront/storefront-mobile-search.jpg" alt="Search overlay open over the storefront on a mobile viewport." loading="lazy"><span>Open capture</span></button><figcaption>Search overlay</figcaption></figure>
  <figure class="shot"><button class="shot-button" type="button" data-lightbox="assets/storefront/storefront-mobile-menu.jpg" data-caption="Mobile navigation drawer"><img src="assets/storefront/storefront-mobile-menu.jpg" alt="Mobile navigation drawer open over the home page." loading="lazy"><span>Open capture</span></button><figcaption>Mobile menu</figcaption></figure>
</div>
"""),

dict(
    id='payments', group='Storefront',
    title='Payment gateways',
    html="""
<p>Fourteen payment methods ship in the box: twelve online gateways plus cash
on delivery and bank transfer. They are defined as constants on
<code>PaymentGatewayService</code>:</p>

<div class="api-facts"><span><b>ONLINE</b> 12</span><span><b>OFFLINE</b> 2</span><span><b>TOTAL</b> 14</span><span><b>REFUNDABLE</b> 3</span></div>

<table class="data-table">
<thead><tr><th>Gateway</th><th>Key</th><th>Configuration fields</th></tr></thead>
<tbody>
<tr><td>Stripe</td><td><code>card</code></td><td>mode, publishable key, secret key</td></tr>
<tr><td>SSLCommerz</td><td><code>sslcommerz</code></td><td>mode, store id, store password, currency</td></tr>
<tr><td>PayPal</td><td><code>paypal</code></td><td>mode, client id, client secret, currency</td></tr>
<tr><td>Mollie</td><td><code>mollie</code></td><td>mode, API key, currency</td></tr>
<tr><td>Paystack</td><td><code>paystack</code></td><td>mode, secret key, currency</td></tr>
<tr><td>Flutterwave</td><td><code>flutterwave</code></td><td>mode, secret key, webhook hash, currency</td></tr>
<tr><td>Razorpay</td><td><code>razorpay</code></td><td>mode, key id, key secret, currency</td></tr>
<tr><td>Mercado Pago</td><td><code>mercadopago</code></td><td>mode, access token</td></tr>
<tr><td>MyFatoorah</td><td><code>myfatoorah</code></td><td>mode, API token</td></tr>
<tr><td>Xendit</td><td><code>xendit</code></td><td>mode, secret key</td></tr>
<tr><td>PhonePe</td><td><code>phonepe</code></td><td>mode, merchant id, salt key, salt index</td></tr>
<tr><td>Midtrans</td><td><code>midtrans</code></td><td>mode, server key</td></tr>
<tr><td>Bank transfer</td><td><code>bank_transfer</code></td><td>label, description, instructions, and a list of accounts (bank name, account name, account number)</td></tr>
<tr><td>Cash on delivery</td><td><code>cod</code></td><td>label, description, instructions, extra fee</td></tr>
</tbody></table>

<div class="callout"><strong><code>card</code> means Stripe.</strong>
<p>The internal key is <code>card</code> for historical reasons.
<code>normalize()</code> maps <code>stripe</code> to <code>card</code>, and
<code>configKey()</code> maps <code>card</code> back to <code>stripe</code> for
settings storage. Use <code>card</code> in code and <code>stripe</code> in the
settings table.</p></div>

<h3 class="heading-2">Configuration and availability</h3>
<p>Credentials are stored in the <code>settings</code> table under
<code>gw_&lt;gateway&gt;_…</code> keys and read through
<code>Setting::gateway()</code>. They are deliberately not in
<code>.env</code>, so an operator can rotate a key from the admin panel
without touching the server. A gateway is only offered at checkout when it is
enabled <em>and</em> every required credential is filled, as decided by
<code>PaymentGatewayService::isConfigured()</code>.</p>

<p>Admins configure all of this at
<code>/admin/settings/payment-gateways</code>.</p>

<h3 class="heading-2">Where the code lives</h3>
<div class="workflow-columns">
  <article><h3>Order payments</h3><p><code>CheckoutController</code> holds a
  <code>pay*</code> and an <code>initiate*</code> pair per gateway, plus
  <code>paymentSuccess</code>, <code>paymentCancel</code>,
  <code>paymentFail</code>, and the
  <code>paymentIpn</code> webhook receiver.</p></article>
  <article><h3>Everything else</h3><p><code>OnlineGatewayPaymentService</code>
  handles non-order payables: vendor package subscriptions, featured product
  promotions, and wallet top-ups. It exposes one
  <code>launch()</code> and one <code>verify()</code> for all twelve
  gateways.</p></article>
</div>

<div class="callout callout--warn"><strong>Raw cURL, no SDKs.</strong>
<p>Gateway calls are hand-rolled cURL requests in
<code>OnlineGatewayPaymentService</code>. There is no vendor SDK in
<code>composer.json</code>, which keeps the install light but means signature
verification is your responsibility when you add a gateway.</p></div>

<h3 class="heading-2">Scope limits worth knowing</h3>
<ul>
  <li>Vendor-facing payments are restricted to
      <code>VENDOR_ONLINE_METHODS</code>: Stripe, SSLCommerz, and PayPal only.</li>
  <li>Wallet top-ups accept all twelve online gateways, but never
      <code>wallet</code> or <code>bank_transfer</code>.</li>
  <li>Only three gateways support refunds: Stripe, PayPal, and SSLCommerz.
      <code>refundStripe</code>, <code>refundPaypal</code>, and
      <code>refundSslCommerz</code> live in the admin controller.</li>
</ul>
"""),

dict(
    id='customer-account', group='Storefront',
    title='Customer accounts, loyalty, wallet, and digital downloads',
    html="""
<h3 class="heading-2">Accounts</h3>
<p>Customers register with email and password or sign in with Google. The
Google client id is served from the API so the apps and the site share one
configuration. Password recovery is an OTP flow: request, verify, then reset.
Addresses live in a per-customer address book.</p>

<figure class="doc-figure">
  <button class="doc-shot-btn" type="button" data-lightbox="assets/storefront/storefront-login-desktop.jpg" data-caption="Customer sign-in page"><img class="doc-shot" src="assets/storefront/storefront-login-desktop.jpg" alt="Storefront customer sign-in page with email and password fields." loading="lazy"></button>
  <figcaption>Customer sign-in</figcaption>
</figure>

<h3 class="heading-2">Loyalty</h3>
<p><code>LoyaltyService</code> earns points on delivered and paid orders, lets
customers redeem tiers as vouchers, and expires stale balances. Every movement
is a row in <code>loyalty_transactions</code> with its type, points, linked
order or coupon, description, and expiry, so a balance is always auditable.</p>
<p>Administrators configure earning rules at <code>/admin/loyalty</code> and
can adjust any customer's balance by hand with a recorded reason.</p>

<h3 class="heading-2">Wallet</h3>
<table class="data-table">
<thead><tr><th>Concern</th><th>Implementation</th></tr></thead>
<tbody>
<tr><td>Balance</td><td><code>wallets</code>, one per customer.</td></tr>
<tr><td>Ledger</td><td><code>wallet_transactions</code> with type, amount, status, reference, method, description, the acting admin, and free-form metadata.</td></tr>
<tr><td>Top-ups</td><td>Pending by default; an administrator approves or rejects before the balance moves.</td></tr>
<tr><td>Manual adjustment</td><td>Administrators credit or debit any wallet from <code>/admin/wallets</code>.</td></tr>
</tbody></table>

<p>The <em>use it or lose it</em> rule is deliberate: a pending top-up that is
never approved is reversed rather than left dangling.</p>

<h3 class="heading-2">Digital library</h3>
<p>Purchased digital goods appear in the customer's library as
<code>digital_entitlements</code> with a download count, a download limit, and
an expiry. File delivery uses a signed URL with a thirty-minute expiry, and
each download is written to <code>digital_download_logs</code>.</p>

<div class="callout callout--warn"><strong>Signed URLs are not access control.</strong>
<p>A signed URL proves the link was minted by this server; it does not prove
who is asking. Entitlement access is checked when the link is minted, and the
file route must verify the caller before streaming. See the launch checklist
before going live.</p></div>
"""),

dict(
    id='storefront-content', group='Storefront',
    title='Pages, blog, menus, media, and the page builder',
    html="""
<h3 class="heading-2">Pages</h3>
<p>Built-in pages (home, about, contact, FAQ, privacy, terms) are edited at
<code>/admin/pages/&lt;slug&gt;/edit</code>. Additional pages are created with
the visual custom page builder at <code>/admin/pages/custom</code>, so
non-technical staff can compose landing pages without touching Blade.</p>

<p>The homepage hero is a separate editor at <code>/admin/hero</code>.
<code>HomePageContent</code> and <code>HomePageSchema</code> make it
theme-aware: each theme declares which content keys exist and what fields they
accept, so switching themes does not strand a half-configured homepage.</p>

<h3 class="heading-2">Menus</h3>
<p><code>MenuService</code> reads and writes the header and footer navigation
trees at <code>/admin/pages/menus</code>. Menus are nestable, and the reset
action restores the theme's shipped default rather than leaving an empty
menu.</p>

<h3 class="heading-2">Blog</h3>
<p>Posts are managed at <code>/admin/blog</code> with draft and publish state,
cover imagery, categories, and bulk actions. Post content goes through the same
translation pipeline as products and pages.</p>

<h3 class="heading-2">Media library</h3>
<p><code>MediaService</code> backs a shared library at
<code>/admin/media</code>, with upload, delete, and bulk delete. Uploads are
written under <code>storage/app/public</code> and served through
<code>PublicMedia::url()</code>.</p>

<p>Upload roots are enumerated by <code>BackfillMedia</code> and cover
products, categories, brands, blog, branding, customers, vendors, admins, and
AI output. The library is isolated per owner where it matters: a vendor sees
their own media, an administrator sees everything.</p>

<div class="callout callout--warn"><strong>Validate uploads server-side.</strong>
<p>Do not trust the client extension or MIME type. Store uploads outside the
document root or with a fixed safe extension, and never let an upload land on
a path the web server will execute.</p></div>

<h3 class="heading-2">Cookie consent</h3>
<p>The consent banner is configured at <code>/admin/settings/cookie</code> and
rendered by the shared layout partial, so it appears on every theme without
per-theme work.</p>
"""),

dict(
    id='localization', group='Storefront',
    title='Languages, RTL, and the translation editor',
    html="""
<p>MONO ships English, Arabic, and Bengali. Arabic is a full right-to-left
experience, not a mirrored stylesheet: layouts, the admin and vendor panels,
and the storefront all flip, and <code>PanelRtlLocalizationTest</code> guards
that behaviour.</p>

<h3 class="heading-2">Two independent defaults</h3>
<p>This is the detail that trips people up. Each language has a
<em>web</em> default and a separate <em>mobile</em> default, stored as
<code>default</code> and <code>default_mobile</code>. Setting English as the
web default does not make English the app default. Admins toggle each
independently at <code>/admin/languages</code>.</p>

<table class="data-table">
<thead><tr><th>Capability</th><th>Where</th></tr></thead>
<tbody>
<tr><td>Enable or disable a language</td><td><code>/admin/languages</code></td></tr>
<tr><td>Set the web default</td><td><code>/admin/languages</code></td></tr>
<tr><td>Set the mobile default</td><td><code>/admin/languages</code>, the mobile toggle</td></tr>
<tr><td>Edit translations</td><td><code>/admin/languages/&lt;language&gt;/translations</code></td></tr>
<tr><td>Switch locale, signed in</td><td><code>/locale/&lt;code&gt;</code>, <code>/admin/locale/&lt;code&gt;</code>, <code>/vendor/locale/&lt;code&gt;</code></td></tr>
</tbody></table>

<h3 class="heading-2">Where strings live</h3>
<div class="workflow-columns">
  <article><h3>Interface strings</h3><p>PHP translation files under
  <code>lang/en</code>, <code>lang/ar</code>, and <code>lang/bn</code>, with
  JSON files for the long-tail strings.</p></article>
  <article><h3>Mobile strings</h3><p>Dedicated <code>lang/mobile-en</code> and
  <code>lang/mobile-ar</code> namespaces, served to the apps from the
  <code>/translations/{code}</code> API endpoint.</p></article>
</div>

<h3 class="heading-2">Content translation</h3>
<p>Products, categories, pages, and posts all carry a <code>translations</code>
column, with a separate <code>seo_translations</code> on products so metadata
can be translated independently of body copy. Bulk translation runs through
<code>AiTranslationService</code>, which chunks long fields and keeps every
field that succeeded, returning the list of anything it had to skip rather
than failing the whole record.</p>
"""),

# ============================================================ ADMIN PANEL
dict(
    id='admin-dashboard', group='Admin panel',
    title='Dashboard and admin navigation',
    html="""
<p>The admin panel is served from <code>/admin</code> behind
<code>auth:admin</code>. The sidebar is defined as PHP arrays in
<code>resources/views/layouts/admin.blade.php</code> and filtered by
permission, so an administrator only ever sees the modules they can actually
use. The same permission keys guard the routes, which means the menu is not
the security boundary — the middleware is.</p>

<h3 class="heading-2">Navigation groups</h3>
<table class="data-table">
<thead><tr><th>Group</th><th>Modules</th></tr></thead>
<tbody>
<tr><td>Overview</td><td>Dashboard</td></tr>
<tr><td>Commerce</td><td>Orders, Invoices, Coupons, Loyalty, Reviews</td></tr>
<tr><td>Notification</td><td>Push notifications, Newsletter, Promos</td></tr>
<tr><td>Customers</td><td>Customers</td></tr>
<tr><td>Marketplace</td><td>Vendors, Delivery pickup, Applications</td></tr>
<tr><td>Content</td><td>Pages, Blog, Media</td></tr>
<tr><td>Communication</td><td>Messages, Inbox</td></tr>
<tr><td>Administration</td><td>Administrators, Languages</td></tr>
<tr><td>Themes &amp; appearance</td><td>Themes</td></tr>
<tr><td>Settings</td><td>Settings</td></tr>
</tbody></table>

<h3 class="heading-2">Dashboard</h3>
<p>The landing page shows revenue, order, vendor, and customer totals each with
a thirty-day delta, a revenue chart, order status counts, the six most recent
orders, the five most recent pending vendor applications, and the five top
vendors. Every figure is computed from current rows rather than a cached
summary, so it cannot drift.</p>

<h3 class="heading-2">Global admin search</h3>
<p><code>/admin/search</code> is a JSON endpoint that searches a fixed index of
roughly forty admin pages plus records, so an operator can jump straight to a
setting or an order from anywhere in the panel.</p>

<h3 class="heading-2">Your own profile</h3>
<p><code>/admin/profile</code> edits your name, email, avatar, and password.
It is deliberately outside every permission gate: changing your own password
must never depend on a role assignment that someone else controls.</p>
"""),

dict(
    id='admin-access', group='Admin panel',
    title='Administrators, roles, and the permission system',
    html="""
<p>There is no admin self-registration. The first account is created by the
installer; every account after that is created by another administrator at
<code>/admin/administrators</code>. Administrators authenticate against the
<code>admin</code> guard and the <code>App\\Models\\Admin</code> model, which is
entirely separate from customers and vendors.</p>

<h3 class="heading-2">How permissions work</h3>
<p>Roles and permissions are hand-rolled, not Spatie. Five tables carry it:
<code>roles</code>, <code>permissions</code>, the <code>role_permission</code>
pivot, the <code>admin_role</code> pivot, and <code>admins</code>. A role
carries an <code>is_super</code> flag, and
<code>Admin::hasPermission()</code> returns true unconditionally for a super
administrator.</p>

<p>Routes declare a permission through the <code>permission:</code> middleware.
Pipe-separated values mean "any of", so
<code>permission:products.manage|blogs.manage|pages.manage</code> grants access
to any one of the three.</p>

<h3 class="heading-2">Seeded roles</h3>
<table class="data-table">
<thead><tr><th>Role</th><th>Super</th><th>Access</th></tr></thead>
<tbody>
<tr><td><code>super_admin</code></td><td>Yes</td><td>Everything, plus the bypass in <code>hasPermission()</code>.</td></tr>
<tr><td><code>administrator</code></td><td>No</td><td>All 32 permissions. Effectively identical day to day; it simply cannot grant itself new ones by virtue of existing.</td></tr>
<tr><td><code>editor</code></td><td>No</td><td><code>dashboard.view</code>, <code>orders.view</code>, <code>coupons.manage</code>, <code>reviews.manage</code>, <code>products.manage</code>, <code>customers.manage</code>.</td></tr>
</tbody></table>

<p>Administrators and roles are managed at
<code>/admin/administrators</code> and <code>/admin/roles</code>, guarded by
<code>admins.manage</code> and <code>roles.manage</code>.</p>

<h3 class="heading-2">The thirty-two permissions</h3>
<table class="data-table">
<thead><tr><th>Group</th><th>Permissions</th></tr></thead>
<tbody>
<tr><td>Overview</td><td><code>dashboard.view</code></td></tr>
<tr><td>Commerce</td><td><code>orders.view</code>, <code>coupons.manage</code>, <code>loyalty.manage</code>, <code>notifications.manage</code>, <code>promos.manage</code>, <code>reviews.manage</code>, <code>products.manage</code>, <code>customers.manage</code>, <code>wallets.manage</code></td></tr>
<tr><td>Marketplace</td><td><code>vendors.manage</code>, <code>vendors.impersonate</code>, <code>registrations.manage</code>, <code>packages.manage</code>, <code>delivery.settings.manage</code>, <code>applications.manage</code>, <code>payouts.manage</code>, <code>delivery.manage</code></td></tr>
<tr><td>Administration</td><td><code>messages.manage</code>, <code>languages.manage</code>, <code>themes.manage</code>, <code>shipping.manage</code>, <code>taxes.manage</code>, <code>locations.manage</code>, <code>payments.manage</code>, <code>settings.manage</code>, <code>blogs.manage</code>, <code>pages.manage</code>, <code>media.manage</code>, <code>roles.manage</code>, <code>admins.manage</code></td></tr>
</tbody></table>

<div class="callout callout--warn"><strong>Impersonation is a separate grant.</strong>
<p><code>vendors.impersonate</code> is deliberately not bundled into
<code>vendors.manage</code>. "Login as vendor" signs you in as a seller with
their full session, so it should be held by as few people as possible and
revoked when someone leaves.</p></div>
"""),

dict(
    id='admin-orders', group='Admin panel',
    title='Orders, invoices, and refunds',
    html="""
<p>Everything in the commerce group sits behind <code>orders.view</code>. The
order list filters by status, including the <code>returned</code> state, and
the detail page is the hub for everything about a purchase.</p>

<h3 class="heading-2">Order actions</h3>
<table class="data-table">
<thead><tr><th>Action</th><th>Route</th><th>Effect</th></tr></thead>
<tbody>
<tr><td>Create</td><td><code>POST /admin/orders</code></td><td>Manual order, with product and customer search endpoints behind it.</td></tr>
<tr><td>Change status</td><td><code>PATCH /admin/orders/{order}/status</code></td><td>Drives customer notifications and loyalty accrual.</td></tr>
<tr><td>Change payment</td><td><code>PATCH /admin/orders/{order}/payment</code></td><td>Status, method, and reference.</td></tr>
<tr><td>Generate invoice</td><td><code>POST /admin/orders/{order}/invoice</code></td><td>Renders a PDF through dompdf.</td></tr>
<tr><td>Email invoice</td><td><code>POST /admin/orders/{order}/invoice/send</code></td><td>Sends the rendered document.</td></tr>
<tr><td>Delete</td><td><code>DELETE /admin/orders/{order}</code></td><td>Single, or bulk via <code>bulk-destroy</code>.</td></tr>
</tbody></table>

<h3 class="heading-2">Invoices</h3>
<p><code>InvoiceService</code> issues numbered invoices and is idempotent per
(kind, trigger, reference), so a repeated trigger cannot produce a duplicate
document. Each invoice stores its number, sequence, fiscal year, kind, trigger,
bill-to details, a line breakdown, the company block as a JSON snapshot, the
generated PDF path, and its email delivery status and error.</p>

<p>Triggers are configurable at <code>/admin/settings/invoices</code>: order
placed, paid, delivered, status change, refund, wallet adjustment, package
purchase, and featured promotion. The number prefix, tax ID, and footer are set
in the same place.</p>

<div class="callout"><strong>One active invoice per order.</strong>
<p>Regenerating supersedes rather than stacks, and the invoice list at
<code>/admin/invoices</code> shows the current document for each order plus
the full history of downloads and re-sends.</p></div>

<h3 class="heading-2">Refunds</h3>
<p>Refunds are supported for three gateways only: Stripe, PayPal, and
SSLCommerz. The admin controller exposes <code>refundStripe</code>,
<code>refundPaypal</code>, and <code>refundSslCommerz</code>. There is no
generic refund path, because a generic path would be a generic way to lose
money.</p>
"""),

dict(
    id='admin-catalog', group='Admin panel',
    title='Catalog administration',
    html="""
<p>The whole catalog block shares one permission,
<code>products.manage</code>. That is a deliberate simplification: a catalog
that a role can add to but not moderate is worse than one it cannot touch at
all.</p>

<div class="service-grid">
  <article class="service-card"><span>PRODUCTS</span><h3>Listing and editing</h3>
  <ul><li>Create and edit products with digital assets, variations, SEO, and
  per-field translations.</li>
  <li>Bulk and single delete.</li>
  <li>Digital assets, removed files, and bulk licence keys are handled by
  <code>DigitalProductService</code>, shared with the vendor form.</li></ul></article>

  <article class="service-card service-card--teal"><span>BUNDLES</span><h3>Bundled sets</h3>
  <ul><li>Create and edit bundles at <code>/admin/product-bundles</code>.</li>
  <li>Candidate lookup for choosing line items.</li>
  <li>Variable children can be pinned to a specific variation.</li>
  <li>Cancellation restocks every line.</li></ul></article>

  <article class="service-card service-card--amber"><span>FEATURED</span><h3>Paid promotion</h3>
  <ul><li>Feature or unfeature any product by hand.</li>
  <li>Approve or reject vendor featured-placement requests.</li>
  <li>Define and price the featured packages themselves.</li>
  <li><code>featured:expire</code> clears lapsed placements
  automatically.</li></ul></article>
</div>

<h3 class="heading-2">Taxonomy approval</h3>
<p>Vendors create their own categories, brands, and attributes. Those entries
are pending until an administrator acts on them:</p>
<ul>
  <li>Categories are a tree via <code>parent_id</code> and are approved or
      rejected at <code>/admin/categories</code>.</li>
  <li>Brands and attributes can be promoted to global with "make global",
      which makes them available to every vendor.</li>
  <li>Every list view has a JSON search endpoint, which is what the pickers in
      the product forms call.</li>
</ul>

<h3 class="heading-2">Review moderation</h3>
<p>Reviews are managed at <code>/admin/reviews</code> with approve, reject,
status change, and bulk delete. <code>ProductReviewService</code> resolves who
is allowed to review what from the review settings, so the eligibility rule is
one decision rather than one per entry point.</p>
"""),

dict(
    id='admin-customers', group='Admin panel',
    title='Customers, wallets, coupons, and loyalty',
    html="""
<div class="service-grid">
  <article class="service-card"><span><code>customers.manage</code></span><h3>Customer accounts</h3>
  <ul><li>List, create, edit, and delete customer accounts.</li>
  <li>Bulk delete for cleanup.</li>
  <li>Search powers the manual-order customer picker.</li></ul></article>

  <article class="service-card service-card--teal"><span><code>wallets.manage</code></span><h3>Wallets</h3>
  <ul><li>Wallet list, single wallet detail, and the full transaction ledger.</li>
  <li>Pending top-ups queue for approval or rejection.</li>
  <li>Manual credit and debit with an attributed administrator.</li></ul></article>

  <article class="service-card service-card--amber"><span><code>coupons.manage</code> · <code>loyalty.manage</code></span><h3>Discounts and points</h3>
  <ul><li>Coupon CRUD, bulk delete, and scoped target search.</li>
  <li>Loyalty settings and redemption tier CRUD.</li>
  <li>Manual point adjustment with a customer search.</li></ul></article>
</div>

<h3 class="heading-2">Wallet approval flow</h3>
<ol class="walkthrough">
  <li><strong>Customer requests a top-up.</strong>
    <p>The request is written to <code>wallet_transactions</code> as pending.
    Money has not moved and the balance has not changed.</p></li>
  <li><strong>It appears in the admin queue.</strong>
    <p><code>/admin/wallets/pending</code> lists every outstanding request with
    its method, reference, and amount.</p></li>
  <li><strong>An administrator approves or rejects.</strong>
    <p>Approval credits the wallet and records the administrator. Rejection
    leaves the balance untouched. Neither is silent: both are ledger rows.</p></li>
</ol>

<p>Unapproved requests that expire are reversed rather than left open, which
is why a pending top-up never becomes a surprise balance later.</p>

<div class="callout callout--warn"><strong>Wallet writes are auditable by design.</strong>
<p>Every transaction row carries the acting <code>admin_id</code> when a person
caused it, plus a reference, method, and free-form metadata. If you add a
balance path, populate all four.</p></div>
"""),

dict(
    id='admin-marketplace', group='Admin panel',
    title='Vendors, packages, settlements, and withdrawals',
    html="""
<p>This is the largest group in the admin panel, and it is split across three
permissions so that approving a seller, selling them a plan, and paying them
are three separate decisions.</p>

<h3 class="heading-2">Getting vendors on the platform</h3>
<table class="data-table">
<thead><tr><th>Surface</th><th>Route</th><th>Permission</th><th>What it does</th></tr></thead>
<tbody>
<tr><td>Applications</td><td><code>/admin/applications</code></td><td><code>applications.manage</code></td><td>Submissions from the public "become a vendor" form, with per-item and bulk status actions.</td></tr>
<tr><td>Registrations</td><td><code>/admin/vendors/registrations</code></td><td><code>registrations.manage</code></td><td>Approval workflow with a configurable approval mode and its own settings page.</td></tr>
<tr><td>Vendors</td><td><code>/admin/vendors</code></td><td><code>vendors.manage</code></td><td>CRUD, verify toggle, suspend toggle, bulk delete.</td></tr>
<tr><td>Impersonation</td><td><code>POST /admin/vendors/{vendor}/impersonate</code></td><td><code>vendors.impersonate</code></td><td>Opens a full vendor session as that seller.</td></tr>
<tr><td>Store FAQs</td><td><code>/admin/faqs</code></td><td><code>vendors.manage</code></td><td>Per-store FAQs, with translations.</td></tr>
</tbody></table>

<p>Verification, suspension, and approval are independent states. A verified
vendor can still be suspended, and suspending one does not delete their
catalog.</p>

<h3 class="heading-2">Subscription packages</h3>
<p>Vendors buy plans. A <code>vendor_packages</code> row carries price,
duration, a benefits array, and either a global commission or a per-package
commission percentage and fixed amount. <code>VendorBillingService</code> owns
the maths, and subscriptions snapshot price, duration, and commission at the
moment of purchase so a later plan edit cannot rewrite history.</p>

<div class="workflow-columns">
  <article><h3>Lifecycle</h3><ul>
    <li>Requested, then approved, rejected, or cancelled by an administrator.</li>
    <li>Payment status tracked separately from subscription status.</li>
    <li><code>vendor-packages:notify-expiry</code> warns vendors before a plan
    lapses.</li></ul></article>
  <article><h3>Settlement lines</h3><ul>
    <li>One line per vendor and subscription.</li>
    <li>Gross, discount, commission, vendor earning, admin earning.</li>
    <li>Refund columns so a reversed commission stays visible instead of
    vanishing.</li></ul></article>
</div>

<h3 class="heading-2">Money out</h3>
<ul>
  <li><strong>Settlements</strong> at <code>/admin/vendors/settlements</code>
      show the full ledger: gross, discount, commission, vendor earning, and
      admin earning per line.</li>
  <li><strong>Withdrawal requests</strong> at
      <code>/admin/vendors/withdrawals</code> are approved or rejected; paid and
      rejected history is kept separately at
      <code>/admin/vendors/withdrawals/history</code>.</li>
  <li><strong>Global presets</strong> at
      <code>/admin/vendors/withdrawal-presets</code> define the supported
      methods (bank transfer, PayPal, bKash, and so on).</li>
  <li><strong>Per-vendor accounts</strong> at
      <code>/admin/vendors/{vendor}/withdrawal-methods</code> hold the payout
      destination for that seller.</li>
</ul>

<div class="callout callout--warn"><strong>Route ordering matters here.</strong>
<p>The payouts group must stay above the vendors group in
<code>routes/web.php</code>. The static <code>withdrawal-presets</code> path has
to match before the <code>/vendors/{vendor}</code> wildcard swallows it. If you
reorder those groups, that page will 404.</p></div>

<h3 class="heading-2">AI credit packs</h3>
<p>Sellors can buy token packs for the AI suite. Packs are defined at
<code>/admin/vendors/ai-packs</code>, purchases are approved or rejected, and a
pack can also be granted directly to a vendor. <code>AiCreditPurchaseObserver</code>
fires the "credits added" notification when a purchase becomes active from
<em>any</em> flow, and de-duplicates it against the explicit notification call
so sellers are not told twice.</p>
"""),

dict(
    id='admin-delivery', group='Admin panel',
    title='Delivery operations',
    html="""
<p>Delivery covers the physical path from a vendor's shelf to a customer's
door. It is split into operations and configuration, because the people who run
shipments are rarely the people who set courier contracts.</p>

<h3 class="heading-2">Operations, behind <code>delivery.manage</code></h3>
<table class="data-table">
<thead><tr><th>Surface</th><th>Route</th><th>What it does</th></tr></thead>
<tbody>
<tr><td>Pickup requests</td><td><code>/admin/delivery/pickup-requests</code></td><td>Vendor to warehouse pickups.</td></tr>
<tr><td>Drop-off requests</td><td><code>/admin/delivery/dropoff-requests</code></td><td>Warehouse to customer drop-offs.</td></tr>
<tr><td>Request lifecycle</td><td><code>POST /admin/delivery/requests/{id}/…</code></td><td>Approve, reject, schedule, assign personnel, change status, add a note, set the warehouse.</td></tr>
<tr><td>Shipments</td><td><code>/admin/delivery/shipments</code></td><td>Outbound shipments with courier, tracking number, and tracking URL.</td></tr>
<tr><td>Tracking</td><td><code>/admin/delivery/tracking</code></td><td>One merged timeline per order.</td></tr>
</tbody></table>

<p>Every state change on a request is written to
<code>delivery_request_events</code>, so the timeline is a record rather than a
reconstruction. <code>TrackingService</code> merges request events and shipment
events into the single per-order timeline that customers and vendors both see.</p>

<div class="callout"><strong>Order status is synced conservatively.</strong>
<p><code>ShipmentService</code> moves the parent order forward only when the
evidence is unambiguous. It will not downgrade an order to match a lagging
shipment, because a late courier scan should never tell a customer their
delivered order is processing again.</p></div>

<h3 class="heading-2">Configuration, behind <code>delivery.settings.manage</code></h3>
<div class="callout-grid">
  <div class="callout"><strong>Delivery personnel</strong><p>CRUD for delivery staff at <code>/admin/delivery/personnel</code>, assignable to any request.</p></div>
  <div class="callout"><strong>Warehouses and pickup points</strong><p><code>/admin/delivery/locations</code>, created, updated, and deleted.</p></div>
  <div class="callout"><strong>Couriers</strong><p><code>/admin/delivery/couriers</code>, the courier partners available when creating a shipment.</p></div>
  <div class="callout"><strong>Feature flags</strong><p><code>/admin/delivery/settings</code> via <code>DeliverySettings</code>, including the <code>delivery_notify_*</code> switches that gate vendor, admin, and customer notifications.</p></div>
</div>

<p><code>DeliveryService</code> is the single source of validation shared by the
vendor panel, the admin panel, and the API, so a request created from any of
the three is checked the same way.</p>
"""),

dict(
    id='admin-messaging', group='Admin panel',
    title='Chat, messages, push, and newsletters',
    html="""
<h3 class="heading-2">Realtime chat inbox</h3>
<p>The admin inbox is the platform operator's view of every customer-vendor
conversation. It uses Ably for delivery with a REST polling fallback, so the
inbox still works if the realtime connection drops.</p>

<table class="data-table">
<thead><tr><th>Route</th><th>Rate limit</th><th>Purpose</th></tr></thead>
<tbody>
<tr><td><code>inbox</code></td><td>none</td><td>Conversation list</td></tr>
<tr><td><code>inbox/{conversation}</code></td><td>none</td><td>Message thread</td></tr>
<tr><td><code>inbox/reply</code></td><td>20 / 1 min</td><td>Send as the platform</td></tr>
<tr><td><code>inbox/{id}/poll</code></td><td>none</td><td>Polling fallback</td></tr>
<tr><td><code>inbox/{id}/delivered</code></td><td>60 / 1 min</td><td>Read and delivered receipts</td></tr>
<tr><td><code>inbox/ably/token</code></td><td>30 / 1 min</td><td>Short-lived client token</td></tr>
<tr><td><code>inbox/messages/remove</code></td><td>none</td><td>Moderation removal</td></tr>
</tbody></table>

<p>The Ably secret never leaves the server. <code>AblyTokenService</code> mints
short-lived client tokens per request, and <code>routes/channels.php</code>
authorises each private channel against the correct guard. Admin access to a
conversation requires both <code>messages.manage</code> and that the
conversation belongs to the platform vendor.</p>

<div class="callout callout--warn"><strong>Message content is untrusted.</strong>
<p>It arrives from customers and vendors. Escape it on render, and do not allow
it to introduce markup. Chat attachments are served through signed URLs with a
one-hour expiry, and the download route must verify the caller.</p></div>

<h3 class="heading-2">Contact messages</h3>
<p>The public contact form feeds <code>/admin/messages</code>.
<code>ContactMessageService</code> persists the message first and then treats
the admin notification email as best-effort, so a mail failure never loses a
customer's enquiry.</p>

<h3 class="heading-2">Push notifications</h3>
<p><code>/admin/notifications/push</code> broadcasts to customer devices over
Firebase Cloud Messaging. <code>FcmClient</code> implements the FCM HTTP v1 API
directly, including JWT-bearer OAuth2 token caching, so no Firebase Admin SDK
is required. <code>SendPushNotification</code> fans out across a customer's
registered devices and prunes tokens that have gone dead.</p>

<p>Service-account credentials are uploaded at
<code>/admin/settings/firebase</code> and stored in the database, not
<code>.env</code>.</p>

<h3 class="heading-2">Newsletters</h3>
<p><code>/admin/newsletter</code> manages subscribers, a campaign editor, CSV
export, test sends, and dispatch.
<code>SendNewsletterCampaign</code> chunks through active subscribers in one
worker run with a thirty-minute timeout, which is why a queue worker matters on
a real site.</p>

<h3 class="heading-2">Promo banners</h3>
<p><code>/admin/promos</code> controls the promotional banner shown on the
mobile apps' home screen. It is a separate surface from the storefront hero, so
a campaign can target app users without changing the website.</p>
"""),

dict(
    id='admin-ai', group='Admin panel',
    title='AI tools, providers, and vendor quotas',
    html="""
<p>The AI toolset is available to authenticated administrators for translating
content, generating copy, and generating images. Providers and model selection
live at <code>/admin/settings/ai</code>.</p>

<h3 class="heading-2">What administrators can do</h3>
<div class="api-facts"><span><b>TRANSLATE</b> 20 / min</span><span><b>TAXONOMY BATCH</b> 10 / min</span><span><b>GENERATE</b> rate limited</span></div>

<ul>
  <li><code>POST /admin/translate</code> translates arbitrary content,
      throttled to 20 requests per minute.</li>
  <li><code>POST /admin/translate/taxonomy</code> bulk-translates taxonomy in
      one pass, throttled to 10 per minute.</li>
  <li><code>POST /admin/generate</code> and
      <code>POST /admin/generate-image</code> produce copy and imagery, gated
      by <code>products.manage|blogs.manage|pages.manage</code>.</li>
</ul>

<p>Translation runs through <code>AiTranslationService</code>, which chunks
long fields and keeps every field that succeeded. A record with one
untranslatable field is partially translated rather than rolled back, and the
response lists what was skipped.</p>

<h3 class="heading-2">Vendors get metered access</h3>
<p>Sellers reach the same tools from the vendor panel and the vendor API, but
through <code>VendorAiQuotaService</code>, which enforces three separate
pools:</p>
<div class="service-grid">
  <article class="service-card"><span>POOL 1</span><h3>Text generation</h3><p>Tokens consumed by copy and description generation.</p></article>
  <article class="service-card service-card--teal"><span>POOL 2</span><h3>Translation</h3><p>A separate token pool, because translation volume scales very differently from authoring.</p></article>
  <article class="service-card service-card--amber"><span>POOL 3</span><h3>Images</h3><p>Counted per generated image rather than per token.</p></article>
</div>

<p>Vendor AI endpoints are throttled to 30 requests per minute each, and
quota is checked before the call, not after. Credits are drawn down from the
active package allowance, and unused allowances expire rather than rolling
over: <code>ai-credits:cancel-expired</code> runs every minute.</p>

<p>Every AI call is recorded in <code>ai_usage</code> with its provider, model,
token counts, and cost attribution, so you can reconcile spend against
packages.</p>

<div class="callout callout--warn"><strong>AI keys live in the database.</strong>
<p>Provider credentials are stored through the settings store and edited from
the admin panel. They are never written to <code>.env</code>, and they are
never returned to the browser.</p></div>
"""),

dict(
    id='admin-appearance', group='Admin panel',
    title='Themes, app themes, and colours',
    html="""
<p>Everything here sits behind <code>themes.manage</code> and lives under
<code>/admin/appearance</code>.</p>

<table class="data-table">
<thead><tr><th>Surface</th><th>Route</th><th>What it does</th></tr></thead>
<tbody>
<tr><td>Branding</td><td><code>/admin/appearance/branding</code></td><td>Site logo, favicon, and brand marks.</td></tr>
<tr><td>Storefront themes</td><td><code>/admin/appearance/themes</code></td><td>Install, activate, and remove storefront themes.</td></tr>
<tr><td>App themes</td><td><code>/admin/appearance/app-themes</code></td><td>Activate the mobile app's visual system.</td></tr>
<tr><td>Colours</td><td><code>/admin/appearance/colors</code></td><td>Edit and reset the active palette.</td></tr>
</tbody></table>

<h3 class="heading-2">Palette resolution</h3>
<p><code>ThemePalette</code> maps a manifest palette onto CSS custom
properties. Each colour carries a label, a default, and a variable name, so an
administrator sees "Button background" rather than
<code>--el-primary-500</code>. The palette also carries shape radii, an
<code>isDark</code> flag, and status colours for the seven order statuses, so a
dark theme automatically gets readable status badges instead of inheriting light
ones.</p>

<h3 class="heading-2">Storefront and app themes move independently</h3>
<p>Switching the storefront theme does not change the mobile app's layout, and
switching the app theme does not change the website. They share a colour
palette, but each has its own activation state. Legacy
<code>/settings/branding</code>, <code>/settings/themes</code>, and
<code>/settings/colors</code> URLs redirect here, so old bookmarks and old
documentation links keep working.</p>

<div class="callout callout--warn"><strong>Removing a theme is destructive.</strong>
<p>Uninstall drops every table the manifest declares. The
<code>mono</code> theme is kept outside the removable tree for exactly this
reason.</p></div>
"""),

dict(
    id='admin-settings', group='Admin panel',
    title='Settings reference',
    html="""
<p><code>/admin/settings</code> redirects to the shop settings page. The rest
of the group is a set of focused screens rather than one long form, so an
operator changes one thing at a time.</p>

<table class="data-table">
<thead><tr><th>Page</th><th>Route</th><th>Permission</th><th>Contains</th></tr></thead>
<tbody>
<tr><td>Shop</td><td><code>/admin/settings/shop</code></td><td><code>settings.manage</code></td><td>Site name, tagline, contact details, currency, free-shipping threshold, flat shipping, product grid columns, pagination.</td></tr>
<tr><td>Shipping</td><td><code>/admin/settings/shipping</code></td><td><code>shipping.manage</code></td><td>Shipping rates, flat rate, free-shipping zone, and shipping method CRUD.</td></tr>
<tr><td>Locations</td><td><code>/admin/settings/countries</code></td><td><code>locations.manage</code></td><td>Countries with nested states and cities.</td></tr>
<tr><td>Taxes</td><td><code>/admin/settings/taxes</code></td><td><code>taxes.manage</code></td><td>Tax classes and rates with priorities.</td></tr>
<tr><td>Payments</td><td><code>/admin/settings/payment-gateways</code></td><td><code>payments.manage</code></td><td>All fourteen gateway configurations.</td></tr>
<tr><td>Invoices</td><td><code>/admin/settings/invoices</code></td><td><code>settings.manage</code></td><td>Enable, triggers, number prefix, tax ID, footer.</td></tr>
<tr><td>SMTP</td><td><code>/admin/settings/smtp</code></td><td><code>settings.manage</code></td><td>Mail server and a test-send button.</td></tr>
<tr><td>Firebase</td><td><code>/admin/settings/firebase</code></td><td><code>settings.manage</code></td><td>FCM web config and service-account upload.</td></tr>
<tr><td>Scheduled jobs</td><td><code>/admin/settings/scheduled-jobs</code></td><td><code>settings.manage</code></td><td>Job table with frequency, enable/disable, and run-now.</td></tr>
<tr><td>Chat</td><td><code>/admin/settings/chat</code></td><td><code>settings.manage</code></td><td>Ably configuration.</td></tr>
<tr><td>Mobile app</td><td><code>/admin/settings/mobile-app</code></td><td><code>settings.manage</code></td><td>App-facing configuration served to both Flutter clients.</td></tr>
<tr><td>AI</td><td><code>/admin/settings/ai</code></td><td><code>settings.manage</code></td><td>Providers, model list, and translator, generator, and image model selection.</td></tr>
<tr><td>Cookie consent</td><td><code>/admin/settings/cookie</code></td><td><code>settings.manage</code></td><td>Consent banner copy and behaviour.</td></tr>
</tbody></table>

<div class="callout callout--warn"><strong>Settings are stored in the database.</strong>
<p>Everything above is key and value rows in the <code>settings</code> table,
not environment variables. That is deliberate: it lets an operator change a
mail server or rotate a payment key without shell access. It also means
backing up the database backs up your configuration.</p></div>
"""),

dict(
    id='admin-platform', group='Admin panel',
    title='Administrators, roles, languages, and media',
    html="""
<p>These four modules sit in the "Administration" group. They are the ones
that change who can do what, in what language, and with what imagery.</p>

<h3 class="heading-2">Administrators</h3>
<p><code>/admin/administrators</code> creates, edits, and deletes admin
accounts behind <code>admins.manage</code>. There is no public registration
path: the installer creates the first account, and every account after that
comes from this screen.</p>

<h3 class="heading-2">Roles</h3>
<p><code>/admin/roles</code> is where permissions are assigned. Each role is a
name, a label, an <code>is_super</code> flag, and a set of permissions drawn
from the 32 available. Changing a role's permission set changes it for every
administrator holding that role, immediately.</p>

<div class="callout callout--warn"><strong>Guard the last super administrator.</strong>
<p>An <code>is_super</code> role bypasses <code>hasPermission()</code>
entirely. If you remove super-admin status from every account, nobody can
restore it through the panel and you will be editing the database by hand.</p></div>

<h3 class="heading-2">Languages</h3>
<p><code>/admin/languages</code> manages the three shipped languages plus any
you add. Each has a web default and an independent mobile default, an
enable/disable switch, and a per-language translation editor at
<code>/admin/languages/{language}/translations</code>.</p>

<h3 class="heading-2">Media</h3>
<p><code>/admin/media</code> is the shared library behind every image picker in
the panel, with a JSON listing endpoint, upload, delete, and bulk delete.
Uploads land under <code>storage/app/public</code> in the owner-appropriate
subdirectory and are served through <code>PublicMedia::url()</code>.</p>

<p>The library is owner-isolated: a vendor only ever sees their own media, while
an administrator sees everything. <code>MediaIsolationTest</code> guards that
boundary.</p>
"""),

# =============================================================== BACKEND
dict(
    id='api-overview', group='Backend',
    title='API version 1: shape, auth, and limits',
    html="""
<p>Both Flutter clients talk to the same versioned JSON API. The prefix is set
once in <code>bootstrap/app.php</code> as <code>api/v1</code>; there is no
content negotiation, so the version is explicit in every path.</p>

<div class="api-url"><span>BASE URL</span><code id="mono-api-base">https://your-domain.com/api/v1</code><button class="copy-button" type="button" data-copy="#mono-api-base">Copy</button></div>

<h3 class="heading-2">Response envelope</h3>
<div class="endpoint-groups">
  <article><h3>Success</h3><p><code>{ "success": true, "data": …, "meta": { … } }</code>.
  Pagination and other collection metadata live in <code>meta</code>, never
  inside <code>data</code>.</p></article>
  <article><h3>Error</h3><p><code>{ "success": false, "error": { "message": …,
  "code": …, "fields": { … } } }</code>. <code>fields</code> is present only on
  validation failures. Rendered centrally by
  <code>App\\Support\\ApiException</code>.</p></article>
</div>

<h3 class="heading-2">Authentication</h3>
<p>Sanctum personal access tokens, sent as <code>Authorization: Bearer</code>.
Two middleware variants exist, and the difference matters when you add a
public endpoint that still wants to know who is asking:</p>
<ul>
  <li><code>auth:sanctum</code> requires a valid token and rejects without
      one.</li>
  <li><code>auth.optional</code> resolves the user when a token is present and
      never rejects. The public catalog runs on it so that wishlisted and
      collected flags can be resolved for a signed-in customer without
      turning browsing into a login wall.</li>
</ul>

<h3 class="heading-2">Rate limits</h3>
<p>There is no global limiter. Limits are declared per route:</p>
<table class="data-table">
<thead><tr><th>Route</th><th>Limit</th></tr></thead>
<tbody>
<tr><td><code>POST /contact/send</code></td><td>10 / min</td></tr>
<tr><td><code>POST /products/{id}/reviews</code></td><td>10 / min</td></tr>
<tr><td><code>POST /checkout/sessions</code>, wallet-pay, cod-pay</td><td>30 / min</td></tr>
<tr><td>Vendor AI generate, generate-image, translate</td><td>30 / min</td></tr>
<tr><td>Vendor <code>messages/start</code></td><td>10 / min</td></tr>
<tr><td>Vendor <code>messages/{id}/reply</code></td><td>30 / min</td></tr>
</tbody></table>

<div class="callout callout--warn"><strong>Auth endpoints are not throttled in this build.</strong>
<p>Login, register, and the OTP endpoints have no rate limit attached. If you
are hardening a public deployment, add a limiter to those before launch; see
the launch checklist.</p></div>

<h3 class="heading-2">Signed routes</h3>
<p>Two download routes sit deliberately outside <code>auth:sanctum</code> and
are guarded by signed URLs with expiry instead: chat attachments at one hour,
and digital product files at thirty minutes. Signing replaces the bearer token
in the query string so the URL can be handed to a browser or a download
manager without leaking a session credential.</p>
"""),

dict(
    id='api-customer', group='Backend',
    title='Customer API surface',
    html="""
<p>Roughly forty endpoint families serve the customer app. The shape below is
grouped by what a user is doing rather than by controller, because that is how
the apps consume it.</p>

<div class="workflow-columns">
  <article><h3>Session</h3><ul>
    <li><code>POST /auth/login</code>, <code>/auth/register</code>,
        <code>/auth/google</code></li>
    <li><code>GET /auth/google-config</code> returns the client id</li>
    <li><code>POST /auth/forgot-password/send-otp</code>,
        <code>/verify-otp</code>, <code>/reset</code></li>
    <li><code>POST /auth/logout</code>, <code>/auth/change-password</code></li>
    <li><code>GET</code> and <code>PUT /auth/profile</code></li>
  </ul></article>

  <article><h3>Discovery</h3><ul>
    <li><code>GET /home</code>, <code>/home/discover</code>,
        <code>/home/featured</code></li>
    <li><code>GET /categories</code>, <code>/products</code>,
        <code>/products/{id}</code>, <code>/products/{id}/related</code></li>
    <li><code>GET /products/{id}/reviews</code>, <code>/flash-sale</code></li>
    <li><code>GET /search/suggestions</code>, <code>/vendors/{id}</code></li>
    <li><code>GET /vouchers</code> — the public voucher pool</li>
  </ul></article>

  <article><h3>Cart and checkout</h3><ul>
    <li><code>GET /cart</code>, <code>POST /cart/add</code>,
        <code>POST /cart/qty</code>, <code>DELETE /cart/{productId}</code>,
        <code>POST /cart/clear</code></li>
    <li><code>POST /coupons/apply</code>, <code>DELETE /coupons</code></li>
    <li><code>GET /checkout</code>, <code>POST /checkout/place</code></li>
    <li><code>POST /checkout/paypal/create</code> for native PayPal</li>
    <li><code>POST /checkout/sessions</code> opens a hosted web checkout;
        <code>/checkout-sessions/{uuid}/status</code>, <code>/cancel</code>,
        <code>/wallet-pay</code>, and <code>/cod-pay</code> complete it</li>
    <li><code>POST /orders/{id}/payment-session</code> retries payment for an
        existing order</li>
  </ul></article>

  <article><h3>Account</h3><ul>
    <li><code>GET /orders</code>, <code>/orders/{id}</code>,
        <code>/orders/{id}/tracking</code>, <code>/orders/{id}/reorder</code></li>
    <li><code>GET /invoices/{id}</code></li>
    <li><code>GET /downloads</code>, <code>/downloads/{entitlement}</code></li>
    <li><code>GET</code>, <code>POST</code>, <code>PUT</code>,
        <code>DELETE /addresses</code></li>
    <li><code>POST /following</code>, <code>POST /vendors/{id}/follow</code></li>
  </ul></article>

  <article><h3>Money</h3><ul>
    <li><code>GET /wallet</code>, <code>/wallet/transactions</code>,
        <code>/wallet/topup-methods</code>, <code>POST /wallet/topup</code></li>
    <li><code>GET /loyalty</code>, <code>/loyalty/transactions</code>,
        <code>POST /loyalty/redeem</code></li>
    <li><code>GET /vouchers/saved</code>, <code>POST /vouchers/{code}/save</code>,
        <code>GET /vouchers/{code}</code></li>
    <li>Wishlist: <code>GET</code>, <code>POST</code>, and
        <code>DELETE /wishlist</code></li>
  </ul></article>

  <article><h3>Engagement</h3><ul>
    <li><code>GET /notifications</code>, <code>/notifications/unread-count</code>,
        <code>/notifications/read-all</code>, and per-item read and delete</li>
    <li><code>POST /notifications/register-token</code> and
        <code>unregister-token</code> for FCM</li>
    <li><code>GET</code> and <code>PUT /settings/notifications</code></li>
    <li><code>GET /chat</code>, <code>/chat/conversations</code>,
        <code>/chat/{id}/poll</code>, <code>POST /chat/send</code>,
        <code>GET /chat/token</code></li>
    <li><code>POST /contact/send</code> for the contact form</li>
  </ul></article>
</div>

<h3 class="heading-2">Content and localisation</h3>
<p><code>GET /content/about</code>, <code>/content/contact</code>, and
<code>/content/page/{slug}</code> return CMS content.
<code>GET /country</code>, <code>/country/states/{cc}</code>, and
<code>/country/cities/{state}</code> drive the address forms.
<code>GET /languages</code> and <code>GET /translations/{code}</code> supply
the app's interface strings, including the separate mobile namespaces.</p>

<div class="callout"><strong>Resources do the shaping.</strong>
<p>Controllers return API Resources, not raw models:
<code>ProductCardResource</code>, <code>ProductDetailResource</code>,
<code>OrderResource</code>, <code>WalletResource</code>, and so on. Add a field
to a Resource rather than to the model, or you will change the admin panel's
own payloads by accident.</p></div>
"""),

dict(
    id='api-vendor', group='Backend',
    title='Vendor API surface',
    html="""
<p>Everything a seller needs is namespaced under
<code>/api/v1/vendor</code>, served by sixteen controllers in
<code>Api/V1/Vendor/</code>. Vendor auth, profile, and settings mirror the
customer equivalents.</p>

<div class="workflow-columns">
  <article><h3>Store</h3><ul>
    <li><code>GET /dashboard</code> — the seller overview</li>
    <li><code>GET</code>, <code>POST /products</code>;
        <code>GET</code>, <code>PUT</code>, <code>DELETE /products/{id}</code></li>
    <li><code>GET /categories</code>, <code>/brands</code>,
        <code>/attributes</code>, <code>/languages</code> as reference data</li>
    <li><code>GET</code>, <code>POST /product-bundles</code> and the item
        routes, with <code>/product-bundles/candidates</code> for the picker</li>
    <li><code>GET</code>, <code>PUT /settings</code>,
        <code>PUT /settings/payouts</code>, <code>/settings/notifications</code></li>
  </ul></article>

  <article><h3>Orders and delivery</h3><ul>
    <li><code>GET /orders</code>, <code>/orders/{id}</code></li>
    <li><code>PATCH /orders/{id}/status</code> for fulfilment</li>
    <li><code>POST /orders/{order}/digital-deliver/{entitlement}</code> for
        per-item digital delivery</li>
    <li><code>GET</code>, <code>POST /delivery/requests</code> and
        <code>POST /delivery/requests/{id}/cancel</code></li>
    <li><code>GET /delivery/history</code>, <code>/delivery/tracking</code>,
        <code>/delivery/tracking/orders/{id}</code></li>
    <li><code>POST /delivery/shipments</code>,
        <code>PATCH /delivery/shipments/{id}/status</code></li>
  </ul></article>

  <article><h3>Growth</h3><ul>
    <li><code>POST /categories/request</code> and
        <code>GET /categories/my-requests</code></li>
    <li><code>GET</code>, <code>POST</code>, <code>PUT</code>,
        <code>DELETE /brands</code> and <code>/attributes</code>, including
        <code>/custom</code> lists</li>
    <li><code>GET /packages</code>,
        <code>POST /packages/{package}/checkout</code></li>
    <li><code>GET /featured/packages</code>, <code>/featured/requests</code>,
        <code>POST /products/{id}/feature/checkout</code></li>
  </ul></article>

  <article><h3>Money and engagement</h3><ul>
    <li><code>GET /wallet</code>, <code>/settlements</code>,
        <code>/withdrawals</code>, <code>POST /withdrawals</code></li>
    <li><code>GET /ai/quota</code>, <code>/ai/credits</code> and the three
        generation endpoints</li>
    <li><code>GET</code>, <code>POST /faqs</code> and
        <code>GET /followers</code></li>
    <li><code>GET /media</code>, <code>POST /media/upload</code>,
        <code>DELETE /media/{id}</code></li>
    <li>The full notification set under <code>/vendor/notifications</code></li>
  </ul></article>
</div>

<div class="callout callout--warn"><strong>Vendor writes are owner-scoped.</strong>
<p>Every mutation on a vendor route is scoped to the authenticated vendor's own
records, independent of the client payload. If you add a vendor endpoint, keep
that scoping in the controller or a policy; do not trust a vendor id from the
request body.</p></div>
"""),

dict(
    id='database', group='Backend',
    title='Schema overview',
    html="""
<p>The application carries 147 migrations producing 94 tables, backed by 78
Eloquent models. Most of the volume is marketplace and delivery surface rather
than framework scaffolding.</p>

<table class="data-table">
<thead><tr><th>Domain</th><th>Tables</th></tr></thead>
<tbody>
<tr><td>People and access</td><td><code>admins</code>, <code>roles</code>, <code>permissions</code>, <code>role_permission</code>, <code>admin_role</code>, <code>customers</code>, <code>vendors</code>, <code>vendor_applications</code>, <code>addresses</code>, <code>password_otps</code>, <code>device_tokens</code></td></tr>
<tr><td>Catalog</td><td><code>categories</code>, <code>brands</code>, <code>attributes</code>, <code>attribute_values</code>, <code>products</code>, <code>product_images</code>, <code>product_variations</code>, <code>product_bundle_items</code></td></tr>
<tr><td>Commerce</td><td><code>orders</code>, <code>order_items</code>, <code>carts</code>, <code>cart_items</code>, <code>wishlists</code>, <code>coupons</code>, <code>coupon_customer</code>, <code>customer_vouchers</code>, <code>reviews</code>, <code>invoices</code>, <code>shipping_methods</code>, <code>tax_classes</code>, <code>tax_rates</code></td></tr>
<tr><td>Money</td><td><code>wallets</code>, <code>wallet_transactions</code>, <code>vendor_payouts</code>, <code>vendor_packages</code>, <code>vendor_package_subscriptions</code>, <code>vendor_withdrawal_methods</code>, <code>vendor_withdrawal_presets</code>, <code>vendor_follows</code></td></tr>
<tr><td>Delivery</td><td><code>delivery_requests</code>, <code>delivery_request_events</code>, <code>shipments</code>, <code>shipment_tracking_events</code>, <code>delivery_personnel</code>, <code>delivery_locations</code>, <code>delivery_couriers</code></td></tr>
<tr><td>Digital goods</td><td><code>digital_assets</code>, <code>digital_license_keys</code>, <code>digital_entitlements</code>, <code>digital_download_logs</code></td></tr>
<tr><td>Engagement</td><td><code>conversations</code>, <code>conversation_messages</code>, <code>conversation_message_attachments</code>, <code>conversation_participants</code>, <code>customer_notifications</code>, <code>vendor_notifications</code>, <code>contact_messages</code>, <code>newsletter_subscriptions</code>, <code>newsletter_campaigns</code>, <code>ably_settings</code></td></tr>
<tr><td>Content and platform</td><td><code>pages</code>, <code>posts</code>, <code>media</code>, <code>languages</code>, <code>settings</code>, <code>themes</code>, <code>countries</code>, <code>states</code>, <code>cities</code>, <code>scheduled_jobs</code>, <code>app_checkout_sessions</code>, <code>loyalty_transactions</code>, <code>loyalty_redemption_tiers</code>, <code>featured_packages</code>, <code>featured_product_requests</code></td></tr>
<tr><td>AI</td><td><code>ai_providers</code>, <code>ai_usage</code>, <code>ai_credit_packs</code>, <code>ai_credit_purchases</code>, <code>ai_pack_consumptions</code></td></tr>
</tbody></table>

<h3 class="heading-2">Design decisions worth knowing</h3>
<div class="callout-grid">
  <div class="callout"><strong>Orders denormalise their customer</strong><p><code>customer_name</code> and <code>email</code> are copied onto the order, so a historical invoice still prints correctly after the customer renames their account or changes their address book.</p></div>
  <div class="callout"><strong>Subscriptions snapshot their terms</strong><p>Price, duration, and commission are copied onto the subscription row at purchase time, so editing a package never rewrites what a vendor was actually sold.</p></div>
  <div class="callout"><strong>Settings are key and value</strong><p>Runtime configuration lives in one <code>settings</code> table rather than in files, which is what makes the admin panel able to change mail servers and payment keys without server access.</p></div>
</div>

<h3 class="heading-2">Demo seeders</h3>
<p><code>DatabaseSeeder</code> orchestrates the rest:
<code>RolePermissionSeeder</code> creates the three roles and the 32
permissions, <code>LocationSeeder</code> fills countries, states, and cities,
<code>TaxSeeder</code> sets tax classes, and
<code>PageSeeder</code> creates the built-in pages. Beyond that,
<code>RealisticOrderAndReviewSeeder</code> generates plausible orders and
reviews, <code>MonoDeskKitSeeder</code> builds a full platform-vendor bundle
catalogue, and <code>DemoDigitalProductsSeeder</code> and
<code>ScopedVoucherSeeder</code> populate digital goods and vouchers per
audience.</p>

<div class="callout callout--warn"><strong>Never ship the demo credentials.</strong>
<p>The seeders create <code>admin@mono.test</code> and
<code>jordan@example.com</code>, both with the password
<code>password</code>, and eight vendors on the same password. They also embed
Firebase web keys. Run <code>migrate</code> without <code>--seed</code> on a
real deployment, or remove these accounts before the site is public.</p></div>
"""),

dict(
    id='services-jobs', group='Backend',
    title='Services, jobs, events, and commands',
    html="""
<p>Business rules live in services, not in controllers. If a rule is about
orders, money, delivery, or entitlement, it belongs in
<code>app/Services</code>.</p>

<h3 class="heading-2">The services that matter most</h3>
<div class="service-grid">
  <article class="service-card"><span>COMMERCE</span><h3>Order placement</h3>
  <p><code>OrderPlacementService</code> is the canonical order path for web and
  API. <code>OrderInventoryService</code> is the only place stock moves.</p></article>
  <article class="service-card service-card--teal"><span>MONEY</span><h3>Billing</h3>
  <p><code>PaymentGatewayService</code> and
  <code>OnlineGatewayPaymentService</code> own gateway availability, launch,
  and verification. <code>VendorBillingService</code> owns commission and
  settlement arithmetic.</p></article>
  <article class="service-card service-card--amber"><span>DELIVERY</span><h3>Fulfilment</h3>
  <p><code>DeliveryService</code> validates requests from every entry point.
  <code>ShipmentService</code> runs the shipment lifecycle,
  <code>TrackingService</code> merges timelines, and
  <code>DeliveryNotificationService</code> fans out the alerts.</p></article>
  <article class="service-card"><span>CONTENT</span><h3>Documents</h3>
  <p><code>InvoiceService</code> numbers and renders invoices.
  <code>DigitalDeliveryService</code> owns entitlement state.
  <code>LoyaltyService</code> and <code>VoucherService</code> own points and
  vouchers.</p></article>
  <article class="service-card service-card--teal"><span>REALTIME</span><h3>Messaging</h3>
  <p><code>ConversationService</code> manages participants.
  <code>AblyTokenService</code> mints short-lived client tokens so the Ably
  secret never leaves the server.</p></article>
  <article class="service-card service-card--amber"><span>PLATFORM</span><h3>Infrastructure</h3>
  <p><code>ScheduledJobService</code> registers the database-driven job table.
  <code>MediaService</code>, <code>MenuService</code>, and
  <code>HomePageContent</code> support the storefront editing surfaces.</p></article>
</div>

<h3 class="heading-2">Jobs and events</h3>
<p>Three queued jobs: <code>SendNewsletterCampaign</code> (chunked,
<code>timeout = 1800</code>), <code>SendPushNotification</code>, and
<code>SendVendorPushNotification</code> (both <code>tries = 2</code>, both
pruning dead device tokens). One observer,
<code>AiCreditPurchaseObserver</code>, fires the vendor notification when a
credit purchase becomes active from any flow and de-duplicates it.</p>

<p>Four broadcast events run through Ably: <code>MessageSent</code>,
<code>MessageRemoved</code>, <code>ChatReceiptUpdated</code>, and
<code>VendorNotificationReceived</code>.</p>

<h3 class="heading-2">Artisan commands</h3>
<table class="data-table">
<thead><tr><th>Command</th><th>Purpose</th></tr></thead>
<tbody>
<tr><td><code>orders:cancel-expired</code></td><td>Cancels unpaid orders past their window and restores stock.</td></tr>
<tr><td><code>ai-credits:cancel-expired</code></td><td>Reverses unsettled AI credit purchases.</td></tr>
<tr><td><code>featured:expire</code></td><td>Clears lapsed featured placements.</td></tr>
<tr><td><code>loyalty:expire-points</code></td><td>Expires stale point balances.</td></tr>
<tr><td><code>badges:expire-new</code></td><td>Retires the "new" badge window.</td></tr>
<tr><td><code>vendor-packages:notify-expiry</code></td><td>Warns vendors before a plan lapses.</td></tr>
<tr><td><code>media:backfill</code></td><td>Re-resolves media records for the upload roots.</td></tr>
<tr><td><code>catalog:export-release</code></td><td>Exports a catalogue artifact for the installer.</td></tr>
<tr><td><code>release:install-catalog-themes</code></td><td>Installs catalogue theme packages on a release host.</td></tr>
<tr><td><code>release:backfill-catalog-media</code></td><td>Restores catalogue imagery after an import.</td></tr>
<tr><td><code>release:verify-schema</code></td><td>Verifies the expected tables exist before go-live.</td></tr>
</tbody></table>

<div class="callout"><strong>Run <code>release:verify-schema</code> after an update.</strong>
<p>It checks that the expected tables are present, which catches a partially
applied migration before it becomes a missing-column error in production.</p></div>
"""),

dict(
    id='deployment', group='Backend',
    title='Going live: deployment and the pre-launch checklist',
    html="""
<h3 class="heading-2">Production configuration</h3>
<div class="build-commands">
  <div><span>ENVIRONMENT</span><code>APP_ENV=production</code></div>
  <div><span>DEBUG</span><code>APP_DEBUG=false</code></div>
  <div><span>URL</span><code>APP_URL=https://your-domain.com</code></div>
  <div><span>CRON</span><code>* * * * * cd /path &amp;&amp; php artisan schedule:run</code></div>
  <div><span>QUEUE</span><code>php artisan queue:work --tries=2</code></div>
  <div><span>SCHEMA CHECK</span><code>php artisan release:verify-schema</code></div>
</div>

<div class="callout callout--warn"><strong>Serve everything over HTTPS.</strong>
<p>Payment gateways reject non-HTTPS callbacks, Sanctum tokens must not travel
in cleartext, and signed URLs are meaningless over an interceptable
connection. Terminate TLS in front of the application and redirect HTTP
permanently.</p></div>

<h3 class="heading-2">Pre-launch checklist</h3>
<ol class="walkthrough">
  <li><strong>Remove the demo data.</strong>
    <p>Delete the seeded admin, customer, and vendor accounts, or run
    <code>migrate</code> without <code>--seed</code>. Confirm no
    <code>@mono.test</code> account can still authenticate.</p></li>

  <li><strong>Delete the installer.</strong>
    <p>Remove <code>public/install.php</code> and confirm
    <code>storage/app/installed.lock</code> exists.</p></li>

  <li><strong>Set the app key and rotate the seeded Firebase keys.</strong>
    <p>Run <code>key:generate</code> for a fresh
    <code>APP_KEY</code>, and replace the Firebase web configuration that the
    seeders wrote.</p></li>

  <li><strong>Configure only the gateways you need.</strong>
    <p>Fill in real credentials at
    <code>/admin/settings/payment-gateways</code> and leave the rest disabled.
    A half-configured gateway is hidden from checkout automatically, which is
    the behaviour you want while you set it up.</p></li>

  <li><strong>Verify mail actually sends.</strong>
    <p>Use the test-send button at <code>/admin/settings/smtp</code>. Until
    mail works, order confirmations, invoices, OTPs, and password resets all
    fail silently from the customer's point of view.</p></li>

  <li><strong>Confirm the cron and the queue worker are running.</strong>
    <p>Unpaid orders will not be cancelled, featured placements will not
    expire, and newsletters and push will not be delivered without them.</p></li>

  <li><strong>Add rate limiting to the auth endpoints.</strong>
    <p>Login, register, and the OTP routes have no limiter in this build. Add
    one before exposing the site publicly.</p></li>

  <li><strong>Review file upload handling.</strong>
    <p>Confirm uploads land outside any executable path, that extensions and
    MIME types are validated server-side, and that chat attachments and
    digital downloads verify the requesting user before streaming a
    file.</p></li>

  <li><strong>Set a real admin password policy and rotate shared logins.</strong>
    <p>Particularly before granting <code>vendors.impersonate</code> to
    anyone.</p></li>
</ol>

<h3 class="heading-2">Backups</h3>
<p>Back up the database and <code>storage/</code> together. The database holds
every setting, every uploaded media record, and the entire wallet and settlement
ledger; <code>storage/</code> holds the actual files and the generated invoice
PDFs. A backup of one without the other is not a backup.</p>

<div class="callout"><strong>Verify a restore before you need one.</strong>
<p>An untested backup is a hypothesis. Restore into a scratch database and run
<code>release:verify-schema</code> to confirm the result is usable.</p></div>
"""),
]
