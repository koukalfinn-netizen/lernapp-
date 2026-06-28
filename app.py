import streamlit as st
from PIL import Image
from openai import OpenAI
import os
import base64
import io
import datetime
import re

# =========================================================================
# 1. MANAGEMENT & API AUTHENTIFIZIERUNG
# =========================================================================
FESTER_API_KEY = "sk-proj-VC0P5MOPeotJSISZshXYEaePtQYCyuqYNuMQGj9N1I-eLkdjwr4lNV-tSKjKSbsJ"

# Globaler Client initialisieren
client = OpenAI(api_key=FESTER_API_KEY)

st.set_page_config(
    page_title="iPad Premium OS Workspace MAX", 
    page_icon="📲", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Strukturierte Server-Verzeichnisse erstellen
for ordner in ["meine_pdfs", "meine_fitness_plaene", "meine_notizen"]:
    if not os.path.exists(ordner):
        os.makedirs(ordner)

# =========================================================================
# 2. ACCURATE STATE ENGINE (Permanentes System-Gedächtnis)
# =========================================================================
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

# Live Echtzeit-Nährstoff- und Aktivitäts-Tracker
if "live_wasser" not in st.session_state:
    st.session_state.live_wasser = 0
if "live_protein" not in st.session_state:
    st.session_state.live_protein = 0
if "live_schritte" not in st.session_state:
    st.session_state.live_schritte = 0
if "live_verbrannte_kalorien" not in st.session_state:
    st.session_state.live_verbrannte_kalorien = 0

# Streaks & Zeitstempel-Historie (Anti-Cheat)
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

# Gedächtnis-Datenbank für KI-Berichte
if "ki_fitness_gedaechtnis" not in st.session_state:
    st.session_state.ki_fitness_gedaechtnis = []
if "ki_lern_gedaechtnis" not in st.session_state:
    st.session_state.ki_lern_gedaechtnis = []
if "chat_history_fitness" not in st.session_state:
    st.session_state.chat_history_fitness = []
if "chat_history_lernen" not in st.session_state:
    st.session_state.chat_history_lernen = []

# Erweiterte Dashboard-Zusatzdaten
if "supplements" not in st.session_state:
    st.session_state.supplements = {"Kreatin": False, "Omega 3": False, "Zink/Magnesium": False}
if "stundenplan" not in st.session_state:
    st.session_state.stundenplan = {"Montag": "", "Dienstag": "", "Mittwoch": "", "Donnerstag": "", "Freitag": ""}

# =========================================================================
# 3. CRON-LOGIK: AUTOMATISCHER VERFALL BEI INAKTIVITÄT
# =========================================================================
heute = datetime.date.today()
if (heute - st.session_state.last_fit_log).days >= 2:
    st.session_state.fit_streak = 0
    st.sidebar.error("⚠️ Inaktivität im Sport! Dein Fitness-Streak wurde auf 0 gesetzt.")
if (heute - st.session_state.last_lern_log).days >= 2:
    st.session_state.lern_streak = 0
    st.sidebar.error("⚠️ Inaktivität in der Schule! Dein Lern-Streak wurde auf 0 gesetzt.")

# =========================================================================
# 4. SIDEBAR: CONTROL CENTER & MATRIX FARBSTUDIO
# =========================================================================
with st.sidebar:
    st.title("📲 iPad Control Center")
    st.markdown("Wähle dein aktives Premium-Modul aus:")
    modus = st.selectbox(
        "App auswählen:", 
        ["🏋️‍♂️ ATHLETE PRO", "🎓 CAMPUS EXPERT", "🏆 MEILENSTEINE & POKALE", "🌆 KI-ABEND-REPORT"]
    )
    
    st.divider()
    st.markdown("### ⚙️ Profil-Einstellungen")
    if modus in ["🏋️‍♂️ ATHLETE PRO", "🏆 MEILENSTEINE & POKALE", "🌆 KI-ABEND-REPORT"]:
        st.session_state.alter = st.number_input("Alter", value=st.session_state.alter, min_value=1, max_value=120)
        st.session_state.gewicht = st.number_input("Gewicht (kg)", value=st.session_state.gewicht, min_value=1, max_value=300)
        st.session_state.groesse = st.number_input("Größe (cm)", value=st.session_state.groesse, min_value=50, max_value=250)
    else:
        st.session_state.klassenstufe = st.selectbox("Klassenstufe:", [f"{i}. Klasse" for i in range(5, 13)], index=5)
        
    st.divider()
    st.markdown("### 🎨 100+ Farbstudio (RGB Matrix Mixer)")
    farb_modus = st.radio("Farbwahl-Methode:", ["🎛️ RGB Mixer", "📌 Beliebte Presets"])
    
    r_val, g_val, b_val = 30, 30, 30
    if farb_modus == "🎛️ RGB Mixer":
        r_val = st.slider("🔴 Rotkanal", 0, 255, 30)
        g_val = st.slider("🟢 Grünkanal", 0, 255, 30)
        b_val = st.slider("🔵 Blaukanal", 0, 255, 30)
        st.session_state.custom_color = f"rgb({r_val}, {g_val}, {b_val})"
    else:
        presets = {
            "⚪ Modernes Grau": "#1e1e1e", 
            "⚫ Deep Black": "#000000", 
            "🧪 Neon Grün": "#39ff14", 
            "🔮 Neon Violett": "#9d00ff", 
            "🛍️ Neon Pink": "#ff1493", 
            "☀️ Helles Weiss": "#f5f5f5", 
            "💛 Helles Gelb": "#fff9a6"
        }
        wahl = st.selectbox("Preset auswählen:", list(presets.keys()))
        st.session_state.custom_color = presets[wahl]
        if wahl in ["☀️ Helles Weiss", "💛 Helles Gelb"]:
            r_val, g_val, b_val = 245, 245, 245

# --- INTELLIGENTE SCHRIFTKONTRAST-LOGIK (VERHINDERT FEHLERHAFTE SCHRIFTFARBEN) ---
luminanz = (r_val * 299 + g_val * 587 + b_val * 114) / 1000
schrift_farbe = "#000000" if luminanz > 1