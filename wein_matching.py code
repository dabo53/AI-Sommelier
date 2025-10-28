import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import os

# KORREKTER SHEETNAME UND SPALTENNAME
SHEET_NAME = "3 Matching Tabellen"
KEYFILE_PATH = os.path.join(os.path.dirname(__file__), "google-sheets-credentials.json")
SPEISEN_SPALTE = "Speisename"  # Korrekt ohne "n" in der Mitte
SPEISEN_AROMA_SPALTE = "Aromaprofil"  # Korrekt ohne "i" am Ende

def verbinde_mit_google_sheets():
    """Verbindung mit Google Sheets herstellen"""
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
    
    return sheet

def hole_daten(sheet):
    """Hole Wein- und Speisendaten aus dem Tabellenblatt"""
    # Das erste Worksheet verwenden
    worksheet = sheet.get_worksheet(0)
    all_data = worksheet.get_all_values()
    
    # Weine und Speisen Abschnitte finden
    weine_start = None
    speisen_start = None
    matching_start = None
    
    # Durchsuche die Daten nach Abschnittsüberschriften
    for i, row in enumerate(all_data):
        if row and row[0] == "Weine":
            weine_start = i
        elif row and row[0] == "Speisen":
            speisen_start = i
        elif row and row[0] == "Matching":
            matching_start = i
    
    if weine_start is None or speisen_start is None:
        raise Exception("Konnte 'Weine' oder 'Speisen' Abschnitte nicht finden")
    
    # Extrahiere Weine-Header und Daten
    weine_header = all_data[weine_start + 1][:6]  # Header-Zeile nach "Weine"
    weine_data = []
    
    for i in range(weine_start + 2, speisen_start):
        if all_data[i][0] and all_data[i][0] != "Speisen":  # Überspringe leere Zeilen und Abschnittstitel
            weine_data.append(all_data[i][:6])
    
    # Extrahiere Speisen-Header und Daten
    speisen_header = all_data[speisen_start + 1][:6]  # Header-Zeile nach "Speisen"
    speisen_data = []
    
    # Finde das Ende des Speisen-Bereichs
    speisen_end = matching_start if matching_start else len(all_data)
    
    for i in range(speisen_start + 2, speisen_end):
        if all_data[i][0] and all_data[i][0] != "Matching":  # Überspringe leere Zeilen und Abschnittstitel
            speisen_data.append(all_data[i][:6])
    
    # Umwandeln in Pandas DataFrames
    weine_df = pd.DataFrame(weine_data, columns=weine_header)
    speisen_df = pd.DataFrame(speisen_data, columns=speisen_header)
    
    # Debug-Ausgabe
    print(f"\nGefundene Weine ({len(weine_df)} Einträge):")
    for i, wein in enumerate(weine_df['Weinname'], 1):
        print(f"  {i}. {wein}")
    
    print(f"\nGefundene Speisen ({len(speisen_df)} Einträge):")
    for i, speise in enumerate(speisen_df[SPEISEN_SPALTE], 1):
        print(f"  {i}. {speise}")
    
    return weine_df, speisen_df

