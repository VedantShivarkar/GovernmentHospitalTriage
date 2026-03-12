import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("CRITICAL: GEMINI_API_KEY is missing from .env")

client = genai.Client(api_key=api_key)


def analyze_symptoms(symptom_text: str) -> dict:
    """
    Takes raw patient symptom text and returns structured triage data.
    """
    prompt = f"""
    You are an expert clinical triage AI for a government hospital.
    Analyze the following patient message and output STRICTLY valid JSON with no markdown formatting or extra text.

    Assign a priority score from 1 to 5 based on the **severity and urgency**:

    1 = CRITICAL / LIFE-THREATENING – Immediate ambulance required. Examples:
        - Unconsciousness, not breathing
        - Severe bleeding (profuse, spurting, uncontrolled)
        - Heart attack symptoms (chest pain radiating to arm/jaw, shortness of breath, sweating)
        - Major trauma (car accident, fall from height, deep wounds, broken bones with heavy bleeding)
        - Stroke symptoms (facial drooping, slurred speech, one-sided weakness)
        - Severe allergic reaction (difficulty breathing, swelling of throat)

    2 = URGENT – Needs medical attention quickly but not immediately life‑threatening. Examples:
        - Moderate bleeding (controlled with pressure)
        - Suspected fracture without major bleeding
        - Severe pain but stable vital signs
        - High fever with confusion (in adults)
        - Difficulty breathing but can speak in sentences

    3 = MODERATE – Non‑urgent but should be seen soon. Examples:
        - High fever without confusion, persistent vomiting
        - Moderate pain (e.g., kidney stone, severe headache but no stroke symptoms)
        - Deep laceration that is not actively bleeding heavily

    4 = MINOR – Can wait, not emergent. Examples:
        - Mild sprains, small cuts, cold/flu symptoms
        - Minor burns, rashes, earache

    5 = NON‑URGENT / ROUTINE – Routine checkup, prescription refill, mild rash.

    Also identify the most likely hospital department (e.g., Cardiology, Orthopedics, General Medicine, ER, Trauma).

    Patient Message: "{symptom_text}"

    Expected JSON Format exactly:
    {{
        "priority": <int>,
        "department": "<string>",
        "clinical_summary": "<string max 10 words in English>"
    }}
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        raw_text = response.text.strip()

        if raw_text.startswith("```json"):
            raw_text = raw_text.replace("```json", "", 1)
        if raw_text.startswith("```"):
            raw_text = raw_text.replace("```", "", 1)
        if raw_text.endswith("```"):
            raw_text = raw_text[::-1].replace("```", "", 1)[::-1]

        parsed_data = json.loads(raw_text.strip())

        required_keys = ["priority", "department", "clinical_summary"]
        for key in required_keys:
            if key not in parsed_data:
                raise KeyError(f"Missing key in LLM response: {key}")

        return parsed_data

    except Exception as e:
        print(f"NLP Engine Error: {str(e)}")
        return {
            "priority": 3,
            "department": "General Medicine - Unclassified",
            "clinical_summary": "Triage AI parsing failed. Manual review required."
        }


def analyze_audio_symptoms(audio_bytes: bytes, mime_type: str) -> dict:
    """
    Takes raw audio bytes (Marathi, Hindi, or English) and returns structured triage data.
    """
    prompt = """
    You are an expert clinical triage AI for a government hospital in Maharashtra.
    Listen to the attached patient voice note. It may be in Marathi, Hindi, or English.

    1. Translate and understand the symptoms.
    2. Output STRICTLY valid JSON with no markdown formatting or extra text.

    Assign a priority score from 1 to 5 based on the **severity and urgency**:

    1 = CRITICAL / LIFE-THREATENING – Immediate ambulance required. Examples:
        - Unconsciousness, not breathing
        - Severe bleeding (profuse, spurting, uncontrolled)
        - Heart attack symptoms (chest pain radiating to arm/jaw, shortness of breath, sweating)
        - Major trauma (car accident, fall from height, deep wounds, broken bones with heavy bleeding)
        - Stroke symptoms (facial drooping, slurred speech, one-sided weakness)
        - Severe allergic reaction (difficulty breathing, swelling of throat)

    2 = URGENT – Needs medical attention quickly but not immediately life‑threatening. Examples:
        - Moderate bleeding (controlled with pressure)
        - Suspected fracture without major bleeding
        - Severe pain but stable vital signs
        - High fever with confusion (in adults)
        - Difficulty breathing but can speak in sentences

    3 = MODERATE – Non‑urgent but should be seen soon. Examples:
        - High fever without confusion, persistent vomiting
        - Moderate pain (e.g., kidney stone, severe headache but no stroke symptoms)
        - Deep laceration that is not actively bleeding heavily

    4 = MINOR – Can wait, not emergent. Examples:
        - Mild sprains, small cuts, cold/flu symptoms
        - Minor burns, rashes, earache

    5 = NON‑URGENT / ROUTINE – Routine checkup, prescription refill, mild rash.

    Identify the most likely hospital department (e.g., Cardiology, Orthopedics, General Medicine, ER, Trauma).

    Expected JSON Format exactly:
    {
        "priority": <int>,
        "department": "<string>",
        "clinical_summary": "<string max 10 words in English>"
    }
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Part.from_bytes(data=audio_bytes, mime_type=mime_type),
                prompt
            ]
        )

        raw_text = response.text.strip()

        if raw_text.startswith("```json"):
            raw_text = raw_text.replace("```json", "", 1)
        if raw_text.startswith("```"):
            raw_text = raw_text.replace("```", "", 1)
        if raw_text.endswith("```"):
            raw_text = raw_text[::-1].replace("```", "", 1)[::-1]

        parsed_data = json.loads(raw_text.strip())

        required_keys = ["priority", "department", "clinical_summary"]
        for key in required_keys:
            if key not in parsed_data:
                raise KeyError(f"Missing key in LLM response: {key}")

        return parsed_data

    except Exception as e:
        print(f"Audio NLP Engine Error: {str(e)}")
        return {
            "priority": 3,
            "department": "General Medicine - Unclassified",
            "clinical_summary": "Audio parsing failed. Manual review required."
        }