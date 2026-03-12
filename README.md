# 🚑 AI-Powered Government Hospital Triage & Scheduling System

**Team YCCE** – Hackathon Submission  
*Revolutionising emergency care through WhatsApp, AI, and real-time ML.*

---

## 📌 Problem Statement

Government hospitals face long queues and inefficient appointment systems. Patients often struggle to navigate complex booking processes, especially in emergencies. We need a system that allows patients to book appointments easily, optimises doctor availability, and reduces waiting time – without requiring patients to download another app.

---

## 💡 Our Solution

We built a **zero‑friction, multilingual AI triage engine** that works entirely through **WhatsApp**. Patients simply send a **voice note** describing their symptoms (in Marathi, Hindi, or English) and optionally share their **location**. Our system:

- 🧠 **Understands** the symptoms using **Gemini 2.5 Flash** (multimodal AI) – translates, triages, and assigns a priority (1–5) and department.
- ⏱️ **Predicts** dynamic wait times using a **Random Forest Regressor** trained on live queue data.
- 🚑 **Dispatches an ambulance automatically** for Priority 1 or 2 cases when location is shared.
- 📧 **Sends email confirmations** to patients (or a demo email) with their triage results and wait time.
- 📊 **Updates a real‑time React dashboard** (via Firebase Firestore) so hospital admins see the queue instantly.

**No app downloads. No typing. Just your voice.**

---

## ✨ Key Features

| Module                     | Description                                                                                         |
|----------------------------|-----------------------------------------------------------------------------------------------------|
| 📱 WhatsApp Voice Intake   | Patients send a voice note in Marathi/Hindi/English; AI extracts symptoms.                         |
| 📍 Location Sharing        | Share location via WhatsApp – used to dispatch ambulance for emergencies.                           |
| 🧠 AI Triage (Gemini)      | Classifies priority (1–5) and suggests department (ER, Cardiology, Orthopedics, etc.).             |
| ⏳ ML‑Based Wait Times     | Random Forest model predicts waiting time based on current queue and priority.                      |
| 🚨 Emergency Dispatch      | Priority 1/2 + location → automatic ambulance trigger (simulated ETA 8 min).                        |
| 📧 Email Notifications     | Sends confirmation email with triage summary and wait time (via Gmail SMTP).                        |
| 📊 Real‑Time Dashboard     | React app that updates instantly via Firebase when new patients arrive. Critical cases flash red.   |
| 🔁 Multi‑Language Support  | Voice notes in Marathi, Hindi, or English are understood natively by Gemini.                        |
| 🐳 Dockerised Deployment   | One‑command deployment using Docker Compose – any hospital can self‑host.                           |

---

## 🏗️ Architecture Overview

```mermaid
graph TD
    A[Patient WhatsApp] -->|Voice Note + Location| B[Twilio Sandbox]
    B -->|Webhook| C[FastAPI Backend]
    C -->|Download audio| B
    C -->|Gemini 2.5 Flash| D{Analyze Symptoms}
    D -->|Priority & Department| E[ML Wait Time Prediction]
    E -->|Wait Time| F[Assemble Payload]
    F --> G[(Firebase Firestore)]
    G --> H[React Dashboard]
    F --> I[Send Email via SMTP]
    F --> J[Reply via WhatsApp]
    J --> A

    Backend: FastAPI (Python) – serves ML predictions, handles webhooks, integrates with Firebase.

ML Models: Random Forest Regressor (wait time), Isolation Forest (anomaly detection).

AI/NLP: Google Gemini 2.5 Flash – multimodal audio understanding.

Database: Firebase Firestore (real‑time sync).

Frontend: React + Tailwind CSS – live dashboard with WebSocket updates.

Communication: Twilio (WhatsApp), Gmail SMTP (email).

Deployment: Docker / Docker Compose.

🛠️ Tech Stack
Area	Technology
Backend	Python, FastAPI, scikit‑learn, pandas, numpy, joblib
AI	Google Gemini 2.5 Flash (via google-genai)
Database	Firebase Firestore (Admin SDK)
Frontend	React, Vite, Tailwind CSS, Firebase Client SDK
Messaging	Twilio (WhatsApp), Gmail SMTP (nodemailer)
Infrastructure	Docker, Docker Compose, Localtunnel / ngrok
Version Ctrl	Git, GitHub
🚀 Getting Started – For Hospitals / Developers
Prerequisites
Docker and Docker Compose

A Twilio Account (free sandbox)

A Google Gemini API Key (free tier)

A Firebase Project (with Firestore in test mode)

A Gmail account with an App Password

1. Clone the Repository
bash
git clone https://github.com/your-org/govt-hospital-triage.git
cd govt-hospital-triage
2. Set Up Environment Variables
Copy the example environment file and fill in your secrets:

bash
cp backend/.env.example backend/.env
Edit backend/.env with your actual keys:

env
GEMINI_API_KEY=AIzaSy...
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=your_auth_token
EMAIL_SENDER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
WHATSAPP_DEMO_EMAIL=demo@hospital.com
FIREBASE_CREDENTIALS=/app/credentials.json
3. Add Firebase Credentials
Download your Firebase service account key (JSON) from the Firebase Console and place it at backend/firebase-credentials.json.

4. Run with Docker Compose
bash
docker-compose up -d
Frontend will be available at http://localhost

Backend API at http://localhost:8000

API documentation at http://localhost:8000/docs

5. Connect Twilio WhatsApp Sandbox
In Twilio Console, go to Messaging → Try it out → Send a WhatsApp message.

Note your sandbox phone number and join code (e.g., join mango-123).

Set the When a message comes in webhook to https://your-public-url/api/v1/triage/whatsapp-webhook (use localtunnel or ngrok for local testing).

From your phone, send the join code to the Twilio number.

📱 Live Demo Flow (For Judges)
Open the React dashboard on the projector – it shows the current queue.

Pick up your phone, open WhatsApp, and go to the Twilio sandbox chat.

Tap + → Location – share your current location. You'll receive a confirmation: "Location received. Now please send a VOICE NOTE describing your symptoms."

Hold the microphone and record a voice note in Marathi/Hindi/English describing an emergency (e.g., "माझ्या छातीत खूप दुखत आहे आणि श्वास घेण्यात त्रास होत आहे.").

Watch the dashboard – within seconds, a red Priority 1 card appears at the top with an ambulance dispatched message.

Your phone buzzes – you receive a WhatsApp reply: 🚑 Ambulance sent. Please proceed to the hospital.

Check your email (the demo email you set) – you'll also receive an email with the triage details.

Everything happens in real time, without a single page refresh or app download.

🧪 Testing Without WhatsApp
You can also test the API directly using the Swagger UI at http://localhost:8000/docs.

POST /api/v1/triage/voice-intake – upload an audio file and optionally pass latitude/longitude.

POST /api/v1/triage/process-symptoms – send raw text symptoms.

🐳 Docker Deployment (One‑Command)
We provide a docker-compose.yml that spins up both the backend and frontend. Make sure you have Docker installed, then:

bash
docker-compose up -d
To stop:

bash
docker-compose down
👥 Team
Vedant Shivarkar – Backend, Integration

Ishika Sakhare – Frontend, Dashboard

Harshal Mohadikar - Firebase

Vansh Meshram - Integration

College: Yeshwantrao Chavan College of Engineering (YCCE), Nagpur

📄 License
This project is open‑source under the MIT License – feel free to use, modify, and deploy for any purpose.

🙏 Acknowledgements
Google Gemini for the powerful multimodal AI.

Twilio for the WhatsApp sandbox.

Firebase for real‑time database.

The hackathon organisers for this inspiring problem statement.
