import functions_framework
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

@functions_framework.http
def wine_pairing(request):
    request_json = request.get_json(silent=True)
    menu_text = request_json.get("menu", "")

    prompt = f"Welcher Wein passt zu diesem Gericht? {menu_text}"

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content