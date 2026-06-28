import streamlit as st
import datetime
import time
import random

# --- SEITENKONFIGURATION ---
st.set_page_config(page_title="AI Learn & Fit Hub", page_icon="⚡", layout="wide")

# --- SITZUNGSSPEICHER (SESSION STATE) ---
TRACKERS = ["chat_history", "consumed_food", "medals"]
for tracker in TRACKERS:
    if tracker not in st.session_state:
        st.session_state[tracker] = []

USER_PROPERTIES = {
    "streak_fitness": 0, 
    "streak_lernen": 0, 
    "klassenstufe": "Klasse 5", 
    "alter": 16, 
    "groesse": 170, 
    "gewicht": 65, 
    "last_activity": datetime.date.today()
}
for key, value in USER_PROPERTIES.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --- SIDEBAR: DESIGN & FARBEN ---
st.sidebar.title("🎨 Design & Farben")
bg_color = st.sidebar.color_picker("Dashboard-Farbe", "#121212")
text_color = st.sidebar.color_picker("Text-Farbe", "#FFFFFF")
accent_color = "#2ECC71" 

# Dynamisches CSS basierend auf deinen Farbreglern
st.markdown(f"""
    <style>
    html, body, [data-testid="stSidebar"], .stApp {{
        background-color: {bg_color} !important;
        color: {text_color} !important;
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
    }}
    h1, h2, h3, h4, h5, h6 {{
        color: {text_color} !important;
    }}
    .stat-box {{
        background-color: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid {accent_color};
        margin-bottom: 15px;
    }}
    .medal-card {{
        background-color: rgba(255, 215, 0, 0.1);
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #FFD700;
        margin: 10px 0px;
        font-size: 1.1rem;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: NAVIGATION ---
st.sidebar.write("---")
st.sidebar.title("🎛️ Navigation")
app_mode = st.sidebar.selectbox("Bereich auswählen", [
    "📚 Lernen & Schule", 
    "💪 Fitness & Ernährung", 
    "🏆 Meine Medaillen & Erfolge", 
    "📅 Abendliche Tageszusammenfassung"
])

# --- KI BACKEND (SIMULIERTER DENKPROZESS - KEYLESS) ---
def execute_background_thought(mode, topic=""):
    with st.spinner("🧠 Analysiere Profildaten... Generiere optimales Feedback..."):
        time.sleep(random.uniform(1.5, 2.5)) 
    
    if mode == "lernzettel":
        return f"### 📝 KI-Lernunterlage: {topic}\n\n*Optimiert für: {st.session_state.klassenstufe}*\n\n1. **Kernkonzept:** Grundlegende Definition und Relevanz für deine nächste Arbeit.\n2. **Wichtige Fakten:** Achte in Prüfungen besonders auf die Zusammenhänge.\n3. **Coach-Tipp:** Schreib dir diese Kernpunkte einmal handschriftlich auf!"
        
    elif mode == "quiz":
        return f"### 🧪 KI-Wissenscheck: {topic}\n\n*Niveau: {st.session_state.klassenstufe}*\n\n* **Frage 1:** Was ist die Hauptursache für die Prozesse hinter {topic}?\n* **Frage 2:** Wie beeinflusst dieses Thema andere Bereiche im Fach?\n* **Frage 3:** Erkläre das Prinzip in einem kurzen Satz."
        
    elif mode == "essen_feedback":
        healthy = ["salat", "wasser", "hähnchen", "apfel", "quark", "gemüse", "fisch", "reis", "ei", "banane"]
        unhealthy = ["cola", "pizza", "burger", "chips", "schokolade", "red bull", "döner", "fanta", "sprite"]
        
        text_lower = topic.lower()
        if any(x in text_lower for x in healthy):
            return f"🟢 **Lob vom Coach:** Überragende Wahl! '{topic}' liefert perfekte Nährstoffe für deinen Körper ({st.session_state.gewicht}kg). Das gibt dir Power ohne Crash!"
        elif any(x in text_lower for x in unhealthy):
            return f"🔴 **Kritik vom Coach:** Aufgepasst! '{topic}' liefert dir fast nur leere Kalorien und Zucker. Das blockiert deinen Fokus beim Lernen und wirft dich im Training zurück."
        else:
            return f"🟡 **Hinweis vom Coach:** '{topic}' ist als neutraler Snack okay. Achte darauf, über den Tag genug Proteine einzubauen."

    elif mode == "tages_fazit":
        mahlzeiten = ", ".join(st.session_state.consumed_food) if st.session_state.consumed_food else "Keine Mahlzeiten eingetragen"
        
        if st.session_state.streak_lernen > 0 and st.session_state.streak_fitness > 0:
            status = "🔥 Absoluter Champion-Tag! Du hast für Kopf und Körper voll abgeliefert!"
        elif st.session_state.streak_lernen == 0 and st.session_state.streak_fitness == 0:
            status = "⚠️ Faulheits-Alarm: Heute steht alles auf Null. Morgen erwarte ich deutlich mehr Disziplin!"
        else:
            status = "⚖️ Halbe Kraft: Ein Bereich lief gut, der andere wurde vernachlässigt. Such die Balance!"

        return f"### 📋 Dein ehrliches Tages-Fazit\n\n* **Status:** {status}\n* **Klassenstufe:** {st.session_state.klassenstufe}\n* **Lern-Streak:** {st.session_state.streak_lernen} Tage\n* **Fitness-Streak:** {st.session_state.streak_fitness} Tage\n* **Ernährung heute:** {mahlzeiten}\n\n*🎯 Coach-Spruch für morgen:* Disziplin bedeutet, das zu tun, was getan werden muss, auch wenn man keine Lust hat!"

# Tracker Reset Logik bei Inaktivität
if (datetime.date.today() - st.session_state.last_activity).days >= 2:
    st.session_state.streak_fitness = 0
    st.session_state.streak_lernen = 0

# =====================================================================
# MODUS 1: LERNEN & SCHULE
# =====================================================================
if app_mode == "📚 Lernen & Schule":
    st.title("📚 AI Lern-Zentrum")
    
    klassenstufen = [f"Klasse {i}" for i in range(1, 13)]
    st.session_state.klassenstufe = st.selectbox("Klassenstufe wählen", klassenstufen, index=klassenstufen.index(st.session_state.klassenstufe))
    
    st.write("")
    thema = st.text_input("Gib dein Thema ein (z.B. 'Fotosynthese')")
    erstellungs_typ = st.radio("Was soll im Hintergrund berechnet werden?", ["Lernzettel", "Quiz"])
    
    if st.button("Generieren") and thema:
        antwort = execute_background_thought(erstellungs_typ.lower(), thema)
        st.markdown(antwort)

    st.write("---")
    st.subheader("⏳ Lern-Tracker")
    st.markdown(f"<div class='stat-box'>🔥 Aktueller Lern-Streak: <b>{st.session_state.streak_lernen} Tage</b></div>", unsafe_allow_html=True)
    
    if st.file_uploader("Lade ein 5-Minuten-Lernvideo hoch", type=["mp4", "mov"], key="learn_vid"):
        if st.button("Video bestätigen & Tracker +1"):
            st.session_state.streak_lernen += 1
            st.session_state.last_activity = datetime.date.today()
            if st.session_state.streak_lernen == 1:
                st.session_state.medals.append("🥇 Erster Schritt (Lernen) - Erstes Video eingereicht!")
            st.success("Erfolg verbucht!")
            st.rerun()

# =====================================================================
# MODUS 2: FITNESS & ERNÄHRUNG
# =====================================================================
elif app_mode == "💪 Fitness & Ernährung":
    st.title("💪 AI Fitness & Ernährungs-Coach")
    
    col1, col2, col3 = st.columns(3)
    st.session_state.alter = col1.number_input("Alter", min_value=10, value=st.session_state.alter)
    st.session_state.groesse = col2.number_input("Größe (in cm)", min_value=100, value=st.session_state.groesse)
    st.session_state.gewicht = col3.number_input("Gewicht (in kg)", min_value=30, value=st.session_state.gewicht)
    
    st.write("---")
    st.subheader("🍎 Ernährungs-Tracker mit Live-Feedback")
    
    with st.form(key='food_form', clear_on_submit=True):
        speise = st.text_input("Was hast du gegessen/getrunken?")
        submit_food = st.form_submit_button("Hinzufügen & Auswerten")
        
        if submit_food and speise:
            st.session_state.consumed_food.append(speise)
            st.session_state["latest_feedback"] = execute_background_thought("essen_feedback", speise)
            st.rerun()

    if "latest_feedback" in st.session_state:
        st.markdown(st.session_state["latest_feedback"])

    if st.session_state.consumed_food:
        st.write("**Heutige Mahlzeiten:**")
        for item in st.session_state.consumed_food:
            st.write(f"• {item}")
            
    st.write("---")
    st.subheader("⏳ Fitness-Tracker")
    st.markdown(f"<div class='stat-box'>🔥 Aktueller Fitness-Streak: <b>{st.session_state.streak_fitness} Tage</b></div>", unsafe_allow_html=True)
    
    if st.file_uploader("Lade ein Workout-Video hoch", type=["mp4", "mov"], key="fit_vid"):
        if st.button("Workout bestätigen & Tracker +1"):
            st.session_state.streak_fitness += 1
            st.session_state.last_activity = datetime.date.today()
            if st.session_state.streak_fitness == 1:
                st.session_state.medals.append("🏅 Erste Trainingseinheit - Sportstreak gestartet!")
            st.success("Stark! Tracker erhöht.")
            st.rerun()

# =====================================================================
# MODUS 3: MEDAILLEN
# =====================================================================
elif app_mode == "🏆 Meine Medaillen & Erfolge":
    st.title("🏆 Dein Trophäenschrank")
    if st.session_state.medals:
        for medal in sorted(list(set(st.session_state.medals))):
            st.markdown(f"<div class='medal-card'>{medal}</div>", unsafe_allow_html=True)
    else:
        st.info("Noch keine Medaillen verdient. Leg los und lade Aktivitäts-Videos hoch! 🚀")

# =====================================================================
# MODUS 4: ABENDLICHE TAGESZUSAMMENFASSUNG
# =====================================================================
elif app_mode == "📅 Abendliche Tageszusammenfassung":
    st.title("📅 Deine Tagesbilanz")
    st.write("Fordere hier am Ende deines Tages dein ehrliches Zeugnis an.")
    
    if st.button("📊 Tagesbericht generieren"):
        bericht = execute_background_thought("tages_fazit")
        st.markdown(bericht)