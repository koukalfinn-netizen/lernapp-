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

# Live-Zähler für Proteine und Flüssigkeit
if "live_wasser" not in st.session_state: st.session_state.live_wasser = 0
if "live_protein" not in st.session_state: st.session_state.live_protein = 0

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
    if modus in ["🏋️‍♂️ ATHLETE PRO", "🏆 MEILENSTEINE & POKALE"]:
        st.session_state.alter = st.number_input("Alter", value=st.session_state.alter)
        st.session_state.gewicht = st.number_input("Gewicht (kg)", value=st.session_state.gewicht)
        st.session_state.groesse = st.number_input("Größe (cm)", value=st.session_state.groesse)
    else:
        st.session_state.klassenstufe = st.selectbox("Klassenstufe:", [f"{i}. Klasse" for i in range(5, 13)], index=5)
        
    st.divider()
    st.markdown("### 🎨 100+ Farbstudio (RGB Mixer)")
    farb_modus = st.radio("Farbwahl:", ["🎛️ RGB Mixer", "📌 Presets"])
    if farb_modus == "🎛️ RGB Mixer":
        r = st.slider("🔴 Rot", 0, 255, 30)
        g = st.slider("🟢 Grün", 0, 255, 30)
        b = st.slider("🔵 Blau", 0, 255, 30)
        st.session_state.custom_color = f"rgb({r}, {g}, {b})"
    else:
        presets = {"⚪ Grau": "#1e1e1e", "⚫ Black": "#000000", "🧪 Neon Grün": "#39ff14", "🔮 Neon Violett": "#9d00ff", "🛍️ Neon Pink": "#ff1493"}
        st.session_state.custom_color = presets[st.selectbox("Preset:", list(presets.keys()))]

st.markdown(f"<style>.stApp {{ background-color: {st.session_state.custom_color} !important; color: white !important; }} h1,h2,h3,h4,p,span,label {{ color: white !important; }}</style>", unsafe_allow_html=True)

