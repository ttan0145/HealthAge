// Fills in the "Matching your profile" loading state with the
// sample risk data below. In the Django version this came from
// a fetch("/api/home") call — here it's just a local object so
// the page works with no backend at all.

const SAMPLE_DATA = {
  top_risk: {
    cause: "Heart disease",
    description: "The leading cause of death for men aged 41 to 59 in Malaysia.",
    note: "Selangor figures are not published for this year, so this uses the national figure for men aged 41 to 59.",
  },
  next_action: {
    type: "screening",
    title: "Book a screening",
    subtitle: "3 government clinics within 5 km. Screening is free under PeKaB40 if you qualify. This is the one thing worth doing first.",
  },
  other_risks: [
    {
      name: "Heart disease",
      level: "High",
      description: "Leading cause of death for men in your age band. Rarely exercising and high work stress raise this further.",
    },
    {
      name: "Stroke",
      level: "Moderate",
      description: "A sudden loss of blood flow to the brain. High work stress is a contributing factor for you.",
    },
    {
      name: "Type 2 diabetes",
      level: "Baseline",
      description: "Your eating pattern keeps this within the national baseline for your profile.",
    },
  ],
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
      <button class="btn-readmore" type="button">
        Read more
        <span class="icon">${ICON_CHEVRON}</span>
      </button>
    </section>
  `;
}

function renderActionCard(action) {
  const isRoutine = action.type === "routine";
  const modifier = isRoutine ? "action-card--routine" : "action-card--screening";
  const icon = isRoutine ? ICON_RUN : ICON_STETHOSCOPE;

  return `
    <button class="action-card ${modifier}" type="button">
      <span class="action-icon">${icon}</span>
      <span class="action-body">
        <p class="action-title">${action.title}</p>
        <p class="action-subtitle">${action.subtitle}</p>
      </span>
      <span class="icon action-chevron">${ICON_CHEVRON}</span>
    </button>
  `;
}


function renderOtherRisks(risks) {
  const cards = risks
    .map(
      (risk) => `
      <div class="risk-card">
        <div class="risk-card-top">
          <span class="risk-card-name">${risk.name}</span>
          <span class="risk-card-right">
            <span class="badge badge--${risk.level}">${risk.level}</span>
            <span class="icon icon--chevron">${ICON_CHEVRON}</span>
          </span>
        </div>
        <p class="risk-card-desc">${risk.description}</p>
      </div>
    `
    )
    .join("");

  return `<div class="risk-cards">${cards}</div>`;
}

function loadDashboard() {
  const data = SAMPLE_DATA;

  document.getElementById("matching-card").outerHTML = renderTopRiskCard(data.top_risk);

  document.getElementById("next-action-area").innerHTML = `
    <div class="section-heading"><h2>What to do next</h2></div>
    ${renderActionCard(data.next_action)}
  `;

  document.getElementById("other-risks-panel").innerHTML = `
    <div class="section-heading">
      <h2>Other risks we checked</h2>
    </div>
    ${renderOtherRisks(data.other_risks)}
  `;
}

// Small delay so the "Matching your profile" state is visible,
// same as the real version did while waiting on the server.
setTimeout(loadDashboard, 600);