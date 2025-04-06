import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime
import time
from math import radians, sin, cos, sqrt, atan2

HEADERS = {"User-Agent": "Mozilla/5.0"}
NERATOVICE_LAT = 50.2597
NERATOVICE_LON = 14.5162

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return round(R * c, 1)

def geocode_with_smart_fallback(address):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        base_url = "https://nominatim.openstreetmap.org/search"

        def try_geocode(query):
            params = {"q": query, "format": "json", "limit": 1}
            response = requests.get(base_url, params=params, headers=headers, timeout=10)
            data = response.json()
            if data:
                return float(data[0]["lat"]), float(data[0]["lon"])
            return None, None

        lat, lon = try_geocode(address)
        if lat and lon:
            return lat, lon

        if "Česká republika" in address:
            base = address.split("Česká republika")[0].strip(", ")
            lat, lon = try_geocode(f"{base}, Česká republika")
            if lat and lon:
                return lat, lon

        candidates = re.split(r"[-–/,]", address)
        for candidate in reversed(candidates):
            city = candidate.strip()
            if len(city) >= 3:
                lat, lon = try_geocode(f"{city}, Česká republika")
                if lat and lon:
                    return lat, lon
    except:
        return None, None
    return None, None

def scrape_idnes(max_pages=2):
    results = []
    seen_links = set()

    for page in range(1, max_pages + 1):
        url = f"https://reality.idnes.cz/s/prodej/pozemky/stavebni-parcely/?price_to=1000000&page={page}"
        print(f"🔎 Procházím stránku {page}: {url}")
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        offers = soup.select("a[href*='/detail/prodej/pozemek/']")
        for a in offers:
            href = a["href"]
            full_url = href if href.startswith("http") else "https://reality.idnes.cz" + href
            if full_url in seen_links:
                continue
            seen_links.add(full_url)

            try:
                detail_r = requests.get(full_url, headers=HEADERS, timeout=10)
                detail_soup = BeautifulSoup(detail_r.text, "html.parser")
                text = detail_soup.get_text(" ", strip=True).lower()

                title = detail_soup.find("h1")
                lokalita = title.get_text(strip=True) if title else None

                cena_tag = detail_soup.find("h2")
                cena_match = re.search(r"(\d[\d\s]*)\s*kč", cena_tag.text) if cena_tag else None
                cena = int(cena_match.group(1).replace(" ", "")) if cena_match else None

                vymera_match = re.search(r"(\d+)\s*m²", title.text) if title else None
                vymera = int(vymera_match.group(1)) if vymera_match else None

                breadcrumbs = detail_soup.select("ul.breadcrumb li")
                okres = breadcrumbs[-2].text.strip() if len(breadcrumbs) >= 2 else None
                kraj = breadcrumbs[-3].text.strip() if len(breadcrumbs) >= 3 else None

                lat, lon = geocode_with_smart_fallback(f"{lokalita}, Česká republika")
                vzdalenost_km = haversine(NERATOVICE_LAT, NERATOVICE_LON, lat, lon) if lat and lon else None
                cesta_autem_min = round(vzdalenost_km / 0.75) if vzdalenost_km else None

                results.append({
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
                    "fotky": len(detail_soup.select("div.photo a img")),
                    "odkaz": full_url,
                    "zdroj": "reality.idnes.cz",
                    "datum_zverejneni": datetime.today().strftime("%Y-%m-%d")
                })

                time.sleep(1)

            except Exception as e:
                print(f"❌ Chyba při zpracování: {e}")
                continue

    print(f"✅ Hotovo – iDNES: nalezeno {len(results)} inzerátů")
    return results