import streamlit as st
from PIL import Image
from openai import OpenAI
import os
import base64
import io

# Seitenkonfiguration für ein moderneres Layout
st.set_page_config(page_title="iPad Lern-App", page_icon="📸", layout="wide")

# App-Titel auf dem Hauptbildschirm
st.title("📸 iPad Foto-zu-Lernzettel App")
st.caption("Mach ein Foto deiner Notizen und lass die KI die Arbeit erledigen!")

# Ordner für die Ablage erstellen
if not os.path.exists("meine_pdfs"):
    os.makedirs("meine_pdfs")

# --- SEITENLEISTE (SIDEBAR) FÜR EINSTELLUNGEN ---
with st.sidebar:
    st.header("⚙️ Einstellungen")
    
    # Sicherer Text-Eingang für den API-Key
    api_key = st.text_input("OpenAI API-Key:", type="password", help="Dein privater Schlüssel von openai.com")
    
    st.divider()
    
    st.subheader("🧠 KI-Modus")
    lern_modus = st.radio(
        "Was soll die KI erstellen?",
        [
            "Übersichtlichen Lernzettel erstellen", 
            "Kleine Probearbeit erstellen", 
            "Interaktives Quiz erstellen"
        ]
    )
    
    st.divider()
    st.info("💡 **Tipp:** Du kannst diese Leiste am iPad oben links über das kleine Pfeil-Symbol einklappen, um mehr Platz zu haben!")

# --- HAUPTBILDSCHIRM ---
uploaded_file = st.file_uploader("Foto aufnehmen oder aus der Mediathek auswählen...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Bild anzeigen (schön verpackt in zwei Spalten)
    col1, col2 = st.columns([1, 1])
    
    with col1:
        image = Image.open(uploaded_file)
        st.image(image, caption="Dein hochgeladenes Foto", use_container_width=True)
    
    with col2:
        st.subheader("⚡ Verarbeitung")
        start_button = st.button("🚀 KI-Generierung starten", use_container_width=True)
        
        if start_button:
            if not api_key:
                st.error("❌ Bitte gib zuerst deinen OpenAI API-Key in der linken Seitenleiste ein!")
            else:
                client = OpenAI(api_key=api_key)
                
                # Schick animierter Lade-Status
                with st.spinner("🧠 KI analysiert das Foto und strukturiert den Inhalt... Bitte kurz warten..."):
                    # Bild für die KI vorbereiten (in Base64 umwandeln)
                    buffered = io.BytesIO()
                    image.save(buffered, format="JPEG")
                    img_str = base64.b64encode(buffered.getvalue()).decode()
                    
                    # Prompts je nach Auswahl festlegen
                    if lern_modus == "Übersichtlichen Lernzettel erstellen":
                        prompt = "Lies den Text auf dem Bild und erstelle daraus einen übersichtlichen, perfekt strukturierten Lernzettel mit Bulletpoints, fetten Überschriften und Definitionen auf Deutsch."
                    elif lern_modus == "Kleine Probearbeit erstellen":
                        prompt = "Lies den Text auf dem Bild und erstelle eine kleine Probearbeit mit 5 offenen Fragen und ausführlichen Lösungen ganz unten."
                    else:
                        prompt = "Lies den Text auf dem Bild und erstelle ein Quiz mit 4 Multiple-Choice-Fragen (A, B, C) und den Lösungen ganz unten."
                    
                    try:
                        # KI aufrufen
                        response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {
                                    "role": "user",
                                    "content": [
                                        {"type": "text", "text": prompt},
                                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}}
                                    ],
                                }
                            ],
                        )
                        
                        ki_ergebnis = response.choices[0].message.content
                        
                        # Ergebnis in der App anzeigen
                        st.success("🎉 Fertig geladen!")
                        st.markdown("### 📄 Dein Ergebnis:")
                        st.info(ki_ergebnis)
                        
                        # --- NEU: ECHTER PDF/TEXT DOWNLOAD-BUTTON ---
                        dateiname = uploaded_file.name.split('.')[0]
                        st.download_button(
                            label="📥 Dokument auf dem iPad speichern (PDF/Text)",
                            data=ki_ergebnis,
                            file_name=f"{dateiname}_Lernzettel.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
                        
                        # Zusätzlich auf dem Server sichern
                        pdf_path = os.path.join("meine_pdfs", f"{dateiname}.txt")
                        with open(pdf_path, "w", encoding="utf-8") as f:
                            f.write(ki_ergebnis)
                            
                    except Exception as e:
                        st.error(f"Fehler bei der Verarbeitung: {e}")

# Verlauf anzeigen
st.divider()
st.subheader("📂 Zuletzt erstellte Dokumente (Verlauf)")
dateien = os.listdir("meine_pdfs")
if dateien:
    for datei in dateien:
        st.write(f"📄 {datei}")
else:
    st.write("Noch keine Dokumente in dieser Sitzung gespeichert.")