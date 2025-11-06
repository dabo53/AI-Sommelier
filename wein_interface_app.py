import streamlit as st
import pandas as pd
from wein_matching import (
    verbinde_mit_google_sheets,
    finde_passenden_wein,
    zeige_ergebnisse,
    speichere_ergebnisse_in_sheet
)

# Verbindung zu Google Sheets herstellen
sheet = verbinde_mit_google_sheets()
weine_sheet = sheet.worksheet("Tabellenblatt4")
speisen_sheet = sheet.worksheet("Tabellenblatt5")

# Daten abrufen
weine_df = pd.DataFrame(weine_sheet.get_all_records())
speisen_df = pd.DataFrame(speisen_sheet.get_all_records())

SPEISEN_SPALTE = "Speisename"

# UI
st.title("🍷 AI-Sommelier: Weinempfehlungen")

speisen_liste = speisen_df[SPEISEN_SPALTE].tolist()
speisenauswahl = st.selectbox("Wähle eine Speise:", speisen_liste)

if speisenauswahl:
    matches = finde_passenden_wein(speisen_df, weine_df, speisenauswahl)
    top_matches = zeige_ergebnisse(matches)

    st.subheader("🌟 Top-Weine:")
    for i, match in enumerate(top_matches, 1):
        st.markdown(f"**{i}. {match['weinname']}**  ")
        st.markdown(f"Punkte: {match['punkte']}")
        if match['gründe']:
            with st.expander("Gründe anzeigen"):
                for grund in match['gründe']:
                    st.write(f"- {grund}")

    # Checkbox zum Speichern
    if st.checkbox("Ergebnisse im Google Sheet speichern"):
        speichere_ergebnisse_in_sheet(sheet, top_matches, speisenauswahl)
        st.success("Ergebnisse wurden gespeichert!")