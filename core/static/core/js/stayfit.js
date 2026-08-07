const stayfitState = {
  routine: null,
  exercises: [],
  selectedRisk: "heart_disease",
  remainingSeconds: 360,
  totalSeconds: 360,
  timerId: null,
  isRunning: false,
};

document.addEventListener("DOMContentLoaded", () => {
  bindTimerControls();
  bindModalControls();
  const params = new URLSearchParams(window.location.search);
  loadRoutine(params.get("risk") || stayfitState.selectedRisk);
});

async function loadRoutine(riskKey = stayfitState.selectedRisk) {
  const list = document.getElementById("exercise-list");
  const params = new URLSearchParams({ level: "beginner" });
  if (riskKey) {
    params.set("risk", riskKey);
  }

  stayfitState.selectedRisk = riskKey || "heart_disease";
  list.classList.add("routine-list--loading");
  list.innerHTML = "<p>Loading exercises...</p>";

  try {
    const response = await fetch(`/api/stayfit/routine/?${params.toString()}`, {
      headers: { Accept: "application/json" },
    });

    if (!response.ok) {
      throw new Error(`Routine API returned ${response.status}`);
    }

    const routine = await response.json();
    applyRoutine(routine);
  } catch (error) {
    list.classList.remove("routine-list--loading");
    list.innerHTML = `
      <div class="routine-error">
        <strong>Routine unavailable</strong>
        <span>Please refresh the page or try again later.</span>
      </div>
    `;
  }
}

function applyRoutine(routine) {
  stayfitState.routine = routine;
  stayfitState.exercises = routine.exercises || [];
  stayfitState.selectedRisk = routine.selected_risk?.key || stayfitState.selectedRisk;

  document.getElementById("routine-title").textContent = routine.title;
  document.getElementById("routine-subtitle").textContent = routine.subtitle;
  document.getElementById("routine-level").textContent = titleCase(routine.level);
  document.getElementById("guidance-title").textContent = routine.guidance_tip.title;
  document.getElementById("guidance-copy").textContent = routine.guidance_tip.text;
  document.getElementById("safety-note").textContent = routine.safety_note;
  document.getElementById("guideline-note").textContent = `${routine.guideline_note} Source: ${routine.source.name}.`;

  const seconds = Math.max(60, Number(routine.duration_minutes || 6) * 60);
  setTimerDuration(seconds);
  renderRiskOptions(routine.risk_options || [], stayfitState.selectedRisk);
  renderExercises();
  syncRiskUrl(stayfitState.selectedRisk);
}

function renderRiskOptions(options, selectedKey) {
  const container = document.getElementById("risk-options");
  if (!container) return;

  container.innerHTML = "";
  options.forEach((option) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `risk-option${option.key === selectedKey ? " risk-option--active" : ""}`;
    button.setAttribute("aria-pressed", option.key === selectedKey ? "true" : "false");
    button.addEventListener("click", () => {
      if (option.key !== stayfitState.selectedRisk) {
        loadRoutine(option.key);
      }
    });

    const label = document.createElement("strong");
    label.textContent = option.label;

    const description = document.createElement("span");
    description.textContent = option.description;

    button.append(label, description);
    container.append(button);
  });
}

function renderExercises() {
  const list = document.getElementById("exercise-list");
  list.classList.remove("routine-list--loading");
  list.innerHTML = "";

  stayfitState.exercises.forEach((exercise, index) => {
    const row = document.createElement("article");
    row.className = "exercise-row exercise-row--interactive";

    const detailButton = document.createElement("button");
    detailButton.type = "button";
    detailButton.className = "exercise-main";
    detailButton.addEventListener("click", () => openExerciseModal(exercise));

    const badge = document.createElement("span");
    badge.className = "exercise-index";
    badge.textContent = String(index + 1);

    const body = document.createElement("span");
    body.className = "exercise-copy";

    const name = document.createElement("strong");
    name.textContent = exercise.name;

    const detail = document.createElement("em");
    detail.textContent = formatExerciseDose(exercise);

    body.append(name, detail);
    detailButton.append(badge, body);

    const swapButton = document.createElement("button");
    swapButton.type = "button";
    swapButton.className = "exercise-swap";
    swapButton.textContent = "Swap";
    swapButton.addEventListener("click", () => reshuffleExercise(index, swapButton));

    row.append(detailButton, swapButton);
    list.append(row);
  });
}

async function reshuffleExercise(index, button) {
  const current = stayfitState.exercises[index];
  if (!current) return;

  button.disabled = true;
  button.textContent = "Loading";

  try {
    const params = new URLSearchParams({
      current: current.id,
      plan: stayfitState.routine?.plan_tag || "cardio_core",
      risk: stayfitState.selectedRisk,
    });
    const response = await fetch(`/api/stayfit/reshuffle/?${params.toString()}`, {
      headers: { Accept: "application/json" },
    });

    if (!response.ok) {
      throw new Error(`Reshuffle API returned ${response.status}`);
    }

    const data = await response.json();
    stayfitState.exercises[index] = data.exercise;
    renderExercises();
  } catch (error) {
    button.disabled = false;
    button.textContent = "Try again";
  }
}

