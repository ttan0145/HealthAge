const habitInputs = [...document.querySelectorAll('.chip-input[name="habits"]')];

function updateHabitAvailability() {
  const selectedCount = habitInputs.filter((input) => input.checked).length;

  habitInputs.forEach((input) => {
    const unavailable = selectedCount >= 2 && !input.checked;
    input.disabled = unavailable;
    input.closest(".chip").classList.toggle("chip--disabled", unavailable);
  });
}

document.querySelectorAll(".chip-input").forEach((input) => {
  input.addEventListener("change", () => {
    input.closest(".chip").classList.toggle("chip--active", input.checked);
    updateHabitAvailability();
  });
});

updateHabitAvailability();
