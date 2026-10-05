from fastapi import FastAPI
from pydantic import BaseModel
from database import get_connection

import sys
from pathlib import Path

# Allow Python to find the RAG folder
sys.path.append(str(Path(__file__).resolve().parent.parent))

from rag.rag_engine import search_policies

from ai_agent import analyze_with_gemini
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="ClassGuard API",
    description="AI-Powered Intelligent Classroom Access & Management System",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# HOME
# =========================

@app.get("/")
def home():
    return {
        "message": "ClassGuard Backend is running!",
        "status": "success"
    }


# =========================
# GET USERS
# =========================

@app.get("/users")
def get_users():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM users")

    users = cursor.fetchall()

    connection.close()

    return [dict(user) for user in users]


# =========================
# GET ROOMS
# =========================

@app.get("/rooms")
def get_rooms():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM rooms")

    rooms = cursor.fetchall()

    connection.close()

    return [dict(room) for room in rooms]


# =========================
# LOGIN
# =========================

class LoginRequest(BaseModel):
    user_id: str


@app.post("/login")
def login(request: LoginRequest):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE user_id = ?",
        (request.user_id,)
    )

    user = cursor.fetchone()

    connection.close()

    if user is None:
        return {
            "success": False,
            "message": "User not found"
        }

    return {
        "success": True,
        "message": "Login successful",
        "user": dict(user)
    }


# =========================
# CLASSROOM REQUEST
# =========================

class ClassroomRequest(BaseModel):
    user_id: str
    purpose: str
    date: str
    start_time: str
    end_time: str
    students: int
    projector_required: bool = False


@app.post("/requests")
def create_request(request: ClassroomRequest):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE user_id = ?",
        (request.user_id,)
    )

    user = cursor.fetchone()

    if user is None:

        connection.close()

        return {
            "success": False,
            "message": "User not found"
        }

    cursor.execute("""
        INSERT INTO requests
        (
            user_id,
            purpose,
            date,
            start_time,
            end_time,
            students,
            projector_required,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        request.user_id,
        request.purpose,
        request.date,
        request.start_time,
        request.end_time,
        request.students,
        int(request.projector_required),
        "PENDING"
    ))

    request_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return {
        "success": True,
        "message": "Classroom request submitted",
        "request_id": request_id,
        "status": "PENDING"
    }


# =========================
# GET REQUESTS
# =========================

@app.get("/requests")
def get_requests():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            requests.*,
            users.name,
            users.department,
            users.role
        FROM requests
        JOIN users
        ON requests.user_id = users.user_id
    """)

    requests = cursor.fetchall()

    connection.close()

    return [dict(request) for request in requests]


# =========================
# AVAILABLE ROOMS
# =========================

@app.get("/available-rooms")
def get_available_rooms(
    date: str,
    start_time: str,
    end_time: str,
    students: int,
    projector_required: bool = False
):

    connection = get_connection()
    cursor = connection.cursor()

    if projector_required:

        cursor.execute("""
            SELECT *
            FROM rooms
            WHERE capacity >= ?
            AND projector = 1
        """, (students,))

    else:

        cursor.execute("""
            SELECT *
            FROM rooms
            WHERE capacity >= ?
        """, (students,))

    rooms = cursor.fetchall()

    available_rooms = []

    for room in rooms:

        cursor.execute("""
            SELECT *
            FROM timetable
            WHERE room_id = ?
            AND date = ?
            AND start_time < ?
            AND end_time > ?
        """, (
            room["room_id"],
            date,
            end_time,
            start_time
        ))

        conflict = cursor.fetchone()

        if conflict is None:

            available_rooms.append({
                "room_id": room["room_id"],
                "capacity": room["capacity"],
                "projector": bool(room["projector"]),
                "room_type": room["room_type"]
            })

    connection.close()

    return {
        "requested_students": students,
        "projector_required": projector_required,
        "available_rooms": available_rooms,
        "total_available": len(available_rooms)
    }


# =========================
# RECOMMEND ROOM
# =========================