function openExerciseModal(exercise) {
  const modal = document.getElementById("exercise-modal");
  const media = document.getElementById("exercise-modal-media");
  const meta = document.getElementById("exercise-modal-meta");

  document.getElementById("exercise-modal-category").textContent = exercise.category;
  document.getElementById("exercise-modal-title").textContent = exercise.name;
  document.getElementById("exercise-modal-instructions").textContent = exercise.instructions;
  document.getElementById("exercise-modal-source").textContent = exercise.source_note;

  media.innerHTML = "";
  if (exercise.video_url) {
    const video = document.createElement("video");
    video.controls = true;
    video.src = exercise.video_url;
    media.append(video);
  } else if (exercise.image_url) {
    const image = document.createElement("img");
    image.src = exercise.image_url;
    image.alt = `${exercise.name} demonstration`;
    media.append(image);
  } else {
    const placeholder = document.createElement("p");
    placeholder.className = "exercise-modal-placeholder";
    placeholder.textContent = "No image or video is available for this exercise, so use the written instructions below.";
    media.append(placeholder);
  }

  meta.innerHTML = "";
  addMetaRow(meta, "Dose", formatExerciseDose(exercise));
  addMetaRow(meta, "Equipment", exercise.equipment);
  addMetaRow(meta, "Muscles", (exercise.muscles || []).join(", "));

  modal.hidden = false;
  document.body.classList.add("modal-open");
}

function closeExerciseModal() {
  document.getElementById("exercise-modal").hidden = true;
  document.body.classList.remove("modal-open");
}

function bindModalControls() {
  document.querySelectorAll("[data-modal-close]").forEach((control) => {
    control.addEventListener("click", closeExerciseModal);
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      closeExerciseModal();
    }
  });
}

function addMetaRow(meta, label, value) {
  const term = document.createElement("dt");
  term.textContent = label;

  const description = document.createElement("dd");
  description.textContent = value || "Not specified";

  meta.append(term, description);
}

function bindTimerControls() {
  document.getElementById("timer-add-minute").addEventListener("click", () => {
    const minutesInput = document.getElementById("timer-minutes");
    minutesInput.value = Math.min(60, Number(minutesInput.value || 0) + 1);
    syncTimerFromInputs();
  });

  document.getElementById("timer-toggle").addEventListener("click", toggleTimer);
  document.getElementById("timer-reset").addEventListener("click", resetTimer);
  document.getElementById("timer-minutes").addEventListener("change", syncTimerFromInputs);
  document.getElementById("timer-seconds").addEventListener("change", syncTimerFromInputs);
}

function toggleTimer() {
  if (stayfitState.isRunning) {
    pauseTimer();
    return;
  }

  if (stayfitState.remainingSeconds <= 0) {
    stayfitState.remainingSeconds = stayfitState.totalSeconds;
  }

  stayfitState.isRunning = true;
  document.getElementById("timer-toggle").textContent = "Pause";
  document.getElementById("timer-status").textContent = "Timer running.";

  stayfitState.timerId = window.setInterval(() => {
    stayfitState.remainingSeconds -= 1;
    updateTimerDisplay();

    if (stayfitState.remainingSeconds <= 0) {
      completeTimer();
    }
  }, 1000);
}

function pauseTimer() {
  window.clearInterval(stayfitState.timerId);
  stayfitState.timerId = null;
  stayfitState.isRunning = false;
  document.getElementById("timer-toggle").textContent = "Start";
  document.getElementById("timer-status").textContent = "Paused.";
}

function completeTimer() {
  window.clearInterval(stayfitState.timerId);
  stayfitState.timerId = null;
  stayfitState.isRunning = false;
  stayfitState.remainingSeconds = 0;
  document.getElementById("timer-toggle").textContent = "Start";
  document.getElementById("timer-status").textContent = "Workout complete.";
  updateTimerDisplay();
}

function resetTimer() {
  window.clearInterval(stayfitState.timerId);
  stayfitState.timerId = null;
  stayfitState.isRunning = false;
  stayfitState.remainingSeconds = stayfitState.totalSeconds;
  document.getElementById("timer-toggle").textContent = "Start";
  document.getElementById("timer-status").textContent = "Ready when you are.";
  updateTimerDisplay();
}

function syncTimerFromInputs() {
  const minutes = clampNumber(document.getElementById("timer-minutes").value, 1, 60);
  const seconds = clampNumber(document.getElementById("timer-seconds").value, 0, 59);
  setTimerDuration(minutes * 60 + seconds);
}

function setTimerDuration(totalSeconds) {
  stayfitState.totalSeconds = totalSeconds;
  stayfitState.remainingSeconds = totalSeconds;
  document.getElementById("timer-minutes").value = Math.floor(totalSeconds / 60);
  document.getElementById("timer-seconds").value = totalSeconds % 60;
  updateTimerDisplay();
}

function updateTimerDisplay() {
  const minutes = Math.floor(stayfitState.remainingSeconds / 60);
  const seconds = stayfitState.remainingSeconds % 60;
  document.getElementById("timer-display").textContent = `${pad(minutes)}:${pad(seconds)}`;
}

function formatExerciseDose(exercise) {
  if (exercise.duration_seconds) {
    return `${exercise.sets} sets x ${exercise.duration_seconds} sec`;
  }
  return `${exercise.sets} sets x ${exercise.reps} reps`;
}

function clampNumber(value, min, max) {
  const number = Number(value);
  if (Number.isNaN(number)) return min;
  return Math.min(max, Math.max(min, number));
}

function pad(value) {
  return String(value).padStart(2, "0");
}

function titleCase(value) {
  if (!value) return "";
  return value.charAt(0).toUpperCase() + value.slice(1);
}

function syncRiskUrl(riskKey) {
  if (!window.history?.replaceState || !riskKey) return;
  const url = new URL(window.location.href);
  url.searchParams.set("risk", riskKey);
  window.history.replaceState({}, "", `${url.pathname}?${url.searchParams.toString()}`);
}
