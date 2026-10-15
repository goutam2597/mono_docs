/* ============================================================
   MONO MARKETPLACE — JAVASCRIPT CONTROLLER
   Sticky header, scroll-driven phone mockup switcher,
   tabbed panel showcase, metric counters, and lightbox modal.
   ============================================================ */

(function () {
  "use strict";

  /* ---------------- 1. Sticky Header & Mobile Toggle ---------------- */
  var header = document.getElementById("siteHeader");
  var mobileToggle = document.getElementById("mobileToggle");
  var navMenu = document.getElementById("navMenu");

  function handleHeaderScroll() {
    if (window.scrollY > 20) {
      header.classList.add("scrolled");
    } else {
      header.classList.remove("scrolled");
    }
  }
  window.addEventListener("scroll", handleHeaderScroll, { passive: true });
  handleHeaderScroll();

  if (mobileToggle && navMenu) {
    mobileToggle.addEventListener("click", function () {
      var isExpanded = navMenu.classList.toggle("mobile-open");
      mobileToggle.setAttribute("aria-expanded", isExpanded ? "true" : "false");
    });

    navMenu.addEventListener("click", function (e) {
      if (e.target.tagName === "A") {
        navMenu.classList.remove("mobile-open");
        mobileToggle.setAttribute("aria-expanded", "false");
      }
    });
  }

  /* ---------------- 2. Scroll Spy Navigation ---------------- */
  var navLinks = document.querySelectorAll(".nav-list a");
  var spySections = [];
  navLinks.forEach(function (link) {
    var href = link.getAttribute("href");
    if (href && href.startsWith("#") && href.length > 1) {
      var targetSec = document.querySelector(href);
      if (targetSec) {
        spySections.push({ link: link, section: targetSec });
      }
    }
  });

  if ("IntersectionObserver" in window && spySections.length > 0) {
    var navObserver = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            navLinks.forEach(function (l) { l.classList.remove("active"); });
            spySections.forEach(function (item) {
              if (item.section === entry.target) {
                item.link.classList.add("active");
              }
            });
          }
        });
      },
      { rootMargin: "-25% 0px -55% 0px" }
    );
    spySections.forEach(function (item) {
      navObserver.observe(item.section);
    });
  }

  /* ---------------- 3. Metric Number Counters ---------------- */
  var counters = document.querySelectorAll(".counter");
  if ("IntersectionObserver" in window && counters.length > 0) {
    var hasRunCounters = false;
    var counterObserver = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting && !hasRunCounters) {
            hasRunCounters = true;
            runCounters();
            counterObserver.disconnect();
          }
        });
      },
      { threshold: 0.3 }
    );

    var metricStrip = document.querySelector(".metrics-strip");
    if (metricStrip) counterObserver.observe(metricStrip);
  }

  function runCounters() {
    counters.forEach(function (counter) {
      var target = parseInt(counter.getAttribute("data-to"), 10) || 0;
      var current = 0;
      var duration = 1200;
      var steps = 40;
      var stepTime = duration / steps;
      var increment = target / steps;

      var timer = setInterval(function () {
        current += increment;
        if (current >= target) {
          counter.textContent = target;
          clearInterval(timer);
        } else {
          counter.textContent = Math.floor(current);
        }
      }, stepTime);
    });
  }

  /* ---------------- 4. STICKY APP SCROLL MOCKUP CONTROLLER ---------------- */
  // As the user scrolls through the 5 steps on the left, the single phone frame
  // on the right stays sticky and cross-fades the screenshot inside!
  var storySteps = document.querySelectorAll(".story-step");
  var mockupScreens = document.querySelectorAll(".mockup-screen");
  var indicatorDots = document.querySelectorAll(".indicator-dot");

  function switchMockupStep(stepIndex) {
    // Update active story step
    storySteps.forEach(function (step) {
      if (step.getAttribute("data-step") === String(stepIndex)) {
        step.classList.add("active");
      } else {
        step.classList.remove("active");
      }
    });

    // Update phone screen inside mockup
    mockupScreens.forEach(function (screen) {
      if (screen.getAttribute("data-step") === String(stepIndex)) {
        screen.classList.add("active");
      } else {
        screen.classList.remove("active");
      }
    });

    // Update indicator dots
    indicatorDots.forEach(function (dot) {
      if (dot.getAttribute("data-step") === String(stepIndex)) {
        dot.classList.add("active");
      } else {
        dot.classList.remove("active");
      }
    });
  }

  if ("IntersectionObserver" in window && storySteps.length > 0) {
    var stepObserver = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            var stepIdx = entry.target.getAttribute("data-step");
            if (stepIdx !== null) {
              switchMockupStep(stepIdx);
            }
          }
        });
      },
      {
        rootMargin: "-25% 0px -35% 0px",
        threshold: 0.1
      }
    );

    storySteps.forEach(function (step) {
      stepObserver.observe(step);
    });
  }

  // Allow clicking indicator dots to scroll smoothly to that step
  indicatorDots.forEach(function (dot) {
    dot.addEventListener("click", function () {
      var stepIdx = dot.getAttribute("data-step");
      var targetStep = document.querySelector('.story-step[data-step="' + stepIdx + '"]');
      if (targetStep) {
        targetStep.scrollIntoView({ behavior: "smooth", block: "center" });
        switchMockupStep(stepIdx);
      }
    });
  });

  /* ---------------- 5. Panels Tab Switcher ---------------- */
  var panelTabBtns = document.querySelectorAll(".panel-tab-btn");
  var panelShowcaseCards = document.querySelectorAll(".panel-showcase-card");

  panelTabBtns.forEach(function (btn) {
    btn.addEventListener("click", function () {
      var targetId = btn.getAttribute("data-target");

      // Update button state
      panelTabBtns.forEach(function (b) { b.classList.remove("active"); });
      btn.classList.add("active");

      // Update visible showcase card
      panelShowcaseCards.forEach(function (card) {
        if (card.id === targetId) {
          card.classList.add("active");
        } else {
          card.classList.remove("active");
        }
      });
    });
  });

  /* ---------------- 6. Lightbox Fullscreen Screenshot Zoom ---------------- */
  var lightboxModal = document.getElementById("lightboxModal");
  var lightboxImg = document.getElementById("lightboxImg");
  var lightboxCaption = document.getElementById("lightboxCaption");
  var lightboxClose = document.getElementById("lightboxClose");
  var lightboxTriggers = document.querySelectorAll(".lightbox-trigger");

  function openLightbox(src, caption) {
    if (!lightboxModal || !lightboxImg) return;
    lightboxImg.src = src;
    lightboxCaption.textContent = caption || "";
    lightboxModal.classList.add("open");
    lightboxModal.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
  }

  function closeLightbox() {
    if (!lightboxModal) return;
    lightboxModal.classList.remove("open");
    lightboxModal.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
    if (lightboxImg) lightboxImg.src = "";
  }

  lightboxTriggers.forEach(function (trigger) {
    trigger.addEventListener("click", function (e) {
      e.stopPropagation();
      var src = trigger.getAttribute("data-src");
      var caption = trigger.getAttribute("data-caption");
      if (src) openLightbox(src, caption);
    });
  });

  if (lightboxClose) {
    lightboxClose.addEventListener("click", closeLightbox);
  }

  if (lightboxModal) {
    lightboxModal.addEventListener("click", function (e) {
      if (e.target === lightboxModal || e.target.classList.contains("lightbox-container")) {
        closeLightbox();
      }
    });
  }

  /* ---------------- 7. Credential Copy Helper ---------------- */
  document.addEventListener("click", function (e) {
    var copyBtn = e.target.closest(".btn-copy-cred");
    if (!copyBtn) return;

    var text = copyBtn.getAttribute("data-copy") || "";
    if (!text) {
      var wrap = copyBtn.closest(".cred-input-wrap");
      if (wrap) {
        var inp = wrap.querySelector("input");
        if (inp) text = inp.value;
      }
    }

    if (text) {
      function showSuccess() {
        copyBtn.classList.add("copied");
        var existing = copyBtn.querySelector(".copied-badge");
        if (!existing) {
          var badge = document.createElement("span");
          badge.className = "copied-badge";
          badge.textContent = "Copied!";
          copyBtn.appendChild(badge);
        }
        setTimeout(function () {
          copyBtn.classList.remove("copied");
          var badgeToRemove = copyBtn.querySelector(".copied-badge");
          if (badgeToRemove && badgeToRemove.parentNode) {
            badgeToRemove.parentNode.removeChild(badgeToRemove);
          }
        }, 1600);
      }

      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(showSuccess).catch(function () {
          fallbackCopy(text);
        });
      } else {
        fallbackCopy(text);
      }

      function fallbackCopy(str) {
        var tempInput = document.createElement("input");
        tempInput.value = str;
        tempInput.style.position = "fixed";
        tempInput.style.opacity = "0";
        document.body.appendChild(tempInput);
        tempInput.focus();
        tempInput.select();
        try {
          document.execCommand("copy");
          showSuccess();
        } catch (err) {
          console.error("Copy failed", err);
        }
        document.body.removeChild(tempInput);
      }
    }
  });

})();
