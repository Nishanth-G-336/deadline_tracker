import json
import streamlit as st
from google import genai
from google.genai import types
from twilio.rest import Client as TwilioClient

from prompts import SUMMARY_REQUEST_PROMPT, SYSTEM_PROMPT, WELCOME_MESSAGE_TEMPLATE

# Model configuration
MODEL_NAME = "gemini-3.8-flash"

st.set_page_config(
    page_title="Deadline Tracker",
    page_icon="📅",
    layout="centered"
)

# Secrets retrieval with friendly error handling
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error(
        "⚠️ GEMINI_API_KEY not found in `.streamlit/secrets.toml`. "
        "Please copy `secrets.toml.example` to `secrets.toml` and add your Gemini API key."
    )
    st.stop()

TWILIO_ACCOUNT_SID = st.secrets.get("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = st.secrets.get("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP_FROM = st.secrets.get("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
TWILIO_CONTENT_SID = st.secrets.get("TWILIO_CONTENT_SID", "")


@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=GEMINI_API_KEY)


@st.cache_resource
def get_twilio_client():
    if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
        return TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    return None


gemini_client = get_gemini_client()
twilio_client = get_twilio_client()


def render_message(message):
    with st.chat_message(message["role"]):
        if message["kind"] == "text":
            st.write(message["content"])
        elif message["kind"] == "image":
            st.image(message["content"])


def add_message(role, kind, content):
    st.session_state.messages.append({"role": role, "kind": kind, "content": content})
    render_message(st.session_state.messages[-1])


def ask_gemini(parts):
    try:
        return st.session_state.chat.send_message(parts).text
    except Exception as error:
        return f"Sorry, something went wrong: {error}"


def clean_whatsapp_text(text):
    if not text:
        return "No upcoming deadlines recorded."
    text = " ".join(text.split())  # collapse whitespace / newlines
    return text[:1500] + "..." if len(text) > 1500 else text


def send_whatsapp(to_number, user_name, summary):
    if not twilio_client:
        return False, "Twilio credentials are not configured in secrets.toml."
    try:
        # If Content Template SID is provided, use Content API (recommended for WhatsApp Business)
        if TWILIO_CONTENT_SID:
            content_variables = json.dumps(
                {"1": user_name, "2": clean_whatsapp_text(summary)}, ensure_ascii=False
            )
            message = twilio_client.messages.create(
                from_=TWILIO_WHATSAPP_FROM,
                to=f"whatsapp:{to_number}",
                content_sid=TWILIO_CONTENT_SID,
                content_variables=content_variables,
            )
        else:
            # Fallback to direct sandbox body message
            body_text = f"Hi {user_name}, here is your Deadline Tracker digest:\n\n{clean_whatsapp_text(summary)}"
            message = twilio_client.messages.create(
                from_=TWILIO_WHATSAPP_FROM,
                to=f"whatsapp:{to_number}",
                body=body_text,
            )
        return True, message.sid
    except Exception as error:
        return False, str(error)


# Step 1: Onboarding Screen
if "onboarded" not in st.session_state:
    st.title("📅 Deadline Tracker")
    st.caption("Snap your syllabus. Extract your deadlines. Text yourself the reminders.")

    with st.form("onboarding_form"):
        name = st.text_input("Your name", placeholder="e.g. Alex")
        whatsapp_number = st.text_input(
            "WhatsApp number (with country code)",
            placeholder="+91XXXXXXXXXX",
            help="This is the number Deadline Tracker will text your deadline reminders to.",
        )
        submitted = st.form_submit_button("Let's go 🚀")

    if submitted:
        if not name.strip() or not whatsapp_number.strip():
            st.warning("Please fill in both your name and WhatsApp number.")
        else:
            st.session_state.name = name.strip()
            st.session_state.whatsapp_number = whatsapp_number.strip()
            st.session_state.chat = gemini_client.chats.create(
                model=MODEL_NAME,
                config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
            )
            st.session_state.messages = []
            st.session_state.onboarded = True
            st.rerun()
    st.stop()


# Step 2: Main Chat & Action Interface
header_col, button_col = st.columns([5, 2], vertical_alignment="center")

with header_col:
    st.title("📅 Deadline Tracker")

with button_col:
    # Disable button until at least one exchange has happened beyond welcome message
    send_disabled = len(st.session_state.messages) <= 2
    if st.button("📤 Send to WhatsApp", disabled=send_disabled, use_container_width=True):
        with st.spinner("Compiling your deadline digest..."):
            summary = ask_gemini([SUMMARY_REQUEST_PROMPT])
            success, info = send_whatsapp(
                st.session_state.whatsapp_number, st.session_state.name, summary
            )
            if success:
                st.success("Sent! Check your WhatsApp 📲")
            else:
                st.error(f"Couldn't send that: {info}")

st.caption(
    f"Logged in as **{st.session_state.name}** • Reminders sent to **{st.session_state.whatsapp_number}**"
)

# Render chat history or initial welcome message
if not st.session_state.messages:
    add_message(
        "assistant", "text", WELCOME_MESSAGE_TEMPLATE.format(name=st.session_state.name)
    )
else:
    for message in st.session_state.messages:
        render_message(message)

# Step 3: Handle Input (Text and Photo Uploads)
user_input = st.chat_input(
    "Ask a question, or attach a photo of your syllabus / timetable",
    accept_file=True,
    file_type=["jpg", "jpeg", "png"],
)

if user_input:
    photo = user_input.files[0] if user_input.files else None
    text = user_input.text
    parts = []

    if photo is not None:
        photo_bytes = photo.getvalue()
        add_message("user", "image", photo_bytes)
        parts.append(types.Part.from_bytes(data=photo_bytes, mime_type=photo.type))

    if text:
        add_message("user", "text", text)
        parts.append(text)
    elif photo is not None:
        parts.append(
            "What are the deadlines, exam dates, and tasks shown in this photo? "
            "Please extract all dates, subject names, and submission details."
        )

    with st.spinner("Scanning for deadlines & schedules..."):
        answer = ask_gemini(parts)
        add_message("assistant", "text", answer)
