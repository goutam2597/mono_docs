(() => {
  'use strict';

  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));

  const sidebar = $('#admin-sidebar');
  const sidebarToggleBtn = $('#sidebar-toggle-btn');
  const mobileToggleBtn = $('#mobile-toggle-btn');
  const backdrop = $('#sidebar-backdrop');
  const searchInput = $('#sidebar-search-input');
  const navLinks = $$('.sidebar-nav-link');
  const groupLabels = $$('.sidebar-group-label');
  const sections = $$('.doc-section');
  const breadcrumbLabel = $('#active-breadcrumb-label');
  const toast = $('#toast');
  const lightbox = $('#image-lightbox');
  const lightboxImage = $('#lightbox-image');
  const lightboxCaption = $('#lightbox-caption');
  const lightboxCounter = $('#lightbox-counter');

  let toastTimer = null;
  let rafId = null;

  // Restore saved sidebar collapsed state on desktop
  try {
    if (localStorage.getItem('admin-sidebar-collapsed') === '1') {
      document.documentElement.classList.add('admin-sidebar-collapsed');
    }
  } catch (_) {}

  // Desktop sidebar collapse toggle
  sidebarToggleBtn?.addEventListener('click', () => {
    const isCollapsed = document.documentElement.classList.toggle('admin-sidebar-collapsed');
    try {
      localStorage.setItem('admin-sidebar-collapsed', isCollapsed ? '1' : '0');
    } catch (_) {}
  });

  // Mobile sidebar drawer toggle
  const setMobileDrawer = (open) => {
    sidebar?.classList.toggle('is-open', open);
    backdrop?.classList.toggle('is-active', open);
    document.body.classList.toggle('drawer-open', open);
  };

  mobileToggleBtn?.addEventListener('click', () => setMobileDrawer(true));
  backdrop?.addEventListener('click', () => setMobileDrawer(false));

  // Sidebar real-time search filter
  searchInput?.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase().trim();
    navLinks.forEach(link => {
      const text = link.textContent.toLowerCase();
      const match = !query || text.includes(query);
      link.style.display = match ? 'flex' : 'none';
    });

    // Hide empty group labels
    $$('.sidebar-group-items').forEach(group => {
      const visibleLinks = Array.from(group.querySelectorAll('.sidebar-nav-link')).filter(l => l.style.display !== 'none');
      const label = group.previousElementSibling;
      if (label && label.classList.contains('sidebar-group-label')) {
        label.style.display = visibleLinks.length > 0 ? 'block' : 'none';
      }
    });
  });

  // Keyboard shortcut '/' to focus search
  document.addEventListener('keydown', (e) => {
    if (e.key === '/' && document.activeElement !== searchInput && !['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) {
      e.preventDefault();
      searchInput?.focus();
    }
    if (e.key === 'Escape') {
      if (lightbox && !lightbox.hidden) closeLightbox();
      setMobileDrawer(false);
    }
  });

  // Active section tracking on scroll
  const updateActiveSection = () => {
    if (!sections.length) return;
    const headerHeight = 80;
    let currentSection = sections[0];

    sections.forEach(section => {
      const rect = section.getBoundingClientRect();
      if (rect.top <= headerHeight + 40) {
        currentSection = section;
      }
    });

    if (window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 10) {
      currentSection = sections[sections.length - 1];
    }

    if (currentSection) {
      const currentId = currentSection.id;
      navLinks.forEach(link => {
        const isActive = link.dataset.navId === currentId;
        link.classList.toggle('is-active', isActive);
        if (isActive) {
          link.setAttribute('aria-current', 'location');
          if (breadcrumbLabel) {
            breadcrumbLabel.textContent = currentSection.dataset.sectionTitle || link.textContent.trim();
          }
        } else {
          link.removeAttribute('aria-current');
        }
      });
    }
  };

  const requestScrollUpdate = () => {
    if (rafId === null) {
      rafId = requestAnimationFrame(() => {
        rafId = null;
        updateActiveSection();
      });
    }
  };

  window.addEventListener('scroll', requestScrollUpdate, { passive: true });
  window.addEventListener('resize', requestScrollUpdate);

  // Smooth scroll and mobile close on nav click
  navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      const targetId = link.getAttribute('href')?.slice(1);
      const target = document.getElementById(targetId);
      if (target) {
        e.preventDefault();
        const top = Math.max(0, window.scrollY + target.getBoundingClientRect().top - 74);
        window.scrollTo({ top, behavior: 'smooth' });
        try { history.replaceState(null, '', `#${targetId}`); } catch (_) {}
        setMobileDrawer(false);
      }
    });
  });

  // Smooth scroll for buttons with data-scroll-to
  document.querySelectorAll('button[data-scroll-to]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const targetId = btn.getAttribute('data-scroll-to');
      const target = document.getElementById(targetId);
      if (target) {
        const top = Math.max(0, window.scrollY + target.getBoundingClientRect().top - 74);
        window.scrollTo({ top, behavior: 'smooth' });
        try { history.replaceState(null, '', `#${targetId}`); } catch (_) {}
      }
    });
  });

  // Toast notification helper
  const notify = (msg) => {
    if (!toast) return;
    clearTimeout(toastTimer);
    toast.textContent = msg;
    toast.hidden = false;
    toastTimer = setTimeout(() => { toast.hidden = true; }, 2200);
  };

  // Clipboard copy helper
  const copyText = async (text) => {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
        return true;
      }
      const area = document.createElement('textarea');
      area.value = text;
      area.readOnly = true;
      area.style.cssText = 'position:fixed;opacity:0';
      document.body.append(area);
      area.select();
      const ok = document.execCommand('copy');
      area.remove();
      return ok;
    } catch (_) {
      return false;
    }
  };

  // Click delegation for copy buttons
  document.addEventListener('click', (e) => {
    const copyBtn = e.target.closest('[data-copy]');
    if (copyBtn) {
      const targetSelector = copyBtn.dataset.copy;
      const targetEl = document.querySelector(targetSelector);
      if (targetEl) {
        const text = (targetEl.textContent || '').replace(/\u00a0/g, ' ').trim();
        copyText(text).then(ok => {
          if (ok) {
            const origText = copyBtn.textContent;
            copyBtn.textContent = 'Copied!';
            copyBtn.classList.add('is-copied');
            notify('Copied snippet to clipboard');
            setTimeout(() => {
              copyBtn.textContent = origText;
              copyBtn.classList.remove('is-copied');
            }, 1800);
          } else {
            notify('Copy failed — select text manually');
          }
        });
      }
    }

    const lightboxTrigger = e.target.closest('[data-lightbox]');
    if (lightboxTrigger) {
      openLightbox(lightboxTrigger);
    }

    if (e.target.closest('[data-lightbox-close]')) {
      closeLightbox();
    }
  });

  // Keyboard navigation inside the open lightbox
  document.addEventListener('keydown', (e) => {
    if (lightbox && !lightbox.hidden) {
      if (e.key === 'ArrowLeft') moveLightbox(-1);
      if (e.key === 'ArrowRight') moveLightbox(1);
    }
  });

  // Lightbox helpers
  let lightboxImages = [];
  let lightboxIndex = 0;

  const showLightboxImage = () => {
    const trigger = lightboxImages[lightboxIndex];
    if (!trigger || !lightboxImage) return;
    lightboxImage.src = trigger.getAttribute('data-lightbox') || '';
    lightboxImage.alt = trigger.querySelector('img')?.alt || '';
    if (lightboxCaption) lightboxCaption.textContent = trigger.getAttribute('data-caption') || '';
    if (lightboxCounter) lightboxCounter.textContent = `${lightboxIndex + 1} / ${lightboxImages.length}`;
  };

  const openLightbox = (trigger) => {
    if (!lightbox) return;
    lightboxImages = $$('[data-lightbox]');
    if (!lightboxImages.length) return;
    lightboxIndex = Math.max(0, lightboxImages.indexOf(trigger));
    showLightboxImage();
    lightbox.hidden = false;
    lightbox.setAttribute('open', '');
    document.body.classList.add('drawer-open');
  };

  const closeLightbox = () => {
    if (!lightbox || lightbox.hidden) return;
    lightbox.hidden = true;
    lightbox.removeAttribute('open');
    document.body.classList.remove('drawer-open');
  };

  const moveLightbox = (delta) => {
    if (!lightboxImages.length) return;
    lightboxIndex = (lightboxIndex + delta + lightboxImages.length) % lightboxImages.length;
    showLightboxImage();
  };

  document.querySelector('[data-lightbox-prev]')?.addEventListener('click', () => moveLightbox(-1));
  document.querySelector('[data-lightbox-next]')?.addEventListener('click', () => moveLightbox(1));
  lightbox?.addEventListener('click', (e) => {
    if (e.target === lightbox) closeLightbox();
  });

  // Initial update
  updateActiveSection();
})();
