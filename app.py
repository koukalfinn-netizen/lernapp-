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
            client = OpenAIimport streamlit as st
from PIL import Image
from openai import OpenAI
import os
import base64
import io
import datetime
import re

# 1. NEUER AKTIVER API KEY (Frisch generiert)
FESTER_API_KEY = "sk-proj-7_X_M8vRlS-mG8p_w9nKTrb6B3YmW-Q9pL4xPqY5zA1bC2d3e4f5g6h7i8j9k"

st.set_page_config(page_title="iPad Premium OS Workspace", page_icon="📲", layout="wide")

# Lokale Dateiordner absichern
if not os.path.exists("meine_pdfs"):
    os.makedirs("meine_pdfs")
if not os.path.exists("meine_fitness_plaene"):
    os.makedirs("meine_fitness_plaene")

# --- PERMANENTES SYSTEM-GEDÄCHTNIS (Session State) ---
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

# Tracker-Werte für Ernährung und Bewegung
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

# --- AUTOMATISCHE STREAK-VERLUST-LOGIK ---
heute = datetime.date.today()
if (heute - st.session_state.last_fit_log).days >= 2:
    st.session_state.fit_streak = 0
    st.sidebar.error("⚠️ Inaktivität im Sport! Dein Fitness-Streak wurde auf 0 gesetzt.")
if (heute - st.session_state.last_lern_log).days >= 2:
    st.session_state.lern_streak = 0
    st.sidebar.error("⚠️ Inaktivität in der Schule! Dein Lern-Streak wurde auf 0 gesetzt.")

# --- SIDEBAR: KONTROLLZENTRUM & RGB MIXER ---
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
        if wahl == "☀️ Helles Weiss" or wahl == "💛 Helles Gelb":
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

# ==========================================
# --- BEREICH 1: FITNESS (ATHLETE PRO) ---
# ==========================================
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
            client = OpenAI(api_key=FESTER_API_KEY)
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
    st.markdown("### 📹 Video-Beweispflicht (Min. 5 Minuten)")
    video_file = st.file_uploader("Trainingsvideo hochladen...", type=["mp4", "mov", "avi"])
    if video_file is not None:
        if st.button("✅ Video-Dauer bestätigen & Streak sichern"):
            st.session_state.fit_streak += 1
            st.session_state.last_fit_log = heute
            st.session_state.last_video_upload = heute
            st.success("Streak erfolgreich um einen Tag verlängert!")
            st.rerun()

    st.divider()
    st.markdown("### 📸 Personalisierter KI-Scanner & Plan-Export")
    fit_option = st.selectbox("Scan-Typ:", ["Trainingsplan (auf mein Gewicht angepasst)", "Kalorien-Check von Fotos", "Technik-Fehleranalyse"])
    uploaded_file = st.file_uploader("Foto hochladen...", type=["jpg", "png", "jpeg"], key="fit_up")
    
    if uploaded_file:
        dateiname = uploaded_file.name.split('.')[0]
        if st.button("🚀 Foto sportwissenschaftlich auswerten"):
            client = OpenAI(api_key=FESTER_API_KEY)
            with st.spinner("Auswertung läuft..."):
                img_str = base64.b64encode(uploaded_file.getvalue()).decode()
                prompt = f"Nutzer: {st.session_state.alter}J, {st.session_state.gewicht}kg. Analysiere das Bild für '{fit_option}'."
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}}]}],
                )
                ki_ergebnis = response.choices[0].message.content
                st.info(ki_ergebnis)
                
                plan_path = os.path.join("meine_fitness_plaene", f"{dateiname}_Plan.txt")
                with io.open(plan_path, "w", encoding="utf-8") as f: 
                    f.write(ki_ergebnis)
                st.download_button("💾 Plan lokal auf iPad sichern", data=ki_ergebnis, file_name=f"{dateiname}_Plan.txt", mime="text/plain", use_container_width=True)

    st.divider()
    st.subheader("📂 Auf dem iPad hinterlegte Dokumente")
    for datei in os.listdir("meine_fitness_plaene"): 
        st.write(f"💪 {datei}")

    st.divider()
    st.markdown("### 💬 Chat mit deinem Personal Trainer")
    for msg in st.session_state.chat_history_fitness:
        with st.chat_message(msg["role"]): 
            st.write(msg["content"])
    u_input = st.chat_input("Frage den Coach...")
    if u_input:
        st.session_state.chat_history_fitness.append({"role": "user", "content": u_input})
        client = OpenAI(api_key=FESTER_API_KEY)
        response = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "system", "content": f"Du bist ein Fitnesscoach. Gewicht: {st.session_state.gewicht}kg."}] + st.session_state.chat_history_fitness[-6:])
        st.session_state.chat_history_fitness.append({"role": "assistant", "content": response.choices[0].message.content})
        st.rerun()

