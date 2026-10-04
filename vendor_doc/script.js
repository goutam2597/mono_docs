(() => {
  'use strict';

  const tocDrawer = document.querySelector('[data-toc-drawer]');
  const tocToggle = document.getElementById('toc-toggle');
  const drawerScrim = document.querySelector('[data-drawer-scrim]');
  const tocLinks = Array.from(document.querySelectorAll('.toc-group a[href^="#"]'));
  const sections = Array.from(document.querySelectorAll('.doc-panel > .doc-section'));
  const toast = document.getElementById('toast');
  const lightbox = document.getElementById('image-lightbox');
  const lightboxImage = document.getElementById('lightbox-image');
  const lightboxCaption = document.getElementById('lightbox-caption');
  const lightboxCounter = document.getElementById('lightbox-counter');
  const lightboxPrevious = document.querySelector('[data-lightbox-prev]');
  const lightboxNext = document.querySelector('[data-lightbox-next]');
  const mobileDrawerQuery = window.matchMedia('(max-width: 1060px)');

  let lastFocusedElement = null;
  let lastLightboxTrigger = null;
  let toastTimer = null;
  let scrollFrame = null;
  let lightboxItems = [];
  let lightboxIndex = 0;

  function prefersReducedMotion() {
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }

  function stickyDocumentOffset() {
    const headerHeight = document.querySelector('.site-header')?.getBoundingClientRect().height || 0;
    const configuredGap = parseFloat(
      window.getComputedStyle(document.documentElement).getPropertyValue('--scroll-gap'),
    );
    const gap = Number.isFinite(configuredGap) ? configuredGap : 24;
    return Math.ceil(headerHeight + gap);
  }

  function setHash(value) {
    if (!value) return;
    if (window.history && typeof window.history.replaceState === 'function') {
      try {
        window.history.replaceState(null, '', value);
        return;
      } catch (_) {
        // Local-file contexts can reject history replacement; navigation still works.
      }
    }
    window.location.hash = value;
  }

  function scrollToElement(target, behavior) {
    if (!target) return;
    const anchor = target.querySelector(':scope > .section-title') || target;
    const top = Math.max(0, window.scrollY + anchor.getBoundingClientRect().top - stickyDocumentOffset());
    window.scrollTo({
      top,
      behavior: behavior || (prefersReducedMotion() ? 'auto' : 'smooth'),
    });
  }

  function setDrawerAccessibility(isAvailable) {
    if (!tocDrawer) return;
    if (isAvailable) {
      tocDrawer.removeAttribute('aria-hidden');
      tocDrawer.removeAttribute('inert');
    } else {
      tocDrawer.setAttribute('aria-hidden', 'true');
      tocDrawer.setAttribute('inert', '');
    }
  }

  function closeDrawer({ restoreFocus = false } = {}) {
    if (!tocDrawer || !tocToggle) return;
    tocDrawer.classList.remove('is-open');
    tocToggle.setAttribute('aria-expanded', 'false');
    document.body.classList.remove('drawer-open');
    if (drawerScrim) drawerScrim.hidden = true;
    setDrawerAccessibility(!mobileDrawerQuery.matches);

    if (restoreFocus && lastFocusedElement && typeof lastFocusedElement.focus === 'function') {
      lastFocusedElement.focus();
    }
  }

  function openDrawer() {
    if (!tocDrawer || !tocToggle) return;
    lastFocusedElement = document.activeElement;
    setDrawerAccessibility(true);
    tocDrawer.classList.add('is-open');
    tocToggle.setAttribute('aria-expanded', 'true');
    document.body.classList.add('drawer-open');
    if (drawerScrim) drawerScrim.hidden = false;
    const firstLink = tocDrawer.querySelector('a[href]');
    if (firstLink) firstLink.focus();
  }

  function keepActiveTocLinkVisible(link) {
    if (!tocDrawer || !link) return;
    const drawerRect = tocDrawer.getBoundingClientRect();
    const linkRect = link.getBoundingClientRect();
    const headerAllowance = drawerRect.width <= 370 ? 76 : 68;
    const visibleTop = drawerRect.top + headerAllowance;
    const visibleBottom = drawerRect.bottom - 16;

    if (linkRect.top < visibleTop) {
      tocDrawer.scrollTop -= visibleTop - linkRect.top;
    } else if (linkRect.bottom > visibleBottom) {
      tocDrawer.scrollTop += linkRect.bottom - visibleBottom;
    }
  }

  function updateActiveSection() {
    if (!sections.length) return;
    const marker = stickyDocumentOffset() + 4;
    let current = sections[0];

    sections.forEach((section) => {
      if (section.getBoundingClientRect().top <= marker) current = section;
    });

    if (window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 3) {
      current = sections[sections.length - 1];
    }

    let activeLink = null;
    tocLinks.forEach((link) => {
      const selected = Boolean(current && link.getAttribute('href') === `#${current.id}`);
      link.classList.toggle('is-active', selected);
      if (selected) {
        link.setAttribute('aria-current', 'location');
        activeLink = link;
      } else {
        link.removeAttribute('aria-current');
      }
    });

    keepActiveTocLinkVisible(activeLink);
  }

  function requestActiveSectionUpdate() {
    if (scrollFrame !== null) return;
    scrollFrame = window.requestAnimationFrame(() => {
      scrollFrame = null;
      updateActiveSection();
    });
  }

  function syncFromLocation() {
    const hash = window.location.hash;
    if (!hash || hash === '#top' || hash === '#main-content') return;
    const targetId = decodeURIComponent(hash.slice(1));
    const target = document.getElementById(targetId);
    if (!target) return;
    window.setTimeout(() => scrollToElement(target, 'auto'), 0);
  }

  function showToast(message) {
    if (!toast) return;
    window.clearTimeout(toastTimer);
    toast.textContent = message;
    toast.hidden = false;
    toastTimer = window.setTimeout(() => {
      toast.hidden = true;
    }, 2300);
  }

  async function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      try {
        await navigator.clipboard.writeText(text);
        return;
      } catch (_) {
        // Fall through to the file-compatible selection method.
      }
    }

    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.setAttribute('readonly', '');
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();

    try {
      const copied = document.execCommand('copy');
      if (!copied) throw new Error('Copy failed');
    } finally {
      textarea.remove();
    }
  }

  function codeText(block) {
    const clone = block.cloneNode(true);
    clone.querySelectorAll('br').forEach((lineBreak) => lineBreak.replaceWith('\n'));
    return (clone.textContent || '').replace(/\u00a0/g, ' ').trim();
  }

  function nearestHeadingText(element) {
    const section = element.closest('.doc-section');
    if (!section) return 'Source snippet';
    const headings = Array.from(section.querySelectorAll('.section-title, .heading-2, .heading-3'));
    let candidate = null;

    headings.forEach((heading) => {
      if (heading === element || heading.contains(element)) return;
      const relation = heading.compareDocumentPosition(element);
      if (relation & Node.DOCUMENT_POSITION_FOLLOWING) candidate = heading;
    });

    const localStrong = element.closest('.info-block, li')?.querySelector('strong');
    const text = (candidate?.textContent || localStrong?.textContent || 'Source snippet')
      .replace(/\s+/g, ' ')
      .trim();
    return text.length > 58 ? `${text.slice(0, 55)}…` : text;
  }

  function enhanceCodeBlocks() {
    document.querySelectorAll('.doc-panel .code-block, .doc-panel .code-block-run').forEach((block) => {
      if (block.closest('.code-shell')) return;
      const shell = document.createElement('div');
      const head = document.createElement('div');
      const label = document.createElement('span');
      const button = document.createElement('button');
      const isCommand = block.classList.contains('code-block-run') || codeText(block).split('\n').length === 1;

      shell.className = `code-shell${isCommand ? ' code-shell--command' : ''}`;
      head.className = 'code-head';
      label.textContent = nearestHeadingText(block);
      button.className = 'copy-button';
      button.type = 'button';
      button.dataset.copyButton = '';
      button.textContent = 'Copy';
      button.setAttribute('aria-label', `Copy ${label.textContent}`);

      block.before(shell);
      head.append(label, button);
      shell.append(head, block);
      block.classList.add('code-block');
      block.setAttribute('tabindex', '0');
    });
  }

  async function handleCopy(button) {
    const block = button.closest('.code-shell')?.querySelector('.code-block');
    if (!block) return;

    try {
      await copyText(codeText(block));
      const previous = button.textContent;
      button.textContent = 'Copied';
      button.classList.add('is-copied');
      showToast('Command copied to clipboard.');
      window.setTimeout(() => {
        button.textContent = previous;
        button.classList.remove('is-copied');
      }, 1800);
    } catch (_) {
      showToast('Copy failed. Select the command text manually.');
    }
  }

  function enhanceImages() {
    document.querySelectorAll('.doc-panel img[src^="assets/"]').forEach((image) => {
      if (image.closest('.image-trigger')) return;
      const trigger = document.createElement('button');
      const overlay = document.createElement('span');
      const source = image.getAttribute('src');
      const alt = image.alt || 'Vendor app screenshot';

      trigger.className = 'image-trigger';
      trigger.type = 'button';
      trigger.dataset.lightbox = source;
      trigger.dataset.lightboxCaption = alt;
      trigger.setAttribute('aria-label', `Enlarge image: ${alt}`);
      overlay.className = 'image-overlay';
      overlay.setAttribute('aria-hidden', 'true');
      overlay.textContent = 'Open image';

      image.before(trigger);
      trigger.append(image, overlay);
      image.loading = 'lazy';
      image.decoding = 'async';
    });

    document.querySelectorAll('.packages-table').forEach((table, index) => {
      if (!table.hasAttribute('aria-label')) {
        table.setAttribute('aria-label', `Vendor documentation table ${index + 1}`);
      }

      const headers = Array.from(table.querySelectorAll('thead th'));
      headers.forEach((header) => header.setAttribute('scope', 'col'));
      table.querySelectorAll('tbody tr').forEach((row) => {
        Array.from(row.children).forEach((cell, cellIndex) => {
          cell.dataset.label = headers[cellIndex]?.textContent.trim() || `Field ${cellIndex + 1}`;
        });
      });
    });
  }

  function enhanceCallouts() {
    document.querySelectorAll('.doc-panel .info-block').forEach((callout) => {
      const text = callout.textContent.replace(/\s+/g, ' ').trim();
      if (/\b(Important|Warning|Common Mistake|Crucial)\b/i.test(text)) {
        callout.classList.add('is-warning');
      }
    });
  }

  function showLightboxItem(index) {
    if (!lightbox || !lightboxImage || !lightboxCaption || !lightboxItems.length) return;
    lightboxIndex = Math.max(0, Math.min(index, lightboxItems.length - 1));
    const trigger = lightboxItems[lightboxIndex];
    const image = trigger.querySelector('img');
    const source = trigger.dataset.lightbox || image?.currentSrc || image?.src;
    if (!source) return;

    lightboxImage.src = source;
    lightboxImage.alt = image?.alt || trigger.dataset.lightboxAlt || 'Vendor app screenshot';
    lightboxCaption.textContent = trigger.dataset.lightboxCaption || image?.alt || '';
    if (lightboxCounter) lightboxCounter.textContent = `${lightboxIndex + 1} / ${lightboxItems.length}`;
    if (lightboxPrevious) lightboxPrevious.disabled = lightboxIndex === 0;
    if (lightboxNext) lightboxNext.disabled = lightboxIndex === lightboxItems.length - 1;
  }

  function openLightbox(trigger) {
    if (!lightbox || !lightboxImage || !lightboxCaption) return;
    const gallery = trigger.closest('.screen-gallery-grid') || trigger.closest('.doc-section') || document;
    lightboxItems = Array.from(gallery.querySelectorAll('[data-lightbox]'));
    const galleryIndex = lightboxItems.indexOf(trigger);
    if (galleryIndex < 0) return;

    lastLightboxTrigger = trigger;
    showLightboxItem(galleryIndex);
    if (typeof lightbox.showModal === 'function') lightbox.showModal();
    else lightbox.setAttribute('open', '');
  }

  function closeLightbox() {
    if (!lightbox) return;
    if (typeof lightbox.close === 'function') lightbox.close();
    else lightbox.removeAttribute('open');
  }

  function focusableDrawerElements() {
    if (!tocDrawer) return [];
    return Array.from(
      tocDrawer.querySelectorAll('a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])'),
    ).filter((element) => element.offsetParent !== null);
  }

  document.addEventListener('click', (event) => {
    const tocLink = event.target.closest('.toc-group a[href^="#"]');
    if (tocLink) {
      event.preventDefault();
      const href = tocLink.getAttribute('href');
      const target = document.getElementById(href.slice(1));
      if (!target) return;

      tocLinks.forEach((link) => {
        const selected = link === tocLink;
        link.classList.toggle('is-active', selected);
        if (selected) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      });
      setHash(href);
      closeDrawer({ restoreFocus: mobileDrawerQuery.matches });
      window.requestAnimationFrame(() => scrollToElement(target));
      return;
    }

    const scrollButton = event.target.closest('[data-scroll-to]');
    if (scrollButton) {
      const target = document.getElementById(scrollButton.dataset.scrollTo);
      if (target) {
        setHash(`#${target.id}`);
        window.requestAnimationFrame(() => scrollToElement(target));
      }
      return;
    }

    const copyButton = event.target.closest('[data-copy-button]');
    if (copyButton) {
      handleCopy(copyButton);
      return;
    }

    const imageTrigger = event.target.closest('[data-lightbox]');
    if (imageTrigger) {
      openLightbox(imageTrigger);
      return;
    }

    if (event.target.closest('[data-drawer-close]')) closeDrawer({ restoreFocus: true });
  });

  if (tocToggle) {
    tocToggle.addEventListener('click', () => {
      if (tocDrawer?.classList.contains('is-open')) closeDrawer({ restoreFocus: true });
      else openDrawer();
    });
  }
  if (drawerScrim) drawerScrim.addEventListener('click', () => closeDrawer({ restoreFocus: true }));

  if (lightbox) {
    lightbox.addEventListener('click', (event) => {
      if (event.target === lightbox) closeLightbox();
    });
    lightbox.addEventListener('close', () => {
      if (lastLightboxTrigger && typeof lastLightboxTrigger.focus === 'function') lastLightboxTrigger.focus();
    });
    lightbox.querySelectorAll('[data-lightbox-close]').forEach((button) => {
      button.addEventListener('click', closeLightbox);
    });
    lightboxPrevious?.addEventListener('click', () => showLightboxItem(lightboxIndex - 1));
    lightboxNext?.addEventListener('click', () => showLightboxItem(lightboxIndex + 1));
  }

  document.addEventListener('keydown', (event) => {
    if (lightbox?.open || lightbox?.hasAttribute('open')) {
      if (event.key === 'ArrowLeft') {
        event.preventDefault();
        showLightboxItem(lightboxIndex - 1);
      } else if (event.key === 'ArrowRight') {
        event.preventDefault();
        showLightboxItem(lightboxIndex + 1);
      } else if (event.key === 'Home') {
        event.preventDefault();
        showLightboxItem(0);
      } else if (event.key === 'End') {
        event.preventDefault();
        showLightboxItem(lightboxItems.length - 1);
      } else if (event.key === 'Escape') {
        event.preventDefault();
        closeLightbox();
      }
      return;
    }

    if (event.key === 'Escape' && tocDrawer?.classList.contains('is-open')) {
      event.preventDefault();
      closeDrawer({ restoreFocus: true });
      return;
    }

    if (event.key !== 'Tab' || !tocDrawer?.classList.contains('is-open')) return;
    const focusable = focusableDrawerElements();
    if (!focusable.length) return;
    const first = focusable[0];
    const last = focusable[focusable.length - 1];

    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  });

  function syncDrawerForViewport() {
    if (!tocDrawer) return;
    if (mobileDrawerQuery.matches) {
      if (!tocDrawer.classList.contains('is-open')) setDrawerAccessibility(false);
      return;
    }
    closeDrawer();
    setDrawerAccessibility(true);
  }

  window.addEventListener('hashchange', syncFromLocation);
  window.addEventListener('load', () => {
    requestActiveSectionUpdate();
    syncFromLocation();
  }, { once: true });
  window.addEventListener('scroll', requestActiveSectionUpdate, { passive: true });
  window.addEventListener('resize', requestActiveSectionUpdate, { passive: true });
  if (typeof mobileDrawerQuery.addEventListener === 'function') {
    mobileDrawerQuery.addEventListener('change', syncDrawerForViewport);
  } else if (typeof mobileDrawerQuery.addListener === 'function') {
    mobileDrawerQuery.addListener(syncDrawerForViewport);
  }

  enhanceCodeBlocks();
  enhanceImages();
  enhanceCallouts();
  syncDrawerForViewport();
  updateActiveSection();
  syncFromLocation();
})();
