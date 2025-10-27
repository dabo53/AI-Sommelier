import anthropic
from anthropic import Anthropic

# Ersetze dies mit deinem tatsächlichen API-Schlüssel
API_KEY = "dein-api-key-hier"

def get_claude_wine_recommendation(speise_name, speise_eigenschaften):
    """Verwendet Claude, um eine natürlichsprachliche Weinempfehlung zu generieren"""
    client = Anthropic(api_key=API_KEY)
    
    # Erstelle eine detaillierte Anfrage an Claude
    prompt = f"""
    Als erfahrener Sommelier, empfehle einen passenden Wein für folgende Speise:
    
    Speise: {speise_name}
    Eigenschaften:
    - Aromaprofil: {speise_eigenschaften['Aromaprofil']}
    - Fettgehalt: {speise_eigenschaften['Fettgehalt']}
    - Säuregehalt: {speise_eigenschaften['Säure']}
    - Würzigkeit: {speise_eigenschaften['Würze']}
    - Süße: {speise_eigenschaften['Süße']}
    
    Erkläre detailliert, warum der Wein gut zu dieser Speise passt, und gib spezifische 
    Empfehlungen für Rebsorten oder Weinstile.
    """
    
    response = client.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.content[0].text

# Beispiel für die Verwendung
speise_name = "Lammhaxe"
speise_eigenschaften = {
    "Aromaprofil": "kräutig-herzhaft",
    "Fettgehalt": "hoch",
    "Säure": "mittel",
    "Würze": "hoch",
    "Süße": "niedrig"
}

# Hole Empfehlung von Claude
print(f"Weinempfehlung für {speise_name}:")
print("-" * 50)
empfehlung = get_claude_wine_recommendation(speise_name, speise_eigenschaften)
print(empfehlung)