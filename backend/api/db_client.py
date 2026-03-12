import os
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

load_dotenv()

cred_path = os.getenv("FIREBASE_CREDENTIALS", "firebase-credentials.json")

# Ensure we only initialize the app once to prevent crashing on server reloads
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        print("Firebase Admin initialized successfully.")
    except Exception as e:
        print(f"CRITICAL: Failed to initialize Firebase. Check your json key. Error: {e}")

db = firestore.client()

def push_patient_to_queue(patient_payload: dict) -> bool:
    """
    Pushes the fully processed patient payload to Firestore.
    Uses the patient_id as the document ID to prevent duplicates.
    """
    try:
        # 1. Create a shallow copy to prevent mutating the API response
        db_payload = patient_payload.copy()
        
        # 2. Add the Firebase-specific timestamp to the copy
        db_payload["timestamp"] = firestore.SERVER_TIMESTAMP
        
        # 3. Push the copy to the database
        doc_ref = db.collection("patients_queue").document(db_payload["patient_id"])
        doc_ref.set(db_payload)
        return True
        
    except Exception as e:
        print(f"Firestore Write Error: {str(e)}")
        return False