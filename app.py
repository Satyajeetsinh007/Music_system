import mysql.connector
import random
from flask import Flask, render_template,request,flash,redirect,url_for
from flask import session

app = Flask(__name__)
app.secret_key = "my-secret-key"

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",      # default XAMPP password is empty
    database="music_db"
)

@app.route("/mainapp")
def home():
    if "user_id" not in session:
        return {"status": "error", "message": "Not logged in"}

    user_id = session["user_id"]

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM songs")
    songs = cursor.fetchall()
    if "user_id" not in session:  #doubt-->userid??
        return redirect(url_for("login"))

    user_id = session["user_id"]

    cursor.execute("""
        SELECT songs.*
        FROM liked_songs
        JOIN songs ON liked_songs.song_id = songs.id
        WHERE liked_songs.user_id = %s
    """, (user_id,))
    liked_songs = cursor.fetchall()

    cursor.execute("SELECT * FROM playlists WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
    playlists = cursor.fetchall()

    cursor.close()

    return render_template(
        "index.html",
        songs=songs,
        liked_songs=liked_songs,
        playlists=playlists
    )

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (email, password)
        )
        user = cursor.fetchone()

        cursor.close()

        if user:
            # login successful
            session["user_id"] = user["id"]   # ⭐ store in session
            session["username"] = user["username"]
            return redirect(url_for("home"))
        else:
            flash("Invalid email or password")
            return redirect(url_for("login"))
    return render_template("login.html")


@app.route("/song/<int:song_id>")
def play_song(song_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = session["user_id"]

    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM songs WHERE id=%s", (song_id,))
    song = cursor.fetchone()

    cursor.execute(
        "SELECT * FROM liked_songs WHERE user_id=%s AND song_id=%s",
        (user_id, song_id)
    )
    liked = cursor.fetchone()  # None or row

    cursor.execute("""
        SELECT songs.*
        FROM liked_songs
        JOIN songs ON liked_songs.song_id = songs.id
        WHERE liked_songs.user_id = %s
    """, (user_id,))
    liked_songs = cursor.fetchall()

    cursor.execute(
        "SELECT * FROM songs WHERE genre=%s AND id!=%s",
        (song["genre"], song_id)
    )
    related = cursor.fetchall()

    cursor.execute("SELECT * FROM playlists WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
    playlists = cursor.fetchall()

    return render_template("song.html", song=song, related_songs=related, liked=liked, liked_songs=liked_songs, playlists=playlists)



@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        cursor = db.cursor(dictionary=True)

        # 1. Check if user already exists
        cursor.execute(
            "SELECT * FROM users WHERE email=%s",
            (email,)
        )
        existing_user = cursor.fetchone()

        if existing_user:
            flash("Email already registered!")
            return redirect(url_for("register"))

        # 2. Insert new user
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
            (username, email, password)
        )
        db.commit()

        cursor.close()

        # 3. Redirect to login page
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/api/search")
def api_search():
    query = request.args.get("q")

    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, title, artist, image FROM songs  WHERE title LIKE %s OR artist LIKE %s LIMIT 5",
        (f"%{query}%", f"%{query}%")
    )
    songs = cursor.fetchall()
    cursor.close()

    return songs  # Flask auto converts to JSON




@app.route("/random")
def random_song():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM songs")
    songs = cursor.fetchall()
    cursor.close()

    song = random.choice(songs)
    return redirect(url_for("play_song", song_id=song["id"]))


@app.route("/like/<int:song_id>")
def like_song(song_id):

    if "user_id" not in session:
        return {"status": "error", "message": "Not logged in"}

    user_id = session["user_id"]
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM liked_songs WHERE user_id=%s AND song_id=%s",
        (user_id, song_id)
    )
    existing = cursor.fetchone()

    if existing:
        # already liked → unlike
        cursor.execute(
            "DELETE FROM liked_songs WHERE user_id=%s AND song_id=%s",
            (user_id, song_id)
        )
        db.commit()
        cursor.close()

        return {
            "status": "unliked",
            "song_id": song_id
        }

    else:
        # not liked → like
        cursor.execute(
            "INSERT INTO liked_songs (user_id, song_id) VALUES (%s, %s)",
            (user_id, song_id)
        )

        cursor.execute("SELECT * FROM songs WHERE id=%s", (song_id,))
        song = cursor.fetchone()

        db.commit()
        cursor.close()

        return {
            "status": "liked",
            "song": song
        }
    
