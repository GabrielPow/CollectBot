import os
from dotenv import load_dotenv
from google import genai
from google.genai.types import GenerateContentConfig
import json
import re


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


def formatter_export(qualified_data: str, schema: list[str]) -> str:
    """Format qualified data into CSV."""
    system_instruction = f"""You are a Formatter agent. Your role is to:
    - Convert the input into a valid CSV
    - Use exactly these columns: {', '.join(schema)}
    - Output ONLY the CSV text, no explanation"""

    result = call_gemini(
        f"Format this data as CSV:\n{qualified_data}",
        system_instruction
    )
    return f"[Formatter] {result}"