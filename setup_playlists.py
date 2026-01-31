import mysql.connector

def create_playlist_tables():
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="music_db"
        )
        cursor = db.cursor()

        # Create playlists table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS playlists (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                name VARCHAR(100) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        print("Table 'playlists' checked/created.")

        # Create playlist_songs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS playlist_songs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                playlist_id INT NOT NULL,
                song_id INT NOT NULL,
                added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (playlist_id) REFERENCES playlists(id) ON DELETE CASCADE,
                FOREIGN KEY (song_id) REFERENCES songs(id) ON DELETE CASCADE,
                UNIQUE KEY unique_song_in_playlist (playlist_id, song_id)
            )
        """)
        print("Table 'playlist_songs' checked/created.")

        db.commit()
        cursor.close()
        db.close()
        print("Database setup completed successfully.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

if __name__ == "__main__":
    create_playlist_tables()
