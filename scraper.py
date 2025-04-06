
import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2
import time

HEADERS = {"User-Agent": "Mozilla/5.0"}
NERATOVICE_LAT = 50.2597
NERATOVICE_LON = 14.5162

def geocode(address):
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": address, "format": "json", "limit": 1}
        r = requests.get(url, params=params, headers=HEADERS)
        data = r.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except:
        return None, None
    return None, None

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return round(R * 2 * atan2(sqrt(a), sqrt(1 - a)), 1)

def get_detail_info(url):
    try:
        r = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(r.text, "html.parser")
        text = soup.get_text(" ", strip=True).lower()

        okres_match = re.search(r"okres\s+([a-zá-ž\-\s]+)", text)
        katastr_match = re.search(r"katastr[a-z]*\s+územ[íi]\s*([a-zá-ž\-\s]+)", text)
        parcela_match = re.search(r"parcela\s*č(?:\.|íslo)?\s*([\w\-/]+)", text)
        uzemni_plan_match = re.search(r"(https?://[\w./-]*uzemni[\w./-]*\.pdf)", text)

        mobilni = any(x in text for x in ["mobilní dům", "mobilheim", "mobilheimy", "mobilní domy", "tiny house", "tinyhouse"])

        return {
            "okres": okres_match.group(1).strip().title() if okres_match else None,
            "katastr": katastr_match.group(1).strip().title() if katastr_match else None,
            "cislo_parcely": parcela_match.group(1).strip() if parcela_match else None,
            "odkaz_uzemni_plan": uzemni_plan_match.group(1) if uzemni_plan_match else None,
            "sit_voda": "voda" in text or "vodovod" in text,
            "sit_cov": "čov" in text or "čistírna" in text,
            "sit_kanalizace": "kanalizace" in text,
            "sit_elektrina": "elektřina" in text or "230v" in text or "400v" in text,
            "mobilni_domy_vhodne": mobilni
        }
    except:
        return {}

def scrape():
    url = "https://www.sreality.cz/hledani/prodej/pozemky/stavebni-parcely?cena-do=2000000"
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")
    links = soup.select("a[href^='/detail/prodej/pozemek']")
    seen = set()
    results = []

    for a in links:
        href = a["href"]
        if href in seen:
            continue
        seen.add(href)

        full_url = "https://www.sreality.cz" + href
        text = a.get_text(" ", strip=True)

        vymera_match = re.search(r"(\d+)\s*m²", text)
        cena_match = re.search(r"(\d[\d\s]*)\s*Kč", text)
        lokalita_match = re.search(r"\d+\s*m²\s+(.+?)\s+\d", text)
        fotky_match = re.search(r"(\d+)\s+fotografi", text)

        vymera = int(vymera_match.group(1)) if vymera_match else None
        cena = int(cena_match.group(1).replace(" ", "")) if cena_match else None
        lokalita = lokalita_match.group(1).strip() if lokalita_match else None
        fotky = int(fotky_match.group(1)) if fotky_match else None

        lat, lon = geocode(lokalita) if lokalita else (None, None)
        vzdalenost = haversine(NERATOVICE_LAT, NERATOVICE_LON, lat, lon) if lat and lon else None

        detail = get_detail_info(full_url)

        results.append({
            "lokalita": lokalita,
            "vymera": vymera,
            "cena": cena,
            "okres": detail.get("okres"),
            "lat": lat,
            "lon": lon,
            "vzdalenost_km": vzdalenost,
            "sit_voda": detail.get("sit_voda"),
            "sit_cov": detail.get("sit_cov"),
            "sit_kanalizace": detail.get("sit_kanalizace"),
            "sit_elektrina": detail.get("sit_elektrina"),
            "mobilni_domy_vhodne": detail.get("mobilni_domy_vhodne"),
            "cislo_parcely": detail.get("cislo_parcely"),
            "katastr": detail.get("katastr"),
            "odkaz_uzemni_plan": detail.get("odkaz_uzemni_plan"),
            "fotky": fotky,
            "odkaz": full_url,
            "zdroj": "sreality.cz",
            "datum_zverejneni": datetime.today().strftime("%Y-%m-%d")
        })

        if len(results) >= 5:
            break
        time.sleep(1.5)

    return results

data = scrape()
with open("/mnt/data/pozemky.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
