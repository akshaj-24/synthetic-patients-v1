from demographics import Demographics
import json
import LLM_CALL
import DSM
import PROMPT
import random

mild = """
    **severity_instruction**: "HIGH FUNCTIONING / MILD"
    - **Masking:** You are very good at hiding your condition. To an outsider, you appear normal, perhaps just tired or slightly stressed.
    - **Behavior:** You are cooperative and polite. You speak in full, coherent sentences.
    - **Symptom Expression:** Your symptoms are internal 'background noise.' You downplay your struggles (e.g., 'It's not a big deal,' 'I'm just a bit off'). 
    - **Resistance:** You only show resistance if the interviewer pushes too hard into deep secrets.
    """

moderate = """
    **severity_instruction**: "DISTRESSED / MODERATE"
    - **Masking:** Your mask is cracking. It is obvious you are struggling, but you are trying to hold it together.
    - **Behavior:** You are moody, hesitant, or easily irritated. You might give shorter answers or use defensive language ("I don't know," "Maybe").
    - **Symptom Expression:** Symptoms leak out through tone and body language descriptions. You admit to problems but may blame them on external stress (work, family).
    - **Resistance:** You are skeptical of the therapy process. You need reassurance to open up.
    """

severe = """
    **severity_instruction**: "CRISIS / SEVERE"
    - **Masking:** Non-existent. You are overwhelmed by the disorder and cannot hide it.
    - **Behavior:** You are volatile, deeply withdrawn, or highly irrational. Your speech may be disjointed, very slow, or rapid-fire (depending on the disorder).
    - **Symptom Expression:** The disorder defines the conversation. You might be hostile (PPD), hopeless (MDD), or panicked (GAD).
    - **Resistance:** You are difficult to engage. You may refuse to answer, answer sarcastically, or spiral into your own narrative regardless of the question.
    """



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
        self.severity = None
        self.severity_instruction = None
        self.last_interviewer_message = ""
        self.last_patient_response = ""
    
    def get_session_patient_data(self):
        fields = [
            "Name", "Age", "Gender", "Education", "Occupation",
            "Marital Status", "Ethnicity", "Disorder", "Intake", "Severity", "Vignette"
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
            "Name", "Disorder", "Severity"
        ]
        return {k: self.patient_data[k] for k in fields if k in self.patient_data}
    
    def set_disorder(self, disorder):
        self.patient_data["Disorder"] = disorder
        
    def create_profile(self):
        self.patient_data["Intake"] = LLM_CALL.get_response_thinking(PROMPT.patient_intake_form_prompt(self))
        self.patient_data["Vignette"] = LLM_CALL.get_response_thinking(PROMPT.patient_vignette_prompt(self))
        # self.severity = random.choice([mild, moderate, severe])
        self.severity_instruction = random.choice([mild, moderate])
        if self.severity_instruction == mild:
            self.severity = "Mild"
        elif self.severity_instruction == moderate:
            self.severity = "Moderate"
        self.patient_data["Severity"] = self.severity

    def generate_text_file(self):
            txt_path = f"transcripts/txt/{self.session_id}.txt"
            with open(self.session_transcript, 'r') as df, open(txt_path, 'w') as fout:
                for row in df:
                    line = json.loads(row)
                    fout.write(f"{line['role']}: {line['content']}\n\n")