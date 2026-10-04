# -*- coding: utf-8 -*-
"""Render the MONO Marketplace documentation site.

Content lives in mono_sections.py. This script wraps it in the dark
dashboard design that is shared with the customer and vendor app docs.

    python build_design.py

Section order in mono_sections.py is document order, and the navigation
is generated in that same order, so the two can never disagree.
"""

import io
import os
import re

from mono_sections import SECTIONS

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'index.html')

# ------------------------------------------------------------------ nav
nav = []
prev_group = None
for section in SECTIONS:
    if section['group'] != prev_group:
        nav.append('          <span class="toc-label">%s</span>' % section['group'])
        prev_group = section['group']
    nav.append('          <a href="#%s">%s</a>' % (section['id'], section['title']))
nav_html = '\n'.join(nav)

# -------------------------------------------------------------- overview
OV = """          <div class="ov" id="top" aria-labelledby="ov-title">
            <div class="ov-bar">
              <p class="ov-kicker"><span>MONO Marketplace</span><span>Storefront &middot; Vendor &middot; Admin</span></p>
              <span class="ov-signal"><i aria-hidden="true"></i>Web product</span>
            </div>

            <div class="ov-head">
              <div class="ov-heading">
                <h1 id="ov-title">Mono.<em> Marketplace.</em></h1>
                <p class="ov-note"><span aria-hidden="true">&bull;</span> Multi-vendor commerce, one Laravel application.</p>
              </div>
              <div class="ov-side">
                <p class="ov-lede">Complete documentation for the MONO Marketplace web product: the themeable storefront, the vendor dashboard, the admin panel, and the Laravel services behind all three. Install it, run the marketplace, and extend it.</p>
                <div class="ov-actions">
                  <button class="action-button action-button--primary" type="button" data-scroll-to="installation">Install the app <span aria-hidden="true">&darr;</span></button>
                  <button class="action-button" type="button" data-scroll-to="admin-dashboard">Admin panel <span aria-hidden="true">&rarr;</span></button>
                </div>
              </div>
            </div>

            <div class="ov-kpis" aria-label="Mono Marketplace headline facts">
              <article class="ov-kpi"><span class="status-index">A / 01</span><p>Engine</p><strong>Laravel 13 / PHP 8.3</strong><span class="status-badge status-badge--blue">Blade + Tailwind 4</span></article>
              <article class="ov-kpi"><span class="status-index">A / 02</span><p>Surface</p><strong>3 panels / 9 themes</strong><span class="status-badge status-badge--teal">14 payment methods</span></article>
              <article class="ov-kpi"><span class="status-index">A / 03</span><p>Scale</p><strong>94 tables / 78 models</strong><span class="status-badge status-badge--amber">32 permissions</span></article>
            </div>
          </div>"""

# --------------------------------------------------------- doc sections
# The permission, payment, and schema tables are wide by nature. Wrapping
# each one lets it scroll sideways on a phone instead of widening the page.
TABLE_OPEN = re.compile(r'(<table\b[^>]*>)', re.I)


def wrap_tables(html):
    out, depth = [], 0
    for chunk in re.split(r'(<table\b[^>]*>|</table>)', html, flags=re.I):
        low = chunk.lower()
        if low.startswith('<table'):
            if depth == 0:
                out.append('<div class="table-scroll">')
            depth += 1
        elif low.startswith('</table>'):
            depth -= 1
            if depth == 0:
                out.append('</div>')
        out.append(chunk)
    assert depth == 0, 'unbalanced table in section content'
    return ''.join(out)


body_out = []
for index, section in enumerate(SECTIONS, start=1):
    intro = ' doc-section--intro' if index == 1 else ''
    # The overview block opens the first section, above its kicker and title.
    lead = OV + '\n' if index == 1 else ''
    body_out.append(
        '        <section class="doc-section%s" id="%s" data-section-title="%s">\n'
        '          %s'
        '          <p class="section-kicker">%02d / %s</p>\n'
        '          <h2 class="section-title">%s</h2>\n'
        '          %s\n'
        '        </section>\n'
        % (intro, section['id'], section['title'].replace('&', '&amp;'), lead,
           index, section['group'], section['title'],
           wrap_tables(section['html'].strip())))

