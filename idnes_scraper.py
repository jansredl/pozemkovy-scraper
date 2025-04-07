
import requests
from bs4 import BeautifulSoup
import json
import re
import time
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2

HEADERS = {"User-Agent": "Mozilla/5.0"}
NERATOVICE_LAT = 50.2597
NERATOVICE_LON = 14.5162

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371
    lat1_rad, lon1_rad = radians(lat1), radians(lon1)
    lat2_rad, lon2_rad = radians(lat2), radians(lon2)
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = sin(dlat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance_km = R * c
    driving_time_min = distance_km / 50 * 60
    return round(distance_km), round(driving_time_min)

def geocode(address):
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": address, "format": "json", "limit": 1}
        r = requests.get(url, params=params, headers=HEADERS, timeout=10)
        data = r.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except:
        return None, None
    return None, None

def parse_listing(article):
    try:
        title_elem = article.select_one("h2.c-products__title")
        location_elem = article.select_one("p.c-products__info")
        price_elem = article.select_one("p.c-products__price strong")
        link_elem = article.select_one("a.c-products__link")
        img_elem = article.select_one("img")

        if not (title_elem and location_elem and price_elem and link_elem):
            return None

        vymera_match = re.search(r"(\d+)\s*m²", title_elem.text)
        cena_match = re.sub(r"[\s\xa0]", "", price_elem.text).replace("Kč", "")
        vymera = int(vymera_match.group(1)) if vymera_match else None
        cena = int(cena_match) if cena_match.isdigit() else None
        lokalita = location_elem.text.strip()
        url = link_elem["href"]
        if not url.startswith("http"):
            url = "https://reality.idnes.cz" + url

        if "podíl" in title_elem.text.lower() or "podíl" in location_elem.text.lower():
            return None

        lat, lon = geocode(f"{lokalita}, Česká republika")
        vzd_km, cesta_min = haversine_distance(lat, lon, NERATOVICE_LAT, NERATOVICE_LON) if lat and lon else (None, None)

        return {
            "lokalita": lokalita,
            "vymera": vymera,
            "cena": cena,
            "okres": None,
            "kraj": None,
            "lat": lat,
            "lon": lon,
            "vzdalenost_od": "Neratovice",
            "vzdalenost_km": vzd_km,
            "cesta_autem_min": cesta_min,
            "sit_voda": None,
            "sit_cov": None,
            "sit_kanalizace": None,
            "sit_elektrina": None,
            "mobilni_dum_vhodne": None,
            "cislo_parcely": None,
            "katastr": None,
            "uzemni_plan_url": None,
            "fotky": None,
            "odkaz": url,
            "zdroj": "reality.idnes.cz",
            "datum_zverejneni": datetime.today().strftime("%Y-%m-%d")
        }

    except Exception as e:
        print(f"Chyba při parsování inzerátu: {e}")
        return None

def scrape_idnes():
    results = []
    base_url = "https://reality.idnes.cz/s/prodej/pozemky/stavebni-pozemek/cena-do-1000000/"
    for page in range(1, 3):  # testujeme 2 stránky
        url = base_url if page == 1 else base_url + f"?page={page}"
        print(f"🔍 Načítám stránku: {url}")
        r = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(r.text, "html.parser")
        articles = soup.select("div.c-products__item article")
        for article in articles:
            item = parse_listing(article)
            if item:
                results.append(item)
        time.sleep(1)

    with open("idnes_pozemky.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"✅ Uloženo {len(results)} inzerátů")
    return results

if __name__ == "__main__":
    scrape_idnes()
