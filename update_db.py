import mysql.connector

try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="", # XAMPP default
        database="music_db"
    )
    cursor = db.cursor()

    print("Checking if 'language' column exists...")
    
    # Check if column exists
    cursor.execute("SHOW COLUMNS FROM songs LIKE 'language'")
    result = cursor.fetchone()

    if not result:
        print("Adding 'language' column...")
        cursor.execute("ALTER TABLE songs ADD COLUMN language VARCHAR(50) DEFAULT 'English'")
        db.commit()
        print("Column 'language' added successfully!")
    else:
        print("Column 'language' already exists. No changes made.")

    cursor.close()
    db.close()

except mysql.connector.Error as err:
    print(f"Error: {err}")
