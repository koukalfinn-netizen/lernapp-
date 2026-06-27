import streamlit as st
from PIL import Image
from openai import OpenAI
import os
import base64
import io
import datetime
import re

# 1. GENERIERTER API KEY
FESTER_API_KEY = "sk-proj-VC0P5MOPeotJSISZshXYEaePtQYCyuqYNuMQGj9N1I-eLkdjwr4lNV-tSKjKSbsJ"

# Initialisiere den OpenAI Client einmal global
client = OpenAI(api_key=FESTER_API_KEY)

st.set_page_config(page_title="iPad Premium OS Workspace", page_icon="📲", layout="wide")

# Lokale Dateiordner absichern
if not os.path.exists("meine_pdfs"):
    os.makedirs("meine_pdfs")
if not os.path.exists("meine_fitness_plaene"):
    os.makedirs("meine_fitness_plaene")

# =========================================================================
# --- PERMANENTES SYSTEM-GEDÄCHTNIS (Session State) ---
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

# Live Nährstoff- und Aktivitäts-Zähler
if "live_wasser" not in st.session_state:
    st.session_state.live_wasser = 0
if "live_protein" not in st.session_state:
    st.session_state.live_protein = 0
if "live_schritte" not in st.session_state:
    st.session_state.live_schritte = 0
if "live_verbrannte_kalorien" not in st.session_state:
    st.session_state.live_verbrannte_kalorien = 0

# Streaks & Historie
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

# Text-Gedächtnis für Abend-Auswertungen
if "ki_fitness_gedaechtnis" not in st.session_state:
    st.session_state.ki_fitness_gedaechtnis = []
if "ki_lern_gedaechtnis" not in st.session_state:
    st.session_state.ki_lern_gedaechtnis = []
if "chat_history_fitness" not in st.session_state:
    st.session_state.chat_history_fitness = []
if "chat_history_lernen" not in st.session_state:
    st.session_state.chat_history_lernen = []

# =========================================================================
# --- AUTOMATISCHE STREAK-VERLUST-LOGIK ---
# =========================================================================
heute = datetime.date.today()
if (heute - st.session_state.last_fit_log).days >= 2:
    st.session_state.fit_streak = 0
    st.sidebar.error("⚠️ Inaktivität im Sport! Dein Fitness-Streak wurde zurückgesetzt.")
if (heute - st.session_state.last_lern_log).days >= 2:
    st.session_state.lern_streak = 0
    st.sidebar.error("⚠️ Inaktivität in der Schule! Dein Lern-Streak wurde zurückgesetzt.")

# =========================================================================
# --- SIDEBAR: KONTROLLZENTRUM & RGB MIXER ---
# =========================================================================
with st.sidebar:
    st.title("📲 iPad Control Center")
    modus = st.selectbox("App auswählen:", ["🏋️‍♂️ ATHLETE PRO", "🎓 CAMPUS EXPERT", "🏆 MEILENSTEINE & POKALE", "🌆 KI-ABEND-REPORT"])
    
    st.divider()
    st.markdown("### ⚙️ Profil-Einstellungen")
    if modus in ["🏋️‍♂️ ATHLETE PRO", "🏆 MEILENSTEINE & POKALE", "🌆 KI-ABEND-REPORT"]:
        st.session_state.alter = st.number_input("Alter", value=st.session_state.alter, min_value=1, max_value=120)
        st.session_state.gewicht = st.number_input("Gewicht (kg)", value=st.session_state.gewicht, min_value=1, max_value=300)
        st.session_state.groesse = st.number_input("Größe (cm)", value=st.session_state.groesse, min_value=50, max_value=250)
    else:
        st.session_state.klassenstufe = st.selectbox("Klassenstufe:", [f"{i}. Klasse" for i in range(5, 13)], index=5)
        
    st.divider()
    st.markdown("### 🎨 100+ Farbstudio (RGB Mixer)")
    farb_modus = st.radio("Farbwahl:", ["🎛️ RGB Mixer", "📌 Presets"])
    
    r_val, g_val, b_val = 30, 30, 30
    if farb_modus == "🎛️ RGB Mixer":
        r_val = st.slider("🔴 Rot", 0, 255, 30)
        g_val = st.slider("🟢 Grün", 0, 255, 30)
        b_val = st.slider("🔵 Blau", 0, 255, 30)
        st.session_state.custom_color = f"rgb({r_val}, {g_val}, {b_val})"
    else:
        presets = {
            "⚪ Modernes Grau": "#1e1e1e", "⚫ Deep Black": "#000000", "🧪 Neon Grün": "#39ff14", 
            "🔮 Neon Violett": "#9d00ff", "🛍️ Neon Pink": "#ff1493", "☀️ Helles Weiss": "#f5f5f5", "💛 Helles Gelb": "#fff9a6"
        }
        wahl = st.selectbox("Preset:", list(presets.keys()))
        st.session_state.custom_color = presets[wahl]
        if wahl in ["☀️ Helles Weiss", "💛 Helles Gelb"]:
            r_val, g_val, b_val = 245, 245, 245

