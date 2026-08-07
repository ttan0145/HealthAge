const stayfitState = {
  routine: null,
  exercises: [],
  remainingSeconds: 360,
  totalSeconds: 360,
  timerId: null,
  isRunning: false,
};

document.addEventListener("DOMContentLoaded", () => {
  bindTimerControls();
  bindModalControls();
  loadRoutine();
});

async function loadRoutine() {
  const list = document.getElementById("exercise-list");

  try {
    const response = await fetch("/api/stayfit/routine/?level=beginner", {
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

  document.getElementById("routine-title").textContent = routine.title;
  document.getElementById("routine-subtitle").textContent = routine.subtitle;
  document.getElementById("routine-level").textContent = titleCase(routine.level);
  document.getElementById("guidance-title").textContent = routine.guidance_tip.title;
  document.getElementById("guidance-copy").textContent = routine.guidance_tip.text;
  document.getElementById("safety-note").textContent = routine.safety_note;
  document.getElementById("guideline-note").textContent = `${routine.guideline_note} Source: ${routine.source.name}.`;

  const seconds = Math.max(60, Number(routine.duration_minutes || 6) * 60);
  setTimerDuration(seconds);
  renderExercises();
}

function renderExercises() {
  const list = document.getElementById("exercise-list");
  list.classList.remove("routine-list--loading");
  list.innerHTML = "";

  stayfitState.exercises.forEach((exercise, index) => {
    const row = document.createElement("article");
    row.className = "sf-step exercise-row exercise-row--interactive";
    row.role = "button";
    row.tabIndex = 0;
    row.addEventListener("click", () => openExerciseModal(exercise));
    row.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        openExerciseModal(exercise);
      }
    });

    const marker = document.createElement("span");
    marker.className = "sf-step-marker";

    const badge = document.createElement("span");
    badge.className = "sf-step-num exercise-index";
    badge.textContent = String(index + 1);
    marker.append(badge);

    const body = document.createElement("span");
    body.className = "sf-step-body exercise-copy";

    const name = document.createElement("strong");
    name.className = "sf-step-title";
    name.textContent = exercise.name;

    const detail = document.createElement("em");
    detail.className = "sf-step-meta";
    detail.textContent = formatExerciseDose(exercise);

    body.append(name, detail);

    const swapButton = document.createElement("button");
    swapButton.type = "button";
    swapButton.className = "sf-pill-btn exercise-swap";
    swapButton.textContent = "Swap";
    swapButton.addEventListener("click", (event) => {
      event.stopPropagation();
      reshuffleExercise(index, swapButton);
    });

    row.append(marker, body, swapButton);
    list.append(row);
  });
}

async function reshuffleExercise(index, button) {
  const current = stayfitState.exercises[index];
  if (!current) return;

  button.disabled = true;
  button.textContent = "Loading";

  try {
    const response = await fetch(`/api/stayfit/reshuffle/?current=${encodeURIComponent(current.id)}&plan=cardio_core`, {
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