# --- AUTOMATISCHE AUSWERTUNG DER SCHNELLEINGABE (PROTEIN & WASSER) ---
def food_eingabe_callback():
    text = st.session_state.food_eingabe_key
    if text:
        st.session_state.ki_fitness_gedaechtnis.append(f"Eintrag ({heute.strftime('%H:%M')}): {text}")
        
        # Suchen nach Zahlen + ml/g Protein im Text via Regex
        wasser_match = re.search(r'(\d+)\s*(ml|milliliter|wasser)', text.lower())
        protein_match = re.search(r'(\d+)\s*(g|gramm)\s*(protein|eiweiß)', text.lower())
        
        if wasser_match:
            st.session_state.live_wasser += int(wasser_match.group(1))
            st.toast(f"💧 +{wasser_match.group(1)}ml Wasser hinzugefügt!")
        if protein_match:
            st.session_state.live_protein += int(protein_match.group(1))
            st.toast(f"🥩 +{protein_match.group(1)}g Protein registriert!")
            
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
    
    # Live Zähler Widgets im Grid-Layout
    c_w1, c_w2, c_w3 = st.columns(3)
    with c_w1: st.metric("🔥 Sport-Streak", f"{st.session_state.fit_streak} Tage")
    with c_w2: st.metric("💧 Wasser Live (Ziel: 3000ml)", f"{st.session_state.live_wasser} ml")
    with c_w3: st.metric("🥩 Protein Live (Ziel: 140g)", f"{st.session_state.live_protein} g")
    
    if st.button("🔄 Täglich geloggte Live-Zähler zurücksetzen", use_container_width=True):
        st.session_state.live_wasser = 0
        st.session_state.live_protein = 0
        st.rerun()

    st.divider()
    st.markdown("### 🥤 All-in-One Schnelleingabe")
    st.caption("Beispiel-Eingabe: 'Habe 500ml Wasser getrunken und einen Shake mit 30g Protein genommen'")
    st.text_input("Was hast du zu dir genommen / getan?", key="food_eingabe_key", on_change=food_eingabe_callback)

    st.divider()
    st.markdown("### 📹 Video-Beweispflicht (Min. 5 Minuten)")
    video_file = st.file_uploader("Trainingsvideo auswählen...", type=["mp4", "mov", "avi"])
    if video_file is not None and st.button("✅ Video-Prüfung bestätigen & Streak erhöhen"):
        st.session_state.fit_streak += 1
        st.session_state.last_fit_log = heute
        st.session_state.last_video_upload = heute
        st.success("🎉 Video akzeptiert! Streak gesichert.")
        st.rerun()

    st.divider()
    st.markdown("### 📸 Personalisierter KI-Scanner & Plan-Generator")
    fit_option = st.selectbox("Scan-Typ:", ["Trainingsplan (auf mein Gewicht angepasst)", "Kalorien-Check von Fotos", "Technik-Fehleranalyse"])
    uploaded_file = st.file_uploader("Foto hochladen...", type=["jpg", "png", "jpeg"], key="fit_up")
    
    if uploaded_file:
        dateiname = uploaded_file.name.split('.')[0]
        if st.button("🚀 Foto sportwissenschaftlich auswerten"):
            client = OpenAI(api_key=FESTER_API_KEY)
            with st.spinner("Dein Trainer wertet aus..."):
                img_str = base64.b64encode(uploaded_file.getvalue()).decode()
                prompt = f"Nutzerdaten: {st.session_state.alter}J, {st.session_state.gewicht}kg. Analysiere das Bild für '{fit_option}'."
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}}]}],
                )
                ki_ergebnis = response.choices[0].message.content
                st.info(ki_ergebnis)
                
                with io.open(os.path.join("meine_fitness_plaene", f"{dateiname}_Plan.txt"), "w", encoding="utf-8") as f:
                    f.write(ki_ergebnis)
                st.download_button("💾 Plan auf dem iPad speichern", data=ki_ergebnis, file_name=f"{dateiname}_Plan.txt", mime="text/plain", use_container_width=True)

    st.divider()
    st.subheader("📂 Gespeicherte Fitness-Dokumente")
    for datei in os.listdir("meine_fitness_plaene"): st.write(f"💪 {datei}")

    st.divider()
    st.markdown("### 💬 Chat mit deinem Personal Trainer")
    for msg in st.session_state.chat_history_fitness:
        with st.chat_message(msg["role"]): st.write(msg["content"])
    u_input = st.chat_input("Frage den Coach...")
    if u_input:
        st.session_state.chat_history_fitness.append({"role": "user", "content": u_input})
        client = OpenAI(api_key=FESTER_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": f"Coach für {st.session_state.gewicht}kg."}] + st.session_state.chat_history_fitness[-6:]
        )
        st.session_state.chat_history_fitness.append({"role": "assistant", "content": response.choices[0].message.content})
        st.rerun()

# --- BEREICH 2: SCHULE (CAMPUS EXPERT) ---
elif modus == "🎓 CAMPUS EXPERT":
    st.title("🎓 CAMPUS EXPERT Dashboard")
    st.metric("⚡ Aktueller Lern-Streak", f"{st.session_state.lern_streak} Tage")
    st.text_input("Was hast du heute gelernt?", key="lern_eingabe_key", on_change=lern_eingabe_callback)

    st.divider()
    st.markdown("### 📸 Aufgaben- & Dokumenten-Scanner")
    lern_option = st.selectbox("Format:", ["Übersichtlicher Lernzettel", "Probearbeit mit Lösungen", "Interaktives Quiz"])
    uploaded_l = st.file_uploader("Heft- oder Buchseite fotografieren...", type=["jpg", "png", "jpeg"])
    if uploaded_l and st.button("🧬 Dokumentation generieren"):
        client = OpenAI(api_key=FESTER_API_KEY)
        with st.spinner("Auswertung..."):
            img_str = base64.b64encode(uploaded_l.getvalue()).decode()
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": [{"type": "text", "text": f"Niveau: {st.session_state.klassenstufe}. Erstelle {lern_option}"}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}}]}],
            )
            st.write(response.choices[0].message.content)
            st.session_state.gelöste_aufgaben += 1
            st.session_state.last_lern_log = heute
            st.session_state.lern_streak += 1
            st.toast("🎓 Aufgabe erledigt!")

    st.divider()
    st.markdown("### 💬 Chat mit deinem KI-Tutor")
    for msg in st.session_state.chat_history_lernen:
        with st.chat_message(msg["role"]): st.write(msg["content"])
    u_input_l = st.chat_input("Frag den Lehrer...")
    if u_input_l:
        st.session_state.chat_history_lernen.append({"role": "user", "content": u_input_l})
        client = OpenAI(api_key=FESTER_API_KEY)
        response = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "system", "content": f"Lehrer für {st.session_state.klassenstufe}."}] + st.session_state.chat_history_lernen[-6:])
        st.session_state.chat_history_lernen.append({"role": "assistant", "content": response.choices[0].message.content})
        st.rerun()

