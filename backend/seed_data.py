from database import get_connection


def insert_data():

    connection = get_connection()
    cursor = connection.cursor()

    # =========================
    # USERS — 25 USERS
    # =========================

    users = [
        ("STU001", "Rahul", "CSE", "Student"),
        ("STU002", "Priya", "CSE", "Student"),
        ("STU003", "Arun", "CSE", "Student"),
        ("STU004", "Divya", "CSE", "Student"),
        ("STU005", "Karthik", "CSE", "Student"),

        ("STU006", "Naveen", "ECE", "Student"),
        ("STU007", "Harini", "ECE", "Student"),
        ("STU008", "Vijay", "ECE", "Student"),
        ("STU009", "Swetha", "ECE", "Student"),
        ("STU010", "Sanjay", "ECE", "Student"),

        ("STU011", "Ajay", "IT", "Student"),
        ("STU012", "Keerthana", "IT", "Student"),
        ("STU013", "Dinesh", "IT", "Student"),
        ("STU014", "Pavithra", "IT", "Student"),
        ("STU015", "Vignesh", "IT", "Student"),

        ("STU016", "Ashwin", "MECH", "Student"),
        ("STU017", "Anitha", "MECH", "Student"),
        ("STU018", "Surya", "MECH", "Student"),
        ("STU019", "Deepa", "MECH", "Student"),
        ("STU020", "Mohan", "MECH", "Student"),

        ("FAC001", "Kumar", "CSE", "Faculty"),
        ("FAC002", "Meena", "ECE", "Faculty"),
        ("FAC003", "Ramesh", "IT", "Faculty"),
        ("FAC004", "Lakshmi", "MECH", "Faculty"),

        ("ADM001", "Admin", "ADMIN", "Admin")
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO users
        (user_id, name, department, role)
        VALUES (?, ?, ?, ?)
    """, users)


    # =========================
    # CLASSROOMS — 25 ROOMS
    # =========================

    rooms = [
        ("A101", 40, 1, "Classroom"),
        ("A102", 50, 1, "Classroom"),
        ("A103", 60, 0, "Classroom"),
        ("A104", 35, 1, "Classroom"),
        ("A105", 45, 0, "Classroom"),

        ("A201", 40, 1, "Classroom"),
        ("A202", 55, 1, "Classroom"),
        ("A203", 70, 1, "Classroom"),
        ("A204", 30, 0, "Classroom"),
        ("A205", 50, 1, "Classroom"),

        ("B101", 40, 0, "Classroom"),
        ("B102", 60, 1, "Classroom"),
        ("B103", 45, 1, "Classroom"),
        ("B104", 35, 0, "Classroom"),
        ("B105", 55, 1, "Classroom"),

        ("B201", 30, 1, "Classroom"),
        ("B202", 50, 0, "Classroom"),
        ("B203", 65, 1, "Classroom"),
        ("B204", 50, 1, "Classroom"),
        ("B205", 40, 0, "Classroom"),

        ("C101", 60, 1, "Classroom"),
        ("C102", 45, 0, "Classroom"),
        ("C103", 70, 1, "Classroom"),
        ("C104", 35, 1, "Classroom"),
        ("C105", 50, 0, "Classroom")
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO rooms
        (room_id, capacity, projector, room_type)
        VALUES (?, ?, ?, ?)
    """, rooms)


    # =========================
    # TIMETABLE
    # =========================

    timetable = [
        ("B204", "2026-10-06", "10:00", "12:00", "CSE Class"),
        ("B204", "2026-10-06", "14:00", "15:00", "Programming Lab"),

        ("A101", "2026-10-06", "09:00", "10:00", "Mathematics"),
        ("A102", "2026-10-06", "11:00", "12:00", "Physics"),
        ("A103", "2026-10-06", "14:00", "16:00", "Database Systems"),

        ("A201", "2026-10-06", "09:00", "11:00", "Operating Systems"),
        ("A202", "2026-10-06", "13:00", "15:00", "Computer Networks"),

        ("A203", "2026-10-06", "10:00", "12:00", "Artificial Intelligence"),
        ("B102", "2026-10-06", "09:00", "10:00", "Digital Electronics"),
        ("B103", "2026-10-06", "11:00", "13:00", "Web Development"),

        ("B105", "2026-10-06", "14:00", "16:00", "Software Engineering"),
        ("B201", "2026-10-06", "09:00", "11:00", "Data Structures"),

        ("B203", "2026-10-06", "10:00", "12:00", "Machine Learning"),
        ("C101", "2026-10-06", "13:00", "15:00", "Cloud Computing"),
        ("C103", "2026-10-06", "09:00", "11:00", "Cyber Security")
    ]

    cursor.executemany("""
        INSERT INTO timetable
        (room_id, date, start_time, end_time, subject)
        VALUES (?, ?, ?, ?, ?)
    """, timetable)


    connection.commit()
    connection.close()

    print("25 users and 25 classrooms added successfully!")


if __name__ == "__main__":
    insert_data()