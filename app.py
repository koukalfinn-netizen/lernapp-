import streamlit as st
from PIL import Image
from openai import OpenAI
import os
import base64
import io

# Seitenkonfiguration für deine Fitness-App
st.set_page_config(page_title="iPad Fitness-App", page_icon="💪", layout="wide")

# --- HIER DEINEN SCHLÜSSEL FEST EINTRAGEN ---
FESTER_API_KEY = "sk-proj-VC0P5MOPeotJSISZshXYEaePtQYCyuqYNuMQGj9N1I-eLkdjwr4lNV-tSKjKSbsJ"

# App-Titel auf dem Hauptbildschirm
st.title("💪 iPad Foto-zu-Fitness App")
st.caption("Fotografiere Lebensmittel, Übungen oder Pläne und lass die KI deinen Fitnesstag strukturieren!")

# Ordner für den Verlauf erstellen
if not os.path.exists("meine_fitness_plaene"):
    os.makedirs("meine_fitness_plaene")

# --- SEITENLEISTE (SIDEBAR) FÜR EINSTELLUNGEN ---
with st.sidebar:
    st.header("⚙️ Einstellungen")
    
    # Statusanzeige für den festen Schlüssel
    if FESTER_API_KEY.startswith("sk-"):
        st.success("🔒 OpenAI API-Key ist dauerhaft aktiv!")
    else:
        st.warning("⚠️ Kein gültiger Schlüssel hinterlegt.")
    
    st.divider()
    
    st.subheader("🏋️‍♂️ KI-Modus")
    fitness_modus = st.radio(
        "Was soll die KI analysieren?",
        [
            "Trainingsplan aus Übungs-Foto erstellen", 
            "Kalorien & Proteine aus Lebensmittel-Foto schätzen", 
            "Motivation & Tipps für diese Übung geben"
        ]
    )
    
    st.divider()
    st.info("💡 **Tipp:** Du kannst diese Leiste am iPad oben links über das kleine Pfeil-Symbol einklappen, um mehr Platz zu haben!")

# --- HAUPTBILDSCHIRM ---
uploaded_file = st.file_uploader("Foto aufnehmen oder aus der Mediathek auswählen...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        image = Image.open(uploaded_file)
        st.image(image, caption="Dein hochgeladenes Foto", use_container_width=True)
    
    with col2:
        st.subheader("⚡ Analyse starten")
        start_button = st.button("🚀 KI-Fitness-Check starten", use_container_width=True)
        
        if start_button:
            client = OpenAI(api_key=FESTER_API_KEY)
            
            with st.spinner("🧠 KI analysiert dein Fitness-Foto... Bitte kurz warten..."):
                buffered = io.BytesIO()
                image.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                
                # Fitness Prompts
                if fitness_modus == "Trainingsplan aus Übungs-Foto erstellen":
                    prompt = "Lies die Notizen oder Übungen auf dem Bild und erstelle daraus einen übersichtlichen, perfekt strukturierten Trainingsplan mit Sätzen, Wiederholungen und Pausenzeiten auf Deutsch."
                elif fitness_modus == "Kalorien & Proteine aus Lebensmittel-Foto schätzen":
                    prompt = "Analysiere das gezeigte Essen auf dem Bild. Schätze die ungefähren Kalorien, Kohlenhydrate, Fette und Proteine (Eiweiß) für eine normale Portion und gib kurze, gesunde Tipps dazu."
                else:
                    prompt = "Analysiere die gezeigte Fitness-Übung oder das Gerät auf dem Bild. Erkläre kurz die perfekte Ausführung, worauf man achten muss, um Verletzungen zu vermeiden, und welche Muskeln trainiert werden."
                
                try:
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
                    
                    st.success("🎉 Analyse fertig!")
                    st.markdown("### 📝 Dein Fitness-Ergebnis:")
                    st.info(ki_ergebnis)
                    
                    dateiname = uploaded_file.name.split('.')[0]
                    st.download_button(
                        label="📥 Plan auf dem iPad speichern",
                        data=ki_ergebnis,
                        file_name=f"{dateiname}_Fitnessplan.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                    
                    plan_path = os.path.join("meine_fitness_plaene", f"{dateiname}.txt")
                    with open(plan_path, "w", encoding="utf-8") as f:
                        f.write(ki_ergebnis)
                        
                except Exception as e:
                    st.error(f"Fehler bei der Verarbeitung: {e}")

# Verlauf anzeigen
st.divider()
st.subheader("📂 Gespeicherte Fitness-Dokumente")
dateien = os.listdir("meine_fitness_plaene") if os.path.exists("meine_fitness_plaene") else []
if dateien:
    for datei in dateien:
        st.write(f"💪 {datei}")
else:
    st.write("Noch keine Pläne in dieser Sitzung gespeichert.")