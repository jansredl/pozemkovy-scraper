from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re
from geopy.distance import geodesic
from time import sleep

NERATOVICE_COORDS = (50.2597, 14.5176)

IGNORE_KEYWORDS = ["polovina", "spoluvlastnictví", "ideální", "část", "podíl"]

def geocode_address(city_text):
    parts = [x.strip() for x in city_text.split(",")]
    city = parts[0] if parts else ""
    okres = ""
    kraj = ""

    coords_map = {
        "Vimperk": (49.0506, 13.7775),
        "Prachatice": (49.0126, 13.9982),
        "Skuhrov": (50.2021, 15.2772),
        "Jedovnice": (49.3499, 16.7461),
        "Moravský Krumlov": (49.0481, 16.3129),
        "Majdalena": (48.9452, 14.9336),
    }
    coords = None
    for key in coords_map:
        if key.lower() in city_text.lower():
            coords = coords_map[key]
            okres = key
            break

    if coords:
        vzdalenost_km = round(geodesic(NERATOVICE_COORDS, coords).km)
        cesta_autem_min = vzdalenost_km * 1.2  # jednoduchý odhad
        return coords[0], coords[1], okres, kraj, vzdalenost_km, int(cesta_autem_min)
    else:
        return None, None, None, None, None, None

def parse_listing(article):
    a = article.select_one("a.c-products__link")
    h2_elem = article.select_one("h2")
    if not h2_elem:
        return None
    title = h2_elem.get_text(strip=True)

    if any(x in title.lower() for x in IGNORE_KEYWORDS):
        return None

    city_elem = article.select_one("p.c-products__info")
    city_text = city_elem.get_text(strip=True) if city_elem else ""

    lat, lon, okres, kraj, vzdalenost_km, cesta_autem_min = geocode_address(city_text)

    price_elem = article.select_one(".c-products__price strong")
    price_val = price_elem.get_text(strip=True).replace("\u00a0", "").replace("Kč", "") if price_elem else None

    area_match = re.search(r"(\d+)[^\d]+m²", title)
    vymera = int(area_match.group(1)) if area_match else None

    odkaz = "https://reality.idnes.cz" + a["href"] if a and a.has_attr("href") else ""

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