@app.get("/recommend-room")
def recommend_room(
    date: str,
    start_time: str,
    end_time: str,
    students: int,
    projector_required: bool = False
):

    connection = get_connection()
    cursor = connection.cursor()

    if projector_required:

        cursor.execute("""
            SELECT *
            FROM rooms
            WHERE capacity >= ?
            AND projector = 1
            ORDER BY capacity ASC
        """, (students,))

    else:

        cursor.execute("""
            SELECT *
            FROM rooms
            WHERE capacity >= ?
            ORDER BY capacity ASC
        """, (students,))

    rooms = cursor.fetchall()

    suitable_rooms = []

    for room in rooms:

        cursor.execute("""
            SELECT *
            FROM timetable
            WHERE room_id = ?
            AND date = ?
            AND start_time < ?
            AND end_time > ?
        """, (
            room["room_id"],
            date,
            end_time,
            start_time
        ))

        conflict = cursor.fetchone()

        if conflict is None:

            suitable_rooms.append({
                "room_id": room["room_id"],
                "capacity": room["capacity"],
                "projector": bool(room["projector"]),
                "room_type": room["room_type"]
            })

    connection.close()

    if not suitable_rooms:

        return {
            "success": False,
            "message": "No suitable classroom available"
        }

    recommended_room = suitable_rooms[0]

    return {
        "success": True,
        "recommended_room": recommended_room,
        "reason": [
            f"Capacity required: {students}",
            f"Room capacity: {recommended_room['capacity']}",
            "No timetable conflict",
            "Required facilities available"
        ],
        "other_available_rooms": suitable_rooms[1:]
    }


# =========================
# ANALYZE REQUEST + RAG + GEMINI
# =========================

@app.get("/analyze-request")
def analyze_request(
    user_id: str,
    date: str,
    start_time: str,
    end_time: str,
    students: int,
    projector_required: bool = False,
    purpose: str = "Project Work"
):

    connection = get_connection()
    cursor = connection.cursor()

    # -------------------------
    # 1. CHECK USER
    # -------------------------

    cursor.execute(
        "SELECT * FROM users WHERE user_id = ?",
        (user_id,)
    )

    user = cursor.fetchone()

    if user is None:

        connection.close()

        return {
            "success": True,
            "decision": "REJECTED",
            "reason": "User is not registered in the system."
        }


    # -------------------------
    # 2. RAG POLICY SEARCH
    # -------------------------

    policy_query = f"""
    User is requesting a classroom for {purpose}.
    Number of students: {students}.
    Requested time: {start_time} to {end_time}.
    Projector required: {projector_required}.
    """

    relevant_policies = search_policies(
        policy_query,
        top_k=3
    )


    # -------------------------
    # 2.5 GEMINI AI ANALYSIS
    # -------------------------

    request_data = {
        "user_id": user_id,
        "purpose": purpose,
        "date": date,
        "start_time": start_time,
        "end_time": end_time,
        "students": students,
        "projector_required": projector_required
    }

    gemini_analysis = analyze_with_gemini(
        request_data,
        relevant_policies
    )


    # -------------------------
    # 3. FIND SUITABLE ROOMS
    # -------------------------

    if projector_required:

        cursor.execute("""
            SELECT *
            FROM rooms
            WHERE capacity >= ?
            AND projector = 1
            ORDER BY capacity ASC
        """, (students,))

    else:

        cursor.execute("""
            SELECT *
            FROM rooms
            WHERE capacity >= ?
            ORDER BY capacity ASC
        """, (students,))

    rooms = cursor.fetchall()

    suitable_rooms = []

    for room in rooms:

        cursor.execute("""
            SELECT *
            FROM timetable
            WHERE room_id = ?
            AND date = ?
            AND start_time < ?
            AND end_time > ?
        """, (
            room["room_id"],
            date,
            end_time,
            start_time
        ))

        conflict = cursor.fetchone()

        if conflict is None:

            suitable_rooms.append(room)


    # -------------------------
    # 4. NO ROOM AVAILABLE
    # -------------------------

    if not suitable_rooms:

        connection.close()

        return {
            "success": True,
            "decision": "REJECTED",
            "reason": "No suitable classroom is available for the requested time.",
            "gemini_analysis": gemini_analysis,
            "relevant_policies": relevant_policies
        }


    # -------------------------
    # 5. RECOMMEND ROOM
    # -------------------------

    recommended_room = suitable_rooms[0]


    # -------------------------
    # 6. FINAL CLASSGUARD DECISION
    # -------------------------

    if students > 20:

        decision = "REVIEW REQUIRED"

        reason = (
            "More than 20 students are requesting the classroom. "
            "Faculty approval is required."
        )

    else:

        decision = "APPROVED"

        reason = (
            "User is verified, classroom is available, "
            "capacity is sufficient and required facilities are available."
        )


    connection.close()


    # -------------------------
    # 7. FINAL RESPONSE
    # -------------------------

    return {

        "success": True,

        "decision": decision,

        "user": {
            "id": user["user_id"],
            "name": user["name"],
            "department": user["department"],
            "role": user["role"]
        },

        "request": {
            "purpose": purpose,
            "date": date,
            "start_time": start_time,
            "end_time": end_time,
            "students": students,
            "projector_required": projector_required
        },

        "recommended_room": {
            "room_id": recommended_room["room_id"],
            "capacity": recommended_room["capacity"],
            "projector": bool(recommended_room["projector"])
        },

        "reason": reason,

        "gemini_analysis": gemini_analysis,

        "relevant_policies": relevant_policies
    }