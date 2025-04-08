from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re
from geopy.distance import geodesic
from time import sleep
import json

NERATOVICE_COORDS = (50.2597, 14.5176)

IGNORE_KEYWORDS = ["polovina", "spoluvlastnictví", "ideální", "část", "podíl"]

# KROK 1: Načti obce.json (soubor musí být ve stejné složce jako tento skript)
with open("obce.json", encoding="utf-8") as f:
    OBCE_DATA = json.load(f)

# KROK 2: Najdi souřadnice obce podle názvu (město, okres, kraj)
def geocode_address(city_text):
    city_text_clean = city_text.lower().strip()
    for obec in OBCE_DATA:
        if obec["nazev_obce"].lower() in city_text_clean:
            lat = float(obec["wgs84_lat"])
            lon = float(obec["wgs84_lon"])
            okres = obec.get("nazev_okresu", "")
            kraj = obec.get("nazev_kraje", "")
            vzdalenost_km = round(geodesic(NERATOVICE_COORDS, (lat, lon)).km)
            cesta_autem_min = int(vzdalenost_km * 1.2)
            return lat, lon, okres, kraj, vzdalenost_km, cesta_autem_min
    return None, None, None, None, None, None

# Parsování jednotlivého inzerátu
def parse_listing(article):
    a = article.select_one("a.c-products__link")
    title_el = article.select_one("h2")
    if not title_el:
        return None
    title = title_el.get_text(strip=True)

    if any(x in title.lower() for x in IGNORE_KEYWORDS):
        return None

    city = article.select_one("p.c-products__info")
    city_text = city.get_text(strip=True) if city else ""

    lat, lon, okres, kraj, vzdalenost_km, cesta_autem_min = geocode_address(city_text)

    price = article.select_one(".c-products__price strong")
    price_val = price.get_text(strip=True).replace("\u00a0", "").replace("Kč", "") if price else None

    area_match = re.search(r"(\d+)[^\d]+m²", title)
    vymera = int(area_match.group(1)) if area_match else None

    odkaz = "https://reality.idnes.cz" + a["href"] if a else ""

    return {
        "lokalita": city_text,
        "vymera": vymera,
        "cena": int(price_val.replace(" ", "")) if price_val else None,
        "okres": okres,
        "kraj": kraj,
        "lat": lat,
        "lon": lon,
        "vzdalenost_od": "Neratovice",
        "vzdalenost_km": vzdalenost_km,
        "cesta_autem_min": cesta_autem_min,
        "sit_voda": False,
        "sit_cov": False,
        "sit_kanalizace": False,
        "sit_elektrina": False,
        "mobilni_dum_vhodne": False,
        "cislo_parcely": "-",
        "katastr": "-",
        "uzemni_plan_url": None,
        "fotky": 0,
        "odkaz": odkaz,
        "zdroj": "reality.idnes.cz",
        "datum_zverejneni": "2025-04-07"
    }

# Hlavní funkce scraperu
def scrape_idnes():
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://reality.idnes.cz/s/prodej/pozemky/stavebni-pozemek/cena-do-1000000/")
        sleep(2)
        html = page.content()
        soup = BeautifulSoup(html, "lxml")
        articles = soup.select("article")

        for article in articles:
            data = parse_listing(article)
            if data:
                results.append(data)

        browser.close()
    return results
