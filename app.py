import streamlit as st
import datetime
from openai import OpenAI

# --- SEITENKONFIGURATION & STYLING ---
st.set_page_config(page_title="AI Learn & Fit Hub", page_icon="⚡", layout="wide")

# --- INITIALISIERUNG SESSION STATE (MERKFUNKTION) ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "consumed_food" not in st.session_state:
    st.session_state.consumed_food = []
if "streak_fitness" not in st.session_state:
    st.session_state.streak_fitness = 0
if "streak_lernen" not in st.session_state:
    st.session_state.streak_lernen = 0
if "medals" not in st.session_state:
    st.session_state.medals = []
if "last_activity" not in st.session_state:
    st.session_state.last_activity = datetime.date.today()
if "openai_key" not in st.session_state:
    st.session_state.openai_key = ""

# Hier werden deine persönlichen Daten dauerhaft in der Sitzung gespeichert:
if "klassenstufe" not in st.session_state:
    st.session_state.klassenstufe = "Klasse 5"
if "alter" not in st.session_state:
    st.session_state.alter = 16
if "groesse" not in st.session_state:
    st.session_state.groesse = 170
if "gewicht" not in st.session_state:
    st.session_state.gewicht = 65

# --- SIDEBAR: DOCK FÜR DEN API KEY ---
st.sidebar.title("🔑 AI Schlüssel")
api_key_input = st.sidebar.text_input("Dein OpenAI Key:", value=st.session_state.openai_key, type="password")

if api_key_input != st.session_state.openai_key:
    st.session_state.openai_key = api_key_input
    st.rerun()

OPENAI_API_KEY = st.session_state.openai_key

# --- SIDEBAR: NAVIGATION & DESIGN ---
st.sidebar.write("---")
st.sidebar.title("🎛️ Navigation")
app_mode = st.sidebar.selectbox("Bereich auswählen", [
    "📚 Lernen & Schule", 
    "💪 Fitness & Ernährung",
    "🏆 Meine Medaillen & Erfolge",
    "📅 Abendliche Tageszusammenfassung" # Neuer Bereich hinzugefügt!
])

st.sidebar.title("🎨 Design & Farben")
bg_color = st.sidebar.color_picker("Dashboard-Farbe", "#121212")
text_color = st.sidebar.color_picker("Text-Farbe", "#FFFFFF")
accent_color = "#2ECC71" 

# CSS für modernere Schriften und Kacheln
st.markdown(f"""
    <style>
    html, body, [data-testid="stSidebar"], .stApp {{
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important;
        background-color: {bg_color} !important;
        color: {text_color} !important;
    }}
    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important;
        color: {text_color} !important;
        font-weight: 700;
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
        font-weight: bold;
    }}
    </style>
    """, unsafe_allow_html=True)

# Hilfsfunktion für echte KI-Abfragen
def get_ai_response(prompt_text):
    if not OPENAI_API_KEY:
        return "⚠️ Bitte trage zuerst deinen OpenAI Key links in der Sidebar ein!"
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt_text}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Fehler bei der KI-Abfrage: {str(e)}"

# --- AUTOMATISCHER STREAK-RESET NACH INAKTIVITÄT ---
days_passed = (datetime.date.today() - st.session_state.last_activity).days
if days_passed >= 2:
    st.session_state.streak_fitness = 0
    st.session_state.streak_lernen = 0
    st.sidebar.warning("⚠️ Deine Tracker wurden wegen 2 Tagen Inaktivität zurückgesetzt!")

if st.sidebar.button("🔴 Tracker manuell zurücksetzen"):
    st.session_state.streak_fitness = 0
    st.session_state.streak_lernen = 0
    st.rerun()


# =====================================================================
# MODUS 1: LERNEN & SCHULE
# =====================================================================
if app_mode == "📚 Lernen & Schule":
    st.title("📚 AI Lern-Zentrum")
    
    # Klassenstufe wird jetzt im Session State gespeichert und bleibt gemerkt
    klassenstufen_liste = [f"Klasse {i}" for i in range(1, 13)]
    default_index = klassenstufen_liste.index(st.session_state.klassenstufe) if st.session_state.klassenstufe in klassenstufen_liste else 4
    
    selected_klasse = st.selectbox("Klassenstufe wählen", klassenstufen_liste, index=default_index)
    if selected_klasse != st.session_state.klassenstufe:
        st.session_state.klassenstufe = selected_klasse
        st.rerun()
        
    st.markdown(f"<div class='stat-box'><b>Aktiver Modus:</b> {st.session_state.klassenstufe}</div>", unsafe_allow_html=True)
    
    st.subheader("📝 KI-Lernunterlagen erstellen")
    themen_input = st.text_input("Gib dein Thema ein (z.B. 'Fotosynthese')")
    erstellungs_typ = st.radio("Was soll die AI erstellen?", ["Lernzettel", "Quiz", "Probearbeit"])
    
    if st.button("Generieren"):
        with st.spinner("KI generiert deine Unterlagen..."):
            prompt = f"Erstelle einen ausführlichen {erstellungs_typ} zum Thema '{themen_input}' für die {st.session_state.klassenstufe} in der Schule. Strukturiere es übersichtlich mit Überschriften."
            antwort = get_ai_response(prompt)
            st.markdown("### Dein generiertes Dokument")
            st.write(antwort)

    st.write("---")
    st.subheader("⏳ Lern-Tracker")
    st.markdown(f"<div class='stat-box'>🔥 Aktueller Lern-Streak: <b>{st.session_state.streak_lernen} Tage</b></div>", unsafe_allow_html=True)
    
    video_file_learn = st.file_uploader("Lade ein 5-Minuten-Lernvideo hoch", type=["mp4", "mov"], key="learn_vid")
    if video_file_learn is not None:
        if st.button("Video bestätigen & Tracker +1"):
            st.session_state.streak_lernen += 1
            st.session_state.last_activity = datetime.date.today()
            
            if st.session_state.streak_lernen == 1:
                st.session_state.medals.append("🥇 Erster Schritt (Lernen) - Du hast dein erstes Video hochgeladen!")
            if st.session_state.streak_lernen == 5:
                st.session_state.medals.append("🧠 Lern-Maschine - 5 Tage hintereinander gelernt!")
                
            st.success("Super! Dein Tracker wurde erhöht.")
            st.rerun()


