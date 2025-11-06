from typing import Dict, List, Tuple

import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials


# --- Konfiguration ---
SHEET_NAME = "3 Matching Tabellen"
SPEISEN_SPALTE = "Speisename"

INTENSITAETS_MAP = {"niedrig": 0, "mittel": 1, "hoch": 2}
SUESSE_MAP = {"niedrig": 0, "mittel": 1, "hoch": 2}

FISCH_KEYWORDS = [
    "fisch",
    "lachs",
    "garnelen",
    "garnele",
    "austern",
    "hamachi",
    "hummer",
    "seeteufel",
    "steinbutt",
    "kabeljau",
    "garnele",
    "auster",
    "sea",
]
GEFLUEGEL_KEYWORDS = [
    "ente",
    "enten",
    "wachtel",
    "huhn",
    "hähn",
    "huhn",
    "poularde",
]
ROTES_FLEISCH_KEYWORDS = [
    "rind",
    "rinder",
    "kalb",
    "reh",
    "lamm",
    "striploin",
    "steak",
    "vieh",
    "beef",
    "ragout",
]
DESSERT_KEYWORDS = ["dessert", "tarte", "kuchen", "pie", "eis", "süß", "sweet"]
VEGETARISCH_KEYWORDS = [
    "salat",
    "kürbis",
    "kohlrabi",
    "spätzle",
    "gemüse",
    "veggie",
]


# --- Helper & Caching ---
@st.cache_resource(show_spinner=False)
def get_gspread_client() -> gspread.Client:
    scopes = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/spreadsheets",
    ]
    creds_info = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
    return gspread.authorize(creds)


@st.cache_data(show_spinner=False)
def lade_daten() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    client = get_gspread_client()
    sheet = client.open(SHEET_NAME)
    weine_df = pd.DataFrame(sheet.worksheet("Tabellenblatt4").get_all_records())
    speisen_df = pd.DataFrame(sheet.worksheet("Tabellenblatt5").get_all_records())
    regeln_df = pd.DataFrame(sheet.worksheet("Tabellenblatt6").get_all_records())
    return weine_df, speisen_df, regeln_df


def klassifiziere_speiseart(name: str) -> str:
    lower = name.lower()
    if any(keyword in lower for keyword in DESSERT_KEYWORDS):
        return "dessert"
    if any(keyword in lower for keyword in FISCH_KEYWORDS):
        return "fisch"
    if any(keyword in lower for keyword in ROTES_FLEISCH_KEYWORDS):
        return "rotes_fleisch"
    if any(keyword in lower for keyword in GEFLUEGEL_KEYWORDS):
        return "gefluegel"
    if any(keyword in lower for keyword in VEGETARISCH_KEYWORDS):
        return "vegetarisch"
    return "unbekannt"


def wert_map(mapper: Dict[str, int], value: str) -> int:
    return mapper.get(str(value).strip().lower(), 0)


def alkohol_level(value: object) -> str:
    """Return qualitative alcohol level for numeric or textual inputs."""
    if value is None or pd.isna(value):
        return "mittel"

    if isinstance(value, (int, float)):
        numeric = float(value)
    else:
        value_str = str(value).strip().lower()
        if value_str in INTENSITAETS_MAP:
            return value_str
        cleaned = value_str.replace("%", "").replace(",", ".")
        try:
            numeric = float(cleaned)
        except ValueError:
            return "mittel"

    if numeric < 12.0:
        return "niedrig"
    if numeric >= 13.5:
        return "hoch"
    return "mittel"


def baue_regel_lookup(regeln_df: pd.DataFrame) -> Dict[str, Dict[str, str]]:
    lookup: Dict[str, Dict[str, str]] = {}
    for _, row in regeln_df.iterrows():
        if not row.get("Kategorie"):
            continue
        lookup[row["Kategorie"]] = row.to_dict()
    return lookup


