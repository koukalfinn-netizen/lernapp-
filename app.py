import streamlit as st
from PIL import Image
from openai import OpenAI
import os
import base64
import io

# 1. HARDCODETER API KEY
FESTER_API_KEY = "sk-proj-VC0P5MOPeotJSISZshXYEaePtQYCyuqYNuMQGj9N1I-eLkdjwr4lNV-tSKjKSbsJ"

st.set_page_config(page_title="iPad OS Workspace", page_icon="📲", layout="wide")

# --- SPEICHER FÜR STATS UND PROFILE INITIALISIEREN ---
if "gewicht" not in st.session_state: st.session_state.gewicht = 70
if "groesse" not in st.session_state: st.session_state.groesse = 175
if "alter" not in st.session_state: st.session_state.alter = 16
if "klassenstufe" not in st.session_state: st.session_state.klassenstufe = "10. Klasse"

# Belohnungen & Streaks
if "fit_streak" not in st.session_state: st.session_state.fit_streak = 3
if "gelöste_aufgaben" not in st.session_state: st.session_state.gelöste_aufgaben = 0
if "bg_design" not in st.session_state: st.session_state.bg_design = "Standard Grau"
if "icon_ordnung" not in st.session_state: st.session_state.icon_ordnung = ["Status-Kacheln", "Ernährungs-Raster", "Nährwert-Tabelle", "Scanner", "Live-Chat"]

# Eingabe-Speicher für das Ernährungs-Raster
if "food_diary" not in st.session_state:
    st.session_state.food_diary = {
        "Frühstück": {"Name": "", "Kalorien": 0, "Protein": 0},
        "Mittagessen": {"Name": "", "Kalorien": 0, "Protein": 0},
        "Abendessen": {"Name": "", "Kalorien": 0, "Protein": 0},
        "Snacks / Shakes": {"Name": "", "Kalorien": 0, "Protein": 0}
    }

# Chat-Speicher
if "chat_history_fitness" not in st.session_state: st.session_state.chat_history_fitness = []
if "chat_history_lernen" not in st.session_state: st.session_state.chat_history_lernen = []

# --- HINTERGRUND-STYLES (APPLE HOMESCREEN VIBES) ---
if st.session_state.bg_design == "Dark Carbon":
    st.markdown("<style>.stApp { background-color: #121212; color: white; }</style>", unsafe_allow_html=True)
elif st.session_state.bg_design == "Gym Vibe (Neon)":
    st.markdown("<style>.stApp { background-color: #0d1b2a; color: #e0e1dd; }</style>", unsafe_allow_html=True)
elif st.session_state.bg_design == "Campus Hell":
    st.markdown("<style>.stApp { background-color: #f8f9fa; color: #212529; }</style>", unsafe_allow_html=True)

# --- SIDEBAR: KONTROLLZENTRUM ---
with st.sidebar:
    st.title("📲 iPad Control Center")
    modus = st.selectbox("App auswählen:", ["🏋️‍♂️ ATHLETE PRO", "🎓 CAMPUS EXPERT", "🏆 MEILENSTEINE & POKALE"])
    
    st.divider()
    st.markdown("### ⚙️ Profil-Einstellungen (Änderbar)")
    if modus == "🏋️‍♂️ ATHLETE PRO":
        st.session_state.alter = st.number_input("Alter", value=st.session_state.alter)
        st.session_state.gewicht = st.number_input("Gewicht (kg)", value=st.session_state.gewicht)
        st.session_state.groesse = st.number_input("Größe (cm)", value=st.session_state.groesse)
    else:
        st.session_state.klassenstufe = st.selectbox("Klassenstufe:", [f"{i}. Klasse" for i in range(5, 13)])
        
    st.divider()
    st.markdown("### 🎨 Homescreen anpassen")
    st.session_state.bg_design = st.radio("Hintergrundbild / Thema:", ["Standard Grau", "Dark Carbon", "Gym Vibe (Neon)", "Campus Hell"])
    
    st.markdown("🔄 **Widgets verschieben:**")
    reihenfolge = st.multiselect(
        "Reihenfolge der Dashboard-Elemente:", 
        ["Status-Kacheln", "Ernährungs-Raster", "Nährwert-Tabelle", "Scanner", "Live-Chat"], 
        default=st.session_state.icon_ordnung
    )
    if len(reihenfolge) >= 3:
        st.session_state.icon_ordnung = reihenfolge

