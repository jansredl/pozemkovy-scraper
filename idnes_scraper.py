
import requests
from bs4 import BeautifulSoup
import re
import time
import json
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
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return round(R * c, 1)

def geocode(address):
    try:
        params = {"q": address, "format": "json", "limit": 1}
        r = requests.get("https://nominatim.openstreetmap.org/search", params=params, headers=HEADERS, timeout=10)
        data = r.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except:
        return None, None
    return None, None

def parse_detail(url):
    r = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    text = soup.get_text(" ", strip=True).lower()

    title = soup.find("h1")
    vymera_match = re.search(r"(\d+)\s*m²", title.text) if title else None
    cena_match = re.search(r"(\d[\d\s]*)\s*kč", r.text)

    vymera = int(vymera_match.group(1)) if vymera_match else None
    cena = int(cena_match.group(1).replace(" ", "")) if cena_match else None

    lokalita = title.get_text(strip=True) if title else None
    fotky = len(soup.select("div.photo a img"))

    breadcrumbs = soup.select("ul.breadcrumb li")
    okres = breadcrumbs[-2].text.strip() if len(breadcrumbs) >= 2 else None
    kraj = breadcrumbs[-3].text.strip() if len(breadcrumbs) >= 3 else None

    lat, lon = geocode(f"{lokalita}, Česká republika")
    vzdalenost_km = haversine(NERATOVICE_LAT, NERATOVICE_LON, lat, lon) if lat and lon else None
    cesta_autem_min = round(vzdalenost_km / 0.75) if vzdalenost_km else None

    return {
        "lokalita": lokalita,
        "vymera": vymera,
        "cena": cena,
        "okres": okres,
        "kraj": kraj,
        "lat": lat,
        "lon": lon,
        "vzdalenost_od": "Neratovice",
        "vzdalenost_km": vzdalenost_km,
        "cesta_autem_min": cesta_autem_min,
        "sit_voda": "voda" in text or "vodovod" in text,
        "sit_cov": "čov" in text or "čistírna" in text,
        "sit_kanalizace": "kanalizace" in text,
        "sit_elektrina": "elektřina" in text or "230v" in text or "400v" in text,
        "mobilni_dum_vhodne": any(x in text for x in ["mobilní dům", "mobilheim", "tiny house"]),
        "cislo_parcely": None,
        "katastr": None,
        "uzemni_plan_url": None,
        "fotky": fotky,
        "odkaz": url,
        "zdroj": "reality.idnes.cz",
        "datum_zverejneni": datetime.today().strftime("%Y-%m-%d")
    }

def scrape_idnes_html(max_pages=2):
    base_url = "https://reality.idnes.cz/s/prodej/pozemky/stavebni-parcely/?price_to=1000000&page={}"
    results = []
    seen = set()

    for page in range(1, max_pages + 1):
        print(f"🔍 Načítám stránku {page}")
        r = requests.get(base_url.format(page), headers=HEADERS)
        soup = BeautifulSoup(r.text, "html.parser")
        links = soup.select("a[href*='/detail/prodej/pozemek/']")
        for a in links:
            href = a.get("href")
            full_url = "https://reality.idnes.cz" + href if href.startswith("/") else href
            if full_url not in seen:
                seen.add(full_url)
                try:
                    print(f"➡️ Zpracovávám: {full_url}")
                    result = parse_detail(full_url)
                    results.append(result)
                    time.sleep(1)
                except Exception as e:
                    print(f"❌ Chyba: {e}")
    print(f"✅ Hotovo – IDNES: {len(results)} inzerátů")
    return results

if __name__ == "__main__":
    data = scrape_idnes_html(max_pages=2)
    with open("idnes_pozemky.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
