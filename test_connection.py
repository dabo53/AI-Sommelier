import gspread
from oauth2client.service_account import ServiceAccountCredentials
import sys
import traceback

# Detaillierte Fehlermeldungen aktivieren
def detailed_exception_hook(exc_type, exc_value, exc_traceback):
    print("\n*** DETAILLIERTE FEHLERMELDUNG ***")
    print("".join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
    print("*** ENDE DER FEHLERMELDUNG ***\n")

sys.excepthook = detailed_exception_hook

# Konstanten
KEYFILE_PATH = "google-sheets-credentials.json"
SHEET_NAME = "3 Matching Tabellen“

def test_connection():
    print(f"Test 1: Basisverbindung mit Google Auth")
    print("-" * 50)
    try:
        # Schritt 1: Authentifizierung testen
        print("Authentifiziere mit den Anmeldeinformationen...")
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/spreadsheets'
        ]
        credentials = ServiceAccountCredentials.from_json_keyfile_name(KEYFILE_PATH, scope)
        client = gspread.authorize(credentials)
        print("✓ Authentifizierung erfolgreich!")
        
        # Schritt 2: Liste aller verfügbaren Sheets anzeigen
        print("\nTest 2: Liste aller verfügbaren Sheets")
        print("-" * 50)
        print("Hole Liste aller Sheets...")
        available_sheets = list(client.openall())
        
        if available_sheets:
            print(f"✓ {len(available_sheets)} Sheets gefunden:")
            for i, s in enumerate(available_sheets, 1):
                print(f"  {i}. {s.title} (ID: {s.id})")
        else:
            print("⚠ Keine Sheets gefunden!")
            print("Bitte überprüfe, ob der Service-Account Zugriff auf Sheets hat.")
            return
        
        # Schritt 3: Versuche, das spezifische Sheet zu öffnen
        print(f"\nTest 3: Öffne das Sheet '{SHEET_NAME}'")
        print("-" * 50)
        print(f"Versuche '{SHEET_NAME}' zu öffnen...")
        
        try:
            sheet = client.open(SHEET_NAME)
            print(f"✓ '{SHEET_NAME}' erfolgreich geöffnet! (ID: {sheet.id})")
            
            # Worksheets auflisten
            worksheets = sheet.worksheets()
            print(f"Gefundene Worksheets: {[ws.title for ws in worksheets]}")
            
            # Teste das Lesen von Daten
            if worksheets:
                print("\nTest 4: Lese Daten aus dem ersten Worksheet")
                print("-" * 50)
                ws = worksheets[0]
                print(f"Lese Daten aus '{ws.title}'...")
                values = ws.get_all_values()
                print(f"✓ {len(values)} Zeilen gelesen!")
                print(f"Beispieldaten (erste Zeile): {values[0]}")
        except gspread.exceptions.SpreadsheetNotFound:
            print(f"⚠ Sheet '{SHEET_NAME}' nicht gefunden!")
            
            # Versuch mit einem verfügbaren Sheet
            if available_sheets:
                first_sheet = available_sheets[0]
                print(f"\nVersuche stattdessen '{first_sheet.title}' zu öffnen...")
                
                worksheets = first_sheet.worksheets()
                print(f"Gefundene Worksheets: {[ws.title for ws in worksheets]}")
                
                if worksheets:
                    ws = worksheets[0]
                    print(f"Lese Daten aus '{ws.title}'...")
                    values = ws.get_all_values()
                    print(f"✓ {len(values)} Zeilen gelesen!")
                    print(f"Beispieldaten (erste Zeile): {values[0]}")
                    
                print("\n⚠ WICHTIG: Bitte überprüfe die Groß-/Kleinschreibung des Sheetnamens!")
                print(f"Der gesuchte Name war: '{SHEET_NAME}'")
                print(f"Verfügbare Namen sind: {[s.title for s in available_sheets]}")
    
    except Exception as e:
        print(f"❌ Fehler aufgetreten: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Google Sheets Verbindungstest")
    print("=============================")
    print(f"Keyfile: {KEYFILE_PATH}")
    print(f"Ziel-Sheet: {SHEET_NAME}")
    print("=============================\n")
    
    test_connection()