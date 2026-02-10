import pandas
import fastapi
import uuid
import json
import os  # <--- ADDED
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Import your modules
import PROMPT
import LLM_CALL
from Session import Session
import database

# Ensure directories exist
os.makedirs("transcripts", exist_ok=True)
os.makedirs("transcripts/txt", exist_ok=True)

class StartRequest(BaseModel):
    disorder: str 

class ChatRequest(BaseModel):
    session_id: str
    message: str
    
class LoadRequest(BaseModel):
    session_id: str

class DeleteRequest(BaseModel):
    session_id: str

class NotesRequest(BaseModel):
    session_id: str
    notes: str

# Initialize App & DB
app = fastapi.FastAPI()
database.init_db()
sessions = {}  # In-memory cache

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- HELPER: Rehydrate Session from State ---
def rehydrate_session(state):
    """Reconstructs a Session object from a DB dictionary."""
    s = Session()
    s.session_id = state['session_id']
    s.patient_data = state['patient_data']
    s.interviewer_dialogues = state.get('interviewer_dialogues', [])
    s.patient_responses = state.get('patient_responses', [])
    s.summary = state.get('summary', "")
    s.feelings = state.get('feelings', "")
    s.turns = state.get('turns', 0)
    
    # CRITICAL: Handle missing transcript path or generate default
    transcript_path = state.get('session_transcript', "")
    if not transcript_path:
        transcript_path = f"transcripts/{s.session_id}.jsonl"
    s.session_transcript = transcript_path
    
    # CRITICAL: Consistent naming for notes
    s.notes = state.get('notes', "") 
    
    return s

@app.post("/api/start")
def start_session(req: StartRequest):
    id = str(uuid.uuid4())
    session = Session()
    session.set_disorder(req.disorder)
    session.session_id = id
    session.session_transcript = f"transcripts/{id}.jsonl"
    
    # Initialize Transcript File
    df = pandas.DataFrame({
        'role':['system', 'system'],
        'content':[f'Session {id} transcript', f'Disorder: {req.disorder}']
    })
    df.to_json(session.session_transcript, orient='records', lines=True)
    
    session.create_profile()
    
    # Save to DB & Cache
    database.save_session_to_db(session)
    sessions[id] = session
    session.notes = ""
    
    return {
        "session_id": id, 
        "message": "Patient initialized.",
        "patient_data": session.get_session_patient_data()
    }

@app.post("/api/chat")
def chat(req: ChatRequest):
    # 1. Ensure Session is Loaded
    if req.session_id not in sessions:
        state = database.load_session_from_db(req.session_id)
        if state:
            sessions[req.session_id] = rehydrate_session(state)
        else:
            raise fastapi.HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[req.session_id]
    
    # 2. Process Chat
    interviewer_message = req.message
    session.turns += 1
    
    if session.turns % 5 == 0:
        session.summary += "\n" + LLM_CALL.get_response_thinking(PROMPT.summary_prompt(session))
        session.interviewer_dialogues = []
        session.patient_responses = []
        
    session.interviewer_dialogues.append(interviewer_message)    
    response = LLM_CALL.get_response_thinking(PROMPT.main_prompt(session, interviewer_message))
    session.patient_responses.append(response)
    session.feelings = LLM_CALL.get_response_thinking(PROMPT.feelings_prompt(session))
    
    # 3. Update Transcript File safely
    new_row = pandas.DataFrame({
        'role':['interviewer', 'patient'], 
        'content':[interviewer_message, response]
    })
    
    # Ensure file exists before appending
    if not os.path.exists(session.session_transcript):
        # Re-create if missing
        df = pandas.DataFrame({'role':['system'], 'content':[f'Session restored: {session.session_id}']})
        df.to_json(session.session_transcript, orient='records', lines=True)

    try:
        existing = pandas.read_json(session.session_transcript, orient='records', lines=True)
        pandas.concat([existing, new_row], ignore_index=True).to_json(session.session_transcript, orient='records', lines=True)
    except ValueError:
        # Handle empty/corrupt file
        new_row.to_json(session.session_transcript, orient='records', lines=True)

    # 4. Save State
    database.save_session_to_db(session)
    
    return response

@app.post("/api/load")
def load_session(req: LoadRequest):
    # 1. Load Session Object (Memory or DB)
    session = None
    
    if req.session_id in sessions:
        session = sessions[req.session_id]
    else:
        state = database.load_session_from_db(req.session_id)
        if state:
            session = rehydrate_session(state)
            sessions[req.session_id] = session # Cache it!
    
    if not session:
        raise fastapi.HTTPException(status_code=404, detail="Session not found")

    # 2. Load Chat History from File
    history = []
    
    # Ensure path is valid
    if not session.session_transcript:
         session.session_transcript = f"transcripts/{session.session_id}.jsonl"

    if os.path.exists(session.session_transcript):
        try:
            df = pandas.read_json(session.session_transcript, orient='records', lines=True)
            for _, row in df.iterrows():
                role = row['role'].lower()
                content = row['content']
                if role == 'interviewer':
                    history.append({"role": "Interviewer", "text": content})
                elif role == 'patient':
                    history.append({"role": "Patient", "text": content})
        except Exception as e:
            print(f"Error reading transcript: {e}")
    else:
        print(f"Transcript file not found: {session.session_transcript}")

    data = session.get_session_patient_data()
    return {
        "session_id": session.session_id,
        "patient_data": data,
        "interviewer_notes": session.notes, # Fixed variable name
        "chat_history": history
    }

@app.post("/api/save_notes")
def save_notes(req: NotesRequest):
    # Ensure session loaded
    if req.session_id not in sessions:
        state = database.load_session_from_db(req.session_id)
        if state:
            sessions[req.session_id] = rehydrate_session(state)
        else:
            raise fastapi.HTTPException(status_code=404, detail="Session not found")
    
    # Update & Save
    sessions[req.session_id].notes = req.notes
    database.save_session_to_db(sessions[req.session_id])
    
    return {"message": "Notes saved"}

@app.get("/api/sessions")
def get_sessions():
    return database.get_all_sessions()

@app.delete("/api/delete/{session_id}")
def delete_session_endpoint(session_id: str):
    if session_id in sessions:
        del sessions[session_id]
        
    database.delete_session(session_id)
    
    # Also delete transcript file if exists
    path = f"transcripts/{session_id}.jsonl"
    if os.path.exists(path):
        os.remove(path)
        
    return {"message": "Session deleted"}

@app.post("/api/file")
def get_file(req: ChatRequest):
    # Ensure session loaded logic is consistent
    if req.session_id not in sessions:
         # Try load from DB just in case
        state = database.load_session_from_db(req.session_id)
        if state:
            sessions[req.session_id] = rehydrate_session(state)
        else:
            raise fastapi.HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[req.session_id]
    session.generate_text_file()
    
    txt_path = f"transcripts/txt/{session.session_id}.txt"
    if not os.path.exists(txt_path):
         raise fastapi.HTTPException(status_code=404, detail="Transcript text file generation failed")

    return FileResponse(
        path=txt_path,
        filename=f"{session.session_id}.txt",
        media_type='text/plain'
    )

@app.get("/")
async def read_index():
    return FileResponse("index.html")
