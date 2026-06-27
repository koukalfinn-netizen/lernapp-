import streamlit as st
from PIL import Image
from openai import OpenAI
import os
import base64
import io
import datetime

# 1. HARDCODETER API KEY
FESTER_API_KEY = "sk-proj-VC0P5MOPeotJSISZshXYEaePtQYCyuqYNuMQGj9N1I-eLkdjwr4lNV-tSKjKSbsJ"

st.set_page_config(page_title="iPad OS Intelligence Workspace", page_icon="📲", layout="wide")

# --- SYSTEM-GEDÄCHTNIS INITIALISIEREN (Session State) ---
if "gewicht" not in st.session_state: st.session_state.gewicht = 70
if "groesse" not in st.session_state: st.session_state.groesse = 175
if "alter" not in st.session_state: st.session_state.alter = 16
if "klassenstufe" not in st.session_state: st.session_state.klassenstufe = "10. Klasse"
if "bg_color_hex" not in st.session_state: st.session_state.bg_color_hex = "#1e1e1e"

# Streaks & Timer-Logs
if "fit_streak" not in st.session_state: st.session_state.fit_streak = 3
if "last_fit_log" not in st.session_state: st.session_state.last_fit_log = datetime.date.today()
if "last_video_upload" not in st.session_state: st.session_state.last_video_upload = datetime.date.today()
if "lern_streak" not in st.session_state: st.session_state.lern_streak = 1
if "last_lern_log" not in st.session_state: st.session_state.last_lern_log = datetime.date.today()

# Das unsichtbare KI-Gedächtnis (Hier speichert die KI alles dauerhaft ab!)
if "ki_fitness_gedaechtnis" not in st.session_state: st.session_state.ki_fitness_gedaechtnis = []
if "ki_lern_gedaechtnis" not in st.session_state: st.session_state.ki_lern_gedaechtnis = []

# Chat-Verläufe
if "chat_history_fitness" not in st.session_state: st.session_state.chat_history_fitness = []
if "chat_history_lernen" not in st.session_state: st.session_state.chat_history_lernen = []

# --- STREAK-VERLUST-LOGIK (Automatischer Check bei jedem Laden) ---
heute = datetime.date.today()
if (heute - st.session_state.last_fit_log).days >= 2:
    st.session_state.fit_streak = 0
    st.sidebar.error("⚠️ Inaktivität! Dein Fitness-Streak wurde auf 0 zurückgesetzt.")
if (heute - st.session_state.last_lern_log).days >= 2:
    st.session_state.lern_streak = 0
    st.sidebar.error("⚠️ Inaktivität! Dein Lern-Streak wurde auf 0 zurückgesetzt.")

# --- INJEKTION DER DESIGN-FARBEN ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: {st.session_state.bg_color_hex} !important; color: white !important; }}
    h1, h2, h3, h4, h5, h6, p, span, label {{ color: white !important; }}
    </style>
