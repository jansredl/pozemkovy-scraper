import re
import json
from bs4 import BeautifulSoup
from geopy.distance import geodesic
from datetime import datetime
from playwright.sync_api import sync_playwright
from time import sleep

NERATOVICE_COORDS = (50.2597, 14.5176)
IGNORE_KEYWORDS = ["polovina", "spoluvlastnictví", "ideální", "část", "podíl"]

# Načtení dat z obce.json
with open("obce.json", encoding="utf-8") as f:
    OBCE = json.load(f)

def extract_obec_okres(text):
    # Příklad: "Kunovice, okres Uherské Hradiště"
    obec = ""
    okres = ""
    if "," in text:
        parts = [x.strip() for x in text.split(",")]
        if len(parts) == 2:
            obec = parts[0]
            if "okres" in parts[1].lower():
                okres = parts[1].lower().replace("okres", "").strip()
    return obec, okres

def find_obec_info(obec_name, okres_name):
    for o in OBCE:
        if o.get("hezkyNazev", "").lower() == obec_name.lower():
            if okres_name == "" or okres_name in o.get("adresaUradu", {}).get("obec", "").lower():
                return o
    return None

def geocode_from_obce(city_text):
    obec, okres = extract_obec_okres(city_text)
    print(f"🔍 Hledám obec: {obec}, okres: {okres}")
    info = find_obec_info(obec, okres)
    if info:
        lat, lon = info["souradnice"]
        okres = info["adresaUradu"]["obec"]
        kraj = info["adresaUradu"]["kraj"]
        vzdalenost_km = round(geodesic(NERATOVICE_COORDS, (lat, lon)).km)
        cesta_autem_min = int(vzdalenost_km * 1.2)
        return lat, lon, okres, kraj, vzdalenost_km, cesta_autem_min
    return None, None, None, None, None, None

def parse_listing(article):
    a = article.select_one("a.c-products__link")
    title_tag = article.select_one("h2")
    if not title_tag:
        return None

    title = title_tag.get_text(strip=True)
    if any(x in title.lower() for x in IGNORE_KEYWORDS):
        return None

    city_tag = article.select_one("p.c-products__info")
    city_text = city_tag.get_text(strip=True) if city_tag else ""

    lat, lon, okres, kraj, vzdalenost_km, cesta_autem_min = geocode_from_obce(city_text)

    price_tag = article.select_one(".c-products__price strong")
    price_val = price_tag.get_text(strip=True).replace("\u00a0", "").replace("Kč", "") if price_tag else None

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
        "datum_zverejneni": datetime.now().strftime("%Y-%m-%d")
    }

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