# ==========================================
# --- BEREICH 2: SCHULE (CAMPUS EXPERT) ---
# ==========================================
elif modus == "🎓 CAMPUS EXPERT":
    st.title("🎓 CAMPUS EXPERT Dashboard")
    st.metric("⚡ Aktueller Lern-Streak", f"{st.session_state.lern_streak} Tage")
    
    st.markdown("### 📚 Schnelleingabe für gelerntes Wissen")
    st.text_input("Was hast du heute gelernt? (Drücke Enter)", key="lern_eingabe_key", on_change=lern_eingabe_callback)

    st.divider()
    st.markdown("### 📸 Aufgaben- & Dokumenten-Scanner")
    lern_option = st.selectbox("Format:", ["Übersichtlicher Lernzettel", "Probearbeit mit Lösungen", "Interaktives Quiz"])
    uploaded_l = st.file_uploader("Buchseite oder Mitschrift fotografieren...", type=["jpg", "png", "jpeg"])
    
    if uploaded_l and st.button("🧬 Dokumentation generieren"):
        client = OpenAI(api_key=FESTER_API_KEY)
        with st.spinner("Inhalte werden strukturiert..."):
            img_str = base64.b64encode(uploaded_l.getvalue()).decode()
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": [{"type": "text", "text": f"Niveau: {st.session_state.klassenstufe}. Generiere ein {lern_option} basierend auf dem Dokument."}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}}]}],
            )
            st.write(response.choices[0].message.content)
            st.session_state.gelöste_aufgaben += 1
            st.session_state.last_lern_log = heute
            st.session_state.lern_streak += 1
            st.toast("Erfolg verzeichnet!")

    st.divider()
    st.markdown("### 💬 Chat mit deinem KI-Tutor")
    for msg in st.session_state.chat_history_lernen:
        with st.chat_message(msg["role"]): 
            st.write(msg["content"])
    u_input_l = st.chat_input("Frag den Lehrer...")
    if u_input_l:
        st.session_state.chat_history_lernen.append({"role": "user", "content": u_input_l})
        client = OpenAI(api_key=FESTER_API_KEY)
        response = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "system", "content": f"Du bist ein geduldiger Lehrer. Niveau: {st.session_state.klassenstufe}."}] + st.session_state.chat_history_lernen[-6:])
        st.session_state.chat_history_lernen.append({"role": "assistant", "content": response.choices[0].message.content})
        st.rerun()

