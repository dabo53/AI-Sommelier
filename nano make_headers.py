import os, base64, datetime
from PIL import Image
import google.genai as genai

API_KEY = os.environ["GOOGLE_API_KEY"]  # ist gesetzt (True)
MODEL = "gemini-2.5-flash-image"        # Bildmodell
N_VARIANTS = 5
SIZE = "1200x400"                       # Breite x Höhe
INPUT_IMAGE_PATH = "input_header.jpg"   # <-- dein Referenzbild hier ablegen
OUTPUT_DIR = "outputs_headers"

def ensure_dir(p):
    os.makedirs(p, exist_ok=True)

def main():
    ensure_dir(OUTPUT_DIR)
    client = genai.Client(api_key=API_KEY)

    with open(INPUT_IMAGE_PATH, "rb") as f:
        ref_bytes = f.read()

    prompt = f"""
Erzeuge {N_VARIANTS} alternative Newsletter-Header-Designs (1200x400) auf Basis des Referenzbildes.
Jede Variante klar unterscheidbar. CI-Rot #A21C1C verwenden.
1) modern minimalistisch (ohne Wappen, große weiße Typo, Claim links),
2) klassisch-edel (mit Wappen, goldene Nuance, ohne Claim),
3) emotional/sonnig (Sonnenstimmung, kleiner Claim mittig),
4) grafisch/verspielt (Wappen rechts dominant, rote Flächen),
5) typografisch stark (Claim im Fokus, Hintergrund leicht abgedunkelt).
Bildformat strikt 1200x400 beibehalten.
""".strip()

    resp = client.images.generate(
        model=MODEL,
        prompt=prompt,
        images=[{"mime_type": "image/jpeg", "data": ref_bytes}],
        n=N_VARIANTS,
        size=SIZE,
    )

    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    saved = []
    for i, img in enumerate(resp.images, start=1):
        data = base64.b64decode(img.data) if isinstance(img.data, str) else img.data
        out_path = os.path.join(OUTPUT_DIR, f"header_variant_{i}_{ts}.jpg")
        with open(out_path, "wb") as f:
            f.write(data)
        # auf Zielgröße normalisieren (falls Modell minimal abweicht)
        im = Image.open(out_path).convert("RGB")
        im = im.resize((1200, 400), Image.Resampling.LANCZOS)
        im.save(out_path, "JPEG", quality=92, optimize=True)
        saved.append(out_path)

    print("\nFertig ✅ Varianten gespeichert:")
    for p in saved:
        print(" •", p)

if __name__ == "__main__":
    main()