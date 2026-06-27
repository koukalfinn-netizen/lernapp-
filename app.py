import streamlit as st
from PIL import Image
from openai import OpenAI
import os
import base64
import io

# 1. HARDCODETER API KEY (Dauerhaft aktiv für alle Funktionen)
FESTER_API_KEY = "sk-proj-VC0P5MOPeotJSISZshXYEaePtQYCyuqYNuMQGj9N1I-eLkdjwr4lNV-tSKjKSbsJ"

# Seiten-Konfiguration
st.set_page_config(page_title="iPad Premium Workspace", page_icon="⚡", layout="wide")

# Ordner-Struktur für Verläufe
for pfad in ["verlauf_fitness", "verlauf_lernen"]:
    if not os.path.exists(pfad):
        os.makedirs(pfad)

# Chat-Speicher initialisieren, falls er noch leer ist
if "chat_history_fitness" not in st.session_state:
    st.session_state.chat_history_fitness = []
if "chat_history_lernen" not in st.session_state:
    st.session_state.chat_history_lernen = []

# --- NAVIGATION IN DER SEITENLEISTE ---
with st.sidebar:
    st.markdown("## 🧭 Multitasking Hub")
    modus = st.selectbox(
        "Bereich wechseln:",
        ["🏋️‍♂️ ATHLETE PRO (Fitness)", "🎓 CAMPUS EXPERT (Schule)"]
    )
    
    st.divider()
    st.success("🔒 OpenAI Key: Permanent Verbunden")
    st.caption("Entwickelt für die Nutzung auf dem iPad.")

# --- BEREICH 1: FITNESS DASHBOARD ---
if modus == "🏋️‍♂️ ATHLETE PRO (Fitness)":
    # Eigenständiges Sport-Design
    st.title("🏋️‍♂️ ATHLETE PRO")
    st.markdown("### *„Der Schmerz von heute ist die Kraft von morgen.“*")
    
    # Dashboard-Kacheln für Fitness-Metriken
    st.markdown("#### 📊 Heutiger Status")
    kachel1, kachel2, kachel3 = st.columns(3)
    with kachel1:
        st.metric(label="💧 Wasser-Ziel", value="0.7 / 3.0 Liter", delta="+0.5L seit letztem Check")
    with kachel2:
        st.metric(label="🍳 Protein-Counter", value="45g / 140g", delta="-95g verbleibend")
    with kachel3:
        st.metric(label="🔥 Aktivität", value="4.200 Schritte", delta="Ziel: 10.000")
        
    st.divider()
    
    # Zwei Spalten: Links KI-Scanner, Rechts der Live-Trainer-Chat
    col_scan, col_chat = st.columns([1, 1])
    
    with col_scan:
        st.markdown("### 📸 KI-Fitness-Scanner")
        fit_option = st.selectbox(
            "Was möchtest du scannen?",
            [
                "🏋️‍♂️ Trainingsplan auswerten (Sätze, RPE, Muskelgruppe)",
                "🥗 Mahlzeit analysieren (Kalorien & Makro-Schätzung)",
                "🛑 Ausführung / Gerät prüfen (Verletzungsschutz)",
                "💊 Supplement- & Booster-Check"
            ]
        )
        uploaded_file = st.file_uploader("Foto hochladen...", type=["jpg", "png", "jpeg"], key="fit_upload")
        
        if uploaded_file:
            st.image(uploaded_file, use_container_width=True)
            if st.button("🚀 Foto sportwissenschaftlich analysieren", use_container_width=True):
                client = OpenAI(api_key=FESTER_API_KEY)
                with st.spinner("Dein Personal Trainer rechnet..."):
                    img_str = base64.b64encode(uploaded_file.getvalue()).decode()
                    prompt = f"Analysiere dieses Sport-/Ernährungsbild im Modus '{fit_option}'. Antworte präzise, motivierend und wissenschaftlich korrekt auf Deutsch."
                    
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}}]}],
                    )
                    ergebnis = response.choices[0].message.content
                    st.success("Analyse abgeschlossen!")
                    st.info(ergebnis)
                    with open(f"verlauf_fitness/{uploaded_file.name}.txt", "w") as f: f.write(ergebnis)

    with col_chat:
        st.markdown("### 💬 Chat mit deinem Personal Trainer")
        st.caption("Stelle Fragen zu Muskelaufbau, Muskelkater, Diäten oder Übungen.")
        
        # Chat-Verlauf anzeigen
        for msg in st.session_state.chat_history_fitness:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
                
        # Neuer Input
        user_input = st.chat_input("Frage deinen Coach etwas...", key="fit_chat_input")
        if user_input:
            st.session_state.chat_history_fitness.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.write(user_input)
                
            client = OpenAI(api_key=FESTER_API_KEY)
            with st.chat_message("assistant"):
                with st.spinner("Coach überlegt..."):
                    system_prompt = "Du bist ein erfahrener Personal Trainer und Ernährungsberater. Antworte kurz, knackig, motivierend und professionell."
                    messages = [{"role": "system", "content": system_prompt}] + st.session_state.chat_history_fitness[-10:]
                    
                    response = client.chat.completions.create(model="gpt-4o-mini", messages=messages)
                    reply = response.choices[0].message.content
                    st.write(reply)
                    st.session_state.chat_history_fitness.append({"role": "assistant", "content": reply})

