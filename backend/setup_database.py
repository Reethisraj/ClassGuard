from database import get_connection


def create_tables():

    connection = get_connection()

    cursor = connection.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)

    # Rooms table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            room_id TEXT PRIMARY KEY,
            capacity INTEGER NOT NULL,
            projector INTEGER DEFAULT 0,
            room_type TEXT NOT NULL
        )
    """)

    # Timetable table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS timetable (
            timetable_id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id TEXT NOT NULL,
            date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            subject TEXT,
            FOREIGN KEY (room_id) REFERENCES rooms(room_id)
        )
    """)

    # Classroom requests table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            request_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            purpose TEXT NOT NULL,
            date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            students INTEGER NOT NULL,
            projector_required INTEGER DEFAULT 0,
            status TEXT DEFAULT 'PENDING',
            ai_decision TEXT,
            assigned_room TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    connection.commit()

    connection.close()

    print("Database tables created successfully!")


if __name__ == "__main__":
    create_tables()