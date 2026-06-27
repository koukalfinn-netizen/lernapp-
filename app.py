import streamlit as st
from PIL import Image
from openai import OpenAI
import os
import base64
import io

# 1. HARDCODETER API KEY
FESTER_API_KEY = "sk-proj-VC0P5MOPeotJSISZshXYEaePtQYCyuqYNuMQGj9N1I-eLkdjwr4lNV-tSKjKSbsJ"

st.set_page_config(page_title="iPad Ultimate Workspace", page_icon="📲", layout="wide")

# --- SPEICHER FÜR STATS UND PROFILE INITIALISIEREN ---
if "gewicht" not in st.session_state: st.session_state.gewicht = 70
if "groesse" not in st.session_state: st.session_state.groesse = 175
if "alter" not in st.session_state: st.session_state.alter = 16
if "klassenstufe" not in st.session_state: st.session_state.klassenstufe = "10. Klasse"

# Belohnungen & Streaks
if "fit_streak" not in st.session_state: st.session_state.fit_streak = 3
if "gelöste_aufgaben" not in st.session_state: st.session_state.gelöste_aufgaben = 0
if "bg_color_hex" not in st.session_state: st.session_state.bg_color_hex = "#1e1e1e"
if "icon_ordnung" not in st.session_state: st.session_state.icon_ordnung = ["📊 Status-Kacheln", "🥤 All-in-One Ernährungs-Tracker", "📋 Nährwert-Nachschlage-Tabelle", "📸 KI-Scanner", "💬 Live-Chat"]

# All-in-One Ernährungs-Speicher (Jetzt als flache Liste für bis zu 6 Einträge ohne Mahlzeiten-Trennung)
if "all_in_one_food" not in st.session_state:
    st.session_state.all_in_one_food = [
        {"Name": "", "Kalorien": 0, "Protein": 0} for _ in range(6)
    ]

# Chat-Speicher
if "chat_history_fitness" not in st.session_state: st.session_state.chat_history_fitness = []
if "chat_history_lernen" not in st.session_state: st.session_state.chat_history_lernen = []

# --- FARB-DEFINITIONEN (Klassisch, Neon & Mischfarben) ---
FARBEN_DICTIONARY = {
    # Klassisch
    "🔴 Klassisch Rot": "#8b0000",
    "🟢 Klassisch Grün": "#1b4d3e",
    "🔵 Klassisch Blau": "#0f2027",
    "⚪ Standard Grau": "#1e1e1e",
    "⚫ Deep Black": "#000000",
    # Neon
    "🧪 Neon Grün": "#39ff14",
    "🔮 Neon Violett": "#9d00ff",
    "🔥 Neon Orange": "#ff5f1f",
    "🐬 Neon Türkis": "#00f5ff",
    "🛍️ Neon Pink": "#ff1493",
    "⚡ Cyberpunk Gelb": "#ccff00",
    # Mischfarben
    "🍵 Mintel-Grau (Salbei & Grau)": "#708238",
    "🍇 Pflaumen-Violett (Blau & Rot)": "#4a0e4e",
    "🍓 Erdbeer-Smoothie (Rot & Weiß)": "#ff6b8b",
    "🪸 Korallen-Orange (Rot & Gelb)": "#ff7f50",
    "🌊 Ozean-Blaugrün (Blau & Grün)": "#008080"
}

