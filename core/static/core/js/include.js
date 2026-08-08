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
  const activeSection = currentNavSection();
  document.querySelectorAll(".lp-topnav-item[href]").forEach((link) => {
    link.classList.remove("lp-topnav-item--active");
    if (link.dataset.navSection === activeSection) {
      link.classList.add("lp-topnav-item--active");
    }
  });
}

function currentNavSection() {
  const path = location.pathname;

  if (path === "/stayfit/") return "stayfit";
  if (path === "/source/") {
    return location.hash === "#specialist" ? "specialist" : "sources";
  }
  if (["/dashboard/", "/readmore/", "/profile/", "/lifestyle/"].includes(path)) {
    return "plan";
  }

  return "";
}

document.addEventListener("DOMContentLoaded", loadIncludes);
window.addEventListener("hashchange", markActiveNavLink);
