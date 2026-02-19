import json
import glob
import os


def generate_text_file(file):
            txt_path = f"transcripts/txt/{os.path.basename(file).replace('.jsonl', '.txt')}"
            with open(file, 'r') as df, open(txt_path, 'w') as fout:
                for row in df:
                    line = json.loads(row)
                    fout.write(f"{line['role']}: {line['content']}\n\n")
                    
                    
for file in glob.glob(os.path.join("transcripts/", "*.jsonl")):
    generate_text_file(file)