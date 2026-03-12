from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from ml_core.predict import get_predictions
from api.nlp_engine import analyze_symptoms, analyze_audio_symptoms
from api.db_client import push_patient_to_queue
from api.email_service import send_triage_email
from dotenv import load_dotenv

load_dotenv()

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