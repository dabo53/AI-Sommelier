import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

def read_google_sheets(credentials_path, spreadsheet_id):
    # Credentials laden
    creds = service_account.Credentials.from_service_account_file(
        credentials_path, 
        scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
    )
    
    # Google Sheets Service initialisieren
    sheets_service = build('sheets', 'v4', credentials=creds)
    
    # Spreadsheet Metadaten abrufen
    spreadsheet = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    
    # Alle Tabellennamen extrahieren
    sheet_names = [sheet['properties']['title'] for sheet in spreadsheet['sheets']]
    
    # Daten für jede Tabelle sammeln
    sheet_data = {}
    for sheet_name in sheet_names:
        # Daten aus der Tabelle abrufen
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, 
            range=sheet_name
        ).execute()
        
        # Werte extrahieren
        values = result.get('values', [])
        sheet_data[sheet_name] = values
    
    return sheet_data

def main():
    # Pfad zu Ihrer Credentials JSON-Datei
    CREDENTIALS_PATH = '/Users/davidpfeiffer/Desktop/AI/google-sheets-credentials.json'
    
    # ID Ihres Google Spreadsheets
    SPREADSHEET_ID = '1W2dkvm0VwR5C3iVpy0US8z8kQgPEvIbREJnCumtUR8U'
    
    # Sheets auslesen
    sheets_content = read_google_sheets(CREDENTIALS_PATH, SPREADSHEET_ID)
    
    # Daten ausgeben
    for sheet_name, data in sheets_content.items():
        print(f"Tabelle: {sheet_name}")
        for row in data:
            print(row)
        print("\n")

if __name__ == '__main__':
    main()