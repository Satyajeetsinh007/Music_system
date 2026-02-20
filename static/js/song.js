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

const songImage = document.getElementById("songImage");
if (songImage) {
  songImage.addEventListener("click", (e) => {
    e.stopPropagation();
    togglePlay();
  });
}

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
  const list = document.getElementById("liked-songs-list");
  if (!list) return;
  if (data.status === "liked") {
    // Prevent duplicates
    if (list.querySelector(`[data-id="${data.song.id}"]`)) return;

    const song = data.song;
    const a = document.createElement("a");
    a.href = `/song/${song.id}`;
    a.className = "sidebar-song";
    a.dataset.id = song.id;

    a.innerHTML = `
      <img src="/static/images/${song.image}">
      <span>${song.title}</span>
    `;

    list.appendChild(a);
  }

  if (data.status === "unliked") {
    const el = list.querySelector(`[data-id="${data.song_id}"]`);
    if (el) el.remove();
  }
  updateEmptyState();
}


closeBtn.addEventListener("click", () => {
  sidebar.classList.remove("open");
});

function updateEmptyState() {
  const list = document.getElementById("liked-songs-list");
  if (list) {
    const items = list.querySelectorAll(".sidebar-song");
    const empty = list.querySelector(".empty");
    if (empty) {
      empty.style.display = items.length === 0 ? "block" : "none";
    }
  }
}

document.addEventListener("click", (e) => {
  if (
    sidebar.classList.contains("open") &&
    !sidebar.contains(e.target) &&
    !toggleBtn.contains(e.target)
  ) {
    sidebar.classList.remove("open");
  }
});