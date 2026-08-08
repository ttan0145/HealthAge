// Fills in the "Matching your profile" loading state with the
// sample risk data below. In the Django version this came from
// a fetch("/api/home") call — here it's just a local object so
// the page works with no backend at all.

// "slug" links a risk to its detail page at /readmore/?risk=<slug>.
// The slugs must match the keys in core/risk_content.py.
const SAMPLE_DATA = {
  top_risk: {
    slug: "heart-disease",
    cause: "Heart disease",
    description: "The leading cause of death for men aged 41 to 59 in Malaysia.",
    note: "Selangor figures are not published for this year, so this uses the national figure for men aged 41 to 59.",
  },
  next_action: {
    type: "routine",
    title: "Start a Stay Fit routine",
    subtitle: "Open a beginner exercise routine matched to your current top risk.",
    target: "/stayfit/?risk=heart-disease",
  },
  // other_risks used to be hardcoded here (heart disease / stroke / diabetes
  // for every profile). It's gone: statistics.js fetches the ranked causes
  // for the user's actual age and gender and fills #other-risks-panel with
  // the top 3 once that request resolves, so a different age band shows a
  // different set of cards.
};

const ICON_CHEVRON = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>`;
const ICON_INFO = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>`;
const ICON_RUN = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="13" cy="4" r="2"/><path d="M9 20l2-6 3 2 2 5"/><path d="M6 14l4-3 2 3 4-2"/></svg>`;
const ICON_STETHOSCOPE = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 3v6a4 4 0 0 0 8 0V3"/><path d="M6 3H4"/><path d="M14 3h2"/><path d="M10 13v3a5 5 0 0 0 10 0v-1"/><circle cx="20" cy="15" r="2"/></svg>`;

function renderTopRiskCard(topRisk) {
  const noteHtml = topRisk.note
    ? `<div class="risk-note"><span class="icon">${ICON_INFO}</span><span>${topRisk.note}</span></div>`
    : "";

  return `
    <section class="card card--risk">
      <p class="eyebrow">Your top risk</p>
      <h2 class="risk-title">${topRisk.cause}</h2>
      <p class="risk-desc">${topRisk.description}</p>
      ${noteHtml}
      <a class="btn-readmore" href="/readmore/?risk=${topRisk.slug}">
        Read more
        <span class="icon">${ICON_CHEVRON}</span>
      </a>
    </section>
  `;
}

function renderActionCard(action) {
  const isRoutine = action.type === "routine";
  const modifier = isRoutine ? "action-card--routine" : "action-card--screening";
  const icon = isRoutine ? ICON_RUN : ICON_STETHOSCOPE;
  const target = action.target || (isRoutine ? "/stayfit/" : "/source/#peka");

  return `
    <a class="action-card ${modifier}" href="${target}">
      <span class="action-icon">${icon}</span>
      <span class="action-body">
        <p class="action-title">${action.title}</p>
        <p class="action-subtitle">${action.subtitle}</p>
      </span>
      <span class="icon action-chevron">${ICON_CHEVRON}</span>
    </a>
  `;
}


function loadDashboard() {
  const data = SAMPLE_DATA;

  document.getElementById("matching-card").outerHTML = renderTopRiskCard(data.top_risk);

  document.getElementById("next-action-area").innerHTML = `
    <div class="section-heading"><h2>What to do next</h2></div>
    ${renderActionCard(data.next_action)}
  `;

  // other-risks-panel is left alone here on purpose. dashboard.html already
  // renders its loading skeleton, and statistics.js swaps in the real top-3
  // cards once its fetch resolves. Re-rendering the skeleton on this timer
  // used to race that: the fetch usually beats this 600ms delay, so the real
  // cards would flash in and then get overwritten back to "loading" for good.
}

// Small delay so the "Matching your profile" state is visible,
// same as the real version did while waiting on the server.
setTimeout(loadDashboard, 600);