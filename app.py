import streamlit as st
import datetime
import time
import random

# --- SEITEN-SETUP ---
st.set_page_config(page_title="Learn & Fit Hub", page_icon="⚡", layout="wide")

# --- SITZUNGSSPEICHER (SESSION STATE) ---
FOR_ORGS = ["chat_history", "consumed_food", "medals"]
for item in FOR_ORGS:
    if item not in st.session_state:
        st.session_state[item] = []

# Standardwerte für Benutzerdaten, falls noch nicht gesetzt
DEFAULTS = {"streak_fitness": 0, "streak_lernen": 0, "klassenstufe": "Klasse 5", "alter": 16, "groesse": 170, "gewicht": 65, "last_activity": datetime.date.today()}
for key, val in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- INTERNES KI-SYSTEM (KOSTENLOS & OHNE KEY) ---
def simulate_ai_thinking(prompt_type, context=""):
    """ Simuliert einen tiefen Denkprozess im Hintergrund und liefert maßgeschneiderte Antworten """
    
    # Der geheime Denkprozess im Hintergrund
    with st.spinner("🧠 KI analysiert Daten und berechnet optimale Ausgabe..."):
        time.sleep(random.uniform(1.5, 3.0)) # Simuliert die Rechenzeit
    
    if prompt_type == "lernzettel":
        return f"### 📚 KI-Lernzettel: {context}\n\n**Wichtige Kernpunkte für die {st.session_state.klassenstufe}:**\n1. *Definition:* Ein zentraler Begriff der Biologie/Physik/Geschichte, den man für die Arbeit kennen muss.\n2. *Zusammenhang:* Wichtig ist hierbei das Zusammenspiel der einzelnen Faktoren.\n3. *Merksatz:* Wer das verstanden hat, schreibt garantiert eine gute Note.\n\n*Tipp vom Coach:* Lies dir das vor dem Schlafen noch zweimal durch!"
    
    elif prompt_type == "quiz":
        return f"### 📝 KI-Quiz zu: {context}\n\n*Beantworte die Fragen im Kopf!*\n\n**Frage 1:** Was ist das Hauptmerkmal von {context}?\n**Frage 2:** Warum ist das für die {st.session_state.klassenstufe} relevant?\n**Frage 3:** Nenne ein praktisches Beispiel hierzu."
    
    elif prompt_type == "essen_feedback":
        lob_antworten = [
            f"🟢 Starke Wahl! '{context}' passt perfekt zu deinem Profil ({st.session_state.gewicht}kg). Weiter so!",
            f"🟢 Richtig gut! Das gibt dir genau die Energie, die du heute für dein Gehirn brauchst."
        ]
        kritik_antworten = [
            f"🔴 Aufgepasst: '{context}' liefert dir gerade eher leere Kalorien. Denk an deine Fitness-Ziele!",
            f"🔴 Hm, als Snack okay, aber versuch heute noch etwas mehr Proteine einzubauen."
        ]
        return random.choice(lob_antworten) if "salat" in context.lower() or "wasser" in context.lower() or "hähnchen" in context.lower() or "apfel" in context.lower() else random.choice(kritik_antworten)

    elif prompt_type == "tages_fazit":
        return f"""
        ### 📊 Dein ehrliches Tages-Fazit:
        
        **Das war gut:**
        * Dein Lern-Streak steht auf {st.session_state.streak_lernen} Tagen. Kontinuität ist alles in der {st.session_state.klassenstufe}!
        * Dein Sport-Streak zeigt {st.session_state.streak_fitness} Tage. Dein Körper wird es dir danken.
        
        **Hier musst du aufpassen:**
        * Achte bei deiner Ernährung darauf, dass du genug trinkst und frische Sachen isst.
        
        *🔥 Coach-Spruch für morgen:* Disziplin schlägt Talent. Morgen direkt nachlegen!
        """
    return "Antwort erfolgreich generiert."