sections_html = '\n'.join(body_out)

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="MONO Marketplace documentation: storefront themes, vendor panel, admin panel, payment gateways, API, and deployment.">
  <meta name="theme-color" content="#0a0a0a">
  <title>MONO Marketplace &mdash; Documentation</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&amp;family=Space+Grotesk:wght@400;500;600;700&amp;display=swap" rel="stylesheet">
  <link rel="stylesheet" href="web.css">
  <script src="script.js" defer></script>
</head>
<body>
  <a class="skip-link" href="#main-content">Skip to content</a>

  <header class="site-header">
    <a class="brand" href="#top" aria-label="MONO Marketplace documentation home">
      <span class="brand-mark" aria-hidden="true">M</span>
      <span class="brand-copy"><strong>MONO</strong><small>Marketplace</small></span>
    </a>
    <div class="header-actions">
      <span class="build-chip"><i aria-hidden="true"></i> Web product</span>
      <button class="toc-toggle" id="toc-toggle" type="button" aria-label="Open contents" aria-controls="toc-drawer" aria-expanded="false">
        <span class="menu-glyph" aria-hidden="true"><i></i><i></i><i></i></span><span>Contents</span>
      </button>
    </div>
  </header>

  <div class="drawer-scrim" data-drawer-scrim hidden></div>

  <main id="main-content">
    <div class="guide-shell">
      <aside class="toc-drawer" id="toc-drawer" aria-label="On this page" data-toc-drawer>
        <div class="toc-header">
          <div>
            <span class="toc-kicker">On this page</span>
            <strong>Documentation</strong>
          </div>
          <button class="icon-button toc-close" type="button" data-drawer-close aria-label="Close contents"><span aria-hidden="true">&times;</span></button>
        </div>
        <nav class="toc-group" aria-label="MONO Marketplace documentation contents">
__NAV__
        </nav>
        <div class="toc-meta"><span>DOC / MM-1.0.0</span><span>__COUNT__ sections</span></div>
      </aside>

      <div class="doc-stage">
        <section class="doc-panel" aria-label="MONO Marketplace documentation">
__SECTIONS__
        </section>

        <footer class="site-footer"><span>MONO MARKETPLACE</span><span>Multi-vendor commerce platform</span><a href="#top">Back to top &uarr;</a></footer>
      </div>
    </div>
  </main>

  <div class="lightbox" id="image-lightbox" role="dialog" aria-modal="true" aria-labelledby="lightbox-caption" hidden><button class="lightbox-close" type="button" data-lightbox-close aria-label="Close image">&times;</button><button class="lightbox-nav lightbox-prev" type="button" data-lightbox-prev aria-label="Previous image">&lsaquo;</button><figure><img id="lightbox-image" src="" alt=""><figcaption id="lightbox-caption"></figcaption><span id="lightbox-counter"></span></figure><button class="lightbox-nav lightbox-next" type="button" data-lightbox-next aria-label="Next image">&rsaquo;</button></div>
  <div class="toast" id="toast" role="status" aria-live="polite" hidden>Copied to clipboard</div>
</body>
</html>
"""

html = (TEMPLATE
        .replace('__NAV__', nav_html)
        .replace('__SECTIONS__', sections_html)
        .replace('__COUNT__', str(len(SECTIONS))))

io.open(OUT, 'w', encoding='utf-8').write(html)

# ---------------------------------------------------------------- checks
ids = [s['id'] for s in SECTIONS]
assert len(ids) == len(set(ids)), 'duplicate section id: %s' % (
    [i for i in ids if ids.count(i) > 1],)
missing = [i for i in ids if 'id="%s"' % i not in html]
assert not missing, 'sections not rendered: %s' % missing
assert nav_html.index('#%s' % ids[0]) < nav_html.index('#%s' % ids[-1]), 'nav out of order'

groups = len({s['group'] for s in SECTIONS})
print('sections: %d | groups: %d | nav links: %d | %d bytes'
      % (len(SECTIONS), groups, len(nav) - groups, len(html)))
print('written :', OUT)
