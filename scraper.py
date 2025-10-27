import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://www.vinum.eu/de/essen-trinken/food-pairing/"

headers = {
   'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
}

response = requests.get(url, headers=headers)
webpage = response.content

soup = BeautifulSoup(webpage, "html.parser")

selectors = [
   "div.teaser", 
   "div.article-item", 
   "div.food-pairing-item",
   "div.post",
   "div.entry",
   ".card",
   ".article"
]

data = []

for selector in selectors:
   items = soup.select(selector)
   print(f"Selector '{selector}' fand {len(items)} Elemente")
   
   if items:
       for item in items:
           title_element = item.find("h2") or item.find("h3") or item.find("h4") or item.find("a")
           title = title_element.text.strip() if title_element else "Kein Titel gefunden"
           
           link_element = title_element if title_element and title_element.name == "a" else item.find("a")
           link = link_element.get("href", "") if link_element else ""
           
           if link and not link.startswith(("http://", "https://")):
               link = f"https://www.vinum.eu{link}" if link.startswith("/") else f"https://www.vinum.eu/{link}"
           
           description_element = (
               item.find("div", class_="excerpt") or 
               item.find("div", class_="description") or 
               item.find("p") or 
               item.find("div", class_="content")
           )
           description = description_element.text.strip() if description_element else ""
           
           data.append({
               "title": title,
               "link": link,
               "description": description
           })

if not data:
   print("Versuche allgemeinen Ansatz...")
   all_links = soup.find_all("a")
   relevant_links = [link for link in all_links if "essen" in link.get("href", "").lower() or "trinken" in link.get("href", "").lower() or "wein" in link.get("href", "").lower()]
   
   for link in relevant_links:
       title = link.text.strip()
       url = link.get("href", "")
       if url and not url.startswith(("http://", "https://")):
           url = f"https://www.vinum.eu{url}" if url.startswith("/") else f"https://www.vinum.eu/{url}"
       
       data.append({
           "title": title,
           "link": url,
           "description": ""
       })

unique_data = []
seen_links = set()

for item in data:
   if item["link"] not in seen_links and item["title"].strip():
       seen_links.add(item["link"])
       unique_data.append(item)

df = pd.DataFrame(unique_data)
print(f"Insgesamt extrahierte einzigartige Datensätze: {len(df)}")

df.to_csv("vinum_food_pairing.csv", index=False, encoding="utf-8")
print("Daten wurden in vinum_food_pairing.csv gespeichert")