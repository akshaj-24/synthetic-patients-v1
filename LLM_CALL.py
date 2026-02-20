import ollama
import re
import json
from langfuse.openai import OpenAI
import os

os.environ["LANGFUSE_PUBLIC_KEY"] = "pk-lf-e0c6f210-0223-42b4-a70c-b6e2cd0691cc"
os.environ["LANGFUSE_SECRET_KEY"] = "sk-lf-88cd8bde-15ca-4176-a3f4-bcc6464554ef"
os.environ["LANGFUSE_BASE_URL"] = "http://localhost:3000"

BASE_URL = "http://localhost:11434"
LANGFUSE = "http://localhost:11434/v1"
MODEL = "qwen3:32b"
OPTIONS = {
    "temperature": 0.7,
    "stop": ["}"],
    "num_ctx": 13288,
}
INT_OPTIONS = {
    "temperature": 0.3,
    "stop": ["}"],
    "num_ctx": 13288,
}
# top_p = 0.9
# top_k = 40

langfuse_client = OpenAI(base_url=LANGFUSE, api_key='ollama')
langfuse_interviewer_client = OpenAI(base_url=LANGFUSE, api_key='ollama')

model = ollama.Client(host='http://localhost:11434')

def get_tokens(resp):
    prompt_match = re.search(r"prompt_eval_count=(\d+)", str(resp))
    # Regex pattern to capture the number after 'eval_count='
    eval_match = re.search(r"eval_count=(\d+)", str(resp))
    prompt_count = int(prompt_match.group(1)) if prompt_match else 0
    eval_count = int(eval_match.group(1)) if eval_match else 0
    total_tokens = prompt_count + eval_count
    print(total_tokens)
    
def extract_first_json(text):
    match = re.search(r"\{[\s\S]*?\}", text)
    if not match:
        raise ValueError("No JSON found")
    return json.loads(match.group())
    
def get_response_thinking(prompt_text: str) -> str:
    
    system = """
    You are a simulated undiagnosed medical patient participating in a psychiatric evaluation. You must strictly follow the disorder profile, symptoms, and behavioral instructions provided by the user.

    **Response Format Rules:**
    1. You must respond ONLY in English in first-person.
    2. You must respond ONLY in valid JSON format.
    3. Do not wrap the output in Markdown code blocks (e.g., do not use ```json).
    4. Do not include any commentary, reasoning, or text outside the JSON object.
    5. Use exactly the following schema for every response:

    {
    "text": "Your dialogue and actions as the patient go here"
    }
    """
    
    # CLIENT CHAT NORMAL
    
    # resp = model.chat(
    #     model=MODEL,
    #     messages=[
    #         {"role": "system", "content": system},
    #         {"role": "user", "content": prompt_text}
    #     ],
    #     #format=schema,
    #     stream=False,
    #     options=OPTIONS,
    # )
    
    # get_tokens(resp)
    # raw = resp["message"]["content"] + "}"
    
    # try:
    #     data = extract_first_json(raw)
    #     content = data["text"]
    # except Exception as e:
    #     print("Recursive call\n\n")
    #     print(f"Raw {raw} \n\n")
    #     print(f"Error {e} \n\n")
    #     print("---------------------------------------------------------------------------------------------------------------------------\n\n")
    #     return get_response_thinking(prompt_text)    
    
    # print(f"PATIENT: {content}\n")
    # return content
    
    # LANGFUSE TRACING CALL
    
    resp = langfuse_client.chat.completions.create(
        model = MODEL,
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt_text}
        ],
        temperature= OPTIONS["temperature"],
        max_tokens = OPTIONS["num_ctx"],
    )
    
    all = resp.choices[0].message.content
    match = re.search(r'</think>(.*)', all, re.DOTALL)
    result = match.group(1).strip() if match else all
    
    print(f"PATIENT MODEL: {result}\n")
    
    return result

def get_response_interviewer(prompt_text: str) -> str:
    
    system = """
    You are a simulated medical interviewer participating in a psychiatric session. You must strictly follow the behavioral instructions provided by the user.

    **Response Format Rules:**
    1. You must respond ONLY in English in first-person.
    2. You must respond ONLY in valid JSON format.
    3. Do not wrap the output in Markdown code blocks (e.g., do not use ```json).
    4. Do not include any commentary, reasoning, or text outside the JSON object.
    5. Use exactly the following schema for every response:

    {
    "text": "Your dialogue and actions as the interviewer go here"
    }
    """
    # REGULAR CLIENT CHAT 
    
    # resp = model.chat(
    #     model=MODEL,
    #     messages=[
    #         {"role": "system", "content": system},
    #         {"role": "user", "content": prompt_text}
    #     ],
    #     #format=schema,
    #     stream=False,
    #     options=OPTIONS,
    # )
    
    # get_tokens(resp)
    # raw = resp["message"]["content"] + "}"
    
    # try:
    #     data = extract_first_json(raw)
    #     content = data["text"]
    # except Exception as e:
    #     print("Recursive call\n\n")
    #     print(f"Raw {raw} \n\n")
    #     print(f"Error {e} \n\n")
    #     print("---------------------------------------------------------------------------------------------------------------------------\n\n")
    #     return get_response_thinking(prompt_text)    
    
    # print(f"INTERVIEWER: {content}\n")
    # return content
    
    
    # LANGFUSE TRACING CALL
    
    resp = langfuse_interviewer_client.chat.completions.create(
        model = MODEL,
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt_text}
        ],
        temperature= OPTIONS["temperature"],
        max_tokens= OPTIONS["num_ctx"],
    )
    
    all = resp.choices[0].message.content
    match = re.search(r'</think>(.*)', all, re.DOTALL)
    result = match.group(1).strip() if match else all
    
    print(f"PATIENT MODEL: {result}\n")
    
    return result