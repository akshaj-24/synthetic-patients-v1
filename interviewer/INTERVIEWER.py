import random
from faker import Faker
import Session

fake = Faker('en_CA')

class Interviewer:
    def __init__(self, session_id):
        self.session_id = session_id
        self.gender = random.choice(["male", "female"])
        self.name = self.generate_name()
        self.interviewer_dialogues = []
        self.patient_dialogues = []
        self.session_summary = ""
        self.session_notes = ""
        self.patient_data = None
        self.phase = 1
        self.last_interviewer_message = ""
        self.last_patient_response = ""

        def generate_name(self):
            if self.gender == "male":
                return fake.first_name_male() + " " + fake.last_name()
            else:
                return fake.first_name_female() + " " + fake.last_name()
            
        def end_phase(self):
            return self.phase > 6
                
            
            
        
