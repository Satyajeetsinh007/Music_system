const input = document.getElementById("searchInput");
const resultsBox = document.getElementById("searchResults");

input.addEventListener("input", async () => {
  const query = input.value.trim();

  if (query.length < 2) {
    resultsBox.style.display = "none";
    return;
  }

  const res = await fetch(`/api/search?q=${query}`);
  const data = await res.json();
  const songs = data.songs || [];
  const artists = data.artists || [];

  resultsBox.innerHTML = "";

  // 1. Render Artists
  if (artists.length > 0) {
    const artistHeader = document.createElement("div");
    artistHeader.className = "search-header small px-2 mt-2";
    artistHeader.innerText = "Artists";
    resultsBox.appendChild(artistHeader);

    artists.forEach(artist => {
      const a = document.createElement("a");
      a.href = `/artist/${artist.id}`;
      a.className = "search-item d-flex align-items-center p-2 text-decoration-none";

      a.innerHTML = `
          <img src="${artist.image_url ? artist.image_url : '/static/images/' + artist.image}" style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover; margin-right: 10px;">
          <div>
            <strong>${artist.name}</strong>
          </div>
        `;
      resultsBox.appendChild(a);
    });
  }

  // 2. Render Songs
  if (songs.length > 0) {
    const songHeader = document.createElement("div");
    songHeader.className = "search-header small px-2 mt-2";
    songHeader.innerText = "Songs";
    resultsBox.appendChild(songHeader);

    songs.forEach(song => {
      const a = document.createElement("a");
      a.href = `/song/${song.id}`;
      a.className = "search-item d-flex align-items-center p-2 text-decoration-none";

      a.innerHTML = `
          <img src="/static/images/${song.image}" style="width: 40px; height: 40px; border-radius: 5px; object-fit: cover; margin-right: 10px;">
          <div>
            <strong>${song.title}</strong><br>
            <small>${song.artist}</small>
          </div>
        `;
      resultsBox.appendChild(a);
    });
  }

  if (songs.length === 0 && artists.length === 0) {
    resultsBox.innerHTML = '<div class="p-2 text-muted">No results found</div>';
  }

  resultsBox.style.display = "block";
});