# ==========================================
# --- BEREICH 3: BELOHNUNGSSYSTEM ---
# ==========================================
elif modus == "🏆 MEILENSTEINE & POKALE":
    st.title("🏆 Dein Trophäenschrank & Erfolgs-Tracker")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 🏋️‍♂️ Fitness & Ernährung")
        st.metric("Sport-Streak", f"{st.session_state.fit_streak} Tage")
        
        st.write(f"💧 Wasser-Ziel: {st.session_state.live_wasser}/3000 ml")
        st.progress(min(st.session_state.live_wasser / 3000, 1.0))
        
        st.write(f"🥩 Protein-Ziel: {st.session_state.live_protein}/140 g")
        st.progress(min(st.session_state.live_protein / 140, 1.0))
        
        st.write(f"🏃‍♂️ Schritt-Ziel: {st.session_state.live_schritte}/10000")
        st.progress(min(st.session_state.live_schritte / 10000, 1.0))
        
        st.divider()
        if st.session_state.fit_streak >= 3: 
            st.success("🥉 Bronze-Athlet (3 Tage Sport-Streak)")
        if st.session_state.live_wasser >= 3000: 
            st.success("👑 Hydration-Elite (3000ml Wasser am Tag)")
        else: 
            st.code("🔒 Hydration-Elite (Benötigt 3000ml Wasser)")
        if st.session_state.live_protein >= 140: 
            st.success("🔱 Protein-Master (140g Eiweiß gedeckt)")
        else: 
            st.code("🔒 Protein-Master (Benötigt 140g Protein)")
        if st.session_state.live_schritte >= 10000: 
            st.success("⚡ Cardio-Gott (10.000 Schritte absolviert)")
        else: 
            st.code("🔒 Cardio-Gott (Benötigt 10.000 Schritte)")

    with c2:
        st.markdown("### 🎓 Schul & Campus Meilensteine")
        st.metric("Lern-Streak", f"{st.session_state.lern_streak} Tage")
        st.metric("Gescannte Dokumente", f"{st.session_state.gelöste_aufgaben} Aufgaben")
        if st.session_state.gelöste_aufgaben >= 1: 
            st.success("📝 Erstes Dokument erfasst")

# ==========================================
# --- BEREICH 4: KI-ABEND-REPORT ---
# ==========================================
else:
    st.title("🌆 Automatischer KI-Abendbericht & Tagesfazit")
    st.write("Die KI wertet deine Einträge und Bewegungswerte knallhart und absolut ehrlich aus.")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 🏋️‍♂️ Auswertung Bewegung & Ernährung")
        if st.session_state.ki_fitness_gedaechtnis:
            for e in st.session_state.ki_fitness_gedaechtnis: 
                st.text(f"• {e}")
            if st.button("🌖 Unbeschönigten KI-Abendbericht generieren"):
                client = OpenAI(api_key=FESTER_API_KEY)
                with st.spinner("Wissenschaftliche Bilanz wird gezogen..."):
                    daten_text = ", ".join(st.session_state.ki_fitness_gedaechtnis)
                    prompt = f"""
                    Du bist ein extrem ehrlicher, kompromissloser wissenschaftlicher Fitness-Coach. 
                    Nutzerdaten: {st.session_state.alter} Jahre, {st.session_state.gewicht(api_key=FESTER_API_KEY)
            with st.spinner("KI berechnet dimport streamlit as st
from PIL import Image
from openai import OpenAI
import os
import base64
import io
import datetime
import re

# 1. FRISCHER, AKTIVER API KEY
FESTER_API_KEY = "sk-proj-VC0P5MOPeotJSISZshXYEaePtQYCyuqYNuMQGj9N1I-eLkdjwr4lNV-tSKjKSbsJ"

st.set_page_config(page_title="iPad Premium OS Workspace", page_icon="📲", layout="wide")

# Lokale Dateiordner absichern
if not os.path.exists("meine_pdfs"):
    os.makedirs("meine_pdfs")
if not os.path.exists("meine_fitness_plaene"):
    os.makedirs("meine_fitness_plaene")

# --- PERMANENTES SYSTEM-GEDÄCHTNIS (Session State) ---
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

# Tracker-Werte für Ernährung und Bewegung
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

# --- AUTOMATISCHE STREAK-VERLUST-LOGIK ---
heute = datetime.date.today()
if (heute - st.session_state.last_fit_log).days >= 2:
    st.session_state.fit_streak = 0
    st.sidebar.error("⚠️ Inaktivität im Sport! Dein Fitness-Streak wurde auf 0 gesetzt.")
if (heute - st.session_state.last_lern_log).days >= 2:
    st.session_state.lern_streak = 0
    st.sidebar.error("⚠️ Inaktivität in der Schule! Dein Lern-Streak wurde auf 0 gesetzt.")

# --- SIDEBAR: KONTROLLZENTRUM & RGB MIXER ---
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

# ==========================================
# --- BEREICH 1: FITNESS (ATHLETE PRO) ---
# ==========================================
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
            client = OpenAI(api_key=FESTER_API_KEY)
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
    st.text_input("Was hast du konsumiert? (z.einen Kalorienverbrauch..."):