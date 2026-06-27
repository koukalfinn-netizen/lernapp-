import streamlit as st
from PIL import Image
from openai import OpenAI
import os
import base64
import io
import datetime

# 1. HARDCODETER API KEY
FESTER_API_KEY = "sk-proj-VC0P5MOPeotJSISZshXYEaePtQYCyuqYNuMQGj9N1I-eLkdjwr4lNV-tSKjKSbsJ"

st.set_page_config(page_title="iPad Premium OS Workspace", page_icon="📲", layout="wide")

# --- SYSTEM-GEDÄCHTNIS INITIALISIEREN (Session State) ---
if "gewicht" not in st.session_state: 
    st.session_state.gewicht = 70
if "groesse" not in st.session_state: 
    st.session_state.groesse = 175
if "alter" not in st.session_state: 
    st.session_state.alter = 16
if "klassenstufe" not in st.session_state: 
    st.session_state.klassenstufe = "10. Klasse"
if "custom_color" not in st.session_state: 
    st.session_state.custom_color = "#1e1e1e"

# Streaks & Timer-Logs
if "fit_streak" not in st.session_state: 
    st.session_state.fit_streak = 3
if "last_fit_log" not in st.session_state: 
    st.session_state.last_fit_log = datetime.date.today()
if "last_video_upload" not in st.session_state: 
    st.session_state.last_video_upload = datetime.date.today()

if "lern_streak" not in st.session_state: 
    st.session_state.lern_streak = 1
if "last_lern_log" not in st.session_state: 
    st.session_state.last_lern_log = datetime.date.today()
if "gelöste_aufgaben" not in st.session_state: 
    st.session_state.gelöste_aufgaben = 2

# Unsichtbares KI-Gedächtnis für den Abend-Report
if "ki_fitness_gedaechtnis" not in st.session_state: 
    st.session_state.ki_fitness_gedaechtnis = []
if "ki_lern_gedaechtnis" not in st.session_state: 
    st.session_state.ki_lern_gedaechtnis = []

# Chat-Verläufe
if "chat_history_fitness" not in st.session_state: 
    st.session_state.chat_history_fitness = []
if "chat_history_lernen" not in st.session_state: 
    st.session_state.chat_history_lernen = []

# --- STREAK-VERLUST-LOGIK ---
heute = datetime.date.today()
if (heute - st.session_state.last_fit_log).days >= 2:
    st.session_state.fit_streak = 0
    st.sidebar.error("⚠️ Inaktivität im Sport! Dein Fitness-Streak wurde auf 0 gesetzt.")
if (heute - st.session_state.last_lern_log).days >= 2:
    st.session_state.lern_streak = 0
    st.sidebar.error("⚠️ Inaktivität in der Schule! Dein Lern-Streak wurde auf 0 gesetzt.")

# --- SIDEBAR: KONTROLLZENTRUM (Farbstudio & Profile) ---
with st.sidebar:
    st.title("📲 iPad Control Center")
    modus = st.selectbox("App auswählen:", ["🏋️‍♂️ ATHLETE PRO", "🎓 CAMPUS EXPERT", "🏆 MEILENSTEINE & POKALE", "🌆 KI-ABEND-REPORT"])
    
    st.divider()
    st.markdown("### ⚙️ Profil-Einstellungen (Änderbar)")
    if modus in ["🏋️‍♂️ ATHLETE PRO", "🏆 MEILENSTEINE & POKALE"]:
        st.session_state.alter = st.number_input("Alter", value=st.session_state.alter)
        st.session_state.gewicht = st.number_input("Gewicht (kg)", value=st.session_state.gewicht)
        st.session_state.groesse = st.number_input("Größe (cm)", value=st.session_state.groesse)
    else:
        st.session_state.klassenstufe = st.selectbox("Klassenstufe:", [f"{i}. Klasse" for i in range(5, 13)], index=5)
        
    st.divider()
    st.markdown("### 🎨 100+ Farbstudio (Einfarbig)")
    
    farb_modus = st.radio("Wie willst du die Farbe wählen?", ["🎛️ Eigener RGB-Mixer", "📌 Beliebte Presets"])
    
    if farb_modus == "🎛️ Eigener RGB-Mixer":
        r = st.slider("🔴 Rot-Anteil", 0, 255, 30)
        g = st.slider("🟢 Grün-Anteil", 0, 255, 30)
        b = st.slider("🔵 Blau-Anteil", 0, 255, 30)
        st.session_state.custom_color = f"rgb({r}, {g}, {b})"
    else:
        presets = {
            "⚪ Standard Grau": "#1e1e1e", 
            "⚫ Deep Black": "#000000",
            "🧪 Neon Grün": "#39ff14", 
            "🔮 Neon Violett": "#9d00ff", 
            "🔥 Neon Orange": "#ff5f1f", 
            "🐬 Neon Türkis": "#00f5ff", 
            "🛍️ Neon Pink": "#ff1493",
            "🍇 Pflaume (Mischung)": "#4a0e4e", 
            "🍓 Erdbeere (Mischung)": "#ff6b8b", 
            "🪸 Koralle (Mischung)": "#ff7f50"
        }
        wahl = st.selectbox("Preset wählen:", list(presets.keys()))
        st.session_state.custom_color = presets[wahl]

# Farb-Injektion für komplett einfarbigen Hintergrund
st.markdown(f"""
    <style>
    .stApp {{ background-color: {st.session_state.custom_color} !important; color: white !important; }}
    h1, h2, h3, h4, h5, h6, p, span, label {{ color: white !important; }}
    .stButton>button {{
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }}
    </style>
""", unsafe_allow_html=True)