def berechne_matching_punkte(speise, wein):
    """Berechnet Matching-Punkte zwischen einer Speise und einem Wein"""
    punkte = 0
    gründe = []
    
    # Regel 1: Aromaprofil-Kompatibilität
    if 'buttrig' in str(speise[SPEISEN_AROMA_SPALTE]) and 'nussig' in str(wein['Aromaprofil']):
        punkte += 1
        gründe.append("Nussiges Aroma ergänzt buttrige Note")
    
    if 'zitronig' in str(speise[SPEISEN_AROMA_SPALTE]) and 'mineralisch' in str(wein['Aromaprofil']):
        punkte += 1
        gründe.append("Mineralischer Wein unterstützt zitronige Noten")
    
    if 'fruchtig' in str(speise[SPEISEN_AROMA_SPALTE]) and 'fruchtig' in str(wein['Aromaprofil']):
        punkte += 2
        gründe.append("Fruchtaromen harmonieren")
        
    if 'kräutig' in str(speise[SPEISEN_AROMA_SPALTE]) and 'würzig' in str(wein['Aromaprofil']):
        punkte += 2
        gründe.append("Würziger Wein ergänzt kräutige Noten")
    
    # Regel 2: Säure-Balance
    if speise['Säure'] == wein['Säure']:
        punkte += 2
        gründe.append(f"Ausgeglichene Säure ({speise['Säure']})")
    
    # Regel 3: Süße-Kompatibilität
    if speise['Süße'] == wein['Süße']:
        punkte += 2
        gründe.append(f"Süße harmoniert ({speise['Süße']})")
    
    # Süß-trocken Kontrast
    if speise['Süße'] == 'hoch' and wein['Süße'] == 'niedrig':
        punkte += 1
        gründe.append("Süß-trocken Kontrast")
    
    # Regel 4: Fett und Tannin
    if speise['Fettgehalt'] == 'hoch' and wein['Tannin'] == 'hoch':
        punkte += 2
        gründe.append("Tannine schneiden durch das Fett")
    
    # Regel 5: Würze und Körper
    if speise['Würze'] == 'hoch' and (wein['Aromaprofil'] == 'würzig' or wein['Aromaprofil'] == 'vollmundig'):
        punkte += 1
        gründe.append("Würze wird ergänzt")
    
    # Regel 6: Farbharmonie
    # Rote Weine zu kräftigen Fleischgerichten
    if speise[SPEISEN_SPALTE] in ['Lammhaxe', 'Rinderfilet']:
        if wein['Farbe'] == 'rot':
            punkte += 2
            gründe.append("Rotwein passt gut zu kräftigem Fleisch")
    
    # Weiße Weine zu Fisch
    if speise[SPEISEN_SPALTE] == 'Kabeljau':
        if wein['Farbe'] == 'weiß':
            punkte += 2
            gründe.append("Weißwein ist klassisch zu Fisch")
    
    # Speziellere Paarungen aus deinem manuellen Matching
    # Ziegenkäse und Cloudy Bay
    if speise[SPEISEN_SPALTE] == 'Ziegenkäse' and wein['Weinname'] == 'Cloudy Bay':
        punkte += 1
        gründe.append("Fruchtige Noten ergänzen den Ziegenkäse")
    
    # Lammhaxe und Vieilles Vignes
    if speise[SPEISEN_SPALTE] == 'Lammhaxe' and wein['Weinname'] == 'Vieilles Vignes':
        punkte += 1
        gründe.append("Würziger Wein harmoniert mit kräutigem Lamm")
    
    # Rinderfilet und Cheval
    if speise[SPEISEN_SPALTE] == 'Rinderfilet' and wein['Weinname'] == 'Cheval':
        punkte += 1
        gründe.append("Vollmundiger Rotwein unterstützt das Rinderfilet")
    
    return punkte, gründe

def finde_passenden_wein(speisen_df, weine_df, speise_name):
    """Findet den passendsten Wein für eine gegebene Speise"""
    # Finde die Speise
    speise = speisen_df[speisen_df[SPEISEN_SPALTE] == speise_name]
    if speise.empty:
        return f"Speise '{speise_name}' nicht gefunden"
    
    speise = speise.iloc[0]
    
    # Matching für alle Weine berechnen
    matches = []
    for _, wein in weine_df.iterrows():
        punkte, gründe = berechne_matching_punkte(speise, wein)
        matches.append({
            'weinname': wein['Weinname'],
            'punkte': punkte,
            'gründe': gründe
        })
    
    # Nach Punkten sortieren
    matches.sort(key=lambda x: x['punkte'], reverse=True)
    return matches

def zeige_ergebnisse(matches, anzahl=3):
    """Zeigt die Top-Matches an"""
    if isinstance(matches, str):  # Fehlerfall
        print(matches)
        return []
        
    print(f"Top {min(anzahl, len(matches))} Weinempfehlungen:")
    print("=" * 50)
    
    for i, match in enumerate(matches[:anzahl], 1):
        print(f"{i}. {match['weinname']} ({match['punkte']} Punkte)")
        if match['gründe']:
            print("   Gründe:")
            for grund in match['gründe']:
                print(f"   - {grund}")
        print()
    
    return matches[:anzahl]

