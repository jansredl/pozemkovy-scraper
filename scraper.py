
import requests
from bs4 import BeautifulSoup
import json
import re
from math import radians, cos, sin, sqrt, atan2
from datetime import datetime
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}
NERATOVICE_LAT = 50.2597
NERATOVICE_LON = 14.5162

def geocode_location(location):
    try:
        url = f"https://nominatim.openstreetmap.org/search"
        params = {"q": location, "format": "json", "addressdetails": 1}
        res = requests.get(url, params=params, headers=HEADERS)
        res.raise_for_status()
        data = res.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception:
        return None, None
    return None, None

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))

def extract_details_from_detail_page(url):
    try:
        r = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(r.text, "html.parser")

        text = soup.get_text(" ", strip=True)
        okres_match = re.search(r"okres\s+([\w\s]+)", text, re.IGNORECASE)
        katastr_match = re.search(r"katastr[a-z]*\s+územ[íi]\s*([\w\s\-]+)", text, re.IGNORECASE)
        site_info = {
            "elektrina": "elektřin" in text,
            "voda": "vodovod" in text or "voda" in text,
            "kanalizace": "kanalizace" in text,
            "plyn": "plyn" in text,
            "cov": "čov" in text or "čistírna" in text
        }

        return {
            "okres": okres_match.group(1).strip() if okres_match else None,
            "katastr": katastr_match.group(1).strip() if katastr_match else None,
            "site": site_info
        }
    except:
        return {}

def scrape_sreality():
    results = []
    for page in range(1, 3):
        url = f"https://www.sreality.cz/hledani/prodej/pozemky/bydleni?cena-do=2000000&strana={page}"
        r = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(r.text, "html.parser")
        listings = soup.select("div.property")

        for listing in listings:
            text = listing.get_text(" ", strip=True)
            odkaz_tag = listing.find("a", href=True)
            if not odkaz_tag:
                continue
            odkaz = "https://www.sreality.cz" + odkaz_tag["href"]

            vymera_match = re.search(r"(\d+)\s*m²", text)
            cena_match = re.search(r"(\d+[\s\d]*)\s*Kč", text)
            lokalita_match = re.search(r"([A-ZÁ-Ž][\w\s\-]+)(?=\s*\|)", text)

            vymera = int(vymera_match.group(1)) if vymera_match else None
            cena = int(cena_match.group(1).replace(" ", "")) if cena_match else None
            lokalita = lokalita_match.group(1).strip() if lokalita_match else None

            detail = extract_details_from_detail_page(odkaz)
            okres = detail.get("okres")
            obec = lokalita

            if okres and obec and okres.lower() not in obec.lower():
                obec = f"{obec}, okres {okres}"

            lat, lon = geocode_location(obec or lokalita)
            vzdalenost = None
            if lat and lon:
                vzdalenost = round(haversine(NERATOVICE_LAT, NERATOVICE_LON, lat, lon), 1)

            results.append({
                "lokalita": lokalita,
                "okres": okres,
                "obec": obec,
                "cena": cena,
                "vymera": vymera,
                "odkaz": odkaz,
                "zdroj": "sreality.cz",
                "datum_zverejneni": datetime.now().strftime("%Y-%m-%d"),
                "lat": lat,
                "lon": lon,
                "vzdalenost_od": "Neratovice",
                "vzdalenost_km": vzdalenost,
                "katastr": detail.get("katastr"),
                "site": detail.get("site"),
            })

            time.sleep(1.2)  # avoid hammering servers
    return results

def run():
    data = scrape_sreality()
    with open("pozemky.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

run()
