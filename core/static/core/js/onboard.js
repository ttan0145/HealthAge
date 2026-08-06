document.querySelectorAll(".chip-input").forEach((input) => {
  input.addEventListener("change", () => {
    input.closest(".chip").classList.toggle("chip--active", input.checked);
  });
});
