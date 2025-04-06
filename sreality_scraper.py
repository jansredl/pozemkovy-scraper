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
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return round(R * 2 * atan2(sqrt(a), sqrt(1 - a)), 1)

def get_detail_info(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        text = soup.get_text(" ", strip=True).lower()

        okres_match = re.search(r"okres\s+([a-zá-ž\-\s]+)", text)
        katastr_match = re.search(r"katastr[a-z]*\s+územ[íi]\s*([a-zá-ž\-\s]+)", text)
        parcela_match = re.search(r"parcela\s*č(?:\.|íslo)?\s*([\w\-/]+)", text)
        uzemni_plan_match = re.search(r"(https?://[\w./-]*uzemni[\w./-]*\.pdf)", text)

        mobilni = any(x in text for x in ["mobilní dům", "mobilheim", "tiny house", "mobilní domy", "mobilheimy"])

        return {
            "okres": okres_match.group(1).strip().title() if okres_match else None,
            "katastr": katastr_match.group(1).strip().title() if katastr_match else None,
            "cislo_parcely": parcela_match.group(1).strip() if parcela_match else None,
            "uzemni_plan_url": uzemni_plan_match.group(1) if uzemni_plan_match else None,
            "sit_voda": "voda" in text or "vodovod" in text,
            "sit_cov": "čov" in text or "čistírna" in text,
            "sit_kanalizace": "kanalizace" in text,
            "sit_elektrina": "elektřina" in text or "230v" in text or "400v" in text,
            "mobilni_dum_vhodne": mobilni
        }
    except Exception as e:
        print(f"⚠️ Chyba při načítání detailu: {e}")
        return {}

def scrape_sreality():
    url = "https://www.sreality.cz/hledani/prodej/pozemky/stavebni-parcely?cena-do=1000000"
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
        print(f"➡️ Zpracovávám inzerát: {full_url}")
        text = a.get_text(" ", strip=True)

        vymera_match = re.search(r"(\d+)\s*m²", text)
        cena_match = re.search(r"(\d[\d\s\xa0]*)\s*Kč", text)
        lokalita_match = re.search(r"\d+\s*m²\s+(.+?)\s+\d", text)
        fotky_match = re.search(r"(\d+)\s+fotografi", text)

        try:
            vymera = int(vymera_match.group(1)) if vymera_match else None
            cena = int(re.sub(r"\s+", "", cena_match.group(1))) if cena_match else None
            lokalita = lokalita_match.group(1).strip() if lokalita_match else None
        except Exception as e:
            print(f"❌ Chyba při parsování čísel: {e}")
            continue

        if not (lokalita and cena and vymera):
            print("❌ Vynecháno – chybí lokalita, cena nebo výměra")
            continue

        fotky = int(fotky_match.group(1)) if fotky_match else None
        detail = get_detail_info(full_url)

        geotext = f"{lokalita}, {detail.get('okres')}, Česká republika" if detail.get("okres") else f"{lokalita}, Česká republika"
        lat, lon = geocode(geotext)
        vzdalenost = haversine(NERATOVICE_LAT, NERATOVICE_LON, lat, lon) if lat and lon else None
        cesta_autem_min = round(vzdalenost / 0.75) if vzdalenost else None

        results.append({
            "lokalita": lokalita,
            "vymera": vymera,
            "cena": cena,
            "okres": detail.get("okres"),
            "lat": lat,
            "lon": lon,
            "vzdalenost_od": "Neratovice",
            "vzdalenost_km": vzdalenost,
            "cesta_autem_min": cesta_autem_min,
            "sit_voda": detail.get("sit_voda"),
            "sit_cov": detail.get("sit_cov"),
            "sit_kanalizace": detail.get("sit_kanalizace"),
            "sit_elektrina": detail.get("sit_elektrina"),
            "mobilni_dum_vhodne": detail.get("mobilni_dum_vhodne"),
            "cislo_parcely": detail.get("cislo_parcely"),
            "katastr": detail.get("katastr"),
            "uzemni_plan_url": detail.get("uzemni_plan_url"),
            "fotky": fotky,
            "odkaz": full_url,
            "zdroj": "sreality.cz",
            "datum_zverejneni": datetime.today().strftime("%Y-%m-%d")
        })

        time.sleep(1.2)

    print(f"✅ Hotovo – nalezeno {len(results)} pozemků")
    return results