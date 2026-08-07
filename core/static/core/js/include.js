// Loads shared HTML pieces (nav, footer) into any element with
// a data-include attribute, e.g. <div data-include="nav"></div>
// The pieces themselves are plain HTML files served as static
// files by Django from core/static/core/components/.

async function loadIncludes() {
  const slots = document.querySelectorAll("[data-include]");

  await Promise.all(
    Array.from(slots).map(async (slot) => {
      const name = slot.getAttribute("data-include");
      const res = await fetch(`/static/core/components/${name}.html`);
      slot.outerHTML = await res.text();
    })
  );

  markActiveNavLink();
}

function markActiveNavLink() {
  document.querySelectorAll(".lp-topnav-item[href]").forEach((link) => {
    const linkPath = new URL(link.getAttribute("href"), location.origin).pathname;
    if (linkPath === location.pathname) {
      link.classList.add("lp-topnav-item--active");
    }
  });
}

document.addEventListener("DOMContentLoaded", loadIncludes);
