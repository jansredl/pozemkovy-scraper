
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def parse_price(text):
    match = re.search(r"(\d[\d\s]*)\s*Kč", text)
    if match:
        return int(match.group(1).replace(" ", ""))
    return None

def parse_area(text):
    match = re.search(r"(\d+)\s*m²", text)
    if match:
        return int(match.group(1))
    return None

def scrape_bezrealitky():
    base_url = "https://www.bezrealitky.cz"
    search_url = base_url + "/vypis/nabidka-prodej/pozemek"
    page = 1
    results = []

    while True:
        print(f"📄 Bezrealitky.cz – stránka {page}")
        url = f"{search_url}?page={page}&priceTo=1000000"
        res = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(res.text, "html.parser")

        cards = soup.select("div.property-list__item")
        if not cards:
            break  # konec

        for card in cards:
            title_el = card.select_one(".property-title")
            if not title_el:
                continue

            title = title_el.get_text(strip=True)
            link = card.select_one("a")["href"]
            full_link = base_url + link

            price_el = card.select_one(".property-price__price")
            price = parse_price(price_el.get_text(strip=True)) if price_el else None

            area = parse_area(title)

            locality = card.select_one(".property-location")
            lokalita = locality.get_text(strip=True) if locality else None

            if not (lokalita and price and area):
                continue

            results.append({
                "lokalita": lokalita,
                "vymera": area,
                "cena": price,
                "okres": None,
                "kraj": None,
                "lat": None,
                "lon": None,
                "vzdalenost_od": "Neratovice",
                "vzdalenost_km": None,
                "cesta_autem_min": None,
                "sit_voda": None,
                "sit_cov": None,
                "sit_kanalizace": None,
                "sit_elektrina": None,
                "mobilni_dum_vhodne": any(kw in title.lower() for kw in ["mobilní", "mobilheim", "tiny"]),
                "cislo_parcely": None,
                "katastr": None,
                "uzemni_plan_url": None,
                "fotky": None,
                "odkaz": full_link,
                "zdroj": "bezrealitky.cz",
                "datum_zverejneni": datetime.today().strftime("%Y-%m-%d")
            })

        page += 1
        time.sleep(1.0)

    print(f"✅ Bezrealitky.cz – nalezeno {len(results)} inzerátů")
    return results
