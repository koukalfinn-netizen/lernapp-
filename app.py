import streamlit as st
import datetime
import time
import random

# --- SEITENKONFIGURATION & MOTIVIERENDES SETUP ---
st.set_page_config(page_title="Epic Learn & Fit Hub", page_icon="🔥", layout="wide")

# --- INITIALISIERUNG SESSION STATE (DATEN MERKEN) ---
FOR_ORGS = ["chat_history", "consumed_food", "medals"]
for item in FOR_ORGS:
    if item not in st.session_state:
        st.session_state[item] = []

DEFAULTS = {
    "streak_fitness": 0, 
    "streak_lernen": 0, 
    "klassenstufe": "Klasse 5", 
    "alter": 16, 
    "groesse": 170, 
    "gewicht": 65, 
    "last_activity": datetime.date.today()
}
for key, val in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- SIDEBAR: NAVIGATION & DESIGN ---
st.sidebar.title("⚡ Hub Steuerung")
app_mode = st.sidebar.selectbox("Bereich auswählen", [
    "📚 Lernen & Schule", 
    "💪 Fitness & Ernährung",
    "🏆 Meine Medaillen & Erfolge",
    "📅 Abendliche Tageszusammenfassung"
])

st.sidebar.write("---")
st.sidebar.title("🎨 Deinen Style anpassen")
bg_color = st.sidebar.color_picker("Dashboard-Hintergrund", "#0F172A") # Moderneres Dark-Slate als Standard
text_color = st.sidebar.color_picker("Text-Farbe", "#F8FAFC")
accent_color = "#10B981" # Dynamisches Smaragd-Grün

# --- CUSTOM MODERNES DESIGN (ANTI-MILITÄR-LOOK) ---
st.markdown(f"""
    <style>
    html, body, [data-testid="stSidebar"], .stApp {{
        font-family: 'Inter', '-apple-system', BlinkMacSystemFont, sans-serif !important;
        background-color: {bg_color} !important;
        color: {text_color} !important;
    }}
    h1, h2, h3, h4, h5, h6 {{
        color: {text_color} !important;
        font-weight: 800;
        letter-spacing: -0.5px;
    }}
    /* Coole, abgerundete Lifestyle-Kacheln mit Farbverlauf */
    .stat-box {{
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.01) 100%);
        padding: 24px;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        margin-bottom: 20px;
    }}
    .streak-badge-learn {{
        background: linear-gradient(90deg, #3B82F6 0%, #1D4ED8 100%);
        color: white; padding: 10px 18px; border-radius: 50px; font-weight: bold; display: inline-block;
    }}
    .streak-badge-fit {{
        background: linear-gradient(90deg, #F59E0B 0%, #D97706 100%);
        color: white; padding: 10px 18px; border-radius: 50px; font-weight: bold; display: inline-block;
    }}
    .medal-card {{
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(251, 191, 36, 0.05) 100%);
        padding: 20px;
        border-radius: 16px;
        border: 1px solid #F59E0B;
        margin: 12px 0px;
        font-size: 1.1rem;
        font-weight: 700;
        box-shadow: 0 4px 15px rgba(245, 158, 11, 0.1);
    }}
    /* Inputs und Buttons stylischer machen */
    .stButton>button {{
        border-radius: 12px !important;
        background: linear-gradient(90deg, #10B981 0%, #059669 100%) !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
        padding: 10px 24px !important;
        transition: all 0.3s ease;
    }}
    .stButton>button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(16, 185, 129, 0.4);
    }}
    </style>
    """, unsafe_allow_html=True)

# --- INTELLIGENTER HINTERGRUND-DENKPROZESS (KOSTENLOS) ---
def simulate_ai_thinking(prompt_type, context=""):
    with st.spinner("🧠 KI analysiert deine Daten im Background und berechnet optimales Feedback..."):
        time.sleep(random.uniform(1.2, 2.5)) # Simulierter Denkprozess
    
    if prompt_type == "lernzettel":
        return f"""### 📚 Dein maßgeschneiderter Lernzettel: {context}
        
        **💡 Kernwissen für die {st.session_state.klassenstufe}:**
        1. *Das Fundament:* Hier ist die wichtigste Definition, die du für die nächste Prüfung fehlerfrei beherrschen musst.
        2. *Der wichtigste Zusammenhang:* Achte besonders darauf, wie die einzelnen Faktoren ineinandergreifen.
        3. *Typische Falle im Test:* Lehrer fragen hierzu fast immer die gleiche Fangfrage ab – merk dir diesen Punkt!
        
        *🔥 Coach-Tipp:* Atme kurz durch, schau dir die Punkte an und teste dich in 10 Minuten selbst!"""
        
    elif prompt_type == "quiz":
        return f"""### 📝 KI-Power-Quiz zu: {context}
        
        *Gehirntraining aktivieren! Beantworte diese Fragen kurz im Kopf:*
        
        * **Frage 1:** Was ist die absolute Kernfunktion von '{context}'?
        * **Frage 2:** Wie würdest du das einem Mitschüler aus der {st.session_state.klassenstufe} in eigenen Worten erklären?
        * **Frage 3:** Wo begegnet uns dieses Prinzip im echten Leben?"""
        
    elif prompt_type == "essen_feedback":
        gesund = ["salat", "wasser", "hähnchen", "apfel", "quark", "ei", "fisch", "gemüse", "banane", "reis"]
        is_healthy = any(g in context.lower() for g in gesund)
        
        if is_healthy:
            return f"🟢 **Lob vom Coach:** Überragende Wahl! '{context}' liefert deinem Körper genau die Nährstoffe, die er jetzt für Muskeln und Fokus braucht. Weiter so, du ziehst heute voll durch!"
        else:
            return f"🔴 **Konstruktive Kritik:** '{context}' schmeckt zwar gut, bringt dich deinen Zielen bei {st.session_state.gewicht}kg aber gerade nicht näher (eher leere Kalorien). Ausrutscher sind okay, aber die nächste Mahlzeit wird wieder gecleant! Deal?"

    elif prompt_type == "tages_fazit":
        mahlzeiten = ", ".join(st.session_state.consumed_food) if st.session_state.consumed_food else "Keine Mahlzeiten eingetragen"
        return f"""
        ### 📊 Dein ehrliches Tages-Fazit:
        
        **🔥 Dafür wirst du gelobt:**
        * Dein Lern-Streak steht stolz bei **{st.session_state.streak_lernen} Tagen** in der **{st.session_state.klassenstufe}**. Dranbleiben zahlt sich aus!