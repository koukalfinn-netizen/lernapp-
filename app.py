import streamlit as st
from PIL import Image
from openai import OpenAI
import os
import base64
import io

# App-Titel
st.title("📸 iPad Foto-zu-Lernzettel App")
st.write("Mach ein Foto deiner Notizen und lass die KI alles erledigen!")

# Ordner für die Ablage
if not os.path.exists("meine_pdfs"):
    os.makedirs("meine_pdfs")

# Foto hochladen oder direkt mit der iPad-Kamera aufnehmen
uploaded_file = st.file_uploader("Foto aufnehmen oder auswählen...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Dein Foto", use_container_width=True)
    
    st.subheader("🧠 KI-Optionen")
    api_key = st.text_input("Gib deinen OpenAI API-Key ein:", type="password")
    
    lern_modus = st.selectbox(
        "Was soll die KI tun?",
        ["Übersichtlichen Lernzettel erstellen", "Kleine Probearbeit erstellen", "Interaktives Quiz erstellen"]
    )
    
    if st.button("KI starten"):
        if api_key:
            client = OpenAI(api_key=api_key)
            st.info("KI analysiert das Foto... Bitte kurz warten...")
            
            # Bild für die KI vorbereiten (in Base64 umwandeln)
            buffered = io.BytesIO()
            image.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            # Prompts festlegen
            if lern_modus == "Übersichtlichen Lernzettel erstellen":
                prompt = "Lies den Text auf dem Bild und erstelle daraus einen übersichtlichen, strukturierten Lernzettel mit Bulletpoints und Definitionen auf Deutsch."
            elif lern_modus == "Kleine Probearbeit erstellen":
                prompt = "Lies den Text auf dem Bild und erstelle eine kleine Probearbeit mit 5 offenen Fragen und ausführlichen Lösungen darunter."
            else:
                prompt = "Lies den Text auf dem Bild und erstelle ein Quiz mit 4 Multiple-Choice-Fragen (A, B, C) und den Lösungen ganz unten."
            
            try:
                # KI aufrufen (schaut sich das Bild direkt an)
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
                st.success("Fertig!")
                st.markdown(ki_ergebnis)
                
                # In der App speichern
                dateiname = uploaded_file.name.split('.')[0]
                pdf_path = os.path.join("meine_pdfs", f"{dateiname}.txt")
                with open(pdf_path, "w", encoding="utf-8") as f:
                    f.write(ki_ergebnis)
                    
            except Exception as e:
                st.error(f"Fehler: {e}")
        else:
            st.warning("Bitte gib deinen API-Key ein.")

# Ablage anzeigen
st.hr()
st.subheader("📂 Deine Dokumente")
dateien = os.listdir("meine_pdfs")
if dateien:
    for datei in dateien:
        st.write(f"📄 {datei}")
else:
    st.write("Noch keine Dokumente gespeichert.")
