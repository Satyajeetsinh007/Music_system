const audio = document.getElementById("audio");
const playBtn = document.getElementById("playBtn");
const progress = document.getElementById("progress");
const playerBar = document.getElementById("playerBar");
const imageWrapper = document.getElementById("imageWrapper");
let song_time=document.getElementById("song-time");
let song_length=document.getElementById("song_length")
let heart = document.querySelector(".heart");

function togglePlay() {
  if (audio.paused) {
    audio.play();
    playBtn.textContent = "⏸";
    playerBar.classList.remove("hidden");
    var time =formatTime(audio.duration)
    song_length.innerText=time;
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

  await fetch(`/like/${songId}`);

});
