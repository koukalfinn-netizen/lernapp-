import streamlit as st
from PIL import Image
from openai import OpenAI
import os
import base64
import io
import datetime
import re

# 1. HARDCODETER API KEY (Frisch & Aktiv)
FESTER_API_KEY = "sk-proj-VC0P5MOPeotJSISZshXYEaePtQYCyuqYNuMQGj9N1I-eLkdjwr4lNV-tSKjKSbsJ"

st.set_page_config(page_title="iPad Premium OS Workspace", page_icon="📲", layout="wide")

# Ordner für Dokumente erstellen
if not os.path.exists("meine_pdfs"): os.makedirs("meine_pdfs")
if not os.path.exists("meine_fitness_plaene"): os.makedirs("meine_fitness_plaene")

# --- SYSTEM-GEDÄCHTNIS INITIALISIEREN (Session State) ---
if "gewicht" not in st.session_state: st.session_state.gewicht = 70
if "groesse" not in st.session_state: st.session_state.groesse = 175
if "alter" not in st.session_state: st.session_state.alter = 16
if "klassenstufe" not in st.session_state: st.session_state.klassenstufe = "10. Klasse"
if "custom_color" not in st.session_state: st.session_state.custom_color = "#1e1e1e"

# Live-Zähler für Ernährung & Bewegung
if "live_wasser" not in st.session_state: st.session_state.live_wasser = 0
if "live_protein" not in st.session_state: st.session_state.live_protein = 0
if "live_schritte" not in st.session_state: st.session_state.live_schritte = 0
if "live_verbrannte_kalorien" not in st.session_state: st.session_state.live_verbrannte_kalorien = 0

# Streaks & Logs
if "fit_streak" not in st.session_state: st.session_state.fit_streak = 3
if "last_fit_log" not in st.session_state: st.session_state.last_fit_log = datetime.date.today()
if "last_video_upload" not in st.session_state: st.session_state.last_video_upload = datetime.date.today()

if "lern_streak" not in st.session_state: st.session_state.lern_streak = 1
if "last_lern_log" not in st.session_state: st.session_state.last_lern_log = datetime.date.today()
if "gelöste_aufgaben" not in st.session_state: st.session_state.gelöste_aufgaben = 2

# KI-Gedächtnis & Chats
if "ki_fitness_gedaechtnis" not in st.session_state: st.session_state.ki_fitness_gedaechtnis = []
if "ki_lern_gedaechtnis" not in st.session_state: st.session_state.ki_lern_gedaechtnis = []
if "chat_history_fitness" not in st.session_state: st.session_state.chat_history_fitness = []
if "chat_history_lernen" not in st.session_state: st.session_state.chat_history_lernen = []

# --- STREAK-VERLUST-LOGIK ---
heute = datetime.date.today()
if (heute - st.session_state.last_fit_log).days >= 2:
    st.session_state.fit_streak = 0
    st.sidebar.error("⚠️ Inaktivität im Sport! Dein Fitness-Streak wurde auf 0 gesetzt.")
if (heute - st.session_state.last_lern_log).days >= 2:
    st.session_state.lern_streak = 0
    st.sidebar.error("⚠️ Inaktivität in der Schule! Dein Lern-Streak wurde auf 0 gesetzt.")

# --- SIDEBAR: KONTROLLZENTRUM ---
with st.sidebar:
    st.title("📲 iPad Control Center")
    modus = st.selectbox("App auswählen:", ["🏋️‍♂️ ATHLETE PRO", "🎓 CAMPUS EXPERT", "🏆 MEILENSTEINE & POKALE", "🌆 KI-ABEND-REPORT"])
    
    st.divider()
    st.markdown("### ⚙️ Profil-Einstellungen")
    if modus in ["🏋️‍♂️ ATHLETE PRO", "🏆 MEILENSTEINE & POKALE", "🌆 KI-ABEND-REPORT"]:
        st.session_state.alter = st.number_input("Alter", value=st.session_state.alter)
        st.session_state.gewicht = st.number_input("Gewicht (kg)", value=st.session_state.gewicht)
        st.session_state.groesse = st.number_input("Größe (cm)", value=st.session_state.groesse)
    else:
        st.session_state.klassenstufe = st.selectbox("Klassenstufe:", [f"{i}. Klasse" for i in range(5, 13)], index=5)
        
    st.divider()
    st.markdown("### 🎨 100+ Farbstudio (RGB Mixer)")
    farb_modus = st.radio("Farbwahl:", ["🎛️ RGB Mixer", "📌 Presets"])
    
    r, g, b_val = 30, 30, 30
    if farb_modus == "🎛️ RGB Mixer":
        r = st.slider("🔴 Rot", 0, 255, 30)
        g = st.slider("🟢 Grün", 0, 255, 30)
        b_val = st.slider("🔵 Blau", 0, 255, 30)
        st.session_state.custom_color = f"rgb({r}, {g}, {b_val})"
    else:
        presets = {
            "⚪ Grau": "#1e1e1e", "⚫ Black": "#000000", "🧪 Neon Grün": "#39ff14", 
            "🔮 Neon Violett": "#9d00ff", "🛍️ Neon Pink": "#ff1493", "☀️ Helles Weiss": "#f5f5f5", "💛 Helles Gelb": "#fff9a6"
        }
        wahl = st.selectbox("Preset:", list(presets.keys()))
        st.session_state.custom_color = presets[wahl]
        # Einfache Annäherung für RGB-Werte aus Presets für die Helligkeitsberechnung
        if wahl in ["☀️ Helles Weiss", "💛 Helles Gelb"]: r, g, b_val = 240, 240, 240

