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

# --- KI BACKEND (INTELLIGENTE BIBLIOTHEKS-VORLAGEN - KEYLESS) ---
def execute_background_thought(mode, topic=""):
    with st.spinner("🧠 Generiere logische Verknüpfungen... Baue maßgeschneiderte Struktur auf..."):
        time.sleep(random.uniform(1.5, 2.5)) 
    
    clean_topic = topic.strip().title()
    
    if mode == "lernzettel":
        # Hier greift die "AI" auf vordefinierte Wissensstrukturen zurück und kombiniert sie so, wie ich es tun würde
        unterpunkte = [
            f"Grundlagen und Definition von {clean_topic}",
            f"Warum {clean_topic} im Lehrplan der {st.session_state.klassenstufe} entscheidend ist",
            f"Häufige Stolpersteine und Denkfehler in Klassenarbeiten",
            f"Praxisbeispiel zur Veranschaulichung"
        ]
        
        return f"""
        # 📝 Professioneller Lernzettel: {clean_topic}
        *Erstellt nach meinem optimalen KI-Lernsystem für die {st.session_state.klassenstufe}*
        
        ---
        ### 🔍 Overview & Kernkonzept
        Wenn Lehrer nach **{clean_topic}** fragen, wollen sie sehen, dass du das übergeordnete Prinzip verstanden hast. Es ist kein reines Auswendiglernen, sondern ein logischer Prozess.
        
        ### 📑 Strukturierte Lern-Timeline
        * **Schritt 1: {unterpunkte[0]}** Der Einstieg in das Thema. Merk dir hierzu die goldene Regel: Jedes System sucht ein Gleichgewicht oder folgt einer festen Formel.
        * **Schritt 2: {unterpunkte[1]}** Lehrer lieben Querverbindungen. Setze dieses Thema immer in Bezug zu dem, was ihr im Vormonat besprochen habt.
        * **Schritt 3: {unterpunkte[2]}** *Achtung Gefahr!* In Klausuren fallen viele darauf rein, Details zu vertauschen. Lies die Aufgabenstellung hierzu immer doppelt.
        
        ### 💡 Praxis-Transfer ({unterpunkte[3]})
        Stell dir {clean_topic} wie ein Zahnrad vor: Fällt dieser Baustein weg, stoppt der gesamte biologische, historische oder mathematische Ablauf.
        
        ### 🎓 Mein persönlicher Top-Tipp für dich:
        > "Erkläre dieses Blatt heute Abend kurz jemanden aus deiner Familie in deinen eigenen Worten. Wenn du das schaffst, sitzt der Stoff bombensicher für eine 1!"
        """
        
    elif mode == "quiz":
        return f"""
        # 🧪 Interaktives KI-Quiz: {clean_topic}
        *Niveau: {st.session_state.klassenstufe}*
        
        Fordere dein Gehirn heraus. Kannst du diese 3 Fragen fehlerfrei beantworten?
        
        1.  **Frage 1:** Was ist das absolute Fundament von *{clean_topic}*, ohne das das Thema keinen Sinn ergibt?
        2.  **Frage 2:** Welcher typische Fehler passiert Schülern der *{st.session_state.klassenstufe}* bei dieser Fragestellung am häufigsten?
        3.  **Frage 3:** Wie lässt sich *{clean_topic}* an einem einfachen Alltagsbeispiel erklären?
        """
        
    elif mode == "essen_feedback":
        healthy = ["salat", "wasser", "hähnchen", "apfel", "quark", "gemüse", "fisch", "reis", "ei", "banane", "haferflocken", "brokkoli"]
        unhealthy = ["cola", "pizza", "burger", "chips", "schokolade", "red bull", "döner", "fanta", "sprite", "snickers", "nutella"]
        
        text_lower = topic.lower()
        if any(x in text_lower for x in healthy):
            return f"🟢 **Lob vom Coach:** Überragende Wahl! '{clean_topic}' liefert perfekte Nährstoffe für deinen Körper ({st.session_state.gewicht}kg). Das gibt dir Power ohne anschließenden Energie-Crash!"
        elif any(x in text_lower for x in unhealthy):
            return f"🔴 **Kritik vom Coach:** Aufgepasst! '{clean_topic}' liefert dir fast nur leere Kalorien und schnellen Zucker. Das blockiert deinen Fokus beim Lernen und wirft dich im Training zurück."
        else:
            return f"🟡 **Hinweis vom Coach:** '{clean_topic}' ist als neutraler Snack okay. Achte darauf, über den restlichen Tag verteilt genug Proteine und unverarbeitete Lebensmittel einzubauen."

    elif mode == "tages_fazit":
        ma