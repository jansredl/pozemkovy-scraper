
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from utils import geocode_address, haversine_distance

def scrape_idnes(max_pages=2):
    print("🟦 Spouštím scraper: idnes")
    results = []

    for page in range(1, max_pages + 1):
        if page == 1:
            url = "https://reality.idnes.cz/s/prodej/pozemky/stavebni-pozemek/cena-do-1000000/"
        else:
            url = f"https://reality.idnes.cz/s/prodej/pozemky/stavebni-pozemek/cena-do-1000000/?page={page}"

        print(f"🔍 Procházím stránku {page}: {url}")
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        articles = soup.select("article")  # HTML struktura inzerátů

        for article in articles:
            title_tag = article.select_one("h2 a")
            if not title_tag:
                continue

            odkaz = title_tag["href"]
            lokalita = title_tag.get_text(strip=True)
            info_text = article.get_text(" ", strip=True)

            cena_match = re.search(r"([\d\s]+)\s*Kč", info_text)
            vymera_match = re.search(r"(\d+)\s*m²", info_text)

            cena = int(cena_match.group(1).replace(" ", "")) if cena_match else None
            vymera = int(vymera_match.group(1)) if vymera_match else None

            if not (lokalita and cena and vymera):
                continue

            lat, lon = geocode_address(f"{lokalita}, Česká republika")
            vzdalenost_km, cesta_autem_min = haversine_distance(lat, lon)

            results.append({
                "lokalita": lokalita,
                "vymera": vymera,
                "cena": cena,
                "okres": "Neznámý",
                "kraj": "Neznámý",
                "lat": lat,
                "lon": lon,
                "vzdalenost_od": "Neratovice",
                "vzdalenost_km": vzdalenost_km,
                "cesta_autem_min": cesta_autem_min,
                "sit_voda": None,
                "sit_cov": None,
                "sit_kanalizace": None,
                "sit_elektrina": None,
                "mobilni_dum_vhodne": None,
                "cislo_parcely": None,
                "katastr": None,
                "uzemni_plan_url": None,
                "fotky": None,
                "odkaz": odkaz,
                "zdroj": "reality.idnes.cz",
                "datum_zverejneni": datetime.today().strftime("%Y-%m-%d")
            })

    print(f"✅ idnes: nalezeno {len(results)} inzerátů")
    return results