# --- STYLING (CLEAN & MODERN) ---
st.markdown("""
    <style>
    body, .stApp { background-color: #121212 !important; color: #FFFFFF !important; font-family: 'Segoe UI', Roboto, sans-serif; }
    .card { background: rgba(255, 255, 255, 0.04); padding: 20px; border-radius: 12px; border-left: 4px solid #2ECC71; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR NAVI ---
st.sidebar.title("⚡ Navigation")
app_mode = st.sidebar.selectbox("Wohin möchtest du?", ["📚 Lern-Zentrum", "💪 Fitness & Ernährung", "🏆 Erfolge", "📅 Tagesbilanz"])

# Tracker Reset Logik
if (datetime.date.today() - st.session_state.last_activity).days >= 2:
    st.session_state.streak_fitness = 0
    st.session_state.streak_lernen = 0

# =====================================================================
# LERN-ZENTRUM
# =====================================================================
if app_mode == "📚 Lern-Zentrum":
    st.title("📚 KI-gestütztes Lernzentrum")
    
    # Merkt sich die Auswahl automatisch im Session State
    st.session_state.klassenstufe = st.selectbox("Deine Klassenstufe:", [f"Klasse {i}" for i in range(1, 13)], index=[f"Klasse {i}" for i in range(1, 13)].index(st.session_state.klassenstufe))
    
    st.write("")
    thema = st.text_input("Welches Thema steht gerade an?")
    art = st.radio("Was brauchst du?", ["Lernzettel", "Quiz"])
    
    if st.button("Unterlagen generieren") and thema:
        ergebnis = simulate_ai_thinking(art.lower(), thema)
        st.markdown(ergebnis)

    st.write("---")
    st.subheader("⏳ Dein Lern-Tracker")
    st.info(f"🔥 Aktueller Lern-Streak: {st.session_state.streak_lernen} Tage")
    
    if st.file_uploader("Lernvideo hochladen (5 Min)", type=["mp4", "mov"]) and st.button("Video validieren"):
        st.session_state.streak_lernen += 1
        st.session_state.last_activity = datetime.date.today()
        st.success("Erfolgreich verbucht!")
        st.rerun()

# =====================================================================
# FITNESS & ERNÄHRUNG
# =====================================================================
elif app_mode == "💪 Fitness & Ernährung":
    st.title("💪 Fitness & Ernährung")
    
    c1, c2, c3 = st.columns(3)
    st.session_state.alter = c1.number_input("Alter", value=st.session_state.alter)
    st.session_state.groesse = c2.number_input("Größe (cm)", value=st.session_state.groesse)
    st.session_state.gewicht = c3.number_input("Gewicht (kg)", value=st.session_state.gewicht)

    st.write("---")
    st.subheader("🍎 Live Ernährungs-Feedback")
    
    with st.form("food_entry", clear_on_submit=True):
        food = st.text_input("Was hast du gegessen?")
        if st.form_submit_button("Eintragen") and food:
            st.session_state.consumed_food.append(food)
            st.session_state["latest_feedback"] = simulate_ai_thinking("essen_feedback", food)
            st.rerun()

    if "latest_feedback" in st.session_state:
        st.info(st.session_state["latest_feedback"])

    st.write("---")
    st.subheader("🏃‍♂️ Workout eintragen")
    st.info(f"🔥 Fitness-Streak: {st.session_state.streak_fitness} Tage")
    if st.file_uploader("Workout-Nachweis hochladen", type=["mp4", "mov"]) and st.button("Workout bestätigen"):
        st.session_state.streak_fitness += 1
        st.session_state.last_activity = datetime.date.today()
        st.success("Streak erhöht! Super Job.")
        st.rerun()

# =====================================================================
# TROPHÄEN
# =====================================================================
elif app_mode == "🏆 Erfolge":
    st.title("🏆 Deine Erfolge")
    if st.session_state.streak_lernen >= 1 or st.session_state.streak_fitness >= 1:
        st.success("🥇 Aller Anfang ist gemacht! Du hast deine erste Aktivität registriert.")
    else:
        st.info("Noch keine Medaillen vorhanden. Leg los, um welche freizuschalten!")

# =====================================================================
# TAGESBILANZ
# =====================================================================
elif app_mode == "📅 Tagesbilanz":
    st.title("📅 Abendliche Analyse")
    if st.button("Tagesbericht anfordern"):
        bericht = simulate_ai_thinking("tages_fazit")
        st.markdown(bericht)