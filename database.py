import sqlite3
import json

DB_NAME = "sessions.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                patient_name TEXT,
                disorder TEXT,
                turns INTEGER,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,  -- Interviewer notes
                full_state TEXT  -- Stores the entire Session object as JSON
            )
        """)

def save_session_to_db(session):
    # Serialize the session object
    # We manually build the dict to ensure we catch all fields
    state = {
        "session_id": session.session_id,
        "patient_data": session.patient_data,
        "interviewer_dialogues": session.interviewer_dialogues,
        "patient_responses": session.patient_responses,
        "summary": session.summary,
        "feelings": session.feelings,
        "turns": session.turns,
        "session_transcript": session.session_transcript,
        "notes": session.notes,
        "last_interviewer_message": session.last_interviewer_message,
        "last_patient_response": session.last_patient_response
    }
    
    json_state = json.dumps(state)
    name = session.patient_data.get("Name", "Unknown")
    disorder = session.patient_data.get("Disorder", "Unknown")

    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            INSERT OR REPLACE INTO sessions (session_id, patient_name, disorder, turns, full_state)
            VALUES (?, ?, ?, ?, ?)
        """, (session.session_id, name, disorder, session.turns, json_state))

def load_session_from_db(session_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute("SELECT full_state FROM sessions WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        if row:
            return json.loads(row[0])
    return None

def get_all_sessions():
    """Returns metadata for the card view"""
    with sqlite3.connect(DB_NAME) as conn:
        # Use a dictionary factory for cleaner JSON return
        conn.row_factory = sqlite3.Row 
        cursor = conn.execute("SELECT session_id, patient_name, disorder, turns, last_updated FROM sessions ORDER BY last_updated DESC")
        return [dict(row) for row in cursor]

def delete_session(session_id):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
