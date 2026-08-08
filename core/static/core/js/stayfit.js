const stayfitState = {
  routine: null,
  exercises: [],
  selectedRisk: "heart_disease",
  activeExerciseIndex: 0,
  carouselId: null,
  isGuidanceHovered: false,
  isModalOpen: false,
  remainingSeconds: 360,
  totalSeconds: 360,
  timerId: null,
  isRunning: false,
};

document.addEventListener("DOMContentLoaded", () => {
  bindTimerControls();
  bindModalControls();
  bindGuidanceCarouselControls();
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
  stopExerciseCarousel();
  renderGuidanceLoading();

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
    renderGuidanceLoading("Exercise demonstration unavailable.");
  }
}

function applyRoutine(routine) {
  stayfitState.routine = routine;
  stayfitState.exercises = routine.exercises || [];
  stayfitState.selectedRisk = routine.selected_risk?.key || stayfitState.selectedRisk;
  stayfitState.activeExerciseIndex = 0;

  document.getElementById("routine-title").textContent = routine.title;
  document.getElementById("routine-subtitle").textContent = routine.subtitle;
  document.getElementById("routine-level").textContent = titleCase(routine.level);
  document.getElementById("guidance-title").textContent = routine.guidance_tip.title;
  document.getElementById("guidance-copy").textContent = routine.guidance_tip.text;
  document.getElementById("safety-note").textContent = routine.safety_note;
  renderGuidelineNote(routine);

  const seconds = Math.max(60, Number(routine.duration_minutes || 6) * 60);
  setTimerDuration(seconds);
  renderRiskOptions(routine.risk_options || [], stayfitState.selectedRisk);
  renderExercises();
  showGuidanceExercise(0);
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
    row.className = `exercise-row exercise-row--interactive${index === stayfitState.activeExerciseIndex ? " exercise-row--active" : ""}`;

    const detailButton = document.createElement("button");
    detailButton.type = "button";
    detailButton.className = "exercise-main";
    detailButton.addEventListener("click", () => {
      showGuidanceExercise(index);
    });

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
    stayfitState.activeExerciseIndex = index;
    renderExercises();
    showGuidanceExercise(index);
  } catch (error) {
    button.disabled = false;
    button.textContent = "Try again";
  }
}

function showGuidanceExercise(index) {
  if (!stayfitState.exercises.length) return;
  const safeIndex = ((index % stayfitState.exercises.length) + stayfitState.exercises.length) % stayfitState.exercises.length;
  stayfitState.activeExerciseIndex = safeIndex;
  renderGuidanceExercise(stayfitState.exercises[safeIndex]);
  updateActiveExerciseRow();
}

function startExerciseCarousel() {
  // The exercise order should remain user-directed. Keep this as a no-op
  // guard so older event hooks never restart the previous auto-rotation.
  stopExerciseCarousel();
}

function stopExerciseCarousel() {
  if (!stayfitState.carouselId) return;
  window.clearInterval(stayfitState.carouselId);
  stayfitState.carouselId = null;
}

function updateActiveExerciseRow() {
  document.querySelectorAll(".exercise-row").forEach((row, index) => {
    row.classList.toggle("exercise-row--active", index === stayfitState.activeExerciseIndex);
  });
}

function bindGuidanceCarouselControls() {
  const panel = document.querySelector(".guidance-panel");
  if (!panel) return;

  panel.tabIndex = 0;
  panel.setAttribute("role", "button");
  panel.setAttribute("aria-label", "Open current exercise demonstration");

  panel.addEventListener("mouseenter", pauseGuidanceCarousel);
  panel.addEventListener("focusin", pauseGuidanceCarousel);
  panel.addEventListener("mouseleave", resumeGuidanceCarousel);
  panel.addEventListener("focusout", resumeGuidanceCarousel);
  panel.addEventListener("click", openCurrentGuidanceExercise);
  panel.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      openCurrentGuidanceExercise();
    }
  });
}

function pauseGuidanceCarousel() {
  stayfitState.isGuidanceHovered = true;
  stopExerciseCarousel();
}

function resumeGuidanceCarousel() {
  stayfitState.isGuidanceHovered = false;
}

function openCurrentGuidanceExercise() {
  const exercise = stayfitState.exercises[stayfitState.activeExerciseIndex];
  if (exercise) {
    openExerciseModal(exercise);
  }
}