# --- BEREICH 1: FITNESS ---
if modus == "🏋️‍♂️ ATHLETE PRO":
    st.title("🏋️‍♂️ ATHLETE PRO Dashboard")
    st.caption(f"Profil aktiv: {st.session_state.alter} Jahre | {st.session_state.gewicht}kg | {st.session_state.groesse}cm")
    
    # Widgets dynamisch nach User-Reihenfolge anzeigen
    for widget in st.session_state.icon_ordnung:
        if widget == "Status-Kacheln":
            st.markdown("#### 📊 Live-Widgets")
            k1, k2, k3 = st.columns(3)
            k1.metric("🔥 Aktueller Streak", f"{st.session_state.fit_streak} Tage", "Meilenstein nah!")
            k2.metric("💧 Wasser-Tracker", "1.2 / 3.0L")
            if k3.button("💪 Workout für heute loggen (+1 Streak Day)"):
                st.session_state.fit_streak += 1
                st.toast("🔥 Streak erhöht! Schau in dein Pokal-Menü!")
                st.rerun()
                
        elif widget == "Ernährungs-Raster":
            st.divider()
            st.markdown("### 🍳 Dein Tages-Ernährungsplan (Eingabe-Raster)")
            st.caption("Trage hier ein, was du heute gegessen hast. Die App rechnet deine Gesamtsumme aus!")
            
            total_kcal = 0
            total_protein = 0
            
            # Raster-Layout für Mahlzeiten erzeugen
            for mahlzeit, daten in st.session_state.food_diary.items():
                c_name, c_kcal, c_protein = st.columns([2, 1, 1])
                with c_name:
                    st.session_state.food_diary[mahlzeit]["Name"] = st.text_input(f"{mahlzeit} (Was hast du gegessen?)", value=daten["Name"], key=f"name_{mahlzeit}")
                with c_kcal:
                    st.session_state.food_diary[mahlzeit]["Kalorien"] = st.number_input("Kalorien (kcal)", value=daten["Kalorien"], step=10, key=f"kcal_{mahlzeit}")
                with c_protein:
                    st.session_state.food_diary[mahlzeit]["Protein"] = st.number_input("Protein (g)", value=daten["Protein"], step=1, key=f"prot_{mahlzeit}")
                
                # Werte aufsummieren, wenn etwas eingetragen ist
                if daten["Name"]:
                    total_kcal += st.session_state.food_diary[mahlzeit]["Kalorien"]
                    total_protein += st.session_state.food_diary[mahlzeit]["Protein"]
            
            # Auswertung des Rasters
            st.markdown("#### 📈 Heutige Tagesbilanz:")
            res_c1, res_c2 = st.columns(2)
            res_c1.metric("🔥 Gesamtkalorien", f"{total_kcal} kcal")
            res_c2.metric("🍗 Gesamtprotein", f"{total_protein} g Eiweiß")
            
        elif widget == "Nährwert-Tabelle":
            st.divider()
            st.markdown("### 📋 Fitness-Lebensmittel & Nährwerte (pro 100g)")
            st.caption("Nutze diese Liste, um die Werte für dein Ernährungs-Raster oben schnell nachzuschlagen.")
            
            # Übersichtliches Raster für Nährwerte
            naehrwerte_liste = [
                {"Lebensmittel": "🍗 Hähnchenbrustfilet", "Kalorien": "110 kcal", "Protein": "23g", "Kohlenhydrate": "0g", "Fett": "1g"},
                {"Lebensmittel": "🥣 Haferflocken", "Kalorien": "370 kcal", "Protein": "13g", "Kohlenhydrate": "59g", "Fett": "7g"},
                {"Lebensmittel": "🥛 Magerquark", "Kalorien": "68 kcal", "Protein": "12g", "Kohlenhydrate": "4g", "Fett": "0.2g"},
                {"Lebensmittel": "🍚 Basmati-Reis (ungekocht)", "Kalorien": "350 kcal", "Protein": "8g", "Kohlenhydrate": "77g", "Fett": "1g"},
                {"Lebensmittel": "🥚 Ei (1 Stück / ca. 55g)", "Kalorien": "80 kcal", "Protein": "7g", "Kohlenhydrate": "0.5g", "Fett": "6g"},
                {"Lebensmittel": "🐟 Lachsfilet", "Kalorien": "200 kcal", "Protein": "20g", "Kohlenhydrate": "0g", "Fett": "13g"},
                {"Lebensmittel": "🍌 Banane (1 Stück)", "Kalorien": "95 kcal", "Protein": "1g", "Kohlenhydrate": "22g", "Fett": "0.3g"},
            ]
            st.table(naehrwerte_liste)

        elif widget == "Scanner":
            st.divider()
            st.markdown("### 📸 Personalisierter KI-Scanner")
            fit_option = st.selectbox("Scan-Typ:", ["Trainingsplan (auf mein Gewicht angepasst)", "Kalorien-Check", "Technik-Fehleranalyse"])
            uploaded_file = st.file_uploader("Foto hochladen...", type=["jpg", "png", "jpeg"], key="fit_up")
            if uploaded_file and st.button("🚀 Analyse starten"):
                client = OpenAI(api_key=FESTER_API_KEY)
                with st.spinner("KI berechnet Werte..."):
                    img_str = base64.b64encode(uploaded_file.getvalue()).decode()
                    prompt = f"Nutzerdaten: {st.session_state.alter}J, {st.session_state.gewicht}kg, {st.session_state.groesse}cm. Analysiere das Bild für '{fit_option}' exakt passend zu diesen Körperdaten auf Deutsch."
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}}]}],
                    )
                    st.info(response.choices[0].message.content)
                    
        elif widget == "Live-Chat":
            st.divider()
            st.markdown("### 💬 Chat mit deinem Coach")
            for msg in st.session_state.chat_history_fitness:
                with st.chat_message(msg["role"]): st.write(msg["content"])
            u_input = st.chat_input("Frag den Coach...")
            if u_input:
                st.session_state.chat_history_fitness.append({"role": "user", "content": u_input})
                client = OpenAI(api_key=FESTER_API_KEY)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "system", "content": f"Du bist ein Fitness-Coach. Beachte die Nutzerdaten: {st.session_state.gewicht}kg, {st.session_state.alter}Jahre."}] + st.session_state.chat_history_fitness[-6:]
                )
                st.session_state.chat_history_fitness.append({"role": "assistant", "content": response.choices[0].message.content})
                st.rerun()

