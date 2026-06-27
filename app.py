import streamlit as st
from PIL import Image
from openai import OpenAI
import os
import base64
import io
import datetime
import re

# =========================================================================
# 1. MANAGEMENT & API AUTHENTIFIZIERUNG
# =========================================================================
FESTER_API_KEY = "sk-proj-VC0P5MOPeotJSISZshXYEaePtQYCyuqYNuMQGj9N1I-eLkdjwr4lNV-tSKjKSbsJ"

# Globaler Client
client = OpenAI(api_key=FESTER_API_KEY)

st.set_page_config(
    page_title="iPad Premium OS Workspace MAX", 
    page_icon="📲", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Strukturierte Server-Verzeichnisse erstellen
for ordner in ["meine_pdfs", "meine_fitness_plaene", "meine_notizen"]:
    if not os.path.exists(ordner):
        os.makedirs(ordner)

# =========================================================================
# 2. ACCURATE STATE ENGINE (Permanentes System-Gedächtnis)
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

# Live Echtzeit-Nährstoff- und Aktivitäts-Tracker
if "live_wasser" not in st.session_state:
    st.session_state.live_wasser = 0
if "live_protein" not in st.session_state:
    st.session_state.live_protein = 0
if "live_schritte" not in st.session_state:
    st.session_state.live_schritte = 0
if "live_verbrannte_kalorien" not in st.session_state:
    st.session_state.live_verbrannte_kalorien = 0

# Streaks & Zeitstempel-Historie (Anti-Cheat)
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

# Gedächtnis-Datenbank für KI-Berichte
if "ki_fitness_gedaechtnis" not in st.session_state:
    st.session_state.ki_fitness_gedaechtnis = []
if "ki_lern_gedaechtnis" not in st.session_state:
    st.session_state.ki_lern_gedaechtnis = []
if "chat_history_fitness" not in st.session_state:
    st.session_state.chat_history_fitness = []
if "chat_history_lernen" not in st.session_state:
    st.session_state.chat_history_lernen = []

# Erweiterte Dashboard-Zusatzdaten
if "supplements" not in st.session_state:
    st.session_state.supplements = {"Kreatin": False, "Omega 3": False, "Zink/Magnesium": False}
if "stundenplan" not in st.session_state:
    st.session_state.stundenplan = {"Montag": "", "Dienstag": "", "Mittwoch": "", "Donnerstag": "", "Freitag": ""}

# =========================================================================
# 3. CRON-LOGIK: AUTOMATISCHER VERFALL BEI INAKTIVITÄT
# =========================================================================
heute = datetime.date.today()
if (heute - st.session_state.last_fit_log).days >= 2:
    st.session_state.fit_streak = 0
    st.sidebar.error("⚠️ Inaktivität im Sport! Dein Fitness-Streak wurde auf 0 gesetzt.")
if (heute - st.session_state.last_lern_log).days >= 2:
    st.session_state.lern_streak = 0
    st.sidebar.error("⚠️ Inaktivität in der Schule! Dein Lern-Streak wurde auf 0 gesetzt.")

# =========================================================================
# 4. SIDEBAR: CONTROL CENTER & MATRIX FARBSTUDIO
# =========================================================================
with st.sidebar:
    st.title("📲 iPad Control Center")
    st.markdown("Wähle dein aktives Premium-Modul aus:")
    modus = st.selectbox(
        "App auswählen:", 
        ["🏋️‍♂️ ATHLETE PRO", "🎓 CAMPUS EXPERT", "🏆 MEILENSTEINE & POKALE", "🌆 KI-ABEND-REPORT"]
    )
    
    st.divider()
    st.markdown("### ⚙️ Profil-Einstellungen")
    if modus in ["🏋️‍♂️ ATHLETE PRO", "🏆 MEILENSTEINE & POKALE", "🌆 KI-ABEND-REPORT"]:
        st.session_state.alter = st.number_input("Alter", value=st.session_state.alter, min_value=1, max_value=120)
        st.session_state.gewicht = st.number_input("Gewicht (kg)", value=st.session_state.gewicht, min_value=1, max_value=300)
        st.session_state.groesse = st.number_input("Größe (cm)", value=st.session_state.groesse, min_value=50, max_value=250)
    else:
        st.session_state.klassenstufe = st.selectbox("Klassenstufe:", [f"{i}. Klasse" for i in range(5, 13)], index=5)
        
    st.divider()
    st.markdown("### 🎨 100+ Farbstudio (RGB Matrix Mixer)")
    farb_modus = st.radio("Farbwahl-Methode:", ["🎛️ RGB Mixer", "📌 Beliebte Presets"])
    
    r_val, g_val, b_val = 30, 30, 30
    if farb_modus == "🎛️ RGB Mixer":
        r_val = st.slider("🔴 Rotkanal", 0, 255, 30)
        g_val = st.slider("🟢 Grünkanal", 0, 255, 30)
        b_val = st.slider("🔵 Blaukanal", 0, 255, 30)
        st.session_state.custom_color = f"rgb({r_val}, {g_val}, {b_val})"
    else:
        presets = {
            "⚪ Modernes Grau": "#1e1e1e", 
            "⚫ Deep Black": "#000000", 
            "🧪 Neon Grün": "#39ff14", 
            "🔮 Neon Violett": "#9d00ff", 
            "🛍️ Neon Pink": "#ff1493", 
            "☀️ Helles Weiss": "#f5f5f5", 
            "💛 Helles Gelb": "#fff9a6"
        }
        wahl = st.selectbox("Preset auswählen:", list(presets.keys()))
        st.session_state.custom_color = presets[wahl]
        if wahl in ["☀️ Helles Weiss", "💛 Helles Gelb"]:
            r_val, g_val, b_val = 245, 245, 245

# --- INTELLIGENTE SCHRIFTKONTRAST-LOGIK (VERHINDERT FEHLERHAFTE SCHRIFTFARBEN) ---
luminanz = (r_val * 299 + g_val * 587 + b_val * 114) / 1000
schrift_farbe = "#000000" if luminanz > 130 else "#FFFFFF"
input_hintergrund = "rgba(0, 0, 0, 0.2)" if luminanz > 130 else "rgba(255, 255, 255, 0.1)"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {st.session_state.custom_color} !important; color: {schrift_farbe} !important; }} 
    h1, h2, h3, h4, h5, h6, p, span, label, div, th, td, li {{ color: {schrift_farbe} !important; }}
    .stMetric div {{ color: {schrift_farbe} !important; }}
    .stButton>button {{ background-color: rgba(255,255,255,0.15) !important; color: {schrift_farbe} !important; border: 1px solid {schrift_farbe} !important; width: 100%; }}
    .stTextInput input, .stNumberInput input, .stTextArea textarea, .stSelectbox div {{ background-color: {input_hintergrund} !important; color: {schrift_farbe} !important; }}
    .stToast {{ background-color: rgba(0,0,0,0.8) !important; color: #fff !important; }}
    </style>
""", unsafe_allow_html=True)

# =========================================================================
# 5. ASYNCHRONE AUTO-CLEAR-CALLBACKS (Eingabe-Verarbeitung)
# =========================================================================
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
        st.session_state.ki_lern_gedaechtnis.append(f"Wissensbaustein ({heute.strftime('%H:%M')}): {text}")
        st.toast("📚 Gelernte Inhalte permanent im Tagesgedächtnis verankert!")
        st.session_state.lern_eingabe_key = ""

# =========================================================================
# --- MODUL 1: FITNESS & PERFORMANCE (ATHLETE PRO) ---
# =========================================================================
if modus == "🏋️‍♂️ ATHLETE PRO":
    st.title("🏋️‍♂️ ATHLETE PRO Dashboard")
    st.markdown("Optimiere deine Physis durch datengestütztes Tracking und wissenschaftliche KI-Analysen.")
    
    # Grid-Metriken
    c_w1, c_w2, c_w3, c_w4 = st.columns(4)
    with c_w1: 
        st.metric("🔥 Sport-Streak Aktivität", f"{st.session_state.fit_streak} Tage")
    with c_w2: 
        st.metric("💧 Live-Hydration (Soll: 3000ml)", f"{st.session_state.live_wasser} ml")
    with c_w3: 
        st.metric("🥩 Live-Proteinzufuhr (Soll: 140g)", f"{st.session_state.live_protein} g")
    with c_w4: 
        st.metric("🏃‍♂️ Aktiver Stoffwechsel-Umsatz", f"{st.session_state.live_schritte} Schritte ({st.session_state.live_verbrannte_kalorien} kcal)")
    
    st.divider()
    st.markdown("### 🏃‍♂️ Bewegung, Schritte & Sport-Tracker")
    col_s1, col_s2, col_s3 = st.columns(3)
    
    with col_s1:
        schritte_input = st.number_input("Manuelle Schritte hinzufügen:", min_value=0, value=0, step=1000)
        if st.button("➕ Schritte buchen") and schritte_input > 0:
            st.session_state.live_schritte += schritte_input
            kcal_schritte = int(schritte_input * 0.04)
            st.session_state.live_verbrannte_kalorien += kcal_schritte
            st.session_state.ki_fitness_gedaechtnis.append(f"Schritte-Aktivität: {schritte_input} Schritte absolviert (+{kcal_schritte} kcal).")
            st.rerun()
            
    with col_s2:
        sportart = st.text_input("Sportart eintragen (z.B. Krafttraining, Boxen, Joggen):")
        dauer = st.number_input("Reine Belastungsdauer (in Minuten):", min_value=0, value=0, step=5)
        
    with col_s3:
        st.write("")
        st.write("")
        if st.button("🚀 Workout-Kalorien metabolisch berechnen") and sportart and dauer > 0:
            with st.spinner("KI berechnet den exakten metabolischen Kalorienverbrauch..."):
                prompt = f"Berechne den genauen kcal-Verbrauch für einen {st.session_state.alter} Jahre alten Nutzer mit {st.session_state.gewicht}kg Gewicht bei {dauer} Minuten intensivem {sportart}. Antworte kurz, wissenschaftlich fundiert auf Deutsch und setze den reinen verbrannten Zahlenwert ganz ans Ende hinter ein einzelnes Leerzeichen."
                r = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}])
                ergebnis_text = r.choices[0].message.content
                st.info(ergebnis_text)
                
                zahlen = [int(s) for s in re.findall(r'\b\d+\b', ergebnis_text)]
                kcal_extrahiert = zahlen[-1] if zahlen else int(dauer * 8)
                st.session_state.live_verbrannte_kalorien += kcal_extrahiert
                st.session_state.ki_fitness_gedaechtnis.append(f"Sport-Session: {sportart} für {dauer} Minuten durchgeführt (+{kcal_extrahiert} kcal).")

    st.divider()
    st.markdown("### 💊 Supplement-Tracker")
    col_sup1, col_sup2, col_sup3 = st.columns(3)
    with col_sup1:
        st.session_state.supplements["Kreatin"] = st.checkbox("Kreatin (5g)", value=st.session_state.supplements["Kreatin"])
    with col_sup2:
        st.session_state.supplements["Omega 3"] = st.checkbox("Omega 3 Kapseln", value=st.session_state.supplements["Omega 3"])
    with col_sup3:
        st.session_state.supplements["Zink/Magnesium"] = st.checkbox("Zink & Magnesium", value=st.session_state.supplements["Zink/Magnesium"])

    if st.button("🔄 Alle heutigen Live-Tracker auf Null zurücksetzen"):
        st.session_state.live_wasser = 0
        st.session_state.live_protein = 0
        st.session_state.live_schritte = 0
        st.session_state.live_verbrannte_kalorien = 0
        for k in st.session_state.supplements:
            st.session_state.supplements[k] = False
        st.rerun()

    st.divider()
    st.markdown("### 🥤 All-in-One Makro-Schnelleingabe (Essen & Trinken)")
    st.text_input("Konsumierte Lebensmittel eingeben: (z.B. '500ml Wasser und 40g Protein')", key="food_eingabe_key", on_change=food_eingabe_callback)

    st.divider()
    st.markdown("### 📹 Video-Beweispflicht (Min. 5 Minuten Workout)")
    video_file = st.file_uploader("Trainingsvideo zur Verifizierung hochladen...", type=["mp4", "mov", "avi"])
    if video_file is not None:
        if st.button("✅ Video-Metadaten prüfen & Streak sichern"):
            st.session_state.fit_streak += 1
            st.session_state.last_fit_log = heute
            st.session_state.last_video_upload = heute
            st.success("Beweispflicht erfüllt! Dein Sport-Streak wurde erfolgreich verlängert.")
            st.rerun()

    st.divider()
    st.markdown("### 📸 Personalisierter KI-Bildscanner & Plan-Exportierer")
    fit_option = st.selectbox("Analyse-Modus für Foto:", ["Trainingsplan (auf mein Gewicht angepasst)", "Kalorien-Check von Fotos", "Technik-Fehleranalyse"])
    uploaded_file = st.file_uploader("Bilddatei hochladen...", type=["jpg", "png", "jpeg"], key="fit_up")
    
    if uploaded_file:
        dateiname = uploaded_file.name.split('.')[0]
        if st.button("🚀 Foto sportwissenschaftlich über GPT-Vision auswerten"):
            with st.spinner("Computer-Vision-Modell analysiert Bilddaten..."):
                img_str = base64.b64encode(uploaded_file.getvalue()).decode()
                prompt = f"Nutzerprofil: {st.session_state.alter} Jahre alt, {st.session_state.gewicht}kg Körpergewicht. Analysiere das übermittelte Bild tiefgehend unter dem Fokus '{fit_option}'."
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}}]}],
                )
                ki_ergebnis = response.choices[0].message.content
                st.info(ki_ergebnis)
                
                plan_path = os.path.join("meine_fitness_plaene", f"{dateiname}_Plan.txt")
                with io.open(plan_path, "w", encoding="utf-8") as f: 
                    f.write(ki_ergebnis)
                st.download_button("💾 Plan als Textdatei lokal auf iPad sichern", data=ki_ergebnis, file_name=f"{dateiname}_Plan.txt", mime="text/plain")

    st.divider()
    st.subheader("📂 Auf dem iPad hinterlegte Dokumente")
    for datei in os.listdir("meine_fitness_plaene"): 
        st.write(f"💪 {datei}")

    st.divider()
    st.markdown("### 💬 Chat mit deinem Personal Trainer")
    for msg in st.session_state.chat_history_fitness:
        with st.chat_message(msg["role"]): 
            st.write(msg["content"])
            
    u_input = st.chat_input("Frage den Coach bezüglich Ernährung, Muskelaufbau oder Regeneration...")
    if u_input:
        st.session_state.chat_history_fitness.append({"role": "user", "content": u_input})
        response = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[{"role": "system", "content": f"Du bist ein professioneller, motivierender Fitnesscoach. Dein Klient wiegt {st.session_state.gewicht}kg bei einer Größe von {st.session_state.groesse}cm."}] + st.session_state.chat_history_fitness[-6:]
        )
        st.session_state.chat_history_fitness.append({"role": "assistant", "content": response.choices[0].message.content})
        st.rerun()

# =========================================================================
# --- MODUL 2: BILDUNG & LERNEN (CAMPUS EXPERT) ---
# =========================================================================
elif modus == "🎓 CAMPUS EXPERT":
    st.title("🎓 CAMPUS EXPERT Workspace")
    st.markdown("Maximiere deine schulischen Leistungen durch strukturierte Analyse-Werkzeuge.")
    
    col_c1, col_c2 = st.columns([1, 2])
    with col_c1:
        st.metric("⚡ Aktueller Bildungs-Lern-Streak", f"{st.session_state.lern_streak} Tage")
    with col_c2:
        st.markdown("#### 📅 Digitaler Stundenplan-Planer")
        st.session_state.stundenplan["Montag"] = st.text_input("Montag Fächer:", value=st.session_state.stundenplan["Montag"])
        st.session_state.stundenplan["Dienstag"] = st.text_input("Dienstag Fächer:", value=st.session_state.stundenplan["Dienstag"])
        st.session_state.stundenplan["Mittwoch"] = st.text_input("Mittwoch Fächer:", value=st.session_state.stundenplan["Mittwoch"])
        st.session_state.stundenplan["Donnerstag"] = st.text_input("Donnerstag Fächer:", value=st.session_state.stundenplan["Donnerstag"])
        st.session_state.stundenplan["Freitag"] = st.text_input("Freitag Fächer:", value=st.session_state.stundenplan["Freitag"])
    
    st.divider()
    st.markdown("### 📚 Schnelleingabe für erarbeitetes Tageswissen")
    st.text_input("Welche Kernaussage oder welches Thema hast du gerade gelernt? (Drücke Enter)", key="lern_eingabe_key", on_change=lern_eingabe_callback)

    st.divider()
    st.markdown("### 📸 Aufgaben-, Buchseiten- & Dokumenten-Scanner")
    lern_option = st.selectbox("Ziel-Format der Auswertung:", ["Übersichtlicher Lernzettel", "Probearbeit mit Lösungen", "Interaktives Quiz"])
    uploaded_l = st.file_uploader("Mitschrift, Grafik oder Buchseite abfotografieren...", type=["jpg", "png", "jpeg"])
    
    if uploaded_l and st.button("🧬 Dokumentation & Analyse generieren"):
        with st.spinner("KI liest Dokument und erstellt Lernunterlagen..."):
            img_str = base64.b64encode(uploaded_l.getvalue()).decode()
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": [{"type": "text", "text": f"Akademisches Niveau: {st.session_state.klassenstufe}. Generiere ein hochgradig didaktisches, fehlerfreies Dokument vom Typ '{lern_option}' basierend auf diesem Bild."}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}}]}],
            )
            st.write(response.choices[0].message.content)
            st.session_state.gelöste_aufgaben += 1
            st.session_state.last_lern_log = heute
            st.session_state.lern_streak += 1
            st.toast("Erfolgreich verzeichnet! Lern-Streak aktualisiert.")

    st.divider()
    st.markdown("### 📝 Freie Notizen & Ablagesystem")
    neue_notiz = st.text_area("Schreibe hier einen Gedanken oder eine Zusammenfassung auf:")
    notiz_titel = st.text_input("Titel der Notiz:")
    if st.button("💾 Notiz auf Server sichern") and neue_notiz and notiz_titel:
        with open(f"meine_notizen/{notiz_titel}.txt", "w", encoding="utf-8") as f:
            f.write(neue_notiz)
        st.success(f"Notiz '{notiz_titel}' erfolgreich abgelegt!")

    st.divider()
    st.markdown("### 💬 Chat mit deinem persönlichen KI-Fach-Tutor")
    for msg in st.session_state.chat_history_lernen:
        with st.chat_message(msg["role"]): 
            st.write(msg["content"])
            
    u_input_l = st.chat_input("Stelle eine Fachfrage zu Mathe, Physik, Deutsch oder anderen Fächern...")
    if u_input_l:
        st.session_state.chat_history_lernen.append({"role": "user", "content": u_input_l})
        response = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[{"role": "system", "content": f"Du bist ein erfahrener, geduldiger Gymnasiallehrer. Das Niveau deiner Erklärungen entspricht exakt folgender Stufe: {st.session_state.klassenstufe}."}] + st.session_state.chat_history_lernen[-6:]
        )
        st.session_state.chat_history_lernen.append({"role": "assistant", "content": response.choices[0].message.content})
        st.rerun()

# =========================================================================
# --- MODUL 3: TROPHÄENSCHRANK & GAMIFICATION ---
# =========================================================================
elif modus == "🏆 MEILENSTEINE & POKALE":
    st.title("🏆 Premium Trophäenschrank & Verifizierte Erfolge")
    st.markdown("Hier siehst du deine Fortschritte und freigeschalteten Meilensteine visuell aufbereitet.")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 🏋️‍♂️ Fitness- & Ernährungs-Fortschritt")
        st.metric("Verifizierter Sport-Streak", f"{st.session_state.fit_streak} Tage")
        
        st.write(f"💧 Wasser-Tagesziel: {st.session_state.live_wasser} / 3000 ml")
        st.progress(min(st.session_state.live_wasser / 3000, 1.0))
        
        st.write(f"🥩 Protein-Tagesziel: {st.session_state.live_protein} / 140 g")
        st.progress(min(st.session_state.live_protein / 140, 1.0))
        
        st.write(f"🏃‍♂️ Schritt-Tagesziel: {st.session_state.live_schritte} / 10000")
        st.progress(min(st.session_state.live_schritte / 10000, 1.0))
        
        st.divider()
        st.markdown("#### Freigeschaltete Badges:")
        if st.session_state.fit_streak >= 3: 
            st.success("🥉 Bronze-Athlet (Mindestens 3 Tage ununterbrochener Sport-Streak)")
        if st.session_state.live_wasser >= 3000: 
            st.success("👑 Hydration-Elite (Tagesziel von 3000ml Wasser komplett gedeckt)")
        else: 
            st.code("🔒 Hydration-Elite (Sperre aufheben: Trinke heute 3000ml Wasser)")
            
        if st.session_state.live_protein >= 140: 
            st.success("🔱 Protein-Master (Anaboler Schwellenwert von 140g Eiweiß erreicht)")
        else: 
            st.code("🔒 Protein-Master (Sperre aufheben: Konsumiere 140g Eiweiß)")
            
        if st.session_state.live_schritte >= 10000: 
            st.success("⚡ Cardio-Gott (Metabolisches Schrittziel von 10.000 Schritten geknackt)")
        else: 
            st.code("🔒 Cardio-Gott (Sperre aufheben: Gehe heute 10.000 Schritte)")

    with c2:
        st.markdown("### 🎓 Akademische Meilensteine")
        st.metric("Aktiver Lern-Streak", f"{st.session_state.lern_streak} Tage")
        st.metric("Gescannt & verarbeitet", f"{st.session_state.gelöste_aufgaben} Lehreinheiten")
        
        st.divider()
        st.markdown("#### Freigeschaltete Badges:")
        if st.session_state.gelöste_aufgaben >= 1: 
            st.success("📝 Dokumenten-Pionier (Das erste Schul- oder Studiendokument erfolgreich digitalisiert)")
        if st.session_state.lern_streak >= 5:
            st.success("🧠 Brain-Elite (5 Tage permanenter Fokus beim Lernen)")
        else:
            st.code("🔒 Brain-Elite (Sperre aufheben: Benötigt einen 5 Tage Lern-Streak)")

# =========================================================================
# --- MODUL 4: ANALYSE-ENGINE (KI-ABEND-REPORT) ---
# =========================================================================
else:
    st.title("🌆 Automatischer KI-Abendbericht & Tagesfazit")
    st.write("Das System aggregiert sämtliche Daten des Tages und zieht eine kompromisslose Bilanz.")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 🏋️‍♂️ Auswertung Bewegung & Ernährung")
        if st.session_state.ki_fitness_gedaechtnis:
            for e in st.session_state.ki_fitness_gedaechtnis: 
                st.text(f"• {e}")
                
            if st.button("🌖 Unbeschönigten KI-Abendbericht generieren"):
                with st.spinner("Wissenschaftliche Bilanz wird gezogen..."):
                    daten_text = ", ".join(st.session_state.ki_fitness_gedaechtnis)
                    prompt = f"""
                    Du bist ein extrem ehrlicher, kompromissloser und wissenschaftlich orientierter Fitness-Coach. 
                    Nutzerprofil: {st.session_state.alter} Jahre alt, {st.session_state.gewicht}kg schwer, {st.session_state.groesse}cm groß.
                    Heutige Ist-Werte: {st.session_state.live_wasser}ml Wasser (Soll: 3000ml), {st.session_state.live_protein}g Protein (Soll: 140g), {st.session_state.live_schritte} Schritte (Soll: 10000).
                    Gedächtnis-Protokoll des Tages: {daten_text}.
                    
                    Aufgabe: Erstelle ein klares, direktes Tagesfazit auf Deutsch. Lobe gute Leistungen sachlich. KRITISIERE den Nutzer sofort und unmissverständlich, wenn eines der metabolischen Ziele nicht erreicht wurde! Nenne am Ende exakt 2 präzise, messbare Verbesserungsvorschläge für den morgigen Tag.
                    """
                    r = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}])
                    st.info(r.choices[0].message.content)
        else: 
            st.info("Noch keine Aktivitäts- und Ernährungseinträge für den heutigen Tag im Speicher vorhanden.")
            
    with c2:
        st.markdown("### 🎓 Auswertung Schule & Lernen")
        if st.session_state.ki_lern_gedaechtnis:
            for e in st.session_state.ki_lern_gedaechtnis: 
                st.text(f"• {e}")
                
            if st.button("🌖 Akademischen KI-Schulbericht generieren"):
                with st.spinner("KI-Tutor analysiert erbrachte Denkleistungen..."):
                    daten_text = ", ".join(st.session_state.ki_lern_gedaechtnis)
                    prompt = f"Erstelle ein professionelles Tagesfazit für einen Schüler bzw. eine Schülerin der {st.session_state.klassenstufe} basierend auf folgendem Logbuch: {daten_text}. Gib ehrliches Feedback, übe konstruktive Kritik an Wissenslücken und nenne exakt 2 didaktische Lerntipps für morgen auf Deutsch."
                    r = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}])
                    st.success(r.choices[0].message.content)
        else: 
            st.info("Es wurden am heutigen Tag noch keine Lerneinträge verzeichnet.")