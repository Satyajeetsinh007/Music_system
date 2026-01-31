const audio = document.getElementById("audio");
const playBtn = document.getElementById("playBtn");
const progress = document.getElementById("progress");
const playerBar = document.getElementById("playerBar");
const imageWrapper = document.getElementById("imageWrapper");
let song_time = document.getElementById("song-time");
let song_length = document.getElementById("song_length")
let heart = document.querySelector(".heart");
const closeBtn = document.getElementById("closeSidebar");
let empty = document.querySelector(".empty")


document.addEventListener("DOMContentLoaded", updateEmptyState);
function togglePlay() {
  if (audio.paused) {
    audio.play();
    playBtn.textContent = "⏸";
    playerBar.classList.remove("hidden");
    var time = formatTime(audio.duration)
    song_length.innerText = time;
  } else {
    audio.pause();
    playBtn.textContent = "▶";
  }
}

/* CLICK IMAGE OR BUTTON */
playBtn.addEventListener("click", (e) => {
  e.stopPropagation(); // prevents double trigger
  togglePlay();
});

imageWrapper.addEventListener("click", togglePlay);

function formatTime(time) {
  const min = Math.floor(time / 60);
  const sec = Math.floor(time % 60).toString().padStart(2, "0");
  return `${min}:${sec}`;
}

audio.addEventListener("timeupdate", () => {
  // update time text
  song_time.textContent = formatTime(audio.currentTime);

  // update progress bar
  progress.value = (audio.currentTime / audio.duration) * 100;
});

progress.addEventListener("input", (e) => {
  e.stopPropagation()
  audio.currentTime = (progress.value / 100) * audio.duration;
});


heart.addEventListener("click", async (e) => {
  e.stopPropagation();
  heart.classList.toggle("liked")
  const songId = heart.dataset.id;

  const res = await fetch(`/like/${songId}`);
  const data = await res.json();

  updateSidebar(data);

});

const toggleBtn = document.getElementById("toggleSidebar");
const sidebar = document.querySelector(".sidebar");

toggleBtn.addEventListener("click", () => {
  sidebar.classList.toggle("open");
});

function updateSidebar(data) {
  const sidebar = document.querySelector(".sidebar");

  if (data.status === "liked") {
    // Prevent duplicates
    if (sidebar.querySelector(`[data-id="${data.song.id}"]`)) return;

    const song = data.song;
    const a = document.createElement("a");
    a.href = `/song/${song.id}`;
    a.className = "sidebar-song";
    a.dataset.id = song.id;

    a.innerHTML = `
      <img src="/static/images/${song.image}">
      <span>${song.title}</span>
    `;

    // Insert before the <hr> (separator between liked songs and playlists)
    const separator = sidebar.querySelector("hr");
    if (separator) {
      sidebar.insertBefore(a, separator);
    } else {
      // Fallback if no hr found (shouldn't happen with current template)
      sidebar.appendChild(a);
    }
  }

  if (data.status === "unliked") {
    const el = sidebar.querySelector(`[data-id="${data.song_id}"]`);
    if (el) el.remove();
  }
  updateEmptyState();
}


closeBtn.addEventListener("click", () => {
  sidebar.classList.remove("open");
});

function updateEmptyState() {
  const sidebar = document.querySelector(".sidebar");
  // Only select items that have a data-id attribute (which distinguishes songs from playlists)
  const items = sidebar.querySelectorAll(".sidebar-song[data-id]");
  const empty = sidebar.querySelector(".empty");

  if (items.length === 0) {
    empty.style.display = "block";
  } else {
    empty.style.display = "none";
  }
}