function openExerciseModal(exercise) {
  stayfitState.isModalOpen = true;
  stopExerciseCarousel();
  const modal = document.getElementById("exercise-modal");
  const media = document.getElementById("exercise-modal-media");
  const meta = document.getElementById("exercise-modal-meta");

  document.getElementById("exercise-modal-category").textContent = exercise.category;
  document.getElementById("exercise-modal-title").textContent = exercise.name;
  document.getElementById("exercise-modal-instructions").textContent = exercise.instructions;
  document.getElementById("exercise-modal-source").textContent = exercise.source_note;

  renderExerciseMedia(media, exercise, { controls: true });

  meta.innerHTML = "";
  addMetaRow(meta, "Dose", formatExerciseDose(exercise));
  addMetaRow(meta, "Equipment", exercise.equipment);
  addMetaRow(meta, "Muscles", (exercise.muscles || []).join(", "));

  modal.hidden = false;
  document.body.classList.add("modal-open");
}

function renderGuidanceExercise(exercise) {
  const media = document.getElementById("guidance-media");
  if (!media || !exercise) return;

  renderExerciseMedia(media, exercise, { controls: false, mascotFallback: true });
  document.getElementById("guidance-demo-category").textContent = exercise.category || "Exercise demonstration";
  document.getElementById("guidance-demo-position").textContent = `${stayfitState.activeExerciseIndex + 1} / ${stayfitState.exercises.length}`;
  document.getElementById("guidance-demo-title").textContent = exercise.name || "Exercise";
  document.getElementById("guidance-demo-dose").textContent = formatExerciseDose(exercise);
  document.getElementById("guidance-demo-instructions").textContent = exercise.instructions || "Use the written instructions for this exercise.";
  document.getElementById("guidance-demo-source").textContent = exercise.source_note || "";
}

function renderGuidanceLoading(message = "Loading exercise demonstration...") {
  const media = document.getElementById("guidance-media");
  if (!media) return;
  media.innerHTML = `<p class="exercise-modal-placeholder">${message}</p>`;
  document.getElementById("guidance-demo-category").textContent = "Exercise demonstration";
  document.getElementById("guidance-demo-position").textContent = "";
  document.getElementById("guidance-demo-title").textContent = "Loading exercise...";
  document.getElementById("guidance-demo-dose").textContent = "";
  document.getElementById("guidance-demo-instructions").textContent = "";
  document.getElementById("guidance-demo-source").textContent = "";
}

function renderExerciseMedia(container, exercise, options = {}) {
  container.innerHTML = "";
  container.classList.remove("guidance-media--mascot");

  if (exercise.video_url) {
    const video = document.createElement("video");
    video.controls = Boolean(options.controls);
    video.loop = true;
    video.autoplay = true;
    video.muted = true;
    video.playsInline = true;
    video.src = exercise.video_url;
    container.append(video);
    video.play?.().catch(() => {});
    return;
  }

  if (exercise.image_url) {
    const image = document.createElement("img");
    image.src = exercise.image_url;
    image.alt = `${exercise.name} demonstration`;
    container.append(image);
    return;
  }

  const placeholder = document.createElement("p");
  placeholder.className = options.mascotFallback ? "guidance-mascot-fallback" : "exercise-modal-placeholder";
  placeholder.textContent = "No image or video is available for this exercise, so use the written instructions below.";
  if (options.mascotFallback) {
    container.classList.add("guidance-media--mascot");
    placeholder.innerHTML = `<img src="/static/img/grandpa.png" alt="Friendly exercise mascot">`;
  }
  container.append(placeholder);
}

function closeExerciseModal() {
  document.getElementById("exercise-modal").hidden = true;
  document.body.classList.remove("modal-open");
  stayfitState.isModalOpen = false;
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

function renderGuidelineNote(routine) {
  const note = document.getElementById("guideline-note");
  note.innerHTML = "";

  const guideline = routine.guideline || {};
  const source = routine.source || {};
  const guidelineName = guideline.name || "Saranan Aktiviti Fizikal Malaysia";

  note.append("Exercise recommendations align with ");

  if (guideline.url) {
    const guidelineLink = document.createElement("a");
    guidelineLink.href = guideline.url;
    guidelineLink.target = "_blank";
    guidelineLink.rel = "noopener noreferrer";
    guidelineLink.textContent = guidelineName;
    note.append(guidelineLink);
  } else {
    note.append(guidelineName);
  }

  note.append(` and support SDG3 Good Health and Well-Being. Source: ${source.name || "wger.de Exercise Database"}.`);
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
