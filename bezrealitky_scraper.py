import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime

def scrape_bezrealitky():
    results = []
    base_url = "https://www.bezrealitky.cz/vypis/nabidka-prodej/pozemek/stredocechy?cena-najem-od=0&cena-najem-do=1000000&strana="

    for page in range(1, 51):  # předpoklad max 50 stránek, upravíme později podle reálného počtu
        print(f"📄 Bezrealitky.cz – stránka {page}")
        url = base_url + str(page)
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        offers = soup.select("a.PropertyPreview-Preview__link")
        if not offers:
            print("⛔ Konec výsledků.")
            break

        for offer in offers:
            href = offer.get("href")
            full_url = f"https://www.bezrealitky.cz{href}"

            # Zjednodušené parsování
            results.append({
                "lokalita": "Neznámá",
                "vymera": None,
                "cena": None,
                "okres": None,
                "lat": None,
                "lon": None,
                "vzdalenost_od": "Neratovice",
                "vzdalenost_km": None,
                "cesta_autem_min": None,
                "sit_voda": None,
                "sit_cov": None,
                "sit_kanalizace": None,
                "sit_elektrina": None,
                "mobilni_dum_vhodne": None,
                "cislo_parcely": None,
                "katastr": None,
                "uzemni_plan_url": None,
                "fotky": None,
                "odkaz": full_url,
                "zdroj": "bezrealitky.cz",
                "datum_zverejneni": datetime.today().strftime("%Y-%m-%d")
            })

        time.sleep(1)

    print(f"✅ Hotovo – Bezrealitky: nalezeno {len(results)} inzerátů")
    return results