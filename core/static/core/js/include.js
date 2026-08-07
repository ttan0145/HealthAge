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
  setFooterYear();
}

function markActiveNavLink() {
  document.querySelectorAll(".lp-topnav-item[data-page]").forEach((link) => {
    if (link.getAttribute("data-page") === location.pathname) {
      link.classList.add("lp-topnav-item--active");
    }
  });
}

document.addEventListener("DOMContentLoaded", loadIncludes);

(function () {
    var minInput = document.getElementById('sfMinInput');
    var secInput = document.getElementById('sfSecInput');
    var addMinBtn = document.getElementById('sfAddMin');
    var startBtn = document.getElementById('sfStartBtn');
    var startLabel = document.getElementById('sfStartLabel');
    var startIcon = document.getElementById('sfStartIcon');
    var timeEl = document.getElementById('sfTime');
    var progressCircle = document.querySelector('.sf-ring-progress');

    var radius = progressCircle.r.baseVal.value;
    var circumference = 2 * Math.PI * radius;
    progressCircle.style.strokeDasharray = circumference + ' ' + circumference;

    var totalSeconds = 6 * 60;
    var remaining = totalSeconds;
    var timerId = null;
    var running = false;

    function clamp(val, min, max) {
      return Math.min(Math.max(val, min), max);
    }

    function formatTime(sec) {
      var m = Math.floor(sec / 60);
      var s = sec % 60;
      return String(m).padStart(2, '0') + ':' + String(s).padStart(2, '0');
    }

    function updateRing() {
      var fraction = totalSeconds === 0 ? 0 : remaining / totalSeconds;
      var offset = circumference * (1 - fraction);
      progressCircle.style.strokeDashoffset = offset;
    }

    function updateDisplay() {
      timeEl.textContent = formatTime(remaining);
      updateRing();
    }

    function syncFromInputs() {
      var m = clamp(parseInt(minInput.value, 10) || 0, 0, 99);
      var s = clamp(parseInt(secInput.value, 10) || 0, 0, 59);
      minInput.value = m;
      secInput.value = s;
      totalSeconds = m * 60 + s;
      remaining = totalSeconds;
      updateDisplay();
    }

    function setRunningState(isRunning) {
      running = isRunning;
      minInput.disabled = isRunning;
      secInput.disabled = isRunning;
      startLabel.textContent = isRunning ? 'Pause' : 'Start';
      startIcon.innerHTML = isRunning
        ? '<rect x="3" y="2.5" width="4" height="11" rx="1" fill="currentColor"/><rect x="9" y="2.5" width="4" height="11" rx="1" fill="currentColor"/>'
        : '<path d="M4 2.5v11l9-5.5-9-5.5z" fill="currentColor"/>';
    }

    function tick() {
      remaining -= 1;
      if (remaining <= 0) {
        remaining = 0;
        updateDisplay();
        clearInterval(timerId);
        timerId = null;
        setRunningState(false);
        return;
      }
      updateDisplay();
    }

    function startTimer() {
      if (remaining <= 0) {
        syncFromInputs();
        if (remaining <= 0) return;
      }
      setRunningState(true);
      timerId = setInterval(tick, 1000);
    }

    function pauseTimer() {
      clearInterval(timerId);
      timerId = null;
      setRunningState(false);
    }

    startBtn.addEventListener('click', function () {
      if (running) {
        pauseTimer();
      } else {
        startTimer();
      }
    });

    addMinBtn.addEventListener('click', function () {
      if (running) return;
      var m = clamp((parseInt(minInput.value, 10) || 0) + 1, 0, 99);
      minInput.value = m;
      syncFromInputs();
    });

    minInput.addEventListener('change', function () {
      if (!running) syncFromInputs();
    });
    secInput.addEventListener('change', function () {
      if (!running) syncFromInputs();
    });

    syncFromInputs();
  })();
