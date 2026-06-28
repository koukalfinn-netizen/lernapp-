import streamlit as st
import datetime
import time
import random

# --- METADATEN & INTERFACES ---
st.set_page_config(page_title="Learn & Fit Hub", page_icon="⚡", layout="wide")

# --- SPEICHER-ARCHITEKTUR (SESSION STATE) ---
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

# --- BACKEND LOGIK: INTERNER DENKPROZESS (KEYLESS) ---
def execute_background_thought(mode, topic=""):
    """ Simuliert den tiefen analytischen Denkprozess im Hintergrund und generiert Content """
    
    # Der sichtbare "Denkprozess"
    with st.spinner("🧠 Analysiere Profileigenschaften... Berechne optimale Struktur..."):
        time.sleep(random.uniform(1.8, 3.2)) 
    
    if mode == "lernzettel":
        return f"""
        # 📝 KI-Lernunterlage: {topic}
        *Optimiert für das Niveau: {st.session_state.klassenstufe}*
        
        ---
        ### 🔍 1. Kernkonzept & Definition
        {topic} beschreibt ein fundamentales Prinzip, welches in dieser Jahrgangsstufe oft in Arbeiten abgefragt wird. Es bildet das Fundament für alle Folgekapitel.
        
        ### ⚡ 2. Die wichtigsten 3 Fakten (Must-Know)
        * **Fakt A:** Die Basisstruktur baut direkt auf den Grundgesetzen des Themas auf.
        * **Fakt B:** Ein häufiger Fehler in Prüfungen ist das Verwechseln der Kernfaktoren. Achte genau auf die Details!
        * **Fakt C:** In der Praxis lässt sich dieses Prinzip überall im Alltag wiederfinden.
        
        ### 💡 3. Coach-Merksatz
        > "Wer die logische Kette von {topic} einmal verstanden hat, muss für die Arbeit gar nicht mehr auswendig lernen!"
        """
        
    elif mode == "quiz":
        return f"""
        # 🧪 KI-Wissenscheck: {topic}
        *Testebene: {st.session_state.klassenstufe}*
        
        Prüfe dein Wissen im Kopf oder auf einem Blatt Papier:
        
        1.  **Frage 1:** Wie lässt sich das Phänomen von *{topic}* in eigenen Worten kurz erklären?
        2.  **Frage 2:** Welcher Faktor beeinflusst das Ergebnis am stärksten, wenn man etwas verändert?
        3.  **Frage 3:** Warum ist dieses Thema für deine aktuelle Klassenstufe so wichtig?
        """
        
    elif mode == "essen_feedback":
        healthy_triggers = ["salat", "wasser", "hähnchen", "apfel", "quark", "gemüse", "fisch", "reis"]
        unhealthy_triggers = ["cola", "pizza", "burger", "chips", "schokolade", "red bull", "döner", "süßigkeiten"]
        
        text_lower = topic.lower()
        if any(x in text_lower for x in healthy_triggers):
            return f"🟢 **Lob vom Coach:** Hervorragende Wahl! '{topic}' liefert genau die Mikronährstoffe und Energie, die dein Körper bei {st.session_state.gewicht}kg Gewicht für Muskeln und Gehirn braucht. Mach heute genau so weiter!"
        elif any(x in text_lower for x in unhealthy_triggers):
            return f"🔴 **Kritik vom Coach:** Achtung! '{topic}' bringt dir aktuell fast nur leere Kalorien und Zucker. Das sorgt für einen schnellen Crash beim Lernen und wirft dich bei deinen Fitness-Zielen zurück. Kontere das jetzt mit einem großen Glas Wasser!"
        else:
            return f"🟡 **Hinweis vom Coach:** '{topic}' ist als Zwischenmahlzeit okay. Achte aber darauf, über den restlichen Tag verteilt genug Proteine und unverarbeitete Lebensmittel einzubauen."

    elif mode == "tages_fazit":
        mahlzeiten = ", ".join(st.session_state.consumed_food) if st.session_state.consumed_food else "Keine Mahlzeiten eingetragen"
        
        # Dynamisches Feedback je nach Leistung
        if st.session_state.streak_lernen > 0 and st.session_state.streak_fitness > 0:
            status = "🔥 Absoluter Champion-Tag! Du hast sowohl für deinen Kopf als auch für deinen Körper geliefert. Die Streaks laufen!"
        elif st.session_state.streak_lernen == 0 and st.session_state.streak_fitness == 0:
            status = "⚠️ Achtung: Heute steht alles auf Null. Ein klassischer Durchhänger-Tag. Das muss morgen definitiv besser werden!"
        else:
            status = "⚖️ Halbe Kraft: Du hast heute einen Bereich geschafft, aber den anderen vernachlässigt. Balance ist wichtig!"

        return f"""
        # 📅 Deine abendliche Analyse
        
        ### 📋 Status-Check
        * **Dein Zustand:** {status}
        * **Lern-Streak:** {st.session_state