# =====================================================================
# MODUS 2: FITNESS & ERNÄHRUNG
# =====================================================================
elif app_mode == "💪 Fitness & Ernährung":
    st.title("💪 AI Fitness & Ernährungs-Coach")
    
    # Werte werden direkt aus dem Session State geladen und abgespeichert
    col1, col2, col3 = st.columns(3)
    with col1: 
        input_alter = st.number_input("Alter", min_value=10, max_value=100, value=st.session_state.alter)
    with col2: 
        input_groesse = st.number_input("Größe (in cm)", min_value=100, max_value=250, value=st.session_state.groesse)
    with col3: 
        input_gewicht = st.number_input("Gewicht (in kg)", min_value=30, max_value=200, value=st.session_state.gewicht)
        
    if input_alter != st.session_state.alter or input_groesse != st.session_state.groesse or input_gewicht != st.session_state.gewicht:
        st.session_state.alter = input_alter
        st.session_state.groesse = input_groesse
        st.session_state.gewicht = input_gewicht
        st.rerun()
    
    # Nährstoffberechnung
    grundumsatz = int(10 * st.session_state.gewicht + 6.25 * st.session_state.groesse - 5 * st.session_state.alter + 5) 
    protein = int(st.session_state.gewicht * 1.5)
    kohlenhydrate = int(grundumsatz * 0.5 / 4)
    fett = int(grundumsatz * 0.3 / 9)
    
    st.markdown(f"""
    <div class='stat-box'>
        <h4>📊 Dein berechneter täglicher Bedarf:</h4>
        <p>• <b>Kalorien:</b> ca. {grundumsatz} kcal</p>
        <p>• <b>Eiweiß (Proteine):</b> {protein}g</p>
        <p>• <b>Kohlenhydrate:</b> {kohlenhydrate}g</p>
        <p>• <b>Fett:</b> {fett}g</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("---")
    st.subheader("🍎 Ernährungs-Tracker mit AI-Feedback")
    
    with st.form(key='food_form', clear_on_submit=True):
        speise = st.text_input("Was hast du gegessen/getrunken?")
        submit_food = st.form_submit_button("Hinzufügen & KI-Feedback erhalten")
        
        if submit_food and speise:
            st.session_state.consumed_food.append(speise)
            
            # Sofortiges Lob oder Kritik von der KI triggern
            feedback_prompt = f"Der Nutzer ({st.session_state.alter} Jahre, {st.session_state.groesse}cm, {st.session_state.gewicht}kg) hat gerade folgendes Lebensmittel eingetragen: '{speise}'. Lobe oder kritisiere diese Wahl kurz und knackig (maximal 3 Sätze) basierend auf Fitness und Gesundheit."
            st.session_state["last_food_feedback"] = get_ai_response(feedback_prompt)
            st.rerun()

    # Feedback unter dem Formular anzeigen
    if "last_food_feedback" in st.session_state:
        st.info(f"💬 **KI-Feedback zu deiner Mahlzeit:**\n\n{st.session_state['last_food_feedback']}")

    if st.session_state.consumed_food:
        st.write("**Bisherige Mahlzeiten heute:**")
        for item in st.session_state.consumed_food:
            st.write(f"• {item}")
            
    st.write("---")
    st.subheader("🏃‍♂️ Sport & Kalorien")
    sportart = st.text_input("Welche Sportart hast du gemacht?")
    dauer = st.number_input("Dauer (in Minuten)", min_value=1, value=30)
    
    if st.button("Kalorien berechnen"):
        with st.spinner("KI berechnet..."):
            prompt = f"Ein {st.session_state.alter} Jahre alter Mensch ({st.session_state.groesse}cm, {st.session_state.gewicht}kg) hat {dauer} Minuten lang folgende Sportart gemacht: {sportart}. Schätze kurz und präzise, wie viele Kalorien dabei verbrannt wurden."
            antwort = get_ai_response(prompt)
            st.info(antwort)

    st.write("---")
    st.subheader("⏳ Fitness-Tracker")
    st.markdown(f"<div class='stat-box'>🔥 Aktueller Fitness-Streak: <b>{st.session_state.streak_fitness} Tage</b></div>", unsafe_allow_html=True)
    
    video_file_fit = st.file_uploader("Lade ein 5-Minuten-Workout-Video hoch", type=["mp4", "mov"], key="fit_vid")
    if video_file_fit is not None:
        if st.button("Workout bestätigen & Tracker +1"):
            st.session_state.streak_fitness += 1
            st.session_state.last_activity = datetime.date.today()
            
            if st.session_state.streak_fitness == 1:
                st.session_state.medals.append("🏅 Erste Trainingseinheit - Aller Anfang ist gemacht!")
            if st.session_state.streak_fitness == 5:
                st.session_state.medals.append("⚡ Fitness-Champ - 5 Workouts eingereicht!")
                
            st.success("Stark! Dein Fitness-Tracker ist gestiegen.")
            st.rerun()


# =====================================================================
# MODUS 3: EIGENER AUSWÄHLPUNKT FÜR MEDAILLEN
# =====================================================================
elif app_mode == "🏆 Meine Medaillen & Erfolge":
    st.title("🏆 Dein Trophäenschrank")
    st.write("Hier werden alle deine Medaillen aufgelistet, die du durch das Hochladen von Videos im Lern- oder Fitnessbereich verdienst.")
    
    st.subheader("Deine Auszeichnungen:")
    
    if st.session_state.medals:
        for medal in sorted(list(set(st.session_state.medals))):
            st.markdown(f"<div class='medal-card'>{medal}</div>", unsafe_allow_html=True)
    else:
        st.info("Du hast noch keine Medaillen verdient. Lade in den anderen Modi Videos hoch, um Erfolge freizuschalten! 🚀")


# =====================================================================
# MODUS 4: NEU! ABENDLICHE TAGESZUSAMMENFASSUNG
# =====================================================================
elif app_mode == "📅 Abendliche Tageszusammenfassung":
    st.title("📅 Deine Tagesbilanz & KI-Feedback")
    st.write("Klicke am Ende des Tages hier drauf, um eine vollständige Analyse deiner Leistung zu bekommen. Die KI lobt oder kritisiert dich basierend auf deinen heutigen Aktivitäten.")
    
    if st.button("📊 Tageszusammenfassung generieren"):
        with st.spinner("Die KI wertet deinen Tag aus..."):
            mahlzeiten_text = ", ".join(st.session_state.consumed_food) if st.session_state.consumed_food else "Keine Mahlzeiten eingetragen"
            
            summary_prompt = f"""
            Du bist ein strenger aber fairer Coach für Fitness und Schule. 
            Analysiere den Tag des Nutzers anhand folgender Daten:
            - Alter: {st.session_state.alter} Jahre, Größe: {st.session_state.groesse}cm, Gewicht: {st.session_state.gewicht}kg
            - Klassenstufe: {st.session_state.klassenstufe}
            - Heutiger Lern-Streak: {st.session_state.streak_lernen} Tage
            - Heutiger Fitness-Streak: {st.session_state.streak_fitness} Tage
            - Gegessene Lebensmittel heute: {mahlzeiten_text}
            
            Schreibe eine ehrliche Zusammenfassung des Tages. Lobe den Nutzer ausdrücklich für gute Dinge (z.B. hohe Streaks, gesunde Ernährung) und kritisiere ihn deutlich für schlechte Dinge (z.B. ungesundes Essen oder wenn ein Streak bei 0 steht). Gib am Ende Tipps für morgen.
            """
            zusammenfassung = get_ai_response(summary_prompt)
            st.markdown("### 📝 Deine KI-Auswertung für heute")
            st.info(zusammenfassung)


# =====================================================================
# ALLGEMEINER CHATBOT
# =====================================================================
if app_mode not in ["🏆 Meine Medaillen & Erfolge", "📅 Abendliche Tageszusammenfassung"]:
    st.write("---")
    st.subheader("💬 Dein All-in-One AI Chatbot")

    user_message = st.chat_input("Frag mich etwas...")
    if user_message:
        st.session_state.chat_history.append(("Du", user_message))
        
        with st.spinner("KI antwortet..."):
            if app_mode == "📚 Lernen & Schule":
                system_context = f"Du bist ein hilfreicher Lern-Bot für die {st.session_state.klassenstufe}. Beantworte diese Frage kurz und verständlich: {user_message}"
            else:
                system_context = f"Du bist ein Fitness- und Ernährungscoach. Der Nutzer ist {st.session_state.alter} Jahre alt, {st.session_state.groesse}cm groß und wiegt {st.session_state.gewicht}kg. Beantworte diese Frage: {user_message}"
                
            ai_response = get_ai_response(system_context)
            st.session_state.chat_history.append(("AI", ai_response))

    for rolle, text in st.session_state.chat_history[-6:]:
        with st.chat_message("user" if rolle == "Du" else "assistant"):
            st.write(f"**{rolle}:** {text}")