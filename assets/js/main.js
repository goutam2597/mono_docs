/* Mono Marketplace demo — vanilla JS, no dependencies */
(function () {
  "use strict";

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- loader ---------- */
  var loader = document.getElementById("loader");
  function hideLoader() { if (loader) loader.classList.add("hide"); }
  window.addEventListener("load", function () { setTimeout(hideLoader, 350); });
  setTimeout(hideLoader, 2500); // safety fallback

  /* ---------- nav ---------- */
  var nav = document.getElementById("nav");
  var links = document.getElementById("navLinks");
  var burger = document.getElementById("burger");

  function onScrollNav() {
    if (window.scrollY > 24) nav.classList.add("scrolled");
    else nav.classList.remove("scrolled");
  }
  window.addEventListener("scroll", onScrollNav, { passive: true });
  onScrollNav();

  if (burger && links) {
    burger.addEventListener("click", function () {
      var open = links.classList.toggle("open");
      burger.classList.toggle("open", open);
      burger.setAttribute("aria-expanded", open ? "true" : "false");
    });
    links.addEventListener("click", function (e) {
      if (e.target.tagName === "A") {
        links.classList.remove("open");
        burger.classList.remove("open");
        burger.setAttribute("aria-expanded", "false");
      }
    });
  }

  /* ---------- scroll spy ---------- */
  var navAnchors = document.querySelectorAll(".nav-links a");
  var spySections = [];
  navAnchors.forEach(function (a) {
    var id = a.getAttribute("href");
    if (id && id.charAt(0) === "#") {
      var sec = document.querySelector(id);
      if (sec) spySections.push({ link: a, sec: sec });
    }
  });
  var spy = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      if (en.isIntersecting) {
        navAnchors.forEach(function (a) { a.classList.remove("active"); });
        spySections.forEach(function (s) {
          if (s.sec === en.target) s.link.classList.add("active");
        });
      }
    });
  }, { rootMargin: "-45% 0px -50% 0px" });
  spySections.forEach(function (s) { spy.observe(s.sec); });

  /* ---------- reveal on scroll ---------- */
  document.querySelectorAll(".reveal").forEach(function (el) {
    var d = parseInt(el.getAttribute("data-delay") || "0", 10);
    el.style.setProperty("--d", d);
  });
  var revealOb = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      if (!en.isIntersecting) return;
      en.target.classList.add("in");
      revealOb.unobserve(en.target);
    });
  }, { threshold: 0.12 });
  document.querySelectorAll(".reveal").forEach(function (el) { revealOb.observe(el); });

  /* ---------- counters ---------- */
  function runCounter(el) {
    var to = parseFloat(el.getAttribute("data-to") || "0");
    var dur = 1400, t0 = null;
    function fmt(n) { return Math.round(n).toLocaleString("en-US"); }
    if (reduceMotion) { el.textContent = fmt(to); return; }
    function step(ts) {
      if (!t0) t0 = ts;
      var p = Math.min((ts - t0) / dur, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = fmt(to * eased);
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }
  var countOb = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      if (!en.isIntersecting) return;
      runCounter(en.target);
      countOb.unobserve(en.target);
    });
  }, { threshold: 0.6 });
  document.querySelectorAll(".count").forEach(function (el) { countOb.observe(el); });
})();