@app.route("/create_playlist", methods=["POST"])
def create_playlist():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    user_id = session["user_id"]
    name = request.form.get("name")
    
    if name:
        cursor = db.cursor()
        cursor.execute("INSERT INTO playlists (user_id, name) VALUES (%s, %s)", (user_id, name))
        playlist_id = cursor.lastrowid
        db.commit()
        cursor.close()
        flash("Playlist created!")
        return redirect(url_for("view_playlist", playlist_id=playlist_id))
        
    return redirect(url_for("home"))

@app.route("/playlist/<int:playlist_id>")
def view_playlist(playlist_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
        
    user_id = session["user_id"]
    cursor = db.cursor(dictionary=True)
    
    # Check ownership
    cursor.execute("SELECT * FROM playlists WHERE id=%s AND user_id=%s", (playlist_id, user_id))
    playlist = cursor.fetchone()
    
    if not playlist:
        cursor.close()
        return redirect(url_for("home"))
        
    # Get songs
    cursor.execute("""
        SELECT songs.*, playlist_songs.added_at, playlist_songs.id as link_id
        FROM playlist_songs
        JOIN songs ON playlist_songs.song_id = songs.id
        WHERE playlist_songs.playlist_id = %s
        ORDER BY playlist_songs.added_at DESC
    """, (playlist_id,))
    songs = cursor.fetchall()
    
    # Get all liked songs for sidebar consistency (optional, or we can just fetch all liked songs again)
    # The user asked for "live sidebar updated via fetch + JS", but sidebar usually needs initial state.
    # We'll just fetch liked songs for the layout if needed, but since sidebar is included, we should pass it.
    cursor.execute("""
        SELECT songs.*
        FROM liked_songs
        JOIN songs ON liked_songs.song_id = songs.id
        WHERE liked_songs.user_id = %s
    """, (user_id,))
    liked_songs = cursor.fetchall()
    
    # Also fetch playlists for the sidebar
    cursor.execute("SELECT * FROM playlists WHERE user_id=%s ORDER BY created_at DESC", (user_id,))
    playlists = cursor.fetchall()

    cursor.close()
    
    return render_template(
        "playlist.html", 
        playlist=playlist, 
        songs=songs, 
        liked_songs=liked_songs,
        playlists=playlists
    )

@app.route("/add_to_playlist/<int:playlist_id>/<int:song_id>", methods=["POST"])
def add_to_playlist(playlist_id, song_id):
    if "user_id" not in session:
        return {"status": "error", "message": "Login required"}
        
    user_id = session["user_id"]
    cursor = db.cursor(dictionary=True)
    
    # Verify ownership
    cursor.execute("SELECT id FROM playlists WHERE id=%s AND user_id=%s", (playlist_id, user_id))
    if not cursor.fetchone():
        cursor.close()
        return {"status": "error", "message": "Invalid playlist"}
        
    try:
        cursor.execute("INSERT INTO playlist_songs (playlist_id, song_id) VALUES (%s, %s)", (playlist_id, song_id))
        db.commit()
        status = "success"
        message = "Song added to playlist"
    except mysql.connector.Error as err:
        if err.errno == 1062: # Duplicate entry
            status = "info"
            message = "Song already in playlist"
        else:
            status = "error"
            message = str(err)
            
    cursor.close()
    
    # Check if request is AJAX
    if request.is_json or request.args.get('format') == 'json':
        return {"status": status, "message": message}
    
    flash(message)
    return redirect(url_for("home"))

@app.route("/remove_from_playlist/<int:playlist_id>/<int:song_id>", methods=["POST"])
def remove_from_playlist(playlist_id, song_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
        
    user_id = session["user_id"]
    cursor = db.cursor()
    
    # Verify ownership involves the playlist
    cursor.execute("SELECT id FROM playlists WHERE id=%s AND user_id=%s", (playlist_id, user_id))
    if cursor.fetchone():
        cursor.execute("DELETE FROM playlist_songs WHERE playlist_id=%s AND song_id=%s", (playlist_id, song_id))
        db.commit()
        
    cursor.close()
    return redirect(url_for("view_playlist", playlist_id=playlist_id))

@app.route("/delete_playlist/<int:playlist_id>", methods=["POST"])
def delete_playlist(playlist_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
        
    user_id = session["user_id"]
    cursor = db.cursor()
    
    cursor.execute("DELETE FROM playlists WHERE id=%s AND user_id=%s", (playlist_id, user_id))
    db.commit()
    cursor.close()
    
    return redirect(url_for("home"))

@app.route("/logout")
def logout():
    session.clear()   # removes user_id, username, everything
    return redirect(url_for("login"))
