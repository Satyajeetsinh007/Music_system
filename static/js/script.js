const toggleBtn = document.getElementById("toggleSidebar");
const sidebar = document.querySelector(".sidebar");
const closeBtn = document.getElementById("closeSidebar");

document.addEventListener("DOMContentLoaded", updateEmptyState);

toggleBtn.addEventListener("click", () => {
  sidebar.classList.toggle("open");
});

closeBtn.addEventListener("click", () => {
    sidebar.classList.remove("open");
  });


function updateEmptyState() {
  const sidebar = document.querySelector(".sidebar");
  const items = sidebar.querySelectorAll(".sidebar-song");
  const empty = sidebar.querySelector(".empty");

  if (items.length === 0) {
    empty.style.display = "block";
  } else {
    empty.style.display = "none";
  }
}