# --- BEREICH 2: SCHULE ---
elif modus == "🎓 CAMPUS EXPERT":
    st.title("🎓 CAMPUS EXPERT")
    st.caption(f"Optimiert für: {st.session_state.klassenstufe}")
    
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("### 📸 Aufgaben- & Dokumenten-Scanner")
        lern_option = st.selectbox("Format:", ["Übersichtlicher Lernzettel", "Probearbeit mit Lösungen", "Interaktives Quiz"])
        uploaded_l = st.file_uploader("Heft- oder Buchseite fotografieren...", type=["jpg", "png", "jpeg"])
        if uploaded_l and st.button("📝 Generieren"):
            client = OpenAI(api_key=FESTER_API_KEY)
            with st.spinner("Lese Text..."):
                img_str = base64.b64encode(uploaded_l.getvalue()).decode()
                prompt = f"Erstelle ein(e) '{lern_option}' basierend auf dem Bild. Niveau: {st.session_state.klassenstufe}. Sprache: Deutsch."
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}}]}],
                )
                st.write(response.choices[0].message.content)
                st.session_state.gelöste_aufgaben += 1
                st.toast("🎓 Aufgabe erledigt! Meilenstein-Fortschritt gesichert!")

    with col_r:
        st.markdown("### 💬 Chat mit deinem Tutor")
        for msg in st.session_state.chat_history_lernen:
            with st.chat_message(msg["role"]): st.write(msg["content"])
        u_input_l = st.chat_input("Frag den Lehrer...")
        if u_input_l:
            st.session_state.chat_history_lernen.append({"role": "user", "content": u_input_l})
            client = OpenAI(api_key=FESTER_API_KEY)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": f"Du bist ein geduldiger Lehrer. Erkläre perfekt für die {st.session_state.klassenstufe}."}] + st.session_state.chat_history_lernen[-6:]
            )
            st.session_state.chat_history_lernen.append({"role": "assistant", "content": response.choices[0].message.content})
            st.rerun()

# --- BEREICH 3: BELOHNUNGSSYSTEM ---
else:
    st.title("🏆 Dein Trophäenschrank & Erfolge")
    st.write("Hier siehst du alle Meilensteine, die du durch dein Training und Lernen freigeschaltet hast!")
    
    st.subheader("🏋️‍♂️ Fitness Meilensteine")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 🏃‍♂️ Streak-Pokale")
        if st.session_state.fit_streak >= 3: st.success("🥉 Bronze-Athlet (3 Tage Streak aktiv!)")
        else: st.code("🔒 Bronze-Athlet (Benötigt 3 Tage Streak)")
        
        if st.session_state.fit_streak >= 7: st.success("🥈 Silber-Champ (7 Tage Streak erreicht!)")
        else: st.code("🔒 Silber-Champ (Benötigt 7 Tage Streak)")
        
        if st.session_state.fit_streak >= 30: st.success("🥇 Gold-Legende (30 Tage durchgezogen!)")
        else: st.code("🔒 Gold-Legende (Benötigt 30 Tage Streak)")

    st.subheader("🎓 Schul & Campus Meilensteine")
    with c2:
        st.markdown("#### 🧠 Lern-Zertifikate")
        st.metric("Erledigte Scans / Quizzes", f"{st.session_state.gelöste_aufgaben} Aufgaben")
        
        if st.session_state.gelöste_aufgaben >= 1: st.success("📝 Erster Schritt (1 Aufgabe generiert)")
        else: st.code("🔒 Erster Schritt (Scanne 1 Schul-Foto)")
        
        if st.session_state.gelöste_aufgaben >= 5: st.success("⚡ Quiz-Meister (5 Aufgaben geschafft!)")
        else: st.code("🔒 Quiz-Meister (Scanne 5 Schul-Fotos)")