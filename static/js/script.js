const toggleBtn = document.getElementById("toggleSidebar");
const sidebar = document.querySelector(".sidebar");
const closeBtn = document.getElementById("closeSidebar");

// document.addEventListener("DOMContentLoaded", updateEmptyState);

toggleBtn.addEventListener("click", () => {
  sidebar.classList.toggle("open");
});

closeBtn.addEventListener("click", () => {
  sidebar.classList.remove("open");
});

// Close sidebar when clicking anywhere outside it
document.addEventListener("click", (e) => {
  if (
    sidebar.classList.contains("open") &&
    !sidebar.contains(e.target) &&
    !toggleBtn.contains(e.target)
  ) {
    sidebar.classList.remove("open");
  }
});


// function updateEmptyState() {
//   // 1. Liked Songs
//   const likedList = document.getElementById("liked-songs-list");
//   if (likedList) {
//     const songs = likedList.querySelectorAll(".sidebar-song");
//     const emptyMsg = likedList.querySelector(".empty");
//     // if (emptyMsg) {
//     //emptyMsg.style.display = songs.length === 0 ? "block" : "none";
//     //}
//   }

//   // 2. Playlists
//   const playlistList = document.getElementById("playlists-list");
//   if (playlistList) {
//     const playlists = playlistList.querySelectorAll(".sidebar-song");
//     const emptyMsg = playlistList.querySelector(".empty");
//     //if (emptyMsg) {
//     //emptyMsg.style.display = playlists.length === 0 ? "block" : "none";
//     // }
//   }
// }