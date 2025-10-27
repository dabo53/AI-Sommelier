from google.oauth2 import service_account
from googleapiclient.discovery import build

SERVICE_ACCOUNT_FILE = 'service-account.json'  # Pfad zur JSON-Datei
SPREADSHEET_ID = '1W2dkvm0VwR5C3iVpy0US8z8kQgPEvIbREJnCumtUR8U'  # Deine Sheet-ID
RANGE_NAME = 'Tabellenblatt1!A1:Z1000'  # Lesebereich

# Authentifizierung
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
)

# API-Client erstellen und Daten abrufen
try:
    service = build('sheets', 'v4', credentials=credentials)
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME
    ).execute()
    values = result.get('values', [])

    if not values:
        print("Keine Daten gefunden.")
    else:
        print("Erfolgreich! Erste Zeile:", values[0])  # Nur erste Zeile anzeigen

except Exception as e:
    print("FEHLER:", str(e))