(() => {
  'use strict';
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));
  const toc = $('[data-toc-drawer]');
  const tocToggle = $('#toc-toggle');
  const scrim = $('[data-drawer-scrim]');
  const links = $$('.toc-group a[href^="#"]');
  const sections = $$('.doc-panel > .doc-section');
  const toast = $('#toast');
  const lightbox = $('#image-lightbox');
  const lightboxImage = $('#lightbox-image');
  const lightboxCaption = $('#lightbox-caption');
  const lightboxCounter = $('#lightbox-counter');
  const mediaQuery = window.matchMedia('(max-width: 1060px)');
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  let lastFocus = null;
  let lastLightboxTrigger = null;
  let toastTimer = null;
  let raf = null;
  let images = [];
  let imageIndex = 0;
  let activeNavigationId = null;

  const headerOffset = () => Math.ceil(($('.site-header')?.offsetHeight || 68) + 24);
  const scrollTo = (target, smooth = true) => {
    if (!target) return;
    const top = Math.max(0, window.scrollY + target.getBoundingClientRect().top - headerOffset());
    window.scrollTo({ top, behavior: smooth && !reduceMotion.matches ? 'smooth' : 'auto' });
  };
  const setHash = (hash) => {
    try { history.replaceState(null, '', hash); } catch (_) { window.location.hash = hash; }
  };
  const setDrawer = (open, restore = false) => {
    if (!toc) return;
    toc.classList.toggle('is-open', open);
    tocToggle?.setAttribute('aria-expanded', String(open));
    document.body.classList.toggle('drawer-open', open);
    if (scrim) scrim.hidden = !open;
    if (open) {
      toc.removeAttribute('aria-hidden'); toc.removeAttribute('inert');
      $('a', toc)?.focus();
    } else {
      if (mediaQuery.matches) { toc.setAttribute('aria-hidden', 'true'); toc.setAttribute('inert', ''); }
      else { toc.removeAttribute('aria-hidden'); toc.removeAttribute('inert'); }
      if (restore && lastFocus?.focus) lastFocus.focus();
    }
  };
  const keepActiveVisible = (link) => {
    if (!toc || !link) return;
    const a = link.getBoundingClientRect(), d = toc.getBoundingClientRect();
    if (a.top < d.top + 74) toc.scrollTop -= d.top + 74 - a.top;
    else if (a.bottom > d.bottom - 15) toc.scrollTop += a.bottom - d.bottom + 15;
  };
  const setActiveLink = (id) => {
    const selected = links.find(link => link.hash === `#${id}`);
    if (!selected) return;
    activeNavigationId = id;
    links.forEach(link => {
      const on = link === selected;
      link.classList.toggle('is-active', on);
      if (on) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
    keepActiveVisible(selected);
  };
  const updateActive = () => {
    if (!sections.length) return;
    const marker = headerOffset() + 5;
    let current = sections[0];
    sections.forEach(section => { if (section.getBoundingClientRect().top <= marker) current = section; });
    if (activeNavigationId) {
      const selectedSection = document.getElementById(activeNavigationId)?.closest('.doc-section');
      if (selectedSection) {
        const rect = selectedSection.getBoundingClientRect();
        if (rect.top <= marker + 180 && rect.bottom > 0) current = selectedSection;
        if (rect.top < marker - 220 || rect.bottom < 0) activeNavigationId = null;
      }
    }
    if (window.scrollY + innerHeight >= document.documentElement.scrollHeight - 3) current = sections.at(-1);
    let active;
    links.forEach(link => {
      const on = current && link.hash === `#${current.id}`;
      link.classList.toggle('is-active', on);
      if (on) { link.setAttribute('aria-current', 'location'); active = link; }
      else link.removeAttribute('aria-current');
    });
    keepActiveVisible(active);
  };
  const requestUpdate = () => { if (raf === null) raf = requestAnimationFrame(() => { raf = null; updateActive(); }); };
  const notify = (message) => {
    if (!toast) return;
    clearTimeout(toastTimer); toast.textContent = message; toast.hidden = false;
    toastTimer = setTimeout(() => { toast.hidden = true; }, 2200);
  };
  const copy = async (text) => {
    try {
      if (navigator.clipboard && window.isSecureContext) { await navigator.clipboard.writeText(text); return true; }
      const area = document.createElement('textarea'); area.value = text; area.readOnly = true;
      area.style.cssText = 'position:fixed;opacity:0'; document.body.append(area); area.select();
      const ok = document.execCommand('copy'); area.remove(); return ok;
    } catch (_) { return false; }
  };
  const codeText = (node) => {
    const clone = node.cloneNode(true);
    $$('br', clone).forEach(br => br.replaceWith('\n'));
    return (clone.textContent || '').replace(/\u00a0/g, ' ').trim();
  };
  const enhanceCode = () => {
    $$('.code-block').forEach(block => {
      if (block.closest('.code-shell')) return;
      const pre = block.closest('pre');
      if (!pre) return;
      const shell = document.createElement('div'); shell.className = 'code-shell';
      const head = document.createElement('div'); head.className = 'code-head';
      const id = `generated-code-${Math.random().toString(36).slice(2)}`;
      block.id = id;
      head.innerHTML = `<span>Source snippet</span><button class="copy-button" type="button" data-copy="#${id}">Copy</button>`;
      const parent = pre.parentNode;
      if (!parent) return;
      parent.replaceChild(shell, pre);
      shell.append(head, pre);
    });
  };
  const openLightbox = (trigger) => {
    images = $$('[data-lightbox]');
    if (!images.length) return;
    imageIndex = images.indexOf(trigger);
    lastLightboxTrigger = trigger;
    showImage();
    lightbox.hidden = false;
    document.body.classList.add('drawer-open');
    $('[data-lightbox-close]')?.focus();
  };
  const showImage = () => {
    const item = images[imageIndex]; if (!item) return;
    lightboxImage.src = item.dataset.lightbox; lightboxImage.alt = $('img', item)?.alt || '';
    lightboxCaption.textContent = item.dataset.caption || item.alt || 'Screenshot';
    lightboxCounter.textContent = `${imageIndex + 1} / ${images.length}`;
  };
  const closeLightbox = () => {
    if (!lightbox || lightbox.hidden) return;
    lightbox.hidden = true; document.body.classList.remove('drawer-open');
    if (lastLightboxTrigger?.focus) lastLightboxTrigger.focus();
  };
  const moveLightbox = (delta) => { if (!images.length) return; imageIndex = (imageIndex + delta + images.length) % images.length; showImage(); };

  tocToggle?.addEventListener('click', () => { lastFocus = document.activeElement; setDrawer(!toc.classList.contains('is-open'), true); });
  $('[data-drawer-close]')?.addEventListener('click', () => setDrawer(false, true));
  scrim?.addEventListener('click', () => setDrawer(false, true));
  links.forEach(link => link.addEventListener('click', event => { event.preventDefault(); const id = decodeURIComponent(link.hash.slice(1)); setActiveLink(id); scrollTo(document.getElementById(id)); setHash(link.hash); if (mediaQuery.matches) setDrawer(false); }));
  $$('[data-scroll-to]').forEach(button => button.addEventListener('click', () => { const id = button.dataset.scrollTo; setActiveLink(id); scrollTo(document.getElementById(id)); setHash(`#${id}`); }));
  document.addEventListener('click', event => {
    const copyButton = event.target.closest('[data-copy]');
    if (copyButton) {
      const source = document.querySelector(copyButton.dataset.copy);
      if (source) copy(codeText(source)).then(ok => { if (ok) { copyButton.textContent = 'Copied'; copyButton.classList.add('is-copied'); notify('Copied to clipboard'); setTimeout(() => { copyButton.textContent = 'Copy'; copyButton.classList.remove('is-copied'); }, 1800); } else notify('Copy failed — select the text manually'); });
    }
    const shot = event.target.closest('[data-lightbox]'); if (shot) openLightbox(shot);
    if (event.target.closest('[data-lightbox-close]')) closeLightbox();
  });
  $('[data-lightbox-prev]')?.addEventListener('click', () => moveLightbox(-1));
  $('[data-lightbox-next]')?.addEventListener('click', () => moveLightbox(1));
  lightbox?.addEventListener('click', event => { if (event.target === lightbox) closeLightbox(); });
  document.addEventListener('keydown', event => {
    if (event.key === 'Tab' && mediaQuery.matches && toc?.classList.contains('is-open')) {
      const focusable = $$('a[href], button:not([disabled])', toc).filter(element => element.offsetParent !== null);
      if (focusable.length) {
        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
        else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
      }
    }
    if (event.key === 'Escape') { closeLightbox(); if (toc?.classList.contains('is-open')) setDrawer(false, true); }
    if (!lightbox.hidden && event.key === 'ArrowLeft') moveLightbox(-1);
    if (!lightbox.hidden && event.key === 'ArrowRight') moveLightbox(1);
  });
  mediaQuery.addEventListener?.('change', event => { if (!event.matches) setDrawer(false); else { toc?.setAttribute('aria-hidden', 'true'); toc?.setAttribute('inert', ''); } });
  window.addEventListener('scroll', requestUpdate, { passive: true }); window.addEventListener('resize', requestUpdate);
  if (mediaQuery.matches) { toc?.setAttribute('aria-hidden', 'true'); toc?.setAttribute('inert', ''); }
  enhanceCode();
  updateActive();
})();
