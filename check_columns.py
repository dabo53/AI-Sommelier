import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# Konstanten
SHEET_NAME = "3 Matching Tabellen"
KEYFILE_PATH = "google-sheets-credentials.json"

def verbinde_und_zeige_spalten():
    """Verbindet mit Google Sheets und zeigt detaillierte Spalteninfos an"""
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/spreadsheets'
    ]
    credentials = ServiceAccountCredentials.from_json_keyfile_name(KEYFILE_PATH, scope)
    client = gspread.authorize(credentials)
    
    # Öffne die Tabelle
    sheet = client.open(SHEET_NAME)
    print(f"Verbindung erfolgreich: '{SHEET_NAME}' geöffnet!")
    
    # Das erste Worksheet verwenden
    worksheet = sheet.get_worksheet(0)
    all_data = worksheet.get_all_values()
    
    # Finde Abschnitte
    abschnitte = {}
    for i, row in enumerate(all_data):
        if row and row[0] == "Weine":
            abschnitte["Weine"] = i
        elif row and row[0] == "Speisen":
            abschnitte["Speisen"] = i
        elif row and row[0] == "Matching":
            abschnitte["Matching"] = i
    
    print(f"Gefundene Abschnitte: {abschnitte}")
    
    # Zeige Header für Weine
    if "Weine" in abschnitte:
        weine_header_row = abschnitte["Weine"] + 1
        if weine_header_row < len(all_data):
            weine_header = all_data[weine_header_row]
            print("\nWeine Header-Zeile:")
            print(f"Zeile {weine_header_row+1}: {weine_header}")
            for i, header in enumerate(weine_header):
                if header:
                    print(f"Spalte {chr(65+i)}: '{header}'")
    
    # Zeige Header für Speisen
    if "Speisen" in abschnitte:
        speisen_header_row = abschnitte["Speisen"] + 1
        if speisen_header_row < len(all_data):
            speisen_header = all_data[speisen_header_row]
            print("\nSpeisen Header-Zeile:")
            print(f"Zeile {speisen_header_row+1}: {speisen_header}")
            for i, header in enumerate(speisen_header):
                if header:
                    print(f"Spalte {chr(65+i)}: '{header}'")
    
    # Zeige erste Datenzeile für Speisen
    if "Speisen" in abschnitte:
        speisen_data_row = abschnitte["Speisen"] + 2
        if speisen_data_row < len(all_data):
            speisen_data = all_data[speisen_data_row]
            print("\nErste Speisen-Datenzeile:")
            print(f"Zeile {speisen_data_row+1}: {speisen_data}")
            for i, value in enumerate(speisen_data):
                if i < len(speisen_header) and speisen_header[i]:
                    print(f"'{speisen_header[i]}': '{value}'")

if __name__ == "__main__":
    verbinde_und_zeige_spalten()      