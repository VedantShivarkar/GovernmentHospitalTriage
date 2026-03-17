# 🚑 AI-Powered Government Hospital Triage & Scheduling System

**Team YCCE** – 1st Prize Winner, Innovate X Sprint 1.0  
*Revolutionizing emergency care through WhatsApp, AI, and real-time Machine Learning.*

![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen)
![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![React](https://img.shields.io/badge/React-Vite-61DAFB.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-009688.svg)
![Gemini](https://img.shields.io/badge/AI-Gemini_2.5_Flash-orange.svg)

---

## 📌 Problem Statement

Government hospitals face long queues and inefficient appointment systems. Patients often struggle to navigate complex booking processes, especially in emergencies. We need a system that allows patients to book appointments easily, optimizes doctor availability, and reduces waiting time – without requiring patients to download another app.

---

## 💡 Our Solution

We built a **zero‑friction, multilingual AI triage engine** that works entirely through **WhatsApp**. Patients simply send a **voice note** describing their symptoms (in Marathi, Hindi, or English) and optionally share their **location**. Our system:

- 🧠 **Understands** the symptoms using **Gemini 2.5 Flash** (multimodal AI) – translates, triages, and assigns a priority (1–5) and department.
- ⏱️ **Predicts** dynamic wait times using a **Random Forest Regressor** trained on live queue data.
- 🚑 **Dispatches an ambulance automatically** for Priority 1 or 2 cases when location is shared.
- 📧 **Sends email confirmations** to patients with their triage results and wait time.
- 📊 **Updates a real‑time React dashboard** (via Firebase Firestore) so hospital admins see the queue instantly.

**No app downloads. No typing. Just your voice.**

---

## ✨ Key Features

| Module                     | Description                                                                                         |
|----------------------------|-----------------------------------------------------------------------------------------------------|
| 📱 **WhatsApp Voice Intake** | Patients send a voice note in Marathi/Hindi/English; AI extracts symptoms natively.                 |
| 📍 **Location Sharing** | Share location via WhatsApp to instantly trigger ambulance dispatch for emergencies.                |
| 🧠 **AI Triage (Gemini)** | Classifies priority (1–5) and maps to the correct department (ER, Cardiology, Orthopedics, etc.).   |
| ⏳ **ML‑Based Wait Times** | Random Forest Regressor predicts dynamic waiting times based on current queue load and priority.    |
| 🚨 **Emergency Dispatch** | Priority 1/2 + GPS location → automatic ambulance trigger with estimated ETA.                       |
| 📧 **Email Notifications** | Sends secure confirmation emails with triage summaries and time slots via Gmail SMTP.               |
| 📊 **Real‑Time Dashboard** | React admin panel updates instantly via Firebase WebSockets. Critical cases flash red and bypass the queue. |
| 🐳 **Dockerized Deployment** | One‑command deployment using Docker Compose – ready for hospital self-hosting.                      |

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
🛠️ Tech StackDomainTechnologies UsedBackendPython, FastAPI, Scikit‑Learn, Pandas, NumPy, JoblibAI / NLPGoogle Gemini 2.5 Flash (google-genai SDK)DatabaseFirebase Firestore (Admin SDK)FrontendReact, Vite, Tailwind CSS (v3), Firebase Client SDKMessagingTwilio API (WhatsApp Webhook), Python smtplib (Email)InfrastructureDocker, Docker Compose, Localtunnel / Ngrok🚀 Getting StartedPrerequisitesDocker and Docker ComposeTwilio Account (Free Sandbox)Google AI Studio API Key (Free Tier)Firebase Project (Firestore enabled)Gmail account with an App Password1. Clone the RepositoryBashgit clone https://github.com/your-username/govt-hospital-triage.git
cd govt-hospital-triage
2. Set Up Environment VariablesCreate a .env file in the /backend directory:Code snippetPORT=8000
ENVIRONMENT=development
GEMINI_API_KEY=AIzaSy...
EMAIL_SENDER=your_hospital_email@gmail.com
EMAIL_PASSWORD=your_app_password
FIREBASE_CREDENTIALS=firebase-credentials.json
3. Add Firebase CredentialsDownload your Firebase service account key (JSON) from the Firebase Console and place it in the backend/ folder as firebase-credentials.json.4. Run with Docker ComposeBashdocker-compose up -d
Frontend: http://localhost:5173 (or port specified in your Dockerfile)Backend API: http://localhost:8000Swagger API Docs: http://localhost:8000/docs5. Connect Twilio WhatsApp SandboxExpose your local server using Localtunnel:Bashnpx localtunnel --port 8000
In the Twilio Console, set the "When a message comes in" webhook to:https://<your-localtunnel-url>/api/v1/triage/whatsapp-webhookConnect your phone by sending the Twilio join code (e.g., join mango-123).📱 Live Demo Flow (How it Works)Open the React dashboard on a monitor. The queue is waiting.Open WhatsApp on your phone and enter the Twilio sandbox chat.Tap + → Location to share your current GPS pin.Hold the microphone and record a voice note in Marathi/Hindi/English describing a severe emergency (e.g., "My chest is hurting very badly and my left arm is numb.").Watch the dashboard: Within milliseconds, the React UI flashes red. A Priority 1 ER card bypasses the queue, displaying the English translation and an "Ambulance Dispatched" alert.Watch your phone: Your phone instantly buzzes with a WhatsApp reply: "🚨 EMERGENCY PRIORITY 1: Ambulance dispatched to your location. ETA: 8 minutes. Do not move."👥 The Engineering Squad (Team YCCE)Vedant Shivarkar (Team Lead): Core Architecture, FastAPI Backend, Machine Learning Engine, and Twilio Webhooks.Ishika Sakhare: Frontend UI/UX and React Component Architecture.Harshal Mohadikar: Real-Time State Management and Firebase Listener Integration.Vansh Meshram: Firestore Database Schema and Cloud Connectivity.Built to save lives. Open-sourced for the developer community under the MIT License.
