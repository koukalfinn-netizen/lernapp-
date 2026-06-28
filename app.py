import streamlit as st
import datetime
from openai import OpenAI

# --- SEITENKONFIGURATION & STYLING ---
st.set_page_config(page_title="AI Learn & Fit Hub", page_icon="⚡", layout="wide")

# Initialisierung des Session States
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

# --- SIDEBAR: API KEY & PERSONALISIERUNG ---
st.sidebar.title("🔑 API-Einstellungen")
# Hier trägst du deinen eigenen Key ein, wenn du die App startest
openai_api_key = st.sidebar.text_input("Dein OpenAI API Key", type="password")

st.sidebar.title("🎨 Personalisierung")
bg_color = st.sidebar.color_picker("Wähle deine Dashboard-Farbe", "#1E1E1E")
text_color = st.sidebar.color_picker("Wähle deine Text-Farbe", "#FFFFFF")
app_mode = st.sidebar.selectbox("Modus wechseln", ["📚 Lernen & Schule", "💪 Fitness & Ernährung"])

# CSS für dynamische Farben anwenden
st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color}; color: {text_color}; }}
    </style>
    """, unsafe_allow_html=True)

# Hilfsfunktion für echte KI-Abfragen
def get_ai_response(prompt_text):
    if not openai_api_key:
        return "Bitte gib zuerst deinen OpenAI API-Key in der linken Seitenleiste ein, um diese Funktion zu nutzen!"
    try:
        client = OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini", # Schnelles und günstiges Modell
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
    st.sidebar.warning("Deine Tracker wurden wegen 2 Tagen Inaktivität zurückgesetzt!")

if st.sidebar.button("🔴 Tracker manuell zurücksetzen"):
    st.session_state.streak_fitness = 0
    st.session_state.streak_lernen = 0
    st.rerun()


# =====================================================================
# MODUS 1: LERNEN & SCHULE
# =====================================================================
if app_mode == "📚 Lernen & Schule":
    st.title("📚 AI Lern-Zentrum")
    
    klassenstufe = st.selectbox("Klassenstufe wählen", [f"Klasse {i}" for i in range(1, 13)])
    st.info(f"Modus aktiv für: {klassenstufe}")
    
    st.subheader("📝 KI-Lernunterlagen erstellen")
    themen_input = st.text_input("Gib dein Thema ein (z.B. 'Fotosynthese')")
    erstellungs_typ = st.radio("Was soll die AI erstellen?", ["Lernzettel", "Quiz", "Probearbeit"])
    
    if st.button("Generieren"):
        with st.spinner("KI generiert deine Unterlagen..."):
            prompt = f"Erstelle einen ausführlichen {erstellungs_typ} zum Thema '{themen_input}' für die {klassenstufe} in der Schule. Strukturiere es übersichtlich mit Überschriften."
            antwort = get_ai_response(prompt)
            st.write(antwort)

    st.write("---")
    st.subheader("⏳ Lern-Tracker")
    st.write(f"🔥 Aktueller Lern-Streak: **{st.session_state.streak_lernen}**")
    
    video_file_learn = st.file_uploader("Lade ein 5-Minuten-Lernvideo hoch", type=["mp4", "mov"], key="learn_vid")
    if video_file_learn is not None:
        if st.button("Video bestätigen & Tracker +1"):
            st.session_state.streak_lernen += 1
            st.session_state.last_activity = datetime.date.today()
            if st.session_state.streak_lernen == 1:
                st.session_state.medals.append("🥇 Erster Schritt (Lernen)")
            st.success("Super! Dein Tracker wurde erhöht.")
            st.rerun()


# =====================================================================
# MODUS 2: FITNESS & ERNÄHRUNG
# =====================================================================
elif app_mode == "💪 Fitness & Ernährung":
    st.title("💪 AI Fitness & Ernährungs-Coach")
    
    col1, col2, col3 = st.columns(3)
    with col1: alter = st.number_input("Alter", min_value=10, max_value=100, value=16)
    with col2: groesse = st.number_input("Größe (in cm)", min_value=100, max_value=250, value=170)
    with col3: gewicht = st.number_input("Gewicht (in kg)", min_value=30, max_value=200, value=65)
    
    # Nährstoffberechnung
    grundumsatz = int(10 * gewicht + 6.25 * groesse - 5 * alter + 5) 
    protein = int(gewicht * 1.5)
    kohlenhydrate = int(grundumsatz * 0.5 / 4)
    fett = int(grundumsatz * 0.3 / 9)
    
    st.markdown(f"""
    > 📊 **Dein berechneter täglicher Bedarf:**
    > * **Kalorien:** ca. {grundumsatz} kcal | **Eiweiß:** {protein}g | **Kohlenhydrate:** {kohlenhydrate}g | **Fett:** {fett}g
    """)
    
    st.write("---")
    st.subheader("🍎 Ernährungs-Tracker")
    
    with st.form(key='food_form', clear_on_submit=True):
        speise = st.text_input("Was hast du gegessen/getrunken?")
        submit_food = st.form_submit_button("Hinzufügen")
        
        if submit_food and speise:
            st.session_state.consumed_food.append(speise)
            st.toast(f"'{speise}' wurde gespeichert!")

    if st.session_state.consumed_food:
        st.write("**Von der KI gemerkte Mahlzeiten heute:**")
        for item in st.session_state.consumed_food:
            st.write(f"• {item}")
            
    st.write("---")
    st.subheader("🏃‍♂️ Sport & Kalorien")
    sportart = st.text_input("Welche Sportart hast du gemacht?")
    dauer = st.number_input("Dauer (in Minuten)", min_value=1, value=30)
    
    if st.button("Kalorien berechnen"):
        with st.spinner("KI berechnet..."):
            prompt = f"Ein {alter} Jahre alter Mensch ({groesse}cm, {gewicht}kg) hat {dauer} Minuten lang folgende Sportart gemacht: {sportart}. Schätze kurz und präzise, wie viele Kalorien dabei verbrannt wurden."
            antwort = get_ai_response(prompt)
            st.info(antwort)

    st.write("---")
    st.subheader("⏳ Fitness-Tracker")
    st.write(f"🔥 Aktueller Fitness-Streak: **{st.session_state.streak_fitness}**")
    
    video_file_fit = st.file_uploader("Lade ein 5-Minuten-Workout-Video hoch", type=["mp4", "mov"], key="fit_vid")
    if video_file_fit is not None:
        if st.button("Workout bestätigen & Tracker +1"):
            st.session_state.streak_fitness += 1
            st.session_state.last_activity = datetime.date.today()
            if st.session_state.streak_fitness == 1:
                st.session_state.medals.append("🏅 Erste Trainingseinheit")
            st.success("Stark! Dein Fitness-Tracker ist gestiegen.")
            st.rerun()


# =====================================================================
# ALLGEMEINER CHATBOT (Nutzt jetzt die echte OpenAI API)
# =====================================================================
st.write("---")
st.subheader("💬 Dein All-in-One AI Chatbot")

user_message = st.chat_input("Frag mich etwas...")
if user_message:
    st.session_state.chat_history.append(("Du", user_message))
    
    with st.spinner("KI tippt..."):
        # Kontext-Prompt je nach Modus
        if app_mode == "📚 Lernen & Schule":
            system_context = f"Du bist ein hilfreicher Lern-Bot für die {klassenstufe}. Beantworte diese Frage kurz und verständlich: {user_message}"
        else:
            system_context = f"Du bist ein Fitness- und Ernährungscoach. Der Nutzer ist {alter} Jahre alt, {groesse}cm groß und wiegt {gewicht}kg. Beantworte diese Frage: {user_message}"
            
        ai_response = get_ai_response(system_context)
        st.session_state.chat_history.append(("AI", ai_response))

for rolle, text in st.session_state.chat_history[-6:]:
    with st.chat_message("user" if rolle == "Du" else "assistant"):
        st.write(f"**{rolle}:** {text}")


# =====================================================================
# BELOHNUNGSSYSTEM (MEDAILLEN)
# =====================================================================
st.sidebar.write("---")
st.sidebar.title("🏆 Deine Medaillen")
if st.session_state.medals:
    for medal in set(st.session_state.medals):
        st.sidebar.write(medal)
else:
    st.sidebar.write("Noch keine Medaillen. Leg los! 🚀")