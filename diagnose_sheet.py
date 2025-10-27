import gspread
from oauth2client.service_account import ServiceAccountCredentials

# KONFIGURATION
SHEET_NAME = "3 Matching Tabellen"
KEYFILE_PATH = "google-sheets-credentials.json"

def diagnose_sheet():
    """Diagnose-Funktion für das Google Sheet"""
    try:
        print("Starte Google Sheet Diagnose...")
        
        # Verbindung herstellen
        print("Verbinde mit Google Sheets...")
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/spreadsheets'
        ]
        credentials = ServiceAccountCredentials.from_json_keyfile_name(KEYFILE_PATH, scope)
        client = gspread.authorize(credentials)
        
        # Öffne die Tabelle mit dem korrekten Namen
        sheet = client.open(SHEET_NAME)
        print(f"Verbindung erfolgreich: '{SHEET_NAME}' geöffnet!")
        
        # Alle Worksheets (Tabs) anzeigen
        worksheets = sheet.worksheets()
        print(f"\nGefundene Worksheets ({len(worksheets)}):")
        for i, ws in enumerate(worksheets):
            print(f"  {i+1}. {ws.title} (ID: {ws.id})")
        
        # Das erste Worksheet genauer untersuchen
        if worksheets:
            ws = worksheets[0]
            print(f"\nUntersuche Worksheet: {ws.title}")
            
            # Hole alle Werte
            print("Hole alle Daten...")
            all_data = ws.get_all_values()
            print(f"Anzahl Zeilen: {len(all_data)}")
            
            if len(all_data) > 0:
                print(f"Anzahl Spalten in erster Zeile: {len(all_data[0])}")
            
            # Zeige die ersten 10 Zeilen an
            print("\nErste 10 Zeilen (oder weniger wenn nicht soviele vorhanden):")
            for i, row in enumerate(all_data[:10]):
                print(f"  Zeile {i+1}: {row}")
            
            # Suche nach wichtigen Schlüsselwörtern
            print("\nSuche nach wichtigen Schlüsselwörtern...")
            keywords = ["Weine", "Speisen", "Matching"]
            for keyword in keywords:
                found = False
                for i, row in enumerate(all_data):
                    for j, cell in enumerate(row):
                        if cell == keyword:
                            found = True
                            print(f"  '{keyword}' gefunden in Zeile {i+1}, Spalte {j+1} (Zelle {chr(65+j)}{i+1})")
                if not found:
                    print(f"  '{keyword}' wurde nicht gefunden!")
            
            # Prüfe, ob die Struktur so ist, wie der Code es erwartet
            print("\nPrüfe erwartete Struktur...")
            expected_structure = False
            
            for i, row in enumerate(all_data):
                if i < len(all_data) - 1 and row and row[0] == "Weine" and "Weinname" in all_data[i+1]:
                    print(f"  ✓ 'Weine' mit Header in Zeile {i+1}-{i+2} gefunden")
                    expected_structure = True
            
            if not expected_structure:
                print("  ✗ Die erwartete Struktur ('Weine' gefolgt von Header mit 'Weinname') wurde nicht gefunden!")
        
        print("\nDiagnose abgeschlossen!")
        
    except Exception as e:
        print(f"Fehler bei der Diagnose: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnose_sheet()