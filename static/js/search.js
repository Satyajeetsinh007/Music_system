const input = document.getElementById("searchInput");
const resultsBox = document.getElementById("searchResults");

input.addEventListener("input", async () => {
  const query = input.value.trim();

  if (query.length < 2) {
    resultsBox.style.display = "none";
    return;
  }

  const res = await fetch(`/api/search?q=${query}`);
  const songs = await res.json();

  resultsBox.innerHTML = "";

  songs.forEach(song => {
    const a = document.createElement("a");
    a.href = `/song/${song.id}`;
    a.className = "search-item";

    a.innerHTML = `
      <img src="/static/images/${song.image}">
      <div>
        <strong>${song.title}</strong><br>
        <small>${song.artist}</small>
      </div>
    `;

    resultsBox.appendChild(a);
  });

  resultsBox.style.display = "block";
});
