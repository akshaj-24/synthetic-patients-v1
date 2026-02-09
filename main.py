from demographics import Demographics
import pandas
import profile
import fastapi
from pydantic import BaseModel
import uuid
import json

class StartRequest(BaseModel):
    disorder: str  # "MDD", "GAD", or "PPD"

class ChatRequest(BaseModel):
    session_id: str
    message: str

sessions = {}


class Session:
    def __init__(self):
        self.patient = Demographics()
        self.patient_data = self.patient.get_patient()
        self.patient_data["Disorder"] = None # Based on user input
        self.interviewer_dialogues = [] # every dialogue add at end remove first for more than 5
        self.patient_responses = [] # every dialogue add at end remove first for more than 5
        self.summary = "" # Update every 3 responses
        self.feelings = "" # Update every response based on last patient response and interviewer response, not very detailed, doesnt change much, see if to keep?
        self.turns = 0
        self.session_transcript = "" #Path to save the session transcript, update every response
        self.session_id = None # Generate unique ID for each session
    
        
        
    def set_disorder(self, disorder):
        self.patient_data["Disorder"] = disorder
        
    def create_profile(self):
        # Profile.py will have functions to create the profile based on the patient data and disorder, and return the system prompt for the LLM
        return

    def generate_text_file(self):
            txt_path = f"transcripts/txt/{self.session_id}.txt"
            with open(self.session_transcript, 'r') as df, open(txt_path, 'w') as fout:
                for row in df:
                    line = json.loads(row)
                    fout.write(f"{line['role']}: {line['content']}\n\n")


    
app = fastapi.FastAPI()

app.add_middleware(
    fastapi.middleware.cors.CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/start")
def start_session(req: StartRequest):
    
    # Generate ID and Create Session
    id = str(uuid.uuid4())
    sessions[id] = Session()
    sessions[id].set_disorder(req.disorder)
    sessions[id].session_id = id
    
    sessions[id].session_transcript = f"transcripts/{id}.jsonl"
        
    df = pandas.DataFrame({'role':['system', 'system'],
                           'content':[f'Session {id} transcript', f'Disorder: {req.disorder}']}, index=[0])
    
    df.to_json(sessions[id].session_transcript, orient='records', lines=True)
    
    sessions[id].create_profile()
    
    print(f"Created session {id} for {req.disorder}")
    return {"session_id": id, "message": "Patient initialized."}

@app.post("/api/chat")
def chat(req: ChatRequest):
    if req.session_id not in sessions:
        raise fastapi.HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[req.session_id]
    interviewer_message = req.message
    session.turns += 1
    if session.turns % 5 == 0:
        
        # summarize recent dialogue
        
        session.interviewer_dialogues = []
        session.patient_responses = []
        
        
    session.interviewer_dialogues.append(interviewer_message)
    
    # get patient response
    
    # append to list
    
    # update feelings
    
    # add dialogues to session transcript
    
    return #patient_response

@app.post("/api/file")
def get_file(req: ChatRequest):
    if req.session_id not in sessions:
        raise fastapi.HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[req.session_id]
    session.generate_text_file()
    
    txt_path = f"transcripts/txt/{session.session_id}.txt"
    
    return fastapi.responses.FileResponse(
        path=txt_path,
        filename=f"{session.session_id}.txt",
        media_type='text/plain'
    )