# --- BEREICH 2: SCHUL DASHBOARD ---
else:
    # Eigenständiges Lern-Design
    st.title("🎓 CAMPUS EXPERT")
    st.markdown("### *„Wissen ist die einzige Ressource, die sich vermehrt, wenn man sie teilt.“*")
    
    # Dashboard-Elemente für das Lernen
    st.markdown("#### 🧠 Lern-Zentrale & Organisation")
    k1, k2, k3 = st.columns([1, 1, 1])
    with k1:
        st.markdown("⏱️ **Pomodoro Timer:** 25 Minuten Fokus!")
        if st.button("⏱️ Timer starten", use_container_width=True):
            st.toast("Fokus-Zeit läuft! Lass dich nicht ablenken.")
    with k2:
        st.markdown("📋 **Heutige To-Do Liste:**")
        st.checkbox("Hausaufgaben Mathe")
        st.checkbox("Vokabeln Englisch")
    with k3:
        st.markdown("💡 **Mental-Tipp:**")
        st.info("Trink jetzt ein großes Glas Wasser. Das steigert deine Konzentration um 15%!")

    st.divider()

    # Zwei Spalten: Links Schul-Scanner, Rechts der Nachhilfe-Chat
    col_scan_l, col_chat_l = st.columns([1, 1])
    
    with col_scan_l:
        st.markdown("### 📸 KI-Wissens-Scanner")
        lern_option = st.selectbox(
            "Was soll generiert werden?",
            [
                "📚 Strukturierter Lernzettel mit Kern-Definitionen",
                "📝 Echte Probearbeit (inkl. Lösungen am Ende)",
                "❓ Interaktives Multiple-Choice-Quiz",
                "🇬🇧 Vokabel- & Grammatikübersicht (Sprachen)"
            ]
        )
        uploaded_file_l = st.file_uploader("Foto von Buchseite oder Heft hochladen...", type=["jpg", "png", "jpeg"], key="lern_upload")
        
        if uploaded_file_l:
            st.image(uploaded_file_l, use_container_width=True)
            if st.button("📝 Dokumentation erstellen", use_container_width=True):
                client = OpenAI(api_key=FESTER_API_KEY)
                with st.spinner("KI liest den Text..."):
                    img_str = base64.b64encode(uploaded_file_l.getvalue()).decode()
                    prompt = f"Verarbeite dieses Bild und erstelle folgendes Format: '{lern_option}'. Nutze Markdown, Listen und fette Überschriften. Sprache: Deutsch."
                    
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}}]}],
                    )
                    ergebnis = response.choices[0].message.content
                    st.success("Ergebnis erfolgreich generiert!")
                    st.write(ergebnis)
                    with open(f"verlauf_lernen/{uploaded_file_l.name}.txt", "w") as f: f.write(ergebnis)

    with col_chat_l:
        st.markdown("### 💬 Chat mit deinem KI-Tutor")
        st.caption("Lass dir Rechenwege erklären, Texte zusammenfassen oder geschichtliche Ereignisse erzählen.")
        
        # Chat-Verlauf anzeigen
        for msg in st.session_state.chat_history_lernen:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
                
        # Neuer Input
        user_input_l = st.chat_input("Stelle deinem Tutor eine Frage...", key="lern_chat_input")
        if user_input_l:
            st.session_state.chat_history_lernen.append({"role": "user", "content": user_input_l})
            with st.chat_message("user"):
                st.write(user_input_l)
                
            client = OpenAI(api_key=FESTER_API_KEY)
            with st.chat_message("assistant"):
                with st.spinner("Tutor formuliert verständliche Antwort..."):
                    system_prompt = "Du bist ein extrem geduldiger, freundlicher und kluger Nachhilfelehrer für alle Schulfächer. Erkläre Dinge einfach, benutze Beispiele und stelle sicher, dass Schüler es leicht verstehen."
                    messages = [{"role": "system", "content": system_prompt}] + st.session_state.chat_history_lernen[-10:]
                    
                    response = client.chat.completions.create(model="gpt-4o-mini", messages=messages)
                    reply = response.choices[0].message.content
                    st.write(reply)
                    st.session_state.chat_history_lernen.append({"role": "assistant", "content": reply})