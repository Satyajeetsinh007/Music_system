
document.addEventListener('DOMContentLoaded', () => {
    // Check if playlistSongs is defined globally (from the HTML template)
    if (typeof playlistSongs !== 'undefined' && playlistSongs.length > 0) {
        const playerBar = document.getElementById('player-bar');
        if (playerBar) {
            playerBar.style.display = 'flex';
            initPlayer(playlistSongs);
        }
    }
});

let currentSongIndex = 0;
let isPlaying = false;
let audio = new Audio();
let playlist = []; // Will be populated in HTML

// Initialize player with playlist data
function initPlayer(songs) {
    playlist = songs;
    if (playlist.length > 0) {
        loadSong(0, false); // Load first song but don't auto-play
    }
}

function playSongAtIndex(index) {
    loadSong(index, true);
}

// Load song details into player
function loadSong(index, autoPlay = true) {
    if (index < 0 || index >= playlist.length) return;

    currentSongIndex = index;
    const song = playlist[index];

    // Update Audio Source
    audio.src = `/static/songs/${song.file}`;
    audio.load();

    // Update Player UI
    document.getElementById('player-title').innerText = song.title;
    document.getElementById('player-artist').innerText = song.artist;
    document.getElementById('player-image').src = `/static/images/${song.image}`;

    // Highlight active song in list (optional)
    updateActiveSongInList();

    if (autoPlay) {
        playSong();
    }
}

// Play Logic
function playSong() {
    audio.play();
    isPlaying = true;
    updatePlayPauseButton();
}

// Pause Logic
function pauseSong() {
    audio.pause();
    isPlaying = false;
    updatePlayPauseButton();
}

// Toggle Play/Pause
function togglePlay() {
    if (isPlaying) {
        pauseSong();
    } else {
        playSong();
    }
}

// Next Song
function nextSong() {
    let nextIndex = currentSongIndex + 1;
    if (nextIndex >= playlist.length) {
        nextIndex = 0; // Loop back to start
    }
    loadSong(nextIndex);
}

// Previous Song
function prevSong() {
    let prevIndex = currentSongIndex - 1;
    if (prevIndex < 0) {
        prevIndex = playlist.length - 1; // Loop to end
    }
    loadSong(prevIndex);
}

// Update Play/Pause Button Icon
function updatePlayPauseButton() {
    const btn = document.getElementById('play-pause-btn');
    if (isPlaying) {
        btn.innerHTML = '⏸'; // Pause icon
    } else {
        btn.innerHTML = '▶'; // Play icon
    }
}

// Update Progress Bar & Time
audio.addEventListener('timeupdate', () => {
    const progressBar = document.getElementById('player-progress');
    const currentTimeEl = document.getElementById('current-time');
    const totalDurationEl = document.getElementById('total-duration');

    if (audio.duration) {
        const progress = (audio.currentTime / audio.duration) * 100;
        progressBar.value = progress;

        // Update Time Text
        if (currentTimeEl) currentTimeEl.innerText = formatTime(audio.currentTime);
        if (totalDurationEl) totalDurationEl.innerText = formatTime(audio.duration);
    }
});

// Set duration when metadata loads
audio.addEventListener('loadedmetadata', () => {
    const totalDurationEl = document.getElementById('total-duration');
    if (totalDurationEl && audio.duration) {
        totalDurationEl.innerText = formatTime(audio.duration);
    }
});

function formatTime(seconds) {
    const min = Math.floor(seconds / 60);
    const sec = Math.floor(seconds % 60).toString().padStart(2, '0');
    return `${min}:${sec}`;
}

// Seek functionality
document.getElementById('player-progress').addEventListener('input', (e) => {
    const value = e.target.value;
    const duration = audio.duration;
    audio.currentTime = (value / 100) * duration;
});

// Auto-play next song when ended
audio.addEventListener('ended', nextSong);

// Helper: Update active class in list
function updateActiveSongInList() {
    document.querySelectorAll('.list-group-item').forEach((item, idx) => {
        if (idx === currentSongIndex) {
            item.classList.add('active-song'); // We'll add this class in CSS
            item.style.backgroundColor = '#333'; // Inline fallback
        } else {
            item.classList.remove('active-song');
            item.style.backgroundColor = '';
        }
    });
}
