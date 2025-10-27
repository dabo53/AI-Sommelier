from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd

SERVICE_ACCOUNT_FILE = 'service-account.json'
SPREADSHEET_ID = '1W2dkvm0VwR5C3iVpy0US8z8kQgPEvIbREJnCumtUR8U'

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
)
service = build('sheets', 'v4', credentials=credentials)

sheet_metadata = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
for sheet in sheet_metadata['sheets']:
    print(sheet['properties']['title'])

weine = service.spreadsheets().values().get(
    spreadsheetId=SPREADSHEET_ID,
    range='Tabellenblatt1!A1:F7'
).execute().get('values', [])

speisen = service.spreadsheets().values().get(
    spreadsheetId=SPREADSHEET_ID,
    range='Tabellenblatt1!A9:F15'
).execute().get('values', [])

matching = service.spreadsheets().values().get(
    spreadsheetId=SPREADSHEET_ID,
    range='Tabellenblatt1!A17:C22'
).execute().get('values', [])

df_weine = pd.DataFrame(weine[1:7], columns=weine[0][:6]) if weine and len(weine[0]) == 6 else pd.DataFrame()
df_speisen = pd.DataFrame(speisen[1:7], columns=speisen[0][:6]) if speisen and len(speisen[0]) == 6 else pd.DataFrame()
df_matching = pd.DataFrame(matching[1:6], columns=matching[0][:3]) if matching and len(matching[0]) == 3 else pd.DataFrame()

print(df_matching[df_matching['Matching-Punkte-Formel'].astype(int) >= 7])