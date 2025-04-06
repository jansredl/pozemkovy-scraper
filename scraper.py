
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re
from math import radians, sin, cos, sqrt, atan2
import time

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

def extract_location_from_text(text):
    # Získání obce z textu odkazu
    parts = text.split(" ")
    try:
        if "Kč" in parts[-1]:
            cena_index = parts.index("Kč")
            return parts[cena_index - 1]
    except:
        return None
    return None

def extract_location_from_detail(detail_html):
    soup = BeautifulSoup(detail_html, "html.parser")
    text = soup.get_text(separator=" ", strip=True)

    # Okres (např. "okres Trutnov")
    okres = None
    match = re.search(r"okres\s+([A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽa-záčďéěíňóřšťúůýž\-\s]+)", text)
    if match:
        okres = match.group(1).strip()

    # Inženýrské sítě
    site_keys = {
        "elektřina": ["elektřina", "přípojka elektřiny"],
        "voda": ["vodovod", "voda"],
        "kanalizace": ["kanalizace"],
        "čov": ["čistička", "ČOV", "čistírna odpadních vod"],
        "plyn": ["plyn"]
    }

    site_info = []
    for key, phrases in site_keys.items():
        if any(phrase.lower() in text.lower() for phrase in phrases):
            site_info.append(key)

    # Katastr
    katastr = None
    k_match = re.search(r"část obce\s+(\w[\w\s\-]+)", text)
    if k_match:
        katastr = k_match.group(1).strip()

    return okres, site_info, katastr

def extract_data(text):
    vymera = None
    cena = None
    fotky = None

    fotky_match = re.search(r"(\d+)\s+fotografi", text)
    if fotky_match:
        fotky = int(fotky_match.group(1))

    vymera_match = re.search(r"(\d+)\s*m²", text)
    if vymera_match:
        vymera = int(vymera_match.group(1))

    cena_match = re.search(r"(\d[\d\s]+)\s*Kč", text)
    if cena_match:
        cena = int(re.sub(r"\D", "", cena_match.group(1)))

    return fotky, vymera, cena

def scrape_sreality():
    results = []
    headers = {"User-Agent": "Mozilla/5.0"}
    for page in range(1, 3):
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

            fotky, vymera, cena = extract_data(text)
            obec = extract_location_from_text(text)

            try:
                detail_res = requests.get(odkaz, headers=headers)
                okres, site_info, katastr = extract_location_from_detail(detail_res.text)
                time.sleep(1)
            except:
                okres, site_info, katastr = None, [], None

            # doplnění
            lokalita = obec
            if okres and okres.lower() not in obec.lower():
                lokalita = f"{obec}, okres {okres}"

            lat, lon = get_coordinates(lokalita) if lokalita else (None, None)
            vzdalenost = None
            if lat and lon:
                start_lat, start_lon = get_coordinates(START_CITY)
                vzdalenost = haversine_distance(start_lat, start_lon, lat, lon)

            results.append({
                "lokalita": lokalita,
                "cena": cena,
                "vymera": vymera,
                "fotky": fotky,
                "odkaz": odkaz,
                "zdroj": "sreality.cz",
                "datum_zverejneni": datetime.today().strftime("%Y-%m-%d"),
                "lat": lat,
                "lon": lon,
                "vzdalenost_od": START_CITY,
                "vzdalenost_km": vzdalenost,
                "okres": okres,
                "inzenyrske_site": site_info,
                "katastr": katastr
            })
    return results

def run():
    pozemky = scrape_sreality()
    print(f"Nalezeno {len(pozemky)} pozemků")
    with open("pozemky.json", "w", encoding="utf-8") as f:
        json.dump(pozemky, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    run()