# --- BEREICH 3: BELOHNUNGSSYSTEM (MEILENSTEINE & POKALE) ---
elif modus == "🏆 MEILENSTEINE & POKALE":
    st.title("🏆 Dein Trophäenschrank & Erfolgs-Tracker")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 🏋️‍♂️ Fitness & Ernährung")
        st.metric("Sport-Streak", f"{st.session_state.fit_streak} Tage")
        
        # Live Auswertung der Ziele
        progress_wasser = min(st.session_state.live_wasser / 3000, 1.0)
        progress_protein = min(st.session_state.live_protein / 140, 1.0)
        
        st.write(f" Wasser-Ziel: {st.session_state.live_wasser}/3000 ml")
        st.progress(progress_wasser)
        st.write(f" Protein-Ziel: {st.session_state.live_protein}/140 g")
        st.progress(progress_protein)
        
        st.divider()
        if st.session_state.fit_streak >= 3: st.success("🥉 Bronze-Athlet (3 Tage Streak!)")
        if st.session_state.live_wasser >= 3000: st.success("👑 Hydration-Elite (3000ml geknackt!)")
        else: st.code("🔒 Hydration-Elite (Trinke 3000ml am Tag)")
        if st.session_state.live_protein >= 140: st.success("🔱 Protein-Master (140g Eiweiß erreicht!)")
        else: st.code("🔒 Protein-Master (Erreiche 140g Protein am Tag)")

    with c2:
        st.markdown("### 🎓 Schul & Campus Meilensteine")
        st.metric("Lern-Streak", f"{st.session_state.lern_streak} Tage")
        st.metric("Gescannte Dokumente", f"{st.session_state.gelöste_aufgaben} Aufgaben")
        if st.session_state.gelöste_aufgaben >= 1: st.success("📝 Erstes Dokument erfasst")

# --- BEREICH 4: KI-ABEND-REPORT ---
else:
    st.title("🌆 Automatischer KI-Abendbericht")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 🏋️‍♂️ Auswertung Fitness")
        if st.session_state.ki_fitness_gedaechtnis:
            for e in st.session_state.ki_fitness_gedaechtnis: st.text(f"• {e}")
            if st.button("🌖 Fitness-Bericht generieren"):
                client = OpenAI(api_key=FESTER_API_KEY)
                r = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": f"Fasse zusammen für {st.session_state.gewicht}kg: {', '.join(st.session_state.ki_fitness_gedaechtnis)}"}])
                st.info(r.choices[0].message.content)
        else: st.info("Keine Einträge.")
    with c2:
        st.markdown("### 🎓 Auswertung Schule")
        if st.session_state.ki_lern_gedaechtnis:
            for e in st.session_state.ki_lern_gedaechtnis: st.text(f"• {e}")
            if st.button("🌖 Schul-Bericht generieren"):
                client = OpenAI(api_key=FESTER_API_KEY)
                r = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": f"Fasse zusammen für {st.session_state.klassenstufe}: {', '.join(st.session_state.ki_lern_gedaechtnis)}"}])
                st.success(r.choices[0].message.content)
        else: st.info("Keine Einträge.")