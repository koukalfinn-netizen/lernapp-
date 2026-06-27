import streamlit as st
from PIL import Image
from openai import OpenAI
import os
import base64
import io

# 1. HARDCODETER API KEY (Dauerhaft aktiv)
FESTER_API_KEY = "sk-proj-VC0P5MOPeotJSISZshXYEaePtQYCyuqYNuMQGj9N1I-eLkdjwr4lNV-tSKjKSbsJ"

# Seiten-Konfiguration
st.set_page_config(page_title="iPad Super-App", page_icon="🚀", layout="wide")

# Ordner-Struktur für beide Bereiche
for pfad in ["verlauf_fitness", "verlauf_lernen"]:
    if not os.path.exists(pfad):
        os.makedirs(pfad)

# --- NAVIGATION IN DER SEITENLEISTE ---
with st.sidebar:
    st.title("📱 Hauptmenü")
    modus = st.selectbox(
        "Wähle deine App:",
        ["🏋️ Fitness & Ernährung Coach", "🎓 KI-Lern-Assistent"]
    )
    
    st.divider()
    if FESTER_API_KEY.startswith("sk-"):
        st.success("🔒 KI-Schlüssel: DAUERHAFT AKTIV")
    
    st.divider()
    st.info("💡 **Tipp:** Wechsle hier einfach zwischen Sport und Schule!")

# --- BEREICH 1: FITNESS & ERNÄHRUNG ---
if modus == "🏋️ Fitness & Ernährung Coach":
    st.title("🏋️‍♂️ PRO-Fitness Dashboard")
    st.subheader("Dein KI-Trainer für maximale Performance")
    
    col_settings, col_upload = st.columns([1, 2])
    
    with col_settings:
        st.markdown("### 🎯 Zielsetzung")
        fit_option = st.radio(
            "Analyse-Typ:",
            [
                "Professioneller Trainingsplan (mit RPE & Sätzen)", 
                "Präziser Kalorien- & Makro-Check (Essen)", 
                "Technik-Analyse & Verletzungsprävention",
                "Supplement-Check & Ernährungs-Optimierung"
            ]
        )
        st.write("---")
        st.caption("Dieses Dashboard ist auf sportwissenschaftliche Genauigkeit optimiert.")

    with col_upload:
        uploaded_file = st.file_uploader("Foto hochladen (Essen, Gerät oder Plan)", type=["jpg", "png", "jpeg"])
        if uploaded_file:
            st.image(uploaded_file, width=400)
            if st.button("🚀 Fitness-Analyse starten", use_container_width=True):
                client = OpenAI(api_key=FESTER_API_KEY)
                with st.spinner("Analyse läuft..."):
                    img_str = base64.b64encode(uploaded_file.getvalue()).decode()
                    
                    # Hochpräzise Fitness-Prompts
                    if "Trainingsplan" in fit_option:
                        p = "Erstelle einen Profi-Trainingsplan basierend auf dem Bild. Inkludiere: Übung, Sätze, Wiederholungen, RPE (1-10 Intensität), Pausenzeit und welche Primärmuskeln trainiert werden. Sprache: Deutsch."
                    elif "Kalorien" in fit_option:
                        p = "Analysiere das Essen. Schätze: Kalorien, Protein, KH, Fett. Gib eine Bewertung (Gesund/Ungesund) und nenne eine bessere Alternative für Muskelaufbau. Sprache: Deutsch."
                    elif "Technik" in fit_option:
                        p = "Analysiere die Übung/das Gerät. Erkläre die perfekte Biomechanik, nenne die 3 häufigsten Fehler und gib Tipps für maximale Range of Motion. Sprache: Deutsch."
                    else:
                        p = "Analysiere die gezeigten Infos/Produkte und gib eine wissenschaftlich fundierte Meinung zur Optimierung der Ernährung für einen Sportler ab."

                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": [{"type": "text", "text": p}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}}]}],
                    )
                    ergebnis = response.choices[0].message.content
                    st.success("Analyse fertig!")
                    st.info(ergebnis)
                    # Verlauf speichern
                    with open(f"verlauf_fitness/{uploaded_file.name}.txt", "w") as f: f.write(ergebnis)

# --- BEREICH 2: KI-LERN-ASSISTENT ---
else:
    st.title("🎓 KI-Lern-Zentrum")
    st.subheader("Verwandle Fotos in Wissen")
    
    col_input, col_display = st.columns([1, 1])
    
    with col_input:
        lern_option = st.selectbox("Was soll ich erstellen?", ["Übersichtlicher Lernzettel", "Probearbeit mit Lösungen", "Interaktives Quiz"])
        uploaded_lern = st.file_uploader("Foto deiner Notizen/Buchseite", type=["jpg", "png", "jpeg"])
        
    if uploaded_lern:
        with col_display:
            st.image(uploaded_lern, caption="Deine Vorlage")
            if st.button("📝 Wissen generieren", use_container_width=True):
                client = OpenAI(api_key=FESTER_API_KEY)
                with st.spinner("KI liest mit..."):
                    img_str = base64.b64encode(uploaded_lern.getvalue()).decode()
                    p = f"Erstelle {lern_option} basierend auf dem Bild. Strukturiere es mit Markdown, fettgedruckten Begriffen und klarer Gliederung auf Deutsch."
                    
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": [{"type": "text", "text": p}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}}]}],
                    )
                    ergebnis = response.choices[0].message.content
                    st.markdown("---")
                    st.success("Ergebnis erstellt!")
                    st.write(ergebnis)
                    with open(f"verlauf_lernen/{uploaded_lern.name}.txt", "w") as f: f.write(ergebnis)

# Gemeinsamer Verlauf am Ende
st.divider()
st.subheader("📂 Letzte Aktivitäten")
verlauf_pfad = "verlauf_fitness" if modus == "🏋️ Fitness & Ernährung Coach" else "verlauf_lernen"
dateien = os.listdir(verlauf_pfad)
if dateien:
    for d in dateien[-3:]: st.text(f"✅ {d}")
else:
    st.write("Noch keine Dokumente heute.")