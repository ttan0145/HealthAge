// Collapses a ranked cause list down to the top few, with a button to
// reveal the rest.
//
// Ten rows is a lot to land on, and the tail is mostly sub-2% causes. This
// shows the top three and hides the rest behind "View more".
//
// Used in two places that build their rows differently:
//   - readmore.html renders them server side, picked up on DOMContentLoaded
//   - the dashboard popup builds them in JS, and calls applyStatCollapse()
//     itself once the markup is in the document
//
// Standalone on purpose: no dependency on statistics.js or dashboard.js, and
// safe to load on any page. If the script never runs, every row is simply
// visible, which is the pre-existing behaviour.

(function () {
  const VISIBLE = 3;

  const ICON_CHEVRON_DOWN =
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' +
    '<polyline points="6 9 12 15 18 9"/></svg>';

  function collapse(container) {
    // Guard against running twice over the same list, which would stack
    // duplicate buttons.
    if (container.dataset.collapseReady === "1") return;

    const rows = Array.from(container.children);
    if (rows.length <= VISIBLE) return;

    container.dataset.collapseReady = "1";
    const hidden = rows.slice(VISIBLE);

    const button = document.createElement("button");
    button.type = "button";
    button.className = "stat-more";

    let open = false;

    function apply() {
      hidden.forEach((row) => row.classList.toggle("stat-row--hidden", !open));
      const label = open ? "Show less" : "View more";
      const icon = open ? "stat-more-icon stat-more-icon--up" : "stat-more-icon";
      button.innerHTML =
        `<span class="stat-more-label">${label}</span>` +
        `<span class="${icon}">${ICON_CHEVRON_DOWN}</span>`;
      button.setAttribute("aria-expanded", String(open));
    }

    button.addEventListener("click", () => {
      open = !open;
      apply();
    });

    apply();
    container.insertAdjacentElement("afterend", button);
  }

  function applyStatCollapse(root) {
    const scope = root || document;
    scope.querySelectorAll(".stat-rows[data-collapse]").forEach(collapse);
  }

  // Exposed so the dashboard popup can collapse rows it injected later.
  window.applyStatCollapse = applyStatCollapse;

  document.addEventListener("DOMContentLoaded", () => applyStatCollapse());
})();
