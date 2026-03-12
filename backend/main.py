from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ml_core.predict import get_predictions
from api.nlp_engine import analyze_symptoms
from api.db_client import push_patient_to_queue  # NEW IMPORT
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
    raw_symptoms: str
    current_department_queue: int = 10 
    hour_of_day: int = 14 
    avg_consult_time: float = 15.0 

@app.get("/")
def health_check():
    return {"status": "Enterprise Core Online", "version": "1.2.0"}

@app.post("/api/v1/ml/predict-wait-time")
def predict_wait(context: PatientContext):
    result = get_predictions(
        priority=context.priority,
        queue_length=context.queue_length,
        hour_of_day=context.hour_of_day,
        avg_consult_time=context.avg_consult_time
    )
    return result

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
        "raw_symptoms": request.raw_symptoms, # Keeping this for hospital admin context
        "triage_results": triage_data,
        "queue_analytics": ml_predictions,
        "action_required": "dispatch_ambulance" if ml_predictions.get("requires_immediate_attention") else "schedule_slot"
    }
    
    # 4. Push to Firebase Real-time Queue (NEW STEP)
    db_success = push_patient_to_queue(final_payload)
    
    if not db_success:
        print(f"Warning: Failed to sync patient {request.patient_id} to database.")
    
    return final_payload