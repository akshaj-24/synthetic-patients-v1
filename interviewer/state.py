from os import path
import pandas as pd
from pathlib import Path

class State:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.current_phase: int = 1
        self.phase_transcript: str = f"transcripts/phase/{self.session_id}.jsonl"
        self.patient_notes: str = ""
        self.summary: str = ""
        df = pd.DataFrame(columns=["role", "content"])
        df.to_json(self.phase_transcript, orient="records", lines=True)

    def next_phase(self):
        self.current_phase += 1

    def add_to_phase_transcript(self, role: str, content: str):
        pt = pd.read_json(self.phase_transcript, lines=True)
        pt.loc[len(pt)] = [role, content]
        pt.to_json(self.phase_transcript, orient="records", lines=True)

    def reset_phase_transcript(self):
        df = pd.DataFrame(columns=["role", "content"])
        df.to_json(self.phase_transcript, orient="records", lines=True)
        row = pd.DataFrame([{"role": "system", "content": f"---"}])
        row.to_json(self.phase_transcript, orient="records", lines=True)
        
        return 1

    def get_phase_transcript(self):
        '''RETURNS TEXT OF PHASE TRANSCRIPT'''
        df = pd.read_json(self.phase_transcript, lines=True)
        dialogue = "\n".join([f"{row['role']}: {row['content']}" for index, row in df.iterrows()])
        return dialogue

    def update_patient_notes(self, new_notes: str):
        self.patient_notes += "\n" + new_notes
        return 1

    def reset_patient_notes(self):
        self.patient_notes = ""
        return 1

    def update_summary(self, new_summary: str):
        self.summary += "\n" + new_summary
        return 1

    def reset_summary(self):
        self.summary = ""
        return 1

    def reset_all(self):
        self.reset_phase_transcript()
        self.reset_patient_notes()
        self.reset_summary()
        self.current_phase = 1
        return 1
    