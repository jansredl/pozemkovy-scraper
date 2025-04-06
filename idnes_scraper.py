import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from utils import geocode_address, haversine_distance

BASE_URL = "https://reality.idnes.cz"
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def scrape_idnes(max_pages=3):
    results = []
    for page in range(1, max_pages + 1):
        url = f"{BASE_URL}/s/prodej/pozemky/stavebni-pozemek/cena-do-1000000/?page={page}"
        print(f"🌐 Procházím stránku {page}: {url}")
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        listings = soup.select("a.c-listing__link")
        if not listings:
            break
        for link in listings:
            href = link["href"]
            if not href.startswith("http"):
                href = BASE_URL + href
            data = extract_detail(href)
            if data:
                results.append(data)
    print(f"✅ idnes: nalezeno {len(results)} inzerátů")
    return results

def extract_detail(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        text = soup.get_text(" ", strip=True).lower()

        title = soup.find("h1")
        lokalita = title.get_text(strip=True).split(",")[0] if title else None

        vymera = None
        cena = None
        info_items = soup.select("div.c-property__info div.c-property__row")
        for item in info_items:
            label = item.select_one("div.c-property__label")
            value = item.select_one("div.c-property__value")
            if not label or not value:
                continue
            label_text = label.get_text(strip=True).lower()
            value_text = value.get_text(strip=True).lower()
            if "plocha" in label_text and "m²" in value_text:
                vymera_match = re.search(r"(\d+)", value_text)
                vymera = int(vymera_match.group(1)) if vymera_match else None
            if "cena" in label_text:
                cena = int(re.sub(r"[\s\xa0]+", "", value_text.replace("kč", "").strip()))

        detail_text = soup.get_text(" ", strip=True).lower()
        sit_voda = "voda" in detail_text
        sit_kanalizace = "kanalizace" in detail_text
        sit_cov = "čov" in detail_text or "čistírna" in detail_text
        sit_elektrina = "elektřina" in detail_text or "230v" in detail_text or "400v" in detail_text
        mobilni = any(x in detail_text for x in ["mobilní dům", "mobilheim", "tiny house"])

        lat, lon = geocode_address(lokalita)
        vzdalenost_km, cesta_min = haversine_distance(lat, lon)

        return {
            "lokalita": lokalita,
            "vymera": vymera,
            "cena": cena,
            "okres": None,
            "kraj": None,
            "lat": lat,
            "lon": lon,
            "vzdalenost_od": "Neratovice",
            "vzdalenost_km": vzdalenost_km,
            "cesta_autem_min": cesta_min,
            "sit_voda": sit_voda,
            "sit_cov": sit_cov,
            "sit_kanalizace": sit_kanalizace,
            "sit_elektrina": sit_elektrina,
            "mobilni_dum_vhodne": mobilni,
            "cislo_parcely": None,
            "katastr": None,
            "uzemni_plan_url": None,
            "fotky": len(soup.select("div.gal__item")),
            "odkaz": url,
            "zdroj": "reality.idnes.cz",
            "datum_zverejneni": datetime.today().strftime("%Y-%m-%d")
        }
    except Exception as e:
        print(f"❌ Chyba u {url}: {e}")
        return None