def berechne_match(
    speise: pd.Series,
    wein: pd.Series,
    regel_lookup: Dict[str, Dict[str, str]],
) -> Dict[str, object]:
    score = 0
    details: List[Dict[str, str]] = []

    speise_art = klassifiziere_speiseart(speise[SPEISEN_SPALTE])
    speise_fett = wert_map(INTENSITAETS_MAP, speise.get("Fettgehalt", "mittel"))
    speise_wuerze = wert_map(INTENSITAETS_MAP, speise.get("Würze", "mittel"))
    speise_intensitaet = max(speise_fett, speise_wuerze)

    wein_koerper = wert_map(INTENSITAETS_MAP, wein.get("Körper", "mittel"))
    wein_saeure = wert_map(INTENSITAETS_MAP, wein.get("Säure", "mittel"))
    wein_suesse = wert_map(SUESSE_MAP, wein.get("Süße", "niedrig"))
    wein_tannin = wert_map(INTENSITAETS_MAP, wein.get("Tannin", "niedrig"))
    wein_farbe = str(wein.get("Farbe", "")).lower()
    wein_alkohol_wert = alkohol_level(wein.get("Alkoholgehalt", "mittel"))
    wein_alkohol = wert_map(INTENSITAETS_MAP, wein_alkohol_wert)

    aromaprofil = str(speise.get("Aromaprofil", "")).lower()
    speise_saeure = wert_map(INTENSITAETS_MAP, speise.get("Säure", "mittel"))
    speise_suesse = wert_map(SUESSE_MAP, speise.get("Süße", "niedrig"))

    def fuege_regel_hinzu(kategorie: str, delta: int, erklaerung: str) -> None:
        nonlocal score
        if delta == 0:
            return
        score += delta
        info = regel_lookup.get(kategorie, {})
        details.append(
            {
                "Kategorie": kategorie,
                "Punkte": f"{delta:+d}",
                "Erklärung": erklaerung,
                "Regelbeschreibung": info.get("Regelbeschreibung", ""),
                "Quelle": info.get("Quelle", ""),
            }
        )

    # Intensitätsabgleich
    diff_intensitaet = abs(speise_intensitaet - wein_koerper)
    if diff_intensitaet == 0:
        fuege_regel_hinzu(
            "Intensitätsabgleich (Gewicht)",
            2,
            "Körper und Intensität von Speise und Wein sind ausbalanciert.",
        )
    elif diff_intensitaet >= 2:
        fuege_regel_hinzu(
            "Intensitätsabgleich (Gewicht)",
            -2,
            "Gewicht von Speise und Wein driftet stark auseinander.",
        )

    # Weinfarbe & Speiseart
    if speise_art in {"fisch", "gefluegel", "vegetarisch"}:
        if wein_farbe in {"weiß", "schaumwein"}:
            fuege_regel_hinzu(
                "Weinfarbe & Speiseart",
                2,
                "Helles Gericht mit hellem/Schaumwein kombiniert.",
            )
        elif wein_farbe == "rot" and wein_tannin >= 1:
            fuege_regel_hinzu(
                "Weinfarbe & Speiseart",
                -2,
                "Roter, tanninreicher Wein kann helle Speisen überlagern.",
            )
    elif speise_art == "rotes_fleisch":
        if wein_farbe == "rot":
            fuege_regel_hinzu(
                "Weinfarbe & Speiseart",
                2,
                "Kräftiges Fleisch verlangt nach Rotwein.",
            )
        elif wein_farbe in {"weiß", "schaumwein"}:
            fuege_regel_hinzu(
                "Weinfarbe & Speiseart",
                -2,
                "Helle Weine liefern zu wenig Struktur für rotes Fleisch.",
            )

    # Säure-Balance
    if wein_saeure >= speise_saeure:
        fuege_regel_hinzu(
            "Säure-Balance",
            2,
            "Wein hat gleiche oder höhere Säure als die Speise.",
        )
    else:
        fuege_regel_hinzu(
            "Säure-Balance",
            -2,
            "Säure des Weins reicht nicht an die Speise heran.",
        )

    # Säure-Fett
    if speise_fett >= 2:
        if wein_saeure >= 2:
            fuege_regel_hinzu(
                "Säure-Fett",
                2,
                "Hoher Fettgehalt wird durch hohe Säure balanciert.",
            )
        elif wein_saeure == 0:
            fuege_regel_hinzu(
                "Säure-Fett",
                -2,
                "Fettige Speise trifft auf säurearmen Wein.",
            )

    # Tannin vs Fett
    if speise_art == "rotes_fleisch" or speise_fett >= 2:
        if wein_tannin >= 2:
            fuege_regel_hinzu(
                "Tannin vs Fett",
                2,
                "Stramme Tannine schneiden durch Fett/Protein.",
            )

    # Tannin vs Fisch
    if speise_art == "fisch" and wein_tannin >= 1:
        fuege_regel_hinzu(
            "Tannin vs Fisch",
            -2,
            "Tanninreicher Rotwein macht Fisch metallisch.",
        )

    # Süße-Balance
    if speise_suesse >= 2:
        if wein_suesse >= speise_suesse:
            fuege_regel_hinzu(
                "Süße-Balance",
                2,
                "Süße Speise mit genügend Restsüße im Wein abgeholt.",
            )
        else:
            fuege_regel_hinzu(
                "Süße-Balance",
                -2,
                "Süße Speise lässt trockenen Wein flach wirken.",
            )
    elif speise_suesse == 0 and wein_suesse == 0:
        fuege_regel_hinzu(
            "Süße-Balance",
            1,
            "Trockene Speise und trockener Wein harmonieren.",
        )

    # Salz
    if "salzig" in aromaprofil:
        if wein_tannin >= 1:
            fuege_regel_hinzu(
                "Salz",
                2,
                "Salz puffert Tannin – passt gut zu strukturreichem Wein.",
            )

    # Umami
    if "umami" in aromaprofil:
        if wein_tannin >= 2:
            fuege_regel_hinzu(
                "Umami",
                -2,
                "Umami verstärkt Tannin – milderer Wein wäre besser.",
            )
        elif wein_tannin == 0:
            fuege_regel_hinzu(
                "Umami",
                1,
                "Feines Umami profitiert von sanftem Tanninprofil.",
            )

    # Würze/Schärfe
    if speise_wuerze >= 2 or "scharf" in aromaprofil:
        if wein_suesse >= 1:
            fuege_regel_hinzu(
                "Würze/Schärfe",
                2,
                "Restsüße mildert Schärfe der Speise.",
            )
        if wein_alkohol >= 2:
            fuege_regel_hinzu(
                "Würze/Schärfe",
                -1,
                "Hoher Alkohol kann Schärfe verstärken.",
            )

    # Bitterkeit
    if "herb" in aromaprofil or "bitter" in aromaprofil:
        if wein_tannin >= 2:
            fuege_regel_hinzu(
                "Bitterkeit",
                -2,
                "Bittere Komponenten plus Tannin können hart wirken.",
            )
        elif wein_tannin == 0:
            fuege_regel_hinzu(
                "Bitterkeit",
                1,
                "Feines Tannin vermeidet zusätzliche Bitterkeit.",
            )

    # Textur
    if "cremig" in aromaprofil or "buttrig" in aromaprofil:
        if wein_farbe == "schaumwein" or wein_saeure >= 2:
            fuege_regel_hinzu(
                "Textur",
                1,
                "Prickelnde/straffe Struktur setzt cremige Speise in Szene.",
            )

    # Temperatur (nur weiche Gewichtung)
    if wein_farbe == "schaumwein" and speise_art in {"fisch", "vegetarisch"}:
        fuege_regel_hinzu(
            "Temperatur",
            1,
            "Gekühlter Schaumwein hält leichte Speise frisch.",
        )

    return {
        "weinname": wein.get("Weinname", "Unbekannt"),
        "punkte": score,
        "gründe": details,
    }


