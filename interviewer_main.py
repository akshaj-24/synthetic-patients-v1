from faker import Faker
import main
import interviewer.INTERVIEWER as INTERVIEWER
from fastapi.testclient import TestClient
import json
import PROMPT
import LLM_CALL
from interviewer.INTERVIEWER import Interviewer


def transcript(disorder):

    client = TestClient(main.app)

    start_resp = client.post("/api/start", json={"disorder": disorder}).json()
    session_id = start_resp["session_id"]
    patient_data = start_resp["patient_data"]

    interviewer = INTERVIEWER.Interviewer(session_id)
    interviewer.patient_data = patient_data
    interviewer.name = interviewer.generate_name()
    
    
    while True:
        
        last_question = interviewer.interviewer_dialogues[-1] if interviewer.interviewer_dialogues else ""
        last_answer = interviewer.patient_dialogues[-1] if interviewer.patient_dialogues else ""
        interviewer.last_interviewer_message = last_question
        interviewer.last_patient_response = last_answer
        
        prompt = PROMPT.interviewer_prompt(interviewer)
        
        # get question from LLM CALL
        response = LLM_CALL.get_response_interviewer(prompt)
        
        if response == "--FUNCTION-- end_phase --FUNCTION--":
            
            interviewer.phase += 1
            
            if interviewer.end_phase():
                break
            
            interviewer.session_summary += "\n" + LLM_CALL.get_response_interviewer(PROMPT.interviewer_summary(interviewer))
            interviewer.session_notes += "\n" + LLM_CALL.get_response_interviewer(PROMPT.interviewer_notes(interviewer))
            
            # clear phase variables
            interviewer.interviewer_dialogues = []
            interviewer.patient_dialogues = []
            
            continue
        
        #else
        
        interviewer.interviewer_dialogues.append(response)
        
        # get answer from LLM CALL
        answer = client.post("/api/chat", json={"session_id": session_id, "message": response}).json()
        
        interviewer.patient_dialogues.append(answer)
        
def loop():
    disorder = "MDD"
    transcript(disorder)
    disorder = "GAD"
    transcript(disorder)
    disorder = "PPD"
    transcript(disorder)
    
    
i = 1

while True:
    print(f"Starting session {i}\n\n")
    loop()
    i += 1
        
    
    



    