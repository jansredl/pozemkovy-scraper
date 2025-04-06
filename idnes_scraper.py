
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2

HEADERS = {"User-Agent": "Mozilla/5.0"}
NERATOVICE_LAT = 50.2597
NERATOVICE_LON = 14.5162

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return round(R * 2 * atan2(sqrt(a), sqrt(1 - a)), 1)

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

def scrape_idnes():
    base_url = "https://reality.idnes.cz/s/prodej/pozemky/stavebni-parcely/?price_to=1000000&page="
    results = []

    for page in range(1, 3):  # scraping only first 2 pages for now
        print(f"🔍 Procházím stránku {page}: {base_url}{page}")
        res = requests.get(base_url + str(page), headers=HEADERS)
        soup = BeautifulSoup(res.text, "html.parser")

        listings = soup.select("div.c-listing__item")
        for item in listings:
            try:
                title = item.select_one("h2").get_text(strip=True)
                link_tag = item.select_one("a.c-listing__link")
                url = link_tag["href"] if link_tag else None
                if not url:
                    continue

                location = title.split(" - ")[-1] if " - " in title else title
                vymera_match = re.search(r"(\d+)\s?m²", item.get_text())
                cena_match = re.search(r"(\d[\d\s]*)\s?Kč", item.get_text())

                vymera = int(vymera_match.group(1)) if vymera_match else None
                cena = int(cena_match.group(1).replace(" ", "")) if cena_match else None

                lat, lon = geocode(f"{location}, Česká republika")
                vzdalenost = haversine(NERATOVICE_LAT, NERATOVICE_LON, lat, lon) if lat and lon else None
                cesta_autem = round(vzdalenost / 0.75) if vzdalenost else None

                results.append({
                    "lokalita": location,
                    "vymera": vymera,
                    "cena": cena,
                    "okres": None,
                    "kraj": None,
                    "lat": lat,
                    "lon": lon,
                    "vzdalenost_od": "Neratovice",
                    "vzdalenost_km": vzdalenost,
                    "cesta_autem_min": cesta_autem,
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
                })
            except Exception as e:
                print(f"❌ Chyba u inzerátu: {e}")
    print(f"✅ idnes: nalezeno {len(results)} inzerátů")
    return results
