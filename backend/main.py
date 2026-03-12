from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request, Response
from pydantic import BaseModel
from ml_core.predict import get_predictions
from api.nlp_engine import analyze_symptoms, analyze_audio_symptoms
from api.db_client import push_patient_to_queue
from api.email_service import send_triage_email
from dotenv import load_dotenv
from twilio.twiml.messaging_response import MessagingResponse
import requests
from requests.auth import HTTPBasicAuth
import os
import time

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

app = FastAPI(title="AI Triage & Scheduling Infrastructure API")


class PatientContext(BaseModel):
    priority: int
    queue_length: int
    hour_of_day: int
    avg_consult_time: float


class PatientSymptomRequest(BaseModel):
    patient_id: str
    patient_email: str
    raw_symptoms: str
    current_department_queue: int = 10
    hour_of_day: int = 14
    avg_consult_time: float = 15.0


@app.get("/")
def health_check():
    return {"status": "Enterprise Core Online", "version": "1.3.0"}


@app.post("/api/v1/ml/predict-wait-time")
def predict_wait(context: PatientContext):
    return get_predictions(
        priority=context.priority,
        queue_length=context.queue_length,
        hour_of_day=context.hour_of_day,
        avg_consult_time=context.avg_consult_time
    )


@app.post("/api/v1/triage/process-symptoms")
def process_patient_symptoms(request: PatientSymptomRequest):

    if not request.raw_symptoms:
        raise HTTPException(status_code=400, detail="Symptoms text cannot be empty.")

    triage_data = analyze_symptoms(request.raw_symptoms)

    ml_predictions = get_predictions(
        priority=triage_data["priority"],
        queue_length=request.current_department_queue,
        hour_of_day=request.hour_of_day,
        avg_consult_time=request.avg_consult_time
    )

    final_payload = {
        "patient_id": request.patient_id,
        "patient_email": request.patient_email,
        "raw_symptoms": request.raw_symptoms,
        "triage_results": triage_data,
        "queue_analytics": ml_predictions,
        "action_required": "dispatch_ambulance"
        if ml_predictions.get("requires_immediate_attention")
        else "schedule_slot"
    }

    push_patient_to_queue(final_payload)

    send_triage_email(
        patient_email=request.patient_email,
        priority=triage_data["priority"],
        department=triage_data["department"],
        wait_time=ml_predictions["estimated_wait_time_minutes"],
        summary=triage_data["clinical_summary"]
    )

    return final_payload


@app.post("/api/v1/triage/voice-intake")
async def process_voice_symptoms(
    patient_id: str = Form(...),
    patient_email: str = Form(...),
    latitude: float = Form(None),
    longitude: float = Form(None),
    audio_file: UploadFile = File(...)
):

    audio_bytes = await audio_file.read()

    triage_data = analyze_audio_symptoms(audio_bytes, audio_file.content_type)

    ml_predictions = get_predictions(
        priority=triage_data["priority"],
        queue_length=12,
        hour_of_day=14,
        avg_consult_time=15.0
    )

    action = "schedule_slot"
    ambulance_eta = None

    if ml_predictions.get("requires_immediate_attention") and latitude and longitude:
        action = "dispatch_ambulance"
        ambulance_eta = "8 minutes"
        triage_data["clinical_summary"] = (
            f"[AMBULANCE DISPATCHED to {latitude}, {longitude}] "
            + triage_data["clinical_summary"]
        )

    final_payload = {
        "patient_id": patient_id,
        "patient_email": patient_email,
        "raw_symptoms": "Audio Voice Note Processed",
        "location": {"lat": latitude, "lng": longitude} if latitude else None,
        "triage_results": triage_data,
        "queue_analytics": ml_predictions,
        "action_required": action,
        "ambulance_eta": ambulance_eta
    }

    push_patient_to_queue(final_payload)

    send_triage_email(
        patient_email=patient_email,
        priority=triage_data["priority"],
        department=triage_data["department"],
        wait_time=ml_predictions["estimated_wait_time_minutes"],
        summary=triage_data["clinical_summary"]
    )

    return final_payload


@app.post("/api/v1/triage/whatsapp-webhook")
async def whatsapp_webhook(request: Request):

    form_data = await request.form()

    sender_phone = form_data.get("From", "Unknown_WhatsApp")
    latitude = form_data.get("Latitude")
    longitude = form_data.get("Longitude")
    media_url = form_data.get("MediaUrl0")

    twiml_response = MessagingResponse()

    if not media_url:
        twiml_response.message(
            "Govt Hospital AI Triage: Please send a VOICE NOTE describing your symptoms. Attach your LOCATION if this is an emergency."
        )
        return Response(content=str(twiml_response), media_type="application/xml")

    try:

        media_url = form_data.get("MediaUrl0")

        print(f"Media URL received: {media_url}")

        auth = HTTPBasicAuth(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        for attempt in range(3):
            try:
                audio_response = requests.get(media_url, auth=auth, timeout=10)
                print(f"Attempt {attempt+1} status: {audio_response.status_code}")

                if audio_response.status_code == 200:
                    audio_bytes = audio_response.content
                    break
                else:
                    print(f"Attempt {attempt+1} failed with status {audio_response.status_code}")
                    if attempt < 2:
                        time.sleep(2 ** attempt)

            except Exception as e:
                print(f"Attempt {attempt+1} exception: {e}")
                if attempt < 2:
                    time.sleep(2 ** attempt)

        else:
            raise Exception("Failed to download audio after 3 attempts.")

        mime_type = form_data.get("MediaContentType0", "audio/ogg")

        triage_data = analyze_audio_symptoms(audio_bytes, mime_type)

        ml_predictions = get_predictions(
            priority=triage_data["priority"],
            queue_length=12,
            hour_of_day=14,
            avg_consult_time=15.0
        )

        action = "schedule_slot"
        ambulance_eta = None

        if ml_predictions.get("requires_immediate_attention") and latitude and longitude:
            action = "dispatch_ambulance"
            ambulance_eta = "8 minutes"
            triage_data["clinical_summary"] = (
                f"[AMBULANCE DISPATCHED to {latitude}, {longitude}] "
                + triage_data["clinical_summary"]
            )

            reply_msg = f"🚨 EMERGENCY PRIORITY {triage_data['priority']}: Ambulance dispatched to your location. ETA: {ambulance_eta}. Do not move."

        else:

            reply_msg = (
                f"🏥 Triage complete. Priority: {triage_data['priority']} "
                f"({triage_data['department']}).\nEstimated wait time: "
                f"{ml_predictions['estimated_wait_time_minutes']} mins. "
                f"Please proceed to the hospital."
            )

        final_payload = {
            "patient_id": sender_phone,
            "patient_email": "whatsapp_user@hospital.com",
            "raw_symptoms": "WhatsApp Voice Note Processed",
            "location": {"lat": latitude, "lng": longitude} if latitude else None,
            "triage_results": triage_data,
            "queue_analytics": ml_predictions,
            "action_required": action,
            "ambulance_eta": ambulance_eta
        }

        push_patient_to_queue(final_payload)

        twiml_response.message(reply_msg)

        return Response(content=str(twiml_response), media_type="application/xml")

    except Exception as e:
        print(f"Webhook Error: {str(e)}")

        twiml_response.message(
            "System Error: Failed to process triage. Please proceed directly to the Emergency Room."
        )

        return Response(content=str(twiml_response), media_type="application/xml")