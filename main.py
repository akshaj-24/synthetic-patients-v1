from demographics import Demographics
import pandas
import profile
import fastapi
from pydantic import BaseModel
import uuid

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
        
    def set_disorder(self, disorder):
        self.patient_data["Disorder"] = disorder
        
    def create_profile(self):
        # Profile.py will have functions to create the profile based on the patient data and disorder, and return the system prompt for the LLM
        return
    
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
    
    return #patient_response