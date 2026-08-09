// Work 1 (frontend): show the cause of death statistics for the user's
// age and gender.
//
// Two jobs on the dashboard:
//   1. Replace the note line in the red "Your top risk" card with the
//      headline statistic for this user's group.
//   2. Open a popup with the full breakdown when "Read more" is clicked.
//
// This file deliberately touches nothing in dashboard.js. It waits for that
// script to finish rendering, then works on the DOM it produced, so the two
// parts stay independent.

(function () {
  // Defined here rather than reused from dashboard.js, so this file does not
  // depend on that one's globals or on script load order.
  const ICON_CHEVRON =
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' +
    '<polyline points="9 18 15 12 9 6"/></svg>';
  const ICON_RUN =
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' +
    '<circle cx="13" cy="4" r="2"/><path d="M9 20l2-6 3 2 2 5"/>' +
    '<path d="M6 14l4-3 2 3 4-2"/></svg>';
  const ICON_STETHOSCOPE =
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' +
    '<path d="M6 3v6a4 4 0 0 0 8 0V3"/><path d="M6 3H4"/><path d="M14 3h2"/>' +
    '<path d="M10 13v3a5 5 0 0 0 10 0v-1"/><circle cx="20" cy="15" r="2"/></svg>';

  // The age and sex come from the profile the user filled in at step 1,
  // which the server holds in the session. Only forward them here if this
  // page was opened with explicit values, otherwise sending a default would
  // override what the user actually answered.
  const params = new URLSearchParams(location.search);
  const forwarded = new URLSearchParams();
  for (const field of ["age", "gender"]) {
    if (params.get(field)) forwarded.set(field, params.get(field));
  }

  const query = forwarded.toString();
  const statsPromise = fetch(
    `/api/cause-of-death/${query ? `?${query}` : ""}`
  ).then((res) => {
    if (!res.ok) throw new Error(`stats request failed: ${res.status}`);
    return res.json();
  });

  // ---------------------------------------------------------------
  // Shared rendering: the ranked bars, used by the popup and available
  // to any other page that wants the same block.
  // ---------------------------------------------------------------

  function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, (c) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
    }[c]));
  }

  function renderRows(stats) {
    const widest = stats.causes.reduce((m, c) => Math.max(m, c.share), 0) || 1;

    return stats.causes.map((cause) => {
      const name = escapeHtml(cause.cause);
      const width = (cause.share / widest) * 100;

      // The whole row is the target, not just the name, so the bar and the
      // percentage are clickable too. Falls back to a plain div for any
      // cause we have no page for.
      const body = `
        <span class="stat-row-top">
          <span class="stat-row-name">${name}</span>
          <span class="stat-row-share">${escapeHtml(cause.share_display)}%</span>
        </span>
        <span class="stat-row-bar">
          <span class="stat-row-fill" style="width: ${width}%"></span>
        </span>`;

      if (!cause.slug) {
        return `<div class="stat-row stat-row--${escapeHtml(cause.level)}">${body}</div>`;
      }

      return `
        <a class="stat-row stat-row--link stat-row--${escapeHtml(cause.level)}"
           href="/readmore/?risk=${encodeURIComponent(cause.slug)}">
          ${body}
          <span class="stat-row-go" aria-hidden="true">${ICON_CHEVRON}</span>
        </a>`;
    }).join("");
  }

  //different age or gender shows a different set of cards. work for the other risk we checked
  function renderRiskCards(causes, stats) {
    return causes.map((cause) => {
      const name = escapeHtml(cause.cause);
      const level = escapeHtml(cause.level);
      // No per-cause lifestyle blurb comes back from this endpoint (that
      // copy lives in risk_engine.py, which isn't wired to the frontend),
      // so fall back to the one number we do have for this cause.
      const description = `${escapeHtml(cause.share_display)}% of deaths among ${escapeHtml(stats.group_label)}.`;

      const body = `
        <div class="risk-card-top">
          <span class="risk-card-name">${name}</span>
          <span class="risk-card-right">
            <span class="badge badge--${level}">${level}</span>
            <span class="icon icon--chevron">${ICON_CHEVRON}</span>
          </span>
        </div>
        <p class="risk-card-desc">${description}</p>`;

      if (!cause.slug) {
        return `<div class="risk-card">${body}</div>`;
      }

      return `
        <a class="risk-card" href="/readmore/?risk=${encodeURIComponent(cause.slug)}">
          ${body}
        </a>`;
    }).join("");
  }

  // ---------------------------------------------------------------
  // 3. "Other risks we checked" panel, ranks 1-3 from the same stats
  // ---------------------------------------------------------------

  function applyOtherRisks(stats) {
    waitFor("#other-risks-panel", (panel) => {
      const heading = `<div class="section-heading"><h2>Other risks we checked</h2></div>`;

      if (!stats.available) {
        panel.innerHTML = `${heading}<p class="stat-modal-loading">${escapeHtml(stats.headline)}</p>`;
        return;
      }

      const top3 = stats.causes.slice(0, 3);
      panel.innerHTML = `${heading}<div class="risk-cards">${renderRiskCards(top3, stats)}</div>`;
    });
  }

  function renderBreakdown(stats) {
    if (!stats.available) {
      return `<p class="stat-modal-loading">${escapeHtml(stats.headline)}</p>`;
    }

    const other = stats.other_share
      ? `<p class="stat-other">All other causes make up the remaining
           ${stats.other_share}%.</p>`
      : "";

    const excluded = stats.exclusion_note
      ? `<p class="stat-excluded">${escapeHtml(stats.exclusion_note)}</p>`
      : "";

    return `
      <div class="stat-rows" data-collapse>${renderRows(stats)}</div>
      ${other}
      ${excluded}
      <p class="stat-source">Source: ${escapeHtml(stats.source)}.
        Figures cover ${escapeHtml(stats.group_label)} and are national,
        not state level.</p>`;
  }

  // ---------------------------------------------------------------
  // 1. Headline statistic in the top risk card
  // ---------------------------------------------------------------

  function applyHeadline(stats) {
    // dashboard.js renders the card on a timer, so wait for it to appear.
    waitFor(".card--risk .risk-note", (note) => {
      const text = note.querySelector("span:last-child");
      if (text) text.textContent = stats.headline;
    });

    // The card's static subtitle says the same thing as the headline note.
    // Swap it for the scale line so the two carry different information.
    waitFor(".card--risk .risk-desc", (desc) => {
      if (stats.subtitle) desc.textContent = stats.subtitle;
    });

    // dashboard.js hardcodes the heading to heart disease. Left alone, a
    // profile whose top cause is something else gets a card that contradicts
    // its own statistics.
    waitFor(".card--risk .risk-title", (title) => {
      if (stats.top) title.textContent = stats.top.cause;
    });

    // Point Read more at the matching explanation. Not every cause has one
    // written, so drop the link rather than send the user to the wrong page.
    // The click handler still opens the popup either way.
    waitFor(".btn-readmore", (link) => {
      if (!stats.top) return;
      if (stats.top.slug) {
        link.setAttribute("href", `/readmore/?risk=${encodeURIComponent(stats.top.slug)}`);
      } else {
        link.removeAttribute("href");
        link.style.cursor = "pointer";
      }
    });

    applyStayFitAction(stats);
    applyOtherRisks(stats);
  }

  function applyStayFitAction(stats) {
    if (!stats.top) return;

    // "High" means the top cause's share clears HIGH_SHARE in statistics.py.
    // Moderate and Baseline both still point at the Stay Fit routine — only
    // a High top risk switches the card over to "find a specialist".
    const isHighRisk = stats.top.level === "High";

    waitFor("#next-action-area .action-card", (card) => {
      card.classList.remove("action-card--routine", "action-card--screening", "action-card--specialist");

      if (isHighRisk) {
        card.setAttribute("href", "https://nsr.org.my/list11.asp");
        card.setAttribute("target", "_blank");
        card.setAttribute("rel", "noopener noreferrer");
        card.classList.add("action-card--specialist");

        const icon = card.querySelector(".action-icon");
        if (icon) icon.innerHTML = ICON_STETHOSCOPE;

        const title = card.querySelector(".action-title");
        if (title) title.textContent = "Find a specialist";

        const subtitle = card.querySelector(".action-subtitle");
        if (subtitle) {
          subtitle.textContent = `${stats.top.cause} is a high risk for you - this is worth discussing with a healthcare professional.`;
        }
        return;
      }

      if (!stats.top.slug) return;

      card.removeAttribute("target");
      card.removeAttribute("rel");
      card.setAttribute("href", `/stayfit/?risk=${encodeURIComponent(stats.top.slug)}`);
      card.classList.add("action-card--routine");

      const icon = card.querySelector(".action-icon");
      if (icon) icon.innerHTML = ICON_RUN;

      const title = card.querySelector(".action-title");
      if (title) title.textContent = "Start a Stay Fit routine";

      const subtitle = card.querySelector(".action-subtitle");
      if (subtitle) {
        subtitle.textContent = `Exercise suggestions matched to ${stats.top.cause.toLowerCase()}, your current top risk.`;
      }
    });
  }

  function waitFor(selector, done, timeoutMs = 5000) {
    const existing = document.querySelector(selector);
    if (existing) return done(existing);

    const observer = new MutationObserver(() => {
      const el = document.querySelector(selector);
      if (el) {
        observer.disconnect();
        done(el);
      }
    });

    observer.observe(document.body, { childList: true, subtree: true });
    setTimeout(() => observer.disconnect(), timeoutMs);
  }

  // ---------------------------------------------------------------
  // 2. The popup
  // ---------------------------------------------------------------

  let lastFocused = null;

  function openModal(fallbackHref) {
    lastFocused = document.activeElement;

    const backdrop = document.createElement("div");
    backdrop.className = "stat-modal-backdrop";
    backdrop.innerHTML = `
      <div class="stat-modal" role="dialog" aria-modal="true"
           aria-label="Cause of death statistics">
        <button class="stat-modal-close" type="button" aria-label="Close">&times;</button>
        <div class="stat-modal-body">
          <p class="stat-modal-loading">Loading the figures for your group&hellip;</p>
        </div>
      </div>`;

    document.body.appendChild(backdrop);
    document.body.style.overflow = "hidden";

    backdrop.querySelector(".stat-modal-close").addEventListener("click", closeModal);
    backdrop.addEventListener("click", (e) => {
      if (e.target === backdrop) closeModal();
    });
    document.addEventListener("keydown", onKeydown);
    backdrop.querySelector(".stat-modal-close").focus();

    statsPromise.then((stats) => {
      const body = backdrop.querySelector(".stat-modal-body");
      if (!body) return;
      body.innerHTML = `
        <p class="stat-modal-eyebrow">Your group</p>
        <h2 class="stat-modal-title">Causes of death,
          ${escapeHtml(stats.group_label)}</h2>
        <p class="stat-modal-headline">${escapeHtml(stats.headline)}</p>
        ${renderBreakdown(stats)}
        ${stats.top && stats.top.slug ? `
        <div class="stat-modal-foot">
          <a class="rm-link-pill" href="/readmore/?risk=${encodeURIComponent(stats.top.slug)}">
            Read more about ${escapeHtml(stats.top.cause.toLowerCase())}
          </a>
        </div>` : ""}`;

      // Collapse to the top few now that the rows are in the document.
      if (window.applyStatCollapse) window.applyStatCollapse(body);
    }).catch(() => {
      const body = backdrop.querySelector(".stat-modal-body");
      // If the statistics cannot be loaded, send the user to the full page
      // rather than leaving them looking at a broken popup.
      if (body) {
        body.innerHTML = `
          <p class="stat-modal-loading">Could not load the figures just now.</p>
          <a class="rm-link-pill" href="${escapeHtml(fallbackHref)}">
            Read the full explanation
          </a>`;
      }
    });
  }

  function closeModal() {
    const backdrop = document.querySelector(".stat-modal-backdrop");
    if (backdrop) backdrop.remove();
    document.body.style.overflow = "";
    document.removeEventListener("keydown", onKeydown);
    if (lastFocused) lastFocused.focus();
  }

  function onKeydown(e) {
    if (e.key === "Escape") closeModal();
  }

  // Delegated, so it works no matter when dashboard.js renders the button.
  // Modified clicks (new tab, new window) fall through to the real link.
  document.addEventListener("click", (e) => {
    const link = e.target.closest(".btn-readmore");
    if (!link) return;
    if (e.metaKey || e.ctrlKey || e.shiftKey || e.button !== 0) return;

    e.preventDefault();
    openModal(link.getAttribute("href") || "/readmore/");
  });

  statsPromise.then(applyHeadline).catch((err) => {
    // Leave the original note in place if the request fails.
    console.warn("Cause of death statistics unavailable:", err);
  });
})();