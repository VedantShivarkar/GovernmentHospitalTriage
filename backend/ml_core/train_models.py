import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import joblib
import os

# Ensure the directory exists to save models
os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)
MODEL_DIR = os.path.dirname(os.path.abspath(__file__))

def generate_synthetic_data(num_samples=5000):
    """Generates synthetic hospital queue data for training."""
    np.random.seed(42)
    
    # Features
    # Triage Priority: 1 (Critical) to 5 (Non-Urgent)
    priority = np.random.choice([1, 2, 3, 4, 5], size=num_samples, p=[0.05, 0.15, 0.3, 0.3, 0.2])
    # Current patients in queue
    queue_length = np.random.randint(0, 50, size=num_samples)
    # Hour of the day (0-23)
    hour_of_day = np.random.randint(0, 24, size=num_samples)
    # Average consultation time for the specific department (minutes)
    avg_consult_time = np.random.uniform(5, 30, size=num_samples)
    
    # Target Variable: Wait Time (Minutes)
    # Base calculation + noise
    wait_time = (queue_length * avg_consult_time) / (6 - priority)
    wait_time += np.random.normal(0, 10, size=num_samples) 
    wait_time = np.clip(wait_time, 0, None) # No negative wait times
    
    df = pd.DataFrame({
        'priority': priority,
        'queue_length': queue_length,
        'hour_of_day': hour_of_day,
        'avg_consult_time': avg_consult_time,
        'wait_time': wait_time
    })
    return df

def train_and_save_models():
    print("Generating synthetic hospital data...")
    data = generate_synthetic_data()
    
    X = data[['priority', 'queue_length', 'hour_of_day', 'avg_consult_time']]
    y = data['wait_time']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 1. Train Random Forest Regressor for Wait Time Prediction
    print("Training Random Forest Regressor...")
    rf_model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
    rf_model.fit(X_train, y_train)
    
    predictions = rf_model.predict(X_test)
    mae = mean_absolute_error(y_test, predictions)
    print(f"Wait Time Model MAE: {mae:.2f} minutes")
    
    # 2. Train Isolation Forest for Anomaly Detection (e.g., weird symptom spikes / mass casualties)
    print("Training Anomaly Detection Engine...")
    anomaly_model = IsolationForest(contamination=0.05, random_state=42)
    anomaly_model.fit(X)
    
    # Save Models
    joblib.dump(rf_model, os.path.join(MODEL_DIR, 'wait_time_model.pkl'))
    joblib.dump(anomaly_model, os.path.join(MODEL_DIR, 'anomaly_model.pkl'))
    print(f"Models saved successfully in {MODEL_DIR}")

if __name__ == "__main__":
    train_and_save_models()