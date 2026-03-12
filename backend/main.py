from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ml_core.predict import get_predictions
from api.nlp_engine import analyze_symptoms
from api.db_client import push_patient_to_queue
from api.email_service import send_triage_email # NEW IMPORT
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
    patient_email: str # NEW FIELD
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

    # 1. NLP Parsing
    triage_data = analyze_symptoms(request.raw_symptoms)
    
    # 2. Wait Time Prediction
    ml_predictions = get_predictions(
        priority=triage_data["priority"],
        queue_length=request.current_department_queue,
        hour_of_day=request.hour_of_day,
        avg_consult_time=request.avg_consult_time
    )
    
    # 3. Assemble Payload
    final_payload = {
        "patient_id": request.patient_id,
        "patient_email": request.patient_email,
        "raw_symptoms": request.raw_symptoms,
        "triage_results": triage_data,
        "queue_analytics": ml_predictions,
        "action_required": "dispatch_ambulance" if ml_predictions.get("requires_immediate_attention") else "schedule_slot"
    }
    
    # 4. Push to Firebase
    push_patient_to_queue(final_payload)
    
    # 5. Send Email Notification (NEW STEP)
    send_triage_email(
        patient_email=request.patient_email,
        priority=triage_data["priority"],
        department=triage_data["department"],
        wait_time=ml_predictions["estimated_wait_time_minutes"],
        summary=triage_data["clinical_summary"]
    )
    
    return final_payload