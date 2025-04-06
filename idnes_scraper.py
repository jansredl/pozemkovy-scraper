import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
import time

HEADERS = {"User-Agent": "Mozilla/5.0"}
NERATOVICE_LAT = 50.2597
NERATOVICE_LON = 14.5162

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

def haversine(lat1, lon1, lat2, lon2):
    from math import radians, sin, cos, sqrt, atan2
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return round(R * 2 * atan2(sqrt(a), sqrt(1 - a)), 1)

def is_podil(text):
    return any(podil in text.lower() for podil in ["1/", "1\", "1⁄", "polovina", "spoluvlastnictví", "ideální", "část"])

def scrape_idnes(max_pages=2):
    results = []
    for page in range(1, max_pages + 1):
        url = f"https://reality.idnes.cz/s/prodej/pozemky/stavebni-pozemek/cena-do-1000000/?page={page}"
        print(f"🔎 Načítám stránku {page}: {url}")
        r = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(r.text, "html.parser")
        articles = soup.select("article")

        for art in articles:
            title_tag = art.find("h2")
            if not title_tag or "pozemku" not in title_tag.text.lower():
                continue
            title = title_tag.text.strip().lower()
            if is_podil(title):
                continue

            size_match = re.search(r"(\d+)[\s\xa0]*m²", title)
            vymera = int(size_match.group(1)) if size_match else None

            price_tag = art.select_one(".c-products__price strong")
            cena = int(re.sub(r"[^\d]", "", price_tag.text)) if price_tag else None

            loc_tag = art.select_one(".c-products__info")
            lokalita_full = loc_tag.text.strip() if loc_tag else None
            lokalita = lokalita_full.split(",")[0] if lokalita_full else None
            okres = lokalita_full.split(",")[1].strip() if lokalita_full and "," in lokalita_full else None

            href_tag = art.select_one("a.c-products__link")
            odkaz = href_tag["href"] if href_tag else None
            if odkaz and not odkaz.startswith("http"):
                odkaz = "https://reality.idnes.cz" + odkaz

            fotky = 1

            lat, lon = geocode(f"{lokalita}, {okres}, Česká republika") if lokalita and okres else (None, None)
            vzdalenost = haversine(NERATOVICE_LAT, NERATOVICE_LON, lat, lon) if lat and lon else None
            cesta_autem_min = round(vzdalenost / 0.75) if vzdalenost else None

            results.append({
                "lokalita": lokalita,
                "vymera": vymera,
                "cena": cena,
                "okres": okres,
                "kraj": None,
                "lat": lat,
                "lon": lon,
                "vzdalenost_od": "Neratovice",
                "vzdalenost_km": vzdalenost,
                "cesta_autem_min": cesta_autem_min,
                "sit_voda": None,
                "sit_cov": None,
                "sit_kanalizace": None,
                "sit_elektrina": None,
                "mobilni_dum_vhodne": None,
                "cislo_parcely": None,
                "katastr": None,
                "uzemni_plan_url": None,
                "fotky": fotky,
                "odkaz": odkaz,
                "zdroj": "reality.idnes.cz",
                "datum_zverejneni": datetime.today().strftime("%Y-%m-%d")
            })

            time.sleep(1.0)
    return results

if __name__ == "__main__":
    data = scrape_idnes(max_pages=2)
    with open("pozemky.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
