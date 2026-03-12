import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("CRITICAL: GEMINI_API_KEY is missing from .env")

# Initialize the modern GenAI Client
client = genai.Client(api_key=api_key)

def analyze_symptoms(symptom_text: str) -> dict:
    """
    Takes raw patient symptom text and returns structured triage data.
    Forces the LLM to output valid JSON using the modern SDK.
    """
    prompt = f"""
    You are an expert clinical triage AI for a government hospital.
    Analyze the following patient message and output STRICTLY valid JSON with no markdown formatting or extra text.
    
    Assign a priority score from 1 to 5:
    1 = Critical/Life-threatening (e.g., heart attack, severe bleeding)
    2 = Urgent (e.g., severe pain, fractures, breathing difficulty)
    3 = Moderate (e.g., high fever, persistent vomiting)
    4 = Minor (e.g., mild sprains, cold, minor cuts)
    5 = Non-urgent/Routine (e.g., general checkup, mild rash, refill)
    
    Also, identify the most likely hospital department (e.g., Cardiology, Orthopedics, General Medicine, ER).
    
    Patient Message: "{symptom_text}"
    
    Expected JSON Format exactly:
    {{
        "priority": <int>,
        "department": "<string>",
        "clinical_summary": "<string max 10 words>"
    }}
    """
    
    try:
        # Using the new client.models.generate_content architecture
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        raw_text = response.text.strip()
        
        # Robust parsing: Strip out markdown block formatting
        if raw_text.startswith("```json"):
            raw_text = raw_text.replace("```json", "", 1)
        if raw_text.startswith("```"):
            raw_text = raw_text.replace("```", "", 1)
        if raw_text.endswith("```"):
            raw_text = raw_text[::-1].replace("```", "", 1)[::-1] 
            
        parsed_data = json.loads(raw_text.strip())
        
        # Validate expected keys
        required_keys = ["priority", "department", "clinical_summary"]
        for key in required_keys:
            if key not in parsed_data:
                raise KeyError(f"Missing key in LLM response: {key}")
                
        return parsed_data
        
    except Exception as e:
        print(f"NLP Engine Error: {str(e)}")
        # Production Fallback
        return {
            "priority": 3,
            "department": "General Medicine - Unclassified",
            "clinical_summary": "Triage AI parsing failed. Manual review required."
        }