# --- AUTOMATISCHE SCHRIFTFARBEN-LOGIK (Luminanz-Berechnung) ---
# Formel für Helligkeit: (R * 299 + G * 587 + B * 114) / 1000
helligkeit = (r * 299 + g * 587 + b_val * 114) / 1000
schrift_farbe = "#000000" if helligkeit > 125 else "#FFFFFF"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {st.session_state.custom_color} !important; color: {schrift_farbe} !important; }} 
    h1, h2, h3, h4, p, span, label {{ color: {schrift_farbe} !important; }}
    .stMetric div {{ color: {schrift_farbe} !important; }}
    </style>
""", unsafe_allow_html=True)

# --- CALLBACKS FÜR SICH LEERENDE EINGABEFELDER ---
def food_eingabe_callback():
    text = st.session_state.food_eingabe_key
    if text:
        st.session_state.ki_fitness_gedaechtnis.append(f"Ernährung ({heute.strftime('%H:%M')}): {text}")
        wasser_match = re.search(r'(\d+)\s*(ml|milliliter|wasser)', text.lower())
        protein_match = re.search(r'(\d+)\s*(g|gramm)\s*(protein|eiweiß)', text.lower())
        if wasser_match: st.session_state.live_wasser += int(wasser_match.group(1))
        if protein_match: st.session_state.live_protein += int(protein_match.group(1))
        st.session_state.food_eingabe_key = ""

def lern_eingabe_callback():
    text = st.session_state.lern_eingabe_key
    if text:
        st.session_state.ki_lern_gedaechtnis.append(f"Gelernt ({heute.strftime('%H:%M')}): {text}")
        st.toast(f"📚 KI gemerkt: '{text}'")
        st.session_state.lern_eingabe_key = ""

# --- BEREICH 1: FITNESS (ATHLETE PRO) ---
if modus == "🏋️‍♂️ ATHLETE PRO":
    st.title("🏋️‍♂️ ATHLETE PRO Dashboard")
    
    # Grid für die Live Zähler
    c_w1, c_w2, c_w3, c_w4 = st.columns(4)
    with c_w1: st.metric("🔥 Sport-Streak", f"{st.session_state.fit_streak} Tage")
    with c_w2: st.metric("💧 Wasser (Ziel: 3000ml)", f"{st.session_state.live_wasser} ml")
    with c_w3: st.metric("🥩 Protein (Ziel: 140g)", f"{st.session_state.live_protein} g")
    with c_w4: st.metric("🏃‍♂️ Schritte / Aktivität", f"{st.session_state.live_schritte} Schritte\n({st.session_state.live_verbrannte_kalorien} kcal)")
    
    # NEU: Schrittzähler und Sport-Eingabe
    st.divider()
    st.markdown("### 🏃‍♂️ Bewegung, Schritte & Sport-Tracker")
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        schritte_input = st.number_input("Schritte hinzufügen:", min_value=0, step=500)
        if st.button("➕ Schritte buchen") and schritte_input > 0:
            st.session_state.live_schritte += schritte_input
            berechnete_kcal = int(schritte_input * 0.04) # Ungefährer Wert
            st.session_state.live_verbrannte_kalorien += berechnete_kcal
            st.session_state.ki_fitness_gedaechtnis.append(f"Schritte: {schritte_input} gemacht (+{berechnete_kcal} kcal).")
            st.rerun()
            
    with col_s2:
        sportart = st.text_input("Sportart (z.B. Boxen, Joggen, Krafttraining):")
        dauer = st.number_input("Dauer (in Minuten):", min_value=0, step=5)
    with col_s3:
        st.write("")
        st.write("")
        if st.button("🚀 Workout berechnen & tracken") and sportart and dauer > 0:
            client = OpenAI(api_key=FESTER_API_KEY)
            with st.spinner("KI berechnet deinen Kalorienverbrauch..."):