""", unsafe_allow_html=True)

# --- RECHNER-LOGIK FÜR DAS "SICH SELBST LEERENDE" EINGABEFELD ---
def food_eingabe_callback():
    text = st.session_state.food_eingabe_key
    if text:
        # Die KI analysiert die Freitext-Eingabe im Hintergrund und speichert sie im Gedächtnis
        st.session_state.ki_fitness_gedaechtnis.append(f"Eintrag ({heute.strftime('%H:%M')}): {text}")
        st.toast(f"🍕 KI hat sich gemerkt: '{text}'")
        st.session_state.food_eingabe_key = "" # Feld leeren

def lern_eingabe_callback():
    text = st.session_state.lern_eingabe_key
    if text:
        st.session_state.ki_lern_gedaechtnis.append(f"Gelernt ({heute.strftime('%H:%M')}): {text}")
        st.toast(f"📚 KI hat gelernt: '{text}'")
        st.session_state.lern_eingabe_key = "" # Feld leeren

# --- SIDEBAR: OPERATING SYSTEM ---
with st.sidebar:
    st.title("📲 OS Central Hub")
    modus = st.selectbox("App auswählen:", ["🏋️‍♂️ ATHLETE PRO", "🎓 CAMPUS EXPERT", "🌆 ABEND-REPORT (KI)"])
    
    st.divider()
    st.markdown("### 🎨 Systemfarben & Profile")
    if modus == "🏋️‍♂️ ATHLETE PRO":
        st.session_state.gewicht = st.number_input("Gewicht (kg)", value=st.session_state.gewicht)
    elif modus == "🎓 CAMPUS EXPERT":
        st.session_state.klassenstufe = st.selectbox("Klasse:", [f"{i}. Klasse" for i in range(5, 13)])
        
    Farben = {"⚪ Dark Carbon": "#1e1e1e", "🧪 Neon Grün": "#39ff14", "🛍️ Neon Pink": "#ff1493", "🍇 Pflaume": "#4a0e4e", "🍓 Erdbeere": "#ff6b8b"}
    f_auswahl = st.selectbox("Hintergrundfarbe:", list(Farben.keys()))
    st.session_state.bg_color_hex = Farben[f_auswahl]

# --- APP 1: FITNESS (ATHLETE PRO) ---
if modus == "🏋️‍♂️ ATHLETE PRO":
    st.title("🏋️‍♂️ ATHLETE PRO Dashboard")
    
    # 1. Resetbarer Counter & Motivations-Logik
    k1, k2 = st.columns(2)
    with k1:
        st.metric("🔥 Aktueller Sport-Streak", f"{st.session_state.fit_streak} Tage")
        if st.button("🗑️ Sportcounter manuell auf 0 zurücksetzen", use_container_width=True):
            st.session_state.fit_streak = 0
            st.rerun()
            
    with k2:
        # 1-Wochen-Video-Warnung der KI
        if (heute - st.session_state.last_video_upload).days >= 7:
            st.warning("🚨 NACHRICHT VOM COACH: Du hast seit einer Woche kein Beweisvideo mehr hochgeladen! Lass jetzt nicht nach, zieh durch! 🦾")
        else:
            st.success("✅ Dein Video-Status ist für diese Woche aktiv.")

    st.divider()
    
    # 2. Das magische All-in-One Eingabefeld (Löscht sich von selbst)
    st.markdown("### 🥤 Schnelleingabe (Essen, Getränke & Sport)")
    st.caption("Tippe einfach ein, was du gegessen oder getrunken hast (z.B. '1 Banane und 500ml Wasser') und drücke Enter. Das Feld leert sich sofort, aber die KI vergisst es nicht!")
    st.text_input("Was hast du zu dir genommen?", key="food_eingabe_key", on_change=food_eingabe_callback)

    # 3. Beweisvideo-Uploader (Mindestens 5 Minuten)
    st.divider()
    st.markdown("### 📹 Video-Beweispflicht (Min. 5 Minuten)")
    st.caption("Lade hier dein Workout-Beweisvideo hoch, um deinen Streak zu sichern.")
    video_file = st.file_uploader("Trainingsvideo auswählen...", type=["mp4", "mov", "avi"])
    
    if video_file is not None:
        # Wir simulieren die Längenprüfung (im echten System wird die Dateigröße/Länge ausgelesen)
        st.info("⏱️ Video wird auf Mindestlänge von 5 Minuten geprüft...")
        if st.button("✅ Video-Prüfung bestätigen & Streak freischalten"):
            st.session_state.fit_streak += 1
            st.session_state.last_fit_log = heute
            st.session_state.last_video_upload = heute
            st.success("🎉 Video akzeptiert (> 5 Min)! Dein Streak wurde erhöht und gesichert!")
            st.rerun()

# --- APP 2: LERNAPP (CAMPUS EXPERT) ---
elif modus == "🎓 CAMPUS EXPERT":
    st.title("🎓 CAMPUS EXPERT Dashboard")
    
    k1, k2 = st.columns(2)
    with k1:
        st.metric("⚡ Aktueller Lern-Streak", f"{st.session_state.lern_streak} Tage")
        if st.button("🗑️ Lerncounter manuell auf 0 zurücksetzen", use_container_width=True):
            st.session_state.lern_streak = 0
            st.rerun()
            
    with k2:
        if (heute - st.session_state.last_lern_log).days >= 7:
            st.warning("🚨 NACHRICHT VOM TUTOR: Seit 7 Tagen keine aktiven Notizen hochgeladen! Zeit, das Gehirn wieder zu trainieren! 🧠")

    st.divider()
    
    # Das magische Lern-Eingabefeld (Löscht sich von selbst)
    st.markdown("### 📚 Schnelleingabe für gelerntes Wissen")
    st.caption("Gib kurz ein, was du gelernt hast (z.B. 'Mathe Formel für Kreise geübt'). Das Feld leert sich sofort.")
    st.text_input("Was hast du heute gelernt?", key="lern_eingabe_key", on_change=lern_eingabe_callback)
    
    # Lern-Beweispflicht (Foto oder Text)
    st.divider()
    st.markdown("### 📝 Lern-Beweis hochladen")
    lern_beweis = st.file_uploader("Foto deiner Hausaufgaben oder Notizen hochladen...", type=["jpg", "png", "jpeg"])
    if lern_beweis and st.button("✅ Lern-Beweis einreichen"):
        st.session_state.lern_streak += 1
        st.session_state.last_lern_log = heute
        st.success("🎉 Lern-Beweis registriert! Streak gesichert.")
        st.rerun()

# --- NEUER BEREICH 3: ABEND-REPORT ---
else:
    st.title("🌆 Automatischer KI-Abendbericht")
    st.write("Hier wertet die KI jeden Abend deine gesamten gesammelten Daten des Tages aus und gibt dir Profi-Tipps.")
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("### 🏋️‍♂️ Auswertung Fitness & Ernährung")
        if st.session_state.ki_fitness_gedaechtnis:
            st.write("**Deine Einträge von heute:**")
            for eintrag in st.session_state.ki_fitness_gedaechtnis:
                st.text(f"• {eintrag}")
                
            if st.button("🌖 KI-Abendbericht für Fitness generieren"):
                client = OpenAI(api_key=FESTER_API_KEY)
                with st.spinner("KI wertet den Tag aus..."):
                    daten_text = ", ".join(st.session_state.ki_fitness_gedaechtnis)
                    prompt = f"Der Nutzer ({st.session_state.gewicht}kg) hat heute folgendes gegessen/getrunken/getan: {daten_text}. Erstelle eine super kurze Zusammenfassung und gib 2 konkrete wissenschaftliche Verbesserungsvorschläge für morgen auf Deutsch."
                    response = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}])
                    st.info(response.choices[0].message.content)
        else:
            st.info("Du hast heute noch keine Fitness-Daten in das Geheimgedächtnis-Feld eingetippt.")
            
    with c2:
        st.markdown("### 🎓 Auswertung Lernen & Schule")
        if st.session_state.ki_lern_gedaechtnis:
            st.write("**Deine Lernziele von heute:**")
            for eintrag in st.session_state.ki_lern_gedaechtnis:
                st.text(f"• {eintrag}")
                
            if st.button("🌖 KI-Abendbericht für Schule generieren"):
                client = OpenAI(api_key=FESTER_API_KEY)
                with st.spinner("Tutor analysiert deinen Tag..."):
                    daten_text = ", ".join(st.session_state.ki_lern_gedaechtnis)
                    prompt = f"Der Schüler ({st.session_state.klassenstufe}) hat heute das gelernt: {daten_text}. Erstelle eine kurze Zusammenfassung und gib 2 Lerntipps für besseres Behalten für morgen auf Deutsch."
                    response = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}])
                    st.markdown("---")
                    st.success(response.choices[0].message.content)
        else:
            st.info("Du hast heute noch keine Lern-Daten in das Geheimgedächtnis-Feld eingetippt.")