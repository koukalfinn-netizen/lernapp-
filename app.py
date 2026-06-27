import streamlit as st
from PIL import Image
from openai import OpenAI
import os
import base64
import io
import datetime

# 1. HARDCODETER API KEY (Frisch & Aktiv)
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

# --- STREAK-VERLUST-LOGIK (Automatischer Check auf Inaktivität) ---
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
    st.markdown("### 🎨 100+ Farbstudio (RGB Mixer)")
    
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
            "🛍️ Neon Pink": "#ff1493"
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

# --- RECHNER-LOGIK FÜR SICH LEERENDE EINGABEFELDER (All-in-One &