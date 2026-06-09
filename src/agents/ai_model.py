import os
from dotenv import load_dotenv
from google import genai
from google.genai.types import GenerateContentConfig
import json
import re
import pandas as pd


# Load API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("Missing GEMINI_API_KEY in .env file")

# Configure Gemini
model_id = "gemini-2.5-flash"
client = genai.Client(api_key=api_key)

def upload_csv(file_path: str):
    """Uploads a local CSV to the Gemini Files API."""
    print(f"[System] Uploading {file_path}...")
    # 'text/csv' is the standard MIME type for CSVs
    myfile = client.files.upload(file=file_path, config={'mime_type': 'text/csv'})
    return myfile

def call_gemini(prompt: str, system_instruction: str = "") -> str:
    """Helper to call Gemini with a prompt and optional system instruction."""
    response = client.models.generate_content(
        model=model_id,
        contents=prompt,
        config=GenerateContentConfig(
            system_instruction=system_instruction,
        ) if system_instruction else None
    )
    return response.text.strip()

def collector_fetch_from_file(task: str, file_obj) -> str:
    """Uses an uploaded file object to retrieve data."""
    system_instruction = """You are a Data Collector. 
    Analyze the attached CSV file and extract rows relevant to the user's task."""
    
    # We pass the file_obj directly in the contents list
    response = client.models.generate_content(
        model=model_id,
        contents=[file_obj, f"Task: {task}"],
        config=GenerateContentConfig(system_instruction=system_instruction)
    )
    return response.text.strip()

def collector_fetch(task: str, source_hint: str = "") -> str:
    """Fetch/retrieve raw data based on the task."""
    system_instruction = """You are a Data Collector agent. Your role is to:
    - Extract or describe raw data entries relevant to the given topic
    - If given CSV content, parse and return relevant rows
    - If web data, return raw structured snippets
    - Output raw, unfiltered results — do not clean or score yet"""

    prompt = f"Collect raw data for: {task}"
    if source_hint:
        prompt += f"\n\nSource data:\n{source_hint}"

    result = call_gemini(prompt, system_instruction)
    return f"[Collector] {result}"


def qualifier_analyze(raw_data: str, criteria: str) -> str:
    """Qualify and clean raw data against criteria."""
    system_instruction = "Filter data based on criteria. Return a JSON list of objects."
    
    # Using the 'response_mime_type' ensures you get valid JSON back
    response = client.models.generate_content(
        model=model_id,
        contents=f"Criteria: {criteria}\n\nData: {raw_data}",
        config=GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json" # This is the magic line
        )
    )
    return response.text.strip()

def json_to_csv_dynamic(qualifier_json_output: str) -> str:
    """Dynamically converts any valid JSON array string into a CSV string."""
    try:
        # Clean any markdown fluff if the model returned it (e.g., ```json ... ```)
        clean_json = qualifier_json_output.strip()
        if clean_json.startswith("```"):
            clean_json = "\n".join(clean_json.split("\n")[1:-1])
            
        # Parse JSON and load straight into Pandas
        data = json.loads(clean_json)
        df = pd.DataFrame(data)
        
        # Convert to CSV string format without a messy row index
        return df.to_csv(index=False)
    except Exception as e:
        raise ValueError(f"Failed to dynamically convert JSON to CSV. Error: {e}")