# Farb-Injektion für komplett einfarbigen Hintergrund
gewählte_farbe = st.session_state.bg_color_hex
st.markdown(f"""
    <style>
    .stApp {{
        background-color: {gewählte_farbe} !important;
        color: white !important;
    }}
    h1, h2, h3, h4, h5, h6, p, span, label {{
        color: white !important;
    }}
    .stButton>button {{
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }}
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR: KONTROLLZENTRUM ---
with st.sidebar:
    st.title("📲 iPad Control Center")
    st.caption("Konfiguriere dein System")
    modus = st.selectbox("App auswählen:", ["🏋️‍♂️ ATHLETE PRO", "🎓 CAMPUS EXPERT", "🏆 MEILENSTEINE & POKALE"])
    
    st.divider()
    st.markdown("### ⚙️ Profil-Einstellungen")
    if modus == "🏋️‍♂️ ATHLETE PRO":
        st.session_state.alter = st.number_input("Alter", value=st.session_state.alter)
        st.session_state.gewicht = st.number_input("Gewicht (kg)", value=st.session_state.gewicht)
        st.session_state.groesse = st.number_input("Größe (cm)", value=st.session_state.groesse)
    else:
        st.session_state.klassenstufe = st.selectbox("Klassenstufe:", [f"{i}. Klasse" for i in range(5, 13)])
        
    st.divider()
    st.markdown("### 🎨 Einfarbigen Hintergrund wählen")
    farb_name = st.selectbox("Wähle ein Farbthema aus:", list(FARBEN_DICTIONARY.keys()))
    st.session_state.bg_color_hex = FARBEN_DICTIONARY[farb_name]
    
    st.markdown("🔄 **Widgets auf dem Homescreen verschieben:**")
    reihenfolge = st.multiselect(
        "Reihenfolge der Elemente:", 
        ["📊 Status-Kacheln", "🥤 All-in-One Ernährungs-Tracker", "📋 Nährwert-Nachschlage-Tabelle", "📸 KI-Scanner", "💬 Live-Chat"], 
        default=st.session_state.icon_ordnung
    )
    if len(reihenfolge) >= 3:
        st.session_state.icon_ordnung = reihenfolge

# --- BEREICH 1: FITNESS ---
if modus == "🏋️‍♂️ ATHLETE PRO":
    st.title("🏋️‍♂️ ATHLETE PRO Dashboard")
    st.caption(f"🧬 Profil aktiv: {st.session_state.alter} Jahre | {st.session_state.gewicht}kg | {st.session_state.groesse}cm")
    
    # Widgets dynamisch nach User-Reihenfolge anzeigen
    for widget in st.session_state.icon_ordnung:
        if widget == "📊 Status-Kacheln":
            st.markdown("#### 📊 Live-Statuswerte")
            k1, k2, k3 = st.columns(3)
            k1.metric("🔥 Workout Streak", f"{st.session_state.fit_streak} Tage", "Go for Gold!")
            k2.metric("💧 Hydration", "1.5 / 3.5 Liter")
            if k3.button("🛹 Heutigen Sporttag loggen (+1 Streak)"):
                st.session_state.fit_streak += 1
                st.toast("🔥 Streak verlängert!")
                st.rerun()
                
        elif widget == "🥤 All-in-One Ernährungs-Tracker":
            st.divider()
            st.markdown("### 🥤 All-in-One Ernährungs- & Getränkeliste")
            st.caption("Egal ob Frühstück, Snack oder Post-Workout-Shake: Trage hier einfach alles nacheinander ein.")
            
            total_kcal = 0
            total_protein = 0
            
            # Ein einziges Raster ohne Mahlzeitenunterteilung
            for i in range(6):
                c_name, c_kcal, c_protein = st.columns([2, 1, 1])
                with c_name:
                    st.session_state.all_in_one_food[i]["Name"] = st.text_input(f"Eintrag {i+1} (z.B. Proteinshake, Banane, Pizza...)", value=st.session_state.all_in_one_food[i]["Name"], key=f"aio_name_{i}")
                with c_kcal:
                    st.session_state.all_in_one_food[i]["Kalorien"] = st.number_input("Kalorien (kcal)", value=st.session_state.all_in_one_food[i]["Kalorien"], step=10, key=f"aio_kcal_{i}")
                with c_protein:
                    st.session_state.all_in_one_food[i]["Protein"] = st.number_input("Protein (g)", value=st.session_state.all_in_one_food[i]["Protein"], step=1, key=f"aio_prot_{i}")
                
                if st.session_state.all_in_one_food[i]["Name"]:
                    total_kcal += st.session_state.all_in_one_food[i]["Kalorien"]
                    total_protein += st.session_state.all_in_one_food[i]["Protein"]
            
            st.markdown("#### 🎯 Berechnete Tagesbilanz:")
            res_c1, res_c2 = st.columns(2)
            res_c1.metric("🔥 Gesamte Kalorienaufnahme", f"{total_kcal} kcal")
            res_c2.metric("🍗 Gesamtes Protein (Eiweiß)", f"{total_protein} g")
            
        elif widget == "📋 Nährwert-Nachschlage-Tabelle":
            st.divider()
            st.markdown("### 📋 Nährwert-Datenbank (pro 100g)")
            st.caption("Nutz diese Werte, um sie oben direkt in deinen Tracker einzutragen.")
            
            naehrwerte_liste = [
                {"Lebensmittel / Getränk": "🍗 Hähnchenbrust", "Kalorien": "110 kcal", "Protein": "23g", "Kohlenhydrate": "0g", "Fett": "1g"},
                {"Lebensmittel / Getränk": "🥣 Haferflocken", "Kalorien": "370 kcal", "Protein": "13g", "Kohlenhydrate": "59g", "Fett": "7g"},
                {"Lebensmittel / Getränk": "🥛 Magerquark", "Kalorien": "68 kcal", "Protein": "12g", "Kohlenhydrate": "4g", "Fett": "0.2g"},
                {"Lebensmittel / Getränk": "🍚 Reis (ungekocht)", "Kalorien": "350 kcal", "Protein": "8g", "Kohlenhydrate": "77g", "Fett": "1g"},
                {"Lebensmittel / Getränk": "🥚 Vollei (1 Stück)", "Kalorien": "80 kcal", "Protein": "7g", "Kohlenhydrate": "0.5g", "Fett": "6g"},
                {"Lebensmittel / Getränk": "🥤 Whey Protein Shake", "Kalorien": "120 kcal", "Protein": "24g", "Kohlenhydrate": "2g", "Fett": "1.5g"},
                {"Lebensmittel / Getränk": "🍌 Banane (1 Stück)", "Kalorien": "95 kcal", "Protein": "1g", "Kohlenhydrate": "22g", "Fett": "0.3g"},
            ]
            st.table(naehrwerte_liste)

        elif widget == "📸 KI-Scanner":
            st.divider()
            st.markdown("### 📸 Personalisierter KI-Fitness-Scanner")
            fit_option = st.selectbox("Was scannst du?", ["Trainingsplan (auf mein Gewicht angepasst)", "Kalorien-Check von Fotos", "Technik-Fehleranalyse"])
            uploaded_file = st.file_uploader("Foto knipsen...", type=["jpg", "png", "jpeg"], key="fit_up")
            if uploaded_file and st.button("🚀 Foto wissenschaftlich auswerten"):
                client = OpenAI(api_key=FESTER_API_KEY)
                with st.spinner("Dein digitaler Trainer rechnet..."):
                    img_str = base64.b64encode(uploaded_file.getvalue()).decode()
                    prompt = f"Nutzerdaten: {st.session_state.alter}J, {st.session_state.gewicht}kg, {st.session_state.groesse}cm. Analysiere das Bild für '{fit_option}' exakt passend zu diesen Körperdaten auf Deutsch."
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}}]}],
                    )
                    st.info(response.choices[0].message.content)
                    
        elif widget == "💬 Live-Chat":
            st.divider()
            st.markdown("### 💬 Chat mit deinem Personal Trainer")
            for msg in st.session_state.chat_history_fitness:
                with st.chat_message(msg["role"]): st.write(msg["content"])
            u_input = st.chat_input("Frage stellen...")
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
    st.caption(f"🎯 Niveau eingestellt auf: {st.session_state.klassenstufe}")
    
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("### 📸 Aufgaben- & Dokumenten-Scanner")
        lern_option = st.selectbox("Format:", ["Übersichtlicher Lernzettel", "Probearbeit mit Lösungen", "Interaktives Quiz"])
        uploaded_l = st.file_uploader("Heft- oder Buchseite fotografieren...", type=["jpg", "png", "jpeg"])
        if uploaded_l and st.button("🧬 Dokumentation generieren"):
            client = OpenAI(api_key=FESTER_API_KEY)
            with st.spinner("KI wertet Schul-Inhalt aus..."):
                img_str = base64.b64encode(uploaded_l.getvalue()).decode()
                prompt = f"Erstelle ein(e) '{lern_option}' basierend auf dem Bild. Niveau: {st.session_state.klassenstufe}. Sprache: Deutsch."
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}}]}],
                )
                st.write(response.choices[0].message.content)
                st.session_state.gelöste_aufgaben += 1
                st.toast("🎓 Aufgabe erledigt! Meilenstein gesichert!")

    with col_r:
        st.markdown("### 💬 Chat mit deinem KI-Tutor")
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
    st.title("🏆 Dein Trophäenschrank & Meilensteine")
    st.write("Verfolge deine Erfolge im Sport und in der Schule!")
    
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