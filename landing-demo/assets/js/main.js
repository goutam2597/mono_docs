/* ============================================================
   MONO MARKETPLACE — LANDING DEMO JAVASCRIPT
   1-click credential copying, smooth image fades, and link safety.
   ============================================================ */

(function () {
  "use strict";

  // 1-click copy for credential values
  document.querySelectorAll(".cred-val").forEach(function (el) {
    el.style.cursor = "pointer";
    el.title = "Click to copy";
    el.addEventListener("click", function () {
      var text = el.innerText.trim();
      navigator.clipboard.writeText(text).then(function () {
        var orig = el.innerText;
        el.innerText = "Copied!";
        el.style.background = "#dcfce7";
        el.style.color = "#15803d";
        setTimeout(function () {
          el.innerText = orig;
          el.style.background = "";
          el.style.color = "";
        }, 1500);
      });
    });
  });

  // Ensure all presentation images load smoothly
  document.querySelectorAll(".presentation-banner-img").forEach(function (img) {
    img.addEventListener("error", function () {
      console.warn("Image load failed:", img.src);
    });
  });
})();
