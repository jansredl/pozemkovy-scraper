
import requests
from bs4 import BeautifulSoup
from utils import geocode_address, haversine_distance
from datetime import datetime

BASE_URL = "https://reality.idnes.cz"
LISTING_URL = "https://reality.idnes.cz/s/prodej/pozemky/stavebni-pozemek/cena-do-1000000/"
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def is_podil(text):
    return "podíl" in text.lower() or "podil" in text.lower()

def parse_listing(article):
    title = article.select_one(".c-products__title")
    info = article.select_one(".c-products__info")
    price = article.select_one(".c-products__price strong")
    link_tag = article.select_one("a.c-products__link")

    if not all([title, info, price, link_tag]):
        return None

    text = f"{title.text} {info.text} {price.text}"
    if is_podil(text):
        return None

    url = BASE_URL + link_tag["href"]
    location = info.text.strip()
    area = None
    if "m²" in title.text:
        area = int(title.text.split("m²")[0].split()[-1].replace(" ", "").replace("\xa0", ""))

    price_text = price.text.replace("\xa0", "").replace("Kč", "").replace(" ", "")
    try:
        price_val = int(price_text)
    except ValueError:
        price_val = None

    lat, lon = geocode_address(location)
    vzd_km, cesta_min = haversine_distance(lat, lon)

    return {
        "lokalita": location,
        "vymera": area,
        "cena": price_val,
        "okres": "",
        "kraj": "",
        "lat": lat,
        "lon": lon,
        "vzdalenost_od": "Neratovice",
        "vzdalenost_km": vzd_km,
        "cesta_autem_min": cesta_min,
        "sit_voda": False,
        "sit_cov": False,
        "sit_kanalizace": False,
        "sit_elektrina": False,
        "mobilni_dum_vhodne": False,
        "cislo_parcely": None,
        "katastr": None,
        "uzemni_plan_url": None,
        "fotky": 0,
        "odkaz": url,
        "zdroj": "reality.idnes.cz",
        "datum_zverejneni": datetime.today().strftime('%Y-%m-%d')
    }

def scrape_idnes():
    results = []
    for page in range(1, 3):
        url = LISTING_URL if page == 1 else f"{LISTING_URL}?page={page}"
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.text, "html.parser")
        articles = soup.select("article")

        for article in articles:
            result = parse_listing(article)
            if result:
                results.append(result)

    return results
