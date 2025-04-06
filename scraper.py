
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re
from math import radians, sin, cos, sqrt, atan2

START_CITY = "Neratovice"

def get_coordinates(address):
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": address, "format": "json", "limit": 1}
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except:
        return None, None
    return None, None

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return round(R * c, 1)

def scrape_sreality():
    results = []
    headers = {"User-Agent": "Mozilla/5.0"}
    for page in range(1, 4):
        url = f"https://www.sreality.cz/hledani/prodej/pozemky/stavebni-parcely?cena-do=2000000&strana={page}"
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        links = soup.select('a[href^="/detail/prodej/"]')
        seen = set()

        for link in links:
            href = link.get("href")
            if href in seen:
                continue
            seen.add(href)

            odkaz = "https://www.sreality.cz" + href
            text = link.get_text(separator=" ", strip=True)

            cena_match = re.search(r"([\d\s]+)\s*Kč", text)
cena = int(re.sub(r"\\D", "", cena_match.group(1))) if cena_match else None

            vymera_match = re.search(r"(\d+)\s*m²", text)
            vymera = int(vymera_match.group(1)) if vymera_match else None

            lokalita_match = re.search(r"([\wěščřžýáíéúůĚŠČŘŽÝÁÍÉÚŮ\-\s]+)", text)
            lokalita = lokalita_match.group(1).strip() if lokalita_match else None

            lat, lon = get_coordinates(lokalita) if lokalita else (None, None)
            vzdalenost = None
            if lat and lon:
                start_lat, start_lon = get_coordinates(START_CITY)
                vzdalenost = haversine_distance(start_lat, start_lon, lat, lon)

            results.append({
                "nazev": "Pozemek",
                "lokalita": lokalita,
                "cena": cena,
                "vymera": vymera,
                "odkaz": odkaz,
                "zdroj": "sreality.cz",
                "datum_zverejneni": datetime.today().strftime("%Y-%m-%d"),
                "lat": lat,
                "lon": lon,
                "vzdalenost_od": START_CITY,
                "vzdalenost_km": vzdalenost
            })
    return results

def run():
    pozemky = scrape_sreality()
    print(f"Nalezeno {len(pozemky)} pozemků")
    with open("pozemky.json", "w", encoding="utf-8") as f:
        json.dump(pozemky, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    run()
