import mysql.connector
import random
from flask import Flask, render_template, request, flash, redirect, url_for, session
import os
from werkzeug.utils import secure_filename
import string

app = Flask(__name__)
app.secret_key = "my-secret-key"


db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",      # default XAMPP password is empty
    database="music_db"
)

# Configuration
UPLOAD_FOLDER = 'static/songs'
IMAGE_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'ogg'}
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['IMAGE_FOLDER'] = IMAGE_FOLDER

# Helps to check file extension
def allowed_file(filename, extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in extensions

@app.route("/mainapp")
def home():
    # if "user_id" not in session:
    #     return {"status": "error", "message": "Not logged in"}

    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    cursor = db.cursor(dictionary=True)
    # Fetch 8 random songs for Quick Picks
    cursor.execute("SELECT * FROM songs ORDER BY RAND() LIMIT 8")
    songs = cursor.fetchall()
    

    # user_id = session["user_id"]

    cursor.execute("""
        SELECT songs.*
        FROM liked_songs
        JOIN songs ON liked_songs.song_id = songs.id
        WHERE liked_songs.user_id = %s
    """, (user_id,))
    liked_songs = cursor.fetchall()

    cursor.execute("SELECT * FROM playlists WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
    playlists = cursor.fetchall()

    #  NEW: Fetch songs by language 
    language_sections = []
    
    # 1. Get all distinct languages
    cursor.execute("SELECT DISTINCT language FROM songs WHERE language IS NOT NULL AND language != ''")
    languages = [row['language'] for row in cursor.fetchall()]

    for lang in languages:
        # 2. For each language, fetch 4 random songs
        cursor.execute("SELECT * FROM songs WHERE language=%s ORDER BY RAND() LIMIT 4", (lang,))
        lang_songs = cursor.fetchall()
        
        if lang_songs:
            language_sections.append({
                "title": f"{lang} Songs", # e.g. "Hindi Songs"
                "songs": lang_songs
            })


    cursor.close()

    return render_template(
        "index.html",
        songs=songs,
        liked_songs=liked_songs,
        playlists=playlists,
        language_sections=language_sections
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
            session["user_id"] = user["id"]   #  store in session
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
        "SELECT * FROM songs WHERE language=%s AND id!=%s",
        (song["language"], song_id)
    )
    related = cursor.fetchall()

    cursor.execute("SELECT * FROM playlists WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
    playlists = cursor.fetchall()

    # Splits artists for linking
    artist_names = [a.strip() for a in song['artist'].split(',')]
    song_artists = []
    for name in artist_names:
        cursor.execute("SELECT id FROM artists WHERE name = %s", (name,))
        res = cursor.fetchone()
        if res:
            song_artists.append({'name': name, 'id': res['id']})
        else:
            # Fallback if artist distinct record not found (shouldn't happen ideally but good for safety)
            song_artists.append({'name': name, 'id': '#'})

    return render_template("song.html", song=song, related_songs=related, liked=liked, liked_songs=liked_songs, playlists=playlists, song_artists=song_artists)



@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_pass=request.form["confirm_password"]

        if password != confirm_pass:
            flash("password and confirm password doesn't match!")
            return redirect(url_for("register"))

        # Check for spaces in password
        if " " in password:
            flash("Password must not contain spaces")
            return redirect(url_for("register"))

        # Check for Special Characters in password
        flag=True
        for i in string.punctuation:
            if i in password:
                flag=False
                break

        if flag:
            flash("Must contain atleast one special character")
            return redirect(url_for("register"))

        cursor = db.cursor(dictionary=True)

        # 1. Check if email already exists
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

    # 1. Search Songs
    cursor.execute(
        "SELECT id, title, artist, image FROM songs WHERE title LIKE %s OR artist LIKE %s LIMIT 5",
        (f"%{query}%", f"%{query}%")
    )
    songs = cursor.fetchall()

    # 2. Search Artists
    cursor.execute(
        "SELECT id, name, image FROM artists WHERE name LIKE %s LIMIT 5",
        (f"%{query}%",)
    )
    artists = cursor.fetchall()
    
    # Get artist API image
    for artist in artists:
        artist['image_url'] = get_artist_image_url(artist['name'])

    cursor.close()

    return {"songs": songs, "artists": artists}

import requests


# to get artist image from Deezer api
def get_artist_image_url(artist_name):
    try:
        response = requests.get(f"https://api.deezer.com/search/artist?q={artist_name}")
        data = response.json()
        if data and 'data' in data and len(data['data']) > 0:
            return data['data'][0]['picture_xl'] # or picture_medium, picture_big
    except Exception as e:
        print(f"Error fetching artist image: {e}")
    return None

@app.route("/artist/<int:artist_id>")
def artist_page(artist_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = session["user_id"]

    cursor = db.cursor(dictionary=True)

    # 1. Get Artist Details
    cursor.execute("SELECT * FROM artists WHERE id=%s", (artist_id,))
    artist = cursor.fetchone()

    if not artist:
        cursor.close()
        return redirect(url_for("home"))
        
    # Fetch image from API (in Real-time)
    artist_image_url = get_artist_image_url(artist['name'])

    # 2. Get Songs by this Artist
    # Fetch broadly using LIKE, then filter in Python for exact match
    # This matches "Artist A", "Artist A, Artist B", "Artist B, Artist A"
    cursor.execute("SELECT * FROM songs WHERE artist LIKE %s", (f"%{artist['name']}%",))
    potential_songs = cursor.fetchall()
    
    songs = []
    for s in potential_songs:
        # Split song's artist string: "Artist A, Artist B" -> ["Artist A", "Artist B"]
        song_artists = [a.strip() for a in s['artist'].split(',')]
        if artist['name'] in song_artists:
            songs.append(s)

    # 3. Get Liked Songs (for sidebar/heart status)
    cursor.execute("SELECT song_id FROM liked_songs WHERE user_id=%s", (user_id,))
    liked_song_ids = [row['song_id'] for row in cursor.fetchall()]

    # 4. Get Playlists (for sidebar)
    cursor.execute("SELECT * FROM playlists WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
    playlists = cursor.fetchall()

    cursor.close()

    return render_template(
        "artist.html", 
        artist=artist, 
        songs=songs, 
        liked_song_ids=liked_song_ids,
        playlists=playlists,
        artist_image_url=artist_image_url
    )




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
        cursor = db.cursor(dictionary=True) 
        
        # Check if playlist already exists
        cursor.execute("SELECT id FROM playlists WHERE user_id=%s AND name=%s", (user_id, name))
        existing_playlist = cursor.fetchone()
        
        if existing_playlist:
            cursor.close()
            return redirect(url_for("view_playlist", playlist_id=existing_playlist['id']))
            
        # Create new if not exists
        cursor.execute("INSERT INTO playlists (user_id, name) VALUES (%s, %s)", (user_id, name))
        playlist_id = cursor.lastrowid
        db.commit()
        cursor.close()
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
    
    # Get all liked songs for sidebar consistency
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
    except mysql.connector.Error as err:
        print(err)
            
    cursor.close()
    
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

@app.route("/admin", methods=["GET", "POST"])
def admin_panel():
    # 1. Handle Login
    if request.method == "POST":
        passkey = request.form.get("passkey")
        if passkey == "admin123":
            session["is_admin"] = True
            return redirect(url_for("admin_panel"))
        else:
            flash("Incorrect Admin Passkey!", "error")
            return redirect(url_for("admin_panel"))

    # 2. Check Admin Session
    if not session.get("is_admin"):
        return render_template("admin.html", mode="login")

    # 3. Show Dashboard
    return render_template("admin.html", mode="dashboard")


@app.route("/admin/add_song", methods=["POST"])
def admin_add_song():
    if not session.get("is_admin"):
        return redirect(url_for("admin_panel"))

    title = request.form.get("title")
    artist = request.form.get("artist")
    # genre = request.form.get("genre") # Removed
    language = request.form.get("language")
    
    # File Handling
    if 'image' not in request.files or 'song' not in request.files:
        flash("No file part", "error")
        return redirect(url_for("admin_panel"))

    image_file = request.files['image']
    song_file = request.files['song']

    if image_file.filename == '' or song_file.filename == '':
        flash("No selected file", "error")
        return redirect(url_for("admin_panel"))

    # Save Image
    if image_file and allowed_file(image_file.filename, ALLOWED_IMAGE_EXTENSIONS):
        image_filename = secure_filename(image_file.filename)
        image_path = os.path.join(app.config['IMAGE_FOLDER'], image_filename)
        image_file.save(image_path)
    else:
        flash("Invalid Image Format", "image_error")
        return redirect(url_for("admin_panel"))

    # Save Song
    if song_file and allowed_file(song_file.filename, ALLOWED_EXTENSIONS):
        song_filename = secure_filename(song_file.filename)
        song_path = os.path.join(app.config['UPLOAD_FOLDER'], song_filename) #static/songs/<song_filename>
        song_file.save(song_path)
    else:
        flash("Invalid Song Format (mp3, wav, ogg only)", "song_error")
        return redirect(url_for("admin_panel"))

    # Database Insert
    cursor = db.cursor()
    try:
        # 1. Insert Song
        cursor.execute(
            "INSERT INTO songs (title, artist, genre, language, file, image) VALUES (%s, %s, %s, %s, %s, %s)",
            (title, artist, "Unknown", language, song_filename, image_filename)
        )
        
        # 2. Handle Multi-Artist Creation
        # Split by comma and strip whitespace
        artist_names = [a.strip() for a in artist.split(',')]
        
        for a_name in artist_names:
            if not a_name: continue
            
            # Check if artist exists
            cursor.execute("SELECT id FROM artists WHERE name=%s", (a_name,))
            if not cursor.fetchone():
                # Create new artist with default image
                # Make sure you have a 'default_artist.png' in static/images or handle missing image in template
                cursor.execute(
                    "INSERT INTO artists (name, image) VALUES (%s, %s)",
                    (a_name, "default_artist.png")
                )

        db.commit()
        flash("Song Added Successfully!", "success")
    except Exception as e:
        flash(f"Error adding song: {e}", "error")
    finally:
        cursor.close()

    return redirect(url_for("admin_panel"))

@app.route("/logout")
def logout():
    session.clear()   # removes user_id, username, everything
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
