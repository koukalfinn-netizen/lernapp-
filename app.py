import streamlit as st
import datetime
import time
import random
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

# Hier werden deine persönlichen Daten dauerhaft gespeichert
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
    "📅 Abendliche Tageszusammenfassung"
])

st.sidebar.title("🎨 Design & Farben")
bg_color = st.sidebar.color_picker("Dashboard-Farbe", "#121212")
text_color = st.sidebar.color_picker("Text-Farbe", "#FFFFFF")
accent_color = "#2ECC71" 

# CSS für moderne Schriften und Kacheln (Fehlerfrei escaped durch Verzicht auf f-String Konflikte)
st.markdown("""
    <style>
    html, body, [data-testid="stSidebar"], .stApp {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important;
        background-color: """ + bg_color + """ !important;
        color: """ + text_color + """ !important;
    }
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important;
        color: """ + text_color + """ !important;
        font-weight: 700;
    }
    .stat-box {
        background-color: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid """ + accent_color + """;
        margin-bottom: 15px;
    }
    .medal-card {
        background-color: rgba(255, 215, 0, 0.1);
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #FFD700;
        margin: 10px 0px;
        font-size: 1.1rem;
        font-weight: bold;
    }
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
    
    klassenstufen_liste = [f"Klasse {i}" for i in range(1, 13)]
    default_index = klassenstufen_liste.index(st.session_state.klassenstufe) if st.session_state.klassenstufe in klassenstufen_liste else 4
    
    selected_klasse = st.selectbox("Klassenstufe wählen", klassenstufen_liste, index=default_index)
    if selected_klasse != st.session_state.klassenstufe:
        st.session_state.klassenstufe = selected_klasse
        st.rerun()
        
    st.markdown(f'<div class="stat-box"><b>Aktiver Modus:</b> {st.session_state.klassenstufe}</div>', unsafe_allow_html=True)
    
    st.subheader("📝 KI-Lernunterlagen erstellen")
    themen_input = st.text_input("Gib dein Thema ein (z.B. 'Fotosynthese')")
    erstellungs_typ = st.radio("Was soll die AI erstellen?", ["Lernzettel", "Quiz"])
    
    if st.button("Generieren") and themen_input:
        with st.spinner("🧠 Verknüpfe Bibliotheksdaten... Baue Struktur auf..."):
            time.sleep(random.uniform(1.2, 2.2))
            
            clean_topic = themen_input.strip().title()
            
            if erstellungs_typ == "Lernzettel":
                # Optimierte strukturierte Vorlage kombiniert mit KI-Prompt-Inhalten
                prompt_details = f"Erstelle stichpunktartig wichtige Fakten und Stolpersteine für das Thema '{clean_topic}' angepasst an eine {st.session_state.klassenstufe}. Halte es übersichtlich."
                ki_fakten = get_ai_response(prompt_details)
                
                antwort = f"""
# 📝 Professioneller Lernzettel: {clean_topic}
*Optimiert für dein Niveau: {st.session_state.klassenstufe}*

---
### 🔍 Overview & Kernkonzept
Wenn Lehrer nach **{clean_topic}** fragen, wollen sie sehen, dass du das übergeordnete Prinzip verstanden hast. Es ist kein reines Auswendiglernen, sondern ein logischer Prozess.

### 📑 KI-generierte Kernfakten & Details
{ki_fakten}

### 💡 Praxis-Transfer & Merkhilfe
Stell dir {clean_topic} wie ein wichtiges Zahnrad vor: Fällt dieser Baustein weg, stoppt der gesamte biologische, historische oder mathematische Ablauf des Systems.

### 🎓 Mein persönlicher Top-Tipp für dich:
> "Erkläre dieses Blatt heute Abend kurz jemandem aus deiner Familie in deinen eigenen Worten. Wenn du das schaffst, sitzt der Stoff bombensicher für eine 1!"
"""
            else:
                prompt_quiz = f"Erstelle ein interaktives Quiz mit 3 Fragen und kurzen Antwortmöglichkeiten zum Thema '{clean_topic}' für die {st.session_state.klassenstufe}."
                ki_quiz = get_ai_response(prompt_quiz)
                
                antwort = f"""
# 🧪 Interaktives KI-Quiz: {clean_topic}
*Niveau: {st.session_state.klassenstufe}*

Fordere dein Gehirn heraus. Kannst du diese Fragen fehlerfrei beantworten?

{ki_quiz}
"""
                
            st.markdown("### Dein generiertes Dokument")
            st.markdown(antwort)

    st.write("---")
    st.subheader("⏳ Lern-Tracker")
    st.markdown(f'<div class="stat-box">🔥 Aktueller Lern-Streak: <b>{st.session_state.streak_lernen} Tage</b></div>', unsafe_allow_html=True)
    
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
        st.session_state.