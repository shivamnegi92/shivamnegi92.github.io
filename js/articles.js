// Reading progress bar + table-of-contents highlight. Progressive enhancement only.
(function () {
  "use strict";
  var bar = document.createElement("div");
  bar.id = "progress"; bar.setAttribute("aria-hidden", "true");
  document.body.appendChild(bar);
  var article = document.querySelector(".prose");
  function onScroll() {
    if (!article) return;
    var r = article.getBoundingClientRect();
    var total = r.height - window.innerHeight;
    bar.style.width = Math.max(0, Math.min(1, -r.top / (total || 1))) * 100 + "%";
  }
  window.addEventListener("scroll", onScroll, { passive: true }); onScroll();

  var links = document.querySelectorAll(".toc a");
  if (!links.length || !("IntersectionObserver" in window)) return;
  var map = {};
  links.forEach(function (a) { map[a.getAttribute("href").slice(1)] = a; });
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) {
        links.forEach(function (l) { l.classList.remove("on"); l.removeAttribute("aria-current"); });
        var a = map[e.target.id];
        if (a) { a.classList.add("on"); a.setAttribute("aria-current", "true"); }
      }
    });
  }, { rootMargin: "-20% 0px -70% 0px" });
  document.querySelectorAll(".prose h2[id]").forEach(function (h) { io.observe(h); });
})();