# --- KONTRAST-LOGIK (SCHRIFTFARBE PASST SICH AUTOMATISCH AN) ---
luminanz = (r_val * 299 + g_val * 587 + b_val * 114) / 1000
schrift_farbe = "#000000" if luminanz > 130 else "#FFFFFF"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {st.session_state.custom_color} !important; color: {schrift_farbe} !important; }} 
    h1, h2, h3, h4, h5, h6, p, span, label, div {{ color: {schrift_farbe} !important; }}
    .stMetric div {{ color: {schrift_farbe} !important; }}
    .stButton>button {{ background-color: rgba(255,255,255,0.15) !important; color: {schrift_farbe} !important; border: 1px solid {schrift_farbe} !important; }}
    </style>
""", unsafe_allow_html=True)

# --- CALLBACKS FÜR AUTOMATISCH LEERENDE EINGABEFELDER ---
def food_eingabe_callback():
    text = st.session_state.food_eingabe_key
    if text:
        st.session_state.ki_fitness_gedaechtnis.append(f"Ernährung/Aktivität ({heute.strftime('%H:%M')}): {text}")
        wasser_match = re.search(r'(\d+)\s*(ml|milliliter|wasser)', text.lower())
        protein_match = re.search(r'(\d+)\s*(g|gramm)\s*(protein|eiweiß)', text.lower())
        if wasser_match:
            st.session_state.live_wasser += int(wasser_match.group(1))
        if protein_match:
            st.session_state.live_protein += int(protein_match.group(1))
        st.session_state.food_eingabe_key = ""

def lern_eingabe_callback():
    text = st.session_state.lern_eingabe_key
    if text:
        st.session_state.ki_lern_gedaechtnis.append(f"Wissen ({heute.strftime('%H:%M')}): {text}")
        st.toast("📚 Gelerntes permanent gespeichert!")
        st.session_state.lern_eingabe_key = ""

# =========================================================================
# --- BEREICH 1: FITNESS (ATHLETE PRO) ---
# =========================================================================
if modus == "🏋️‍♂️ ATHLETE PRO":
    st.title("🏋️‍♂️ ATHLETE PRO Dashboard")
    
    # Live Nährstoff- und Aktivitäts-Zähler Grid
    c_w1, c_w2, c_w3, c_w4 = st.columns(4)
    with c_w1: 
        st.metric("🔥 Sport-Streak", f"{st.session_state.fit_streak} Tage")
    with c_w2: 
        st.metric("💧 Wasser-Live (Ziel: 3000ml)", f"{st.session_state.live_wasser} ml")
    with c_w3: 
        st.metric("🥩 Protein-Live (Ziel: 140g)", f"{st.session_state.live_protein} g")
    with c_w4: 
        st.metric("🏃‍♂️ Aktivitäts-Umsatz", f"{st.session_state.live_schritte} Schritte ({st.session_state.live_verbrannte_kalorien} kcal)")
    
    st.divider()
    st.markdown("### 🏃‍♂️ Bewegung, Schritte & Sport-Tracker")
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        schritte_input = st.number_input("Schritte hinzufügen:", min_value=0, step=1000)
        if st.button("➕ Schritte buchen") and schritte_input > 0:
            st.session_state.live_schritte += schritte_input
            kcal_schritte = int(schritte_input * 0.04)
            st.session_state.live_verbrannte_kalorien += kcal_schritte
            st.session_state.ki_fitness_gedaechtnis.append(f"Schritte: {schritte_input} gegangen (+{kcal_schritte} kcal).")
            st.rerun()
            
    with col_s2:
        sportart = st.text_input("Sportart (z.B. Boxen, Fußball, Joggen):")
        dauer = st.number_input("Dauer (in Minuten):", min_value=0, step=5)
    with col_s3:
        st.write("")
        st.write("")
        if st.button("🚀 Workout-Kalorien berechnen") and sportart and dauer > 0:
            with st.spinner("KI berechnet genauen Kalorienverbrauch..."):
                prompt = f"Berechne den genauen kcal-Verbrauch für {st.session_state.gewicht}kg, {st.session_state.alter} Jahre, bei {dauer} Minuten {sportart}. Antworte kurz auf Deutsch und setze die verbrannte Zahl ganz ans Ende hinter ein Leerzeichen."
                r = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}])
                ergebnis_text = r.choices[0].message.content
                st.info(ergebnis_text)
                
                zahlen = [int(s) for s in re.findall(r'\b\d+\b', ergebnis_text)]
                kcal_extrahiert = zahlen[-1] if zahlen else int(dauer * 8)
                st.session_state.live_verbrannte_kalorien += kcal_extrahiert
                st.session_state.ki_fitness_gedaechtnis.append(f"Sport: {sportart} für {dauer} Min (+{kcal_extrahiert} kcal).")

    if st.button("🔄 Alle heutigen Live-Tracker zurücksetzen", use_container_width=True):
        st.session_state.live_wasser = 0
        st.session_state.live_protein = 0
        st.session_state.live_schritte = 0
        st.session_state.live_verbrannte_kalorien = 0
        st.rerun()

    st.divider()
    st.markdown("### 🥤 All-in-One Schnelleingabe (Essen & Trinken)")
    st.text_input("Was hast du konsumiert? (z.B. '30g Protein Shake und 600ml Wasser')", key="food_eingabe_key", on_change=food_eingabe_callback)

    st.divider()
    st.markdown("### 📹 Video-Beweispflicht