# 📅 Deadline Tracker — AI Vision & Multimodal Chatbot

**Deadline Tracker** is an AI-powered study and deadline assistant built with **Streamlit**, **Google Gemini (Vision + Chat)**, and **Twilio (WhatsApp)**. 

Students can simply photograph a syllabus, timetable, assignment sheet, or notice board—or type their upcoming academic tasks—and Deadline Tracker automatically extracts, organizes, and structures their deadlines in seconds. With one click, a formatted deadline digest is dispatched straight to their WhatsApp!

---

## 🌟 Features

- **Multimodal AI Vision & Chat**: Upload photos of syllabi, exam schedules, or lecture slides, or type queries directly.
- **Intelligent Date & Task Extraction**: Extracts courses, assignments, exams, due dates, times, and submission instructions with graceful fallback for photos without deadlines.
- **One-Click WhatsApp Digest**: Summarizes all discussed upcoming deadlines into a clean, mobile-friendly text message and sends it to the user's phone via Twilio.
- **Onboarding Experience**: Quick one-time login form capturing the student's name and WhatsApp number.
- **Session Continuity**: Retains chat history and cached Gemini client throughout the Streamlit session.

---

## 📁 Project Structure

```text
deadline_tracker/
├── app.py                     # Main Streamlit application and UI logic
├── prompts.py                 # AI persona, system prompt, and summary templates
├── requirements.txt           # Project dependencies
├── .gitignore                 # Prevents secrets, venv, and cache from being committed
├── README.md                  # Project overview and setup instructions
└── .streamlit/
    ├── secrets.toml.example   # Template for required API keys
    └── secrets.toml           # (Ignored by Git) Local secrets file with your real keys
```

---

## 🚀 Setup & Local Installation

### 1. Prerequisites
- Python 3.9 or newer
- A Google AI Studio API Key ([Google AI Studio](https://aistudio.google.com/))
- A free Twilio Account ([Twilio Console](https://www.twilio.com/try-twilio))

### 2. Clone / Open the Project
```bash
cd deadline_tracker
```

### 3. Create and Activate a Virtual Environment
- **Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
- **macOS / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Secrets
1. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`:
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```
2. Open `.streamlit/secrets.toml` and fill in your actual credentials:
   ```toml
   GEMINI_API_KEY = "AIzaSy..."
   TWILIO_ACCOUNT_SID = "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
   TWILIO_AUTH_TOKEN = "your_auth_token"
   TWILIO_WHATSAPP_FROM = "whatsapp:+14155238886"
   TWILIO_CONTENT_SID = "HXxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # (Optional: for Twilio Content Template)
   ```

### 6. Run the App
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🌐 Deploying to Streamlit Community Cloud

1. Push your repository to GitHub (ensure `.streamlit/secrets.toml` is **not** committed).
2. Go to [share.streamlit.io](https://share.streamlit.io/) and connect your GitHub repository.
3. Select `app.py` as the entrypoint.
4. Go to **Settings → Secrets** in Streamlit Cloud and paste your keys from `.streamlit/secrets.toml`.
5. Click **Deploy**!

---

## 🛡️ Security Note
Never commit your real `.streamlit/secrets.toml` to GitHub. The included `.gitignore` ensures your API keys and credentials stay private.