def finde_naechste_freie_zeile(all_data, start_index):
    """Ermittelt die nächste freie Zeile basierend auf der ersten Spalte."""
    next_row = max(start_index + 1, 0)
    total_rows = len(all_data)

    while next_row < total_rows:
        row = all_data[next_row] if next_row < total_rows else []
        first_cell = row[0] if row else ""
        if first_cell:
            next_row += 1
            continue
        break

    return next_row

def speichere_ergebnisse_in_sheet(sheet, matches, speise_name):
    """Speichert die Matching-Ergebnisse zurück in das Google Sheet mit verbesserter Fehlerbehandlung"""
    try:
        print(f"Versuche Ergebnisse zu speichern für Speise: {speise_name}")
        
        # Verwende das erste Worksheet
        worksheet = sheet.get_worksheet(0)
        print(f"Worksheet gefunden: {worksheet.title}")
        
        # Alle Daten abrufen, um die Struktur zu verstehen
        print("Hole alle Daten aus dem Worksheet...")
        all_data = worksheet.get_all_values()
        print(f"Anzahl Zeilen im Worksheet: {len(all_data)}")
        
        # Finde den Bereich für "Matching"
        matching_start = None
        
        for i, row in enumerate(all_data):
            if row and row[0] == "Matching":
                matching_start = i
                print(f"'Matching' gefunden in Zeile {i+1}")
                break
        
        if matching_start is None:
            print("Konnte 'Matching' nicht finden. Füge Ergebnisse am Ende ein.")
            matching_start = len(all_data) + 2
        
        # Finde die nächste freie Zeile im Matching-Bereich
        next_row_index = finde_naechste_freie_zeile(all_data, matching_start)
        
        print(f"Nächste freie Zeile: {next_row_index + 1}")  # +1 weil Google Sheets 1-basiert ist
        
        # Konvertiere zu Google Sheets Zeilennummer (1-basiert)
        next_row = next_row_index + 1  # 0-basiert zu 1-basiert
        
        # Speichere Datum und Uhrzeit des Matchings
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Überschrift für diesen Matching-Durchgang
        print(f"Füge Überschrift in Zeile {next_row} ein...")
        worksheet.update_cell(next_row, 1, f"Neues Matching für {speise_name} ({timestamp})")
        print("Überschrift eingefügt.")
        next_row += 1
        
        # Für jeden Match einen Eintrag anlegen
        print(f"Füge {len(matches)} Matches ein...")
        for i, match in enumerate(matches):
            current_row = next_row + i
            print(f"  Match {i+1}/{len(matches)} in Zeile {current_row}...")
            
            # Speise
            print(f"    Speichere Speise: {speise_name}")
            worksheet.update_cell(current_row, 1, speise_name)
            
            # Wein
            print(f"    Speichere Wein: {match['weinname']}")
            worksheet.update_cell(current_row, 2, match['weinname'])
            
            # Punktzahl
            print(f"    Speichere Punktzahl: {match['punkte']}")
            worksheet.update_cell(current_row, 3, match['punkte'])
            
            # Gründe
            if match['gründe']:
                grund_text = ", ".join(match['gründe'])
                print(f"    Speichere Gründe ({len(grund_text)} Zeichen)")
                worksheet.update_cell(current_row, 4, grund_text)
        
        print(f"Alle Ergebnisse für {speise_name} erfolgreich gespeichert!")
        
    except Exception as e:
        print(f"Fehler beim Speichern der Ergebnisse: {e}")
        import traceback
        traceback.print_exc()
def hauptprogramm():
    """Hauptfunktion des Programms"""
    # Prüfe, ob die Datei existiert
    if not os.path.exists(KEYFILE_PATH):
        print(f"Fehler: Die Datei {KEYFILE_PATH} wurde nicht gefunden.")
        return
