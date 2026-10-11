// Progressive enhancement only: the page is fully readable without JS.
(function () {
  "use strict";
  document.documentElement.classList.remove("no-js");
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Header background after scrolling past the hero top.
  var header = document.querySelector("header.site");
  function onScroll() { header.classList.toggle("scrolled", window.scrollY > 40); }
  window.addEventListener("scroll", onScroll, { passive: true }); onScroll();

  // Animated numbers, bars, and columns when they enter the viewport.
  function countUp(el) {
    var target = parseFloat(el.dataset.count), dec = (el.dataset.count.split(".")[1] || "").length;
    var suffix = el.dataset.suffix || "";
    if (reduce) { el.textContent = target.toFixed(dec) + suffix; return; }
    var start = null;
    function step(ts) {
      if (!start) start = ts;
      var p = Math.min((ts - start) / 1200, 1), e = 1 - Math.pow(1 - p, 3);
      el.textContent = (target * e).toFixed(dec) + suffix;
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }
  function activate(el) {
    el.classList.add("in");
    el.querySelectorAll("[data-count]").forEach(countUp);
    el.querySelectorAll("[data-w]").forEach(function (f) { f.style.width = f.dataset.w + "%"; });
    el.querySelectorAll("[data-h]").forEach(function (f) { f.style.height = f.dataset.h + "%"; });
  }
  var targets = document.querySelectorAll(".reveal");
  if (reduce) { targets.forEach(activate); }
  else if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { activate(e.target); io.unobserve(e.target); } });
    }, { threshold: 0.15 });
    targets.forEach(function (t) { io.observe(t); });
  } else { targets.forEach(activate); }

  // Publication filters.
  var buttons = document.querySelectorAll(".filters button");
  buttons.forEach(function (b) {
    b.addEventListener("click", function () {
      buttons.forEach(function (x) { x.setAttribute("aria-pressed", String(x === b)); });
      var f = b.dataset.filter;
      document.querySelectorAll(".pub").forEach(function (p) { p.hidden = f !== "all" && p.dataset.type !== f; });
      document.getElementById("pub-status").textContent = "Showing: " + b.textContent;
    });
  });

  // BibTeX copy.
  document.querySelectorAll(".copy").forEach(function (btn) {
    btn.addEventListener("click", function () {
      navigator.clipboard.writeText(btn.previousElementSibling.textContent).then(function () {
        btn.textContent = "Copied"; setTimeout(function () { btn.textContent = "Copy"; }, 1500);
      });
    });
  });

  document.getElementById("year").textContent = new Date().getFullYear();

  // Hero network animation (decorative).
  var canvas = document.getElementById("net");
  if (!canvas || reduce) return;
  var ctx = canvas.getContext("2d"), pts = [], W, H, dpr = Math.min(window.devicePixelRatio || 1, 2);
  function resize() {
    W = canvas.clientWidth; H = canvas.clientHeight;
    canvas.width = W * dpr; canvas.height = H * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    var n = Math.round(Math.min(70, W * H / 16000));
    pts = Array.from({ length: n }, function () {
      return { x: Math.random() * W, y: Math.random() * H, vx: (Math.random() - .5) * .35, vy: (Math.random() - .5) * .35 };
    });
  }
  function frame() {
    ctx.clearRect(0, 0, W, H);
    for (var i = 0; i < pts.length; i++) {
      var a = pts[i]; a.x += a.vx; a.y += a.vy;
      if (a.x < 0 || a.x > W) a.vx *= -1; if (a.y < 0 || a.y > H) a.vy *= -1;
      for (var j = i + 1; j < pts.length; j++) {
        var b = pts[j], d = Math.hypot(a.x - b.x, a.y - b.y);
        if (d < 130) { ctx.strokeStyle = "rgba(140,170,255," + (1 - d / 130) * .35 + ")"; ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke(); }
      }
      ctx.fillStyle = "rgba(160,190,255,.8)"; ctx.beginPath(); ctx.arc(a.x, a.y, 1.6, 0, 6.3); ctx.fill();
    }
    requestAnimationFrame(frame);
  }
  window.addEventListener("resize", resize); resize(); frame();
})();
