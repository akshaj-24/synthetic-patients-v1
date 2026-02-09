from demographics import Demographics
import json
import LLM_CALL
import DSM
import PROMPT

class Session:
    def __init__(self):
        self.patient = Demographics()
        self.patient_data = self.patient.get_patient()
        self.patient_data["Disorder"] = None # Based on user input
        self.patient_data["Intake"] = "Intake form"
        self.interviewer_dialogues = [] # every dialogue add at end remove first for more than 5
        self.patient_responses = [] # every dialogue add at end remove first for more than 5
        self.summary = "Summary:\n" # Update every 3 responses
        self.feelings = "Your Feelings:\n" # Update every response based on last patient response and interviewer response, not very detailed, doesnt change much, see if to keep?
        self.turns = 0
        self.session_transcript = "" #Path to save the session transcript, update every response
        self.session_id = None # Generate unique ID for each session]
        self.notes = "" # Interviewer notes, updated manually by interviewer, not used in LLM prompts but saved in DB for reference
    
    def get_session_patient_data(self):
        fields = [
            "Name", "Age", "Gender", "Education", "Occupation",
            "Marital Status", "Ethnicity", "Disorder", "Intake", "Vignette"
        ]
        return {k: self.patient_data[k] for k in fields if k in self.patient_data}
    
    def conversation_history(self):
        history = ""
        for i in range(len(self.patient_responses)):
            history += f"Interviewer: {self.interviewer_dialogues[i]}\n"
            history += f"Patient: {self.patient_responses[i]}\n"
        return history
    
    def get_display_patient_data(self):
        fields = [
            "Name", "Age", "Gender", "Education", "Occupation",
            "Marital Status", "Ethnicity", "Disorder",
        ]
        return {k: self.patient_data[k] for k in fields if k in self.patient_data}
    
    def set_disorder(self, disorder):
        self.patient_data["Disorder"] = disorder
        
    def create_profile(self):
        self.patient_data["Intake"] = LLM_CALL.get_response_thinking(PROMPT.patient_intake_form_prompt(self))
        self.patient_data["Vignette"] = LLM_CALL.get_response_thinking(PROMPT.patient_vignette_prompt(self))

    def generate_text_file(self):
            txt_path = f"transcripts/txt/{self.session_id}.txt"
            with open(self.session_transcript, 'r') as df, open(txt_path, 'w') as fout:
                for row in df:
                    line = json.loads(row)
                    fout.write(f"{line['role']}: {line['content']}\n\n")