matching_rules = []
try:
    # Verbindung einrichten
    print("Verbinde mit Google Sheets...")
    sheet = verbinde_mit_google_sheets()
    
    # Daten abrufen
    print("Hole Wein- und Speisendaten...")

    print("Hole Weindaten aus Tabellenblatt4...")
    weine_sheet = sheet.worksheet("Tabellenblatt4")
    weine_data = weine_sheet.get_all_records()

    print("Hole Speisendaten aus Tabellenblatt5...")
    speisen_sheet = sheet.worksheet("Tabellenblatt5")
    speisen_data = speisen_sheet.get_all_records()

    print("Hole Matching-Regeln aus Tabellenblatt6...")
    matching_sheet = sheet.worksheet("Tabellenblatt6")
    matching_rules = matching_sheet.get_all_records()

    print(f"\nGefundene Matching-Regeln ({len(matching_rules)} Einträge):")
    for index, rule in enumerate(matching_rules, 1):
        rule_name = (
            rule.get("Regelname")
            or rule.get("Regel")
            or rule.get("Name")
            or rule.get("Bezeichnung")
            or f"Regel #{index}"
        )

        detail_values = [
            str(value).strip()
            for key, value in rule.items()
            if key not in {"Regelname", "Regel", "Name", "Bezeichnung"} and str(value).strip()
        ]

        if detail_values:
            detail_text = " / ".join(detail_values)
            print(f"Regel geladen: {rule_name} → {detail_text}")
        else:
            print(f"Regel geladen: {rule_name}")

except Exception as e:
    print(f"❌ Fehler beim Abrufen der Daten: {e}")

import pandas as pd
weine_df = pd.DataFrame(weine_data)
speisen_df = pd.DataFrame(speisen_data)
        
# Zeige verfügbare Speisen
print("\nVerfügbare Speisen:")
for i, speise in enumerate(speisen_df[SPEISEN_SPALTE].tolist(), 1):
    print(f"{i}. {speise}")
        
# Benutzerauswahl
# Benutzerauswahl
try:
    while True:
        auswahl = input("\nWähle eine Speise (Nummer oder Name), oder 'alle' für alle Speisen, oder 'exit' zum Beenden: ")

        if auswahl.lower() == 'exit':
            break

        if auswahl.lower() == 'alle':
            # Für alle Speisen Matches finden
            for speise in speisen_df[SPEISEN_SPALTE].tolist():
                print(f"\nWeinempfehlungen für {speise}:")
                print("-" * 50)
                matches = finde_passenden_wein(speisen_df, weine_df, speise)
                top_matches = zeige_ergebnisse(matches)
                
                # Frage, ob Ergebnisse gespeichert werden sollen
                save = input("Ergebnisse im Google Sheet speichern? (j/n): ")
                if save.lower() == 'j':
                    speichere_ergebnisse_in_sheet(sheet, top_matches, speise)
        else:
            # Einzelne Speise auswählen
            try:
                if auswahl.isdigit():
                    # Wenn eine Nummer eingegeben wurde
                    speisen_liste = speisen_df[SPEISEN_SPALTE].tolist()
                    index = int(auswahl) - 1
                    if 0 <= index < len(speisen_liste):
                        speise_name = speisen_liste[index]
                    else:
                        print("Ungültige Nummer. Bitte wähle eine Nummer aus der Liste.")
                        continue
                else:
                    # Wenn ein Name eingegeben wurde
                    speise_name = auswahl
                    if speise_name not in speisen_df[SPEISEN_SPALTE].tolist():
                        print(f"Speise '{speise_name}' nicht gefunden. Bitte wähle aus der Liste.")
                        continue
                
                # Matching durchführen
                print(f"\nWeinempfehlungen für {speise_name}:")
                print("-" * 50)
                matches = finde_passenden_wein(speisen_df, weine_df, speise_name)
                top_matches = zeige_ergebnisse(matches)
                
                # Frage, ob Ergebnisse gespeichert werden sollen
                save = input("Ergebnisse im Google Sheet speichern? (j/n): ")
                if save.lower() == 'j':
                    speichere_ergebnisse_in_sheet(sheet, top_matches, speise_name)
                        
            except Exception as e:
                print(f"Fehler: {e}")
except Exception as e:
    print(f"Ein Fehler ist aufgetreten: {e}")
        
if __name__ == "__main__":
    hauptprogramm()
if __name__ == "__main__":
    from wein_matching import verbinde_mit_google_sheets, lade_matrix_daten

    sheet = verbinde_mit_google_sheets()
    matrices = lade_matrix_daten(sheet)

    print("✅ Geladene Matrizen:")
    for name in matrices.keys():
        print(" -", name)