def berechne_top_matches(
    speisen_df: pd.DataFrame,
    weine_df: pd.DataFrame,
    regeln_df: pd.DataFrame,
    speise_name: str,
) -> List[Dict[str, object]]:
    if speise_name not in speisen_df[SPEISEN_SPALTE].values:
        raise ValueError(f"Speise '{speise_name}' nicht gefunden.")

    speise = speisen_df[speisen_df[SPEISEN_SPALTE] == speise_name].iloc[0]
    regel_lookup = baue_regel_lookup(regeln_df)

    matches: List[Dict[str, object]] = []
    for _, wein in weine_df.iterrows():
        result = berechne_match(speise, wein, regel_lookup)
        matches.append(result)

    matches.sort(key=lambda item: item["punkte"], reverse=True)
    return matches[:3]


# --- Streamlit UI ---
st.title("🍷 AI Sommelier Matching")
st.markdown("Wähle eine Speise und erhalte datenbasierte Weinempfehlungen.")

try:
    weine_df, speisen_df, regeln_df = lade_daten()
except Exception as exc:  # pragma: no cover - UI Feedback
    st.error(f"❌ Daten konnten nicht geladen werden: {exc}")
    st.stop()

if speisen_df.empty or weine_df.empty:
    st.warning("Keine Daten in den Google Sheets gefunden.")
    st.stop()

speise_name = st.selectbox("Speise auswählen", speisen_df[SPEISEN_SPALTE].tolist())

if st.button("🔍 Weinempfehlungen anzeigen"):
    with st.spinner("Berechne Empfehlungen..."):
        try:
            top_matches = berechne_top_matches(speisen_df, weine_df, regeln_df, speise_name)
        except Exception as exc:
            st.error(f"⚠️ Matching fehlgeschlagen: {exc}")
        else:
            if not top_matches:
                st.info("Für diese Speise wurden keine passenden Weine gefunden.")
            else:
                st.subheader(f"Top {len(top_matches)} Empfehlungen für: {speise_name}")
                for match in top_matches:
                    punkte = match["punkte"]
                    st.markdown(f"**{match['weinname']}** — {punkte} Punkte")
                    if match["gründe"]:
                        st.markdown("Gründe:")
                        for eintrag in match["gründe"]:
                            st.markdown(
                                f"- {eintrag['Kategorie']}: {eintrag['Erklärung']} ({eintrag['Punkte']})"
                            )
                    with st.expander(f"Debug: Bewertung für {match['weinname']}"):
                        st.dataframe(pd.DataFrame(match["gründe"]))

    with st.expander("Debug: Speisendetails"):
        st.json(
            speisen_df[speisen_df[SPEISEN_SPALTE] == speise_name].iloc[0].to_dict()
        )
