document.querySelectorAll(".chip").forEach((chip) => {
  chip.addEventListener("click", () => {
    chip.classList.toggle("chip--active");
  });
});
