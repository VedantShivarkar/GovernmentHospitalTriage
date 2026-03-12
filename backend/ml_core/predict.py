import joblib
import pandas as pd
import os

MODEL_DIR = os.path.dirname(os.path.abspath(__file__))

# Load models safely
try:
    rf_model = joblib.load(os.path.join(MODEL_DIR, 'wait_time_model.pkl'))
    anomaly_model = joblib.load(os.path.join(MODEL_DIR, 'anomaly_model.pkl'))
except FileNotFoundError:
    rf_model = None
    anomaly_model = None

def get_predictions(priority: int, queue_length: int, hour_of_day: int, avg_consult_time: float):
    if not rf_model or not anomaly_model:
        return {"error": "Models not trained yet."}
        
    input_data = pd.DataFrame([{
        'priority': priority,
        'queue_length': queue_length,
        'hour_of_day': hour_of_day,
        'avg_consult_time': avg_consult_time
    }])
    
    predicted_wait_time = rf_model.predict(input_data)[0]
    # Isolation forest returns -1 for anomaly, 1 for normal
    anomaly_score = anomaly_model.predict(input_data)[0]
    
    return {
        "estimated_wait_time_minutes": round(predicted_wait_time, 2),
        "is_anomaly": bool(anomaly_score == -1),
        "requires_immediate_attention": bool(priority == 1 or anomaly_score == -1)
    }