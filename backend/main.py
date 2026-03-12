from fastapi import FastAPI
from pydantic import BaseModel
from ml_core.predict import get_predictions
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AI Triage & Scheduling Infrastructure API")

class PatientContext(BaseModel):
    priority: int
    queue_length: int
    hour_of_day: int
    avg_consult_time: float

@app.get("/")
def health_check():
    return {"status": "Enterprise Core Online", "version": "1.0.0"}

@app.post("/api/v1/ml/predict-wait-time")
def predict_wait(context: PatientContext):
    result = get_predictions(
        priority=context.priority,
        queue_length=context.queue_length,
        hour_of_day=context.hour_of_day,
        avg_consult_time=context.avg_consult_time
    )
    return result