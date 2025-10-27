import gspread
from oauth2client.service_account import ServiceAccountCredentials

SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
KEYFILE = "google-sheets-credentials.json"
SHEET_NAME = "3 Matching Tabellen"

creds = ServiceAccountCredentials.from_json_keyfile_name(KEYFILE, SCOPE)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1

print("✅ Verbindung erfolgreich! Erste Zeile:")
print(sheet.row_values(1))