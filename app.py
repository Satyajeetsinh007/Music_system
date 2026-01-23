import mysql.connector
import random
from flask import Flask, render_template,request,flash,redirect,url_for

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
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM songs")
    songs = cursor.fetchall()
    cursor.close()
    return render_template("index.html", songs=songs)

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
            return redirect(url_for("home"))
        else:
            flash("Invalid email or password")
            return redirect(url_for("login"))
    return render_template("login.html")


@app.route("/song/<int:song_id>")
def play_song(song_id):
    user_id = 1  # for now

    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM songs WHERE id=%s", (song_id,))
    song = cursor.fetchone()

    cursor.execute(
        "SELECT * FROM liked_songs WHERE user_id=%s AND song_id=%s",
        (user_id, song_id)
    )
    liked = cursor.fetchone()  # None or row

    cursor.execute(
        "SELECT * FROM songs WHERE genre=%s AND id!=%s",
        (song["genre"], song_id)
    )
    related = cursor.fetchall()

    return render_template("song.html", song=song, related_songs=related,liked=liked)



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
    user_id = 1  # for now

    cursor = db.cursor(dictionary=True)

    # check if already liked
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
    else:
        # not liked → like
        cursor.execute(
            "INSERT INTO liked_songs (user_id, song_id) VALUES (%s, %s)",
            (user_id, song_id)
        )

    db.commit()
    cursor.close()

    return {"status": "ok"}

