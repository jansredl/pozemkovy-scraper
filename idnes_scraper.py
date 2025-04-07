import requests
from bs4 import BeautifulSoup
from utils import geocode_address, haversine_distance
import datetime

BASE_URL = "https://reality.idnes.cz"
START_URL = "https://reality.idnes.cz/s/prodej/pozemky/stavebni-pozemek/cena-do-1000000/"

def is_share_offer(title):
    podil_keywords = ["polovina", "spoluvlastnictví", "ideální", "část", "podíl"]
    return any(podil in title.lower() for podil in podil_keywords)

def parse_listing(article):
    title_tag = article.select_one("h2.c-products__title")
    location_tag = article.select_one("p.c-products__info")
    price_tag = article.select_one("p.c-products__price strong")
    size_info = title_tag.get_text(strip=True) if title_tag else ""

    if is_share_offer(size_info):
        return None

    size = None
    if "m²" in size_info:
        try:
            size = int(size_info.split()[-2])
        except:
            pass

    location_text = location_tag.get_text(strip=True) if location_tag else ""
    city = location_text.split(",")[0].strip() if "," in location_text else location_text

    lat, lon, okres, kraj = geocode_address(city)
    if lat is None:
        return None

    vzd_km, cesta_min = haversine_distance(lat, lon, 50.2597, 14.5189)

    return {
        "lokalita": city,
        "vymera": size,
        "cena": parse_price(price_tag.get_text()) if price_tag else None,
        "okres": okres,
        "kraj": kraj,
        "lat": lat,
        "lon": lon,
        "vzdalenost_od": "Neratovice",
        "vzdalenost_km": vzd_km,
        "cesta_autem_min": cesta_min,
        "sit_voda": None,
        "sit_cov": None,
        "sit_kanalizace": None,
        "sit_elektrina": None,
        "mobilni_dum_vhodne": None,
        "cislo_parcely": None,
        "katastr": None,
        "uzemni_plan_url": None,
        "fotky": count_photos(article),
        "odkaz": BASE_URL + article.a["href"],
        "zdroj": "reality.idnes.cz",
        "datum_zverejneni": str(datetime.date.today())
    }

def count_photos(article):
    return len(article.select("span.c-products__img img"))

def parse_price(price_str):
    return int("".join(filter(str.isdigit, price_str)))

def scrape_idnes():
    results = []
    for page in range(1, 3):
        url = START_URL if page == 1 else START_URL + f"?page={page}"
        print(f"🔍 Procházím stránku {page}: {url}")
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        articles = soup.select("div.c-products__item article")
        for article in articles:
            result = parse_listing(article)
            if result:
                print(f"✅ idnes: zpracován inzerát {result['odkaz']}")
                results.append(result)
    print(f"✅ idnes: nalezeno {len(results)} inzerátů")
    return results