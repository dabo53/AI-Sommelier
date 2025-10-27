Python 3.12.1 (v3.12.1:2305ca5144, Dec  7 2023, 17:23:38) [Clang 13.0.0 (clang-1300.0.29.30)] on darwin
Type "help", "copyright", "credits" or "license()" for more information.
>>> from google.oauth2 import service_account
... from googleapiclient.discovery import build
... import pandas as pd
... 
... SERVICE_ACCOUNT_FILE = 'service-account.json'
... SPREADSHEET_ID = '1W2dkvm0VwR5C3iVpy0US8z8kQgPEvIbREJnCumtUR8U'
... 
... credentials = service_account.Credentials.from_service_account_file(
...     SERVICE_ACCOUNT_FILE,
...     scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
... )
... service = build('sheets', 'v4', credentials=credentials)
... 
... weine = service.spreadsheets().values().get(
...     spreadsheetId=SPREADSHEET_ID,
...     range='Tabellenblatt1!A1:F7'
... ).execute().get('values', [])
... 
... speisen = service.spreadsheets().values().get(
...     spreadsheetId=SPREADSHEET_ID,
...     range='Tabellenblatt1!A9:F15'
... ).execute().get('values', [])
... 
... matching = service.spreadsheets().values().get(
...     spreadsheetId=SPREADSHEET_ID,
...     range='Tabellenblatt1!A17:C22'
... ).execute().get('values', [])
... 
... print(weine)  
... print(speisen)  
... print(matching)