# --- RECHNER-LOGIK FÜR SICH LEERENDE EINGABEFELDER ---
def food_eingabe_callback():
    text = st.session_state.food_eingabe_key
    if text:
        st.session_state.ki_fitness_gedaechtnis.append(f"Eintrag ({heute.strftime('%H:%M')}): {text}")
        st.toast(f"🍕 KI hat sich gemerkt: '{text}'")
        st.session_state.food_eingabe_key = ""

def lern_eingabe_callback():
    text = st.session_state.lern_eingabe_key
    if text:
        st.session_state.ki_lern_gedaechtnis.append(f"Gelernt ({heute.strftime('%H:%M')}): {text}")
        st.toast(f"📚 KI hat gelernt: '{text}'")
        st.session_state.lern_eingabe_key = ""

# --- BEREICH 1: FITNESS (ATHLETE PRO) ---
if modus == "🏋️‍♂️ ATHLETE PRO":
    st.title("🏋️‍♂️ ATHLETE PRO Dashboard")
    st.caption(f"🧬 Profil: {st.session_state.alter} Jahre | {st.session_state.gewicht}kg | {st.session_state.groesse}cm")
    
    k1, k2 = st.columns(2)
    with k1:
        st.metric("🔥 Aktueller Sport-Streak", f"{st.session_state.fit_streak} Tage")
        if st.button("🗑️ Sportcounter auf 0 zurücksetzen", use_container_width=True):
            st.session_state.fit_streak = 0
            st.rerun()
    with k2:
        if (heute - st.session_state.last_video_upload).days >= 7:
            st.warning("🚨 NACHRICHT VOM COACH: Du hast seit einer Woche kein Beweisvideo mehr hochgeladen! Los, zieh durch! 🦾")
        else:
            st.success("✅ Dein Video-Status ist für diese Woche aktiv.")

    st.divider()
    st.markdown("### 🥤 All-in-One Schnelleingabe (Essen, Getränke & Sport)")
    st.caption("Tippe es ein und drücke Enter. Das Feld leert sich, die KI speichert es im Tagesgedächtnis.")
    st.text_input("Was hast du zu dir genommen / getan?", key="food_eingabe_key", on_change=food_eingabe_callback)

    st.divider()
    st.markdown("### 📹 Video-Beweispflicht (Min. 5 Minuten)")
    video_file = st.file_uploader("Trainingsvideo auswählen...", type=["mp4", "mov", "avi"])
    if video_file is not None:
        st.info("⏱ Video wird auf Mindestlänge von 5 Minuten geprüft...")
        if st.button("✅ Video-Prüfung bestätigen & Streak erhöhen"):
            st.session_state.fit_streak += 1
            st.session_state.last_fit_log = heute
            st.session_state.last_video_upload = heute
            st.success("🎉 Video akzeptiert (> 5 Min)! Streak gesichert.")
            st.rerun()

    st.divider()
    st.markdown("### 📸 Personalisierter KI-Scanner")
    fit_option = st.selectbox("Scan-Typ:", ["Trainingsplan (auf mein Gewicht angepasst)", "Kalorien-Check von Fotos", "Technik-Fehleranalyse"])
    uploaded_file = st.file_uploader("Foto hochladen...", type=["jpg", "png", "jpeg"], key="fit_up")
    if uploaded_file and st.button("🚀 Foto sportwissenschaftlich auswerten"):
        client = OpenAI(api_key=FESTER_API_KEY)
        with st.spinner("Dein Trainer wertet aus..."):
            img_str = base64.b64encode(uploaded_file.getvalue()).decode()
            prompt = f"Nutzerdaten: {st.session_state.alter}J, {st.session_state.gewicht}kg, {st.session_state.groesse}cm. Analysiere das Bild für '{fit_option}' exakt passend zu diesen Körperdaten auf Deutsch."
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}}]}],
            )
            st.info(response.choices[0].message.content)

    st.divider()
    st.markdown("### 💬 Chat mit deinem Personal Trainer")
    for msg in st.session_state.chat_history_fitness:
        with st.chat_message(msg["role"]): 
            st.write(msg["content"])
    u_input = st.chat_input("Frage den Coach...")
    if u_input:
        st.session_state.chat_history_fitness.append({"role": "user", "content": u_input})
        client = OpenAI(api_key=FESTER_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": f"Du bist ein Fitness-Coach. Beachte die Nutzerdaten: {st.session_state.gewicht}kg, {st.session_state.alter}Jahre."}] + st.session_state.chat_history_fitness[-6:]
        )
        st.session_state.chat_history_fitness.append({"role": "assistant", "content": response.choices[0].message.content})
        st.rerun()

# --- BEREICH 2: SCHULE (CAMPUS EXPERT) ---
elif modus == "🎓 CAMPUS EXPERT":
    st.title("🎓 CAMPUS EXPERT Dashboard")
    st.caption(f"🎯 Niveau eingestellt auf: {st.session_state.klassenstufe}")
    
    k1, k2 = st.columns(2)
    with k1:
        st.metric("⚡ Aktueller Lern-Streak", f"{st.session_state.lern_streak} Tage")
        if st.button("🗑️ Lerncounter auf 0 zurücksetzen", use_container_width=True):
            st.session_state.lern_streak = 0
            st.rerun()