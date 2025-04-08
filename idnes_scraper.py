import re
import json
from bs4 import BeautifulSoup
from geopy.distance import geodesic
from datetime import datetime
from playwright.sync_api import sync_playwright
from time import sleep

NERATOVICE_COORDS = (50.2597, 14.5176)
IGNORE_KEYWORDS = ["polovina", "spoluvlastnictví", "ideální", "část", "podíl"]

with open("obce.json", "r", encoding="utf-8") as f:
    OBCE = json.load(f)

def find_obec_info(nazev):
    nazev = nazev.lower()
    for obec in OBCE:
        if obec["hezkyNazev"].lower() in nazev:
            coords = obec["souradnice"]
            return {
                "lat": coords[0],
                "lon": coords[1],
                "okres": obec["adresaUradu"]["obec"],
                "kraj": obec["adresaUradu"]["kraj"]
            }
    return None

def geocode_from_obce(city_text):
    info = find_obec_info(city_text)
    if not info:
        return None, None, None, None, None, None

    lat, lon = info["lat"], info["lon"]
    okres = info["okres"]
    kraj = info["kraj"]
    vzdalenost_km = round(geodesic(NERATOVICE_COORDS, (lat, lon)).km, 1)
    cesta_autem_min = round(vzdalenost_km * 1.2)
    return lat, lon, okres, kraj, vzdalenost_km, cesta_autem_min

def parse_listing(article):
    a = article.select_one("a.c-products__link")
    if not a:
        return None

    title = article.select_one("h2").get_text(strip=True)
    if any(x in title.lower() for x in IGNORE_KEYWORDS):
        return None

    city_tag = article.select_one("p.c-products__info")
    city_text = city_tag.get_text(strip=True) if city_tag else ""

    lat, lon, okres, kraj, vzdalenost_km, cesta_autem_min = geocode_from_obce(city_text)

    price = article.select_one(".c-products__price strong")
    price_val = price.get_text(strip=True).replace("\u00a0", "").replace("Kč", "") if price else None
    cena = int(price_val.replace(" ", "")) if price_val else None

    area_match = re.search(r"(\d+)[^\d]+m²", title)
    vymera = int(area_match.group(1)) if area_match else None

    fotky = 0  # nelze spolehlivě zjistit z výpisu
    odkaz = "https://reality.idnes.cz" + a["href"] if a else ""

    if not (city_text and cena and vymera):
        return None

    return {
        "lokalita": city_text,
        "vymera": vymera,
        "cena": cena,
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
        "cislo_parcely": None,
        "katastr": None,
        "uzemni_plan_url": None,
        "fotky": fotky,
        "odkaz": odkaz,
        "zdroj": "reality.idnes.cz",
        "datum_zverejneni": datetime.today().strftime("%Y-%m-%d")
    }

def scrape_idnes():
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        url = "https://reality.idnes.cz/s/prodej/pozemky/stavebni-pozemek/cena-do-1000000/"
        page.goto(url)
        sleep(3)

        html = page.content()
        soup = BeautifulSoup(html, "html.parser")
        articles = soup.select("article")

        for article in articles:
            data = parse_listing(article)
            if data:
                results.append(data)

        browser.close()
    return results

if __name__ == "__main__":
    data = scrape_idnes()
    with open("idnes_output.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ Uloženo {len(data)} inzerátů do idnes_output.json")
