import requests
from bs4 import BeautifulSoup
from datetime import datetime
from utils import geocode_address, haversine_distance

BASE_URL = "https://reality.idnes.cz"

NERATOVICE_LAT = 50.2595
NERATOVICE_LON = 14.5173

def is_share_offer(text):
    text = text.lower()
    keywords = ["polovina", "spoluvlastnictví", "ideální", "část", "podíl"]
    return any(keyword in text for keyword in keywords)

def parse_listing(article):
    a_tag = article.find("a")
    if not a_tag or not a_tag.get("href"):
        return None

    odkaz = BASE_URL + a_tag["href"]
    title_tag = article.find("h2")
    title = title_tag.get_text(strip=True) if title_tag else ""

    if is_share_offer(title):
        return None

    info_tag = article.find("p", class_="c-products__info")
    location = info_tag.get_text(strip=True) if info_tag else ""

    price_tag = article.find("p", class_="c-products__price")
    price_strong = price_tag.find("strong") if price_tag else None
    cena = None
    if price_strong:
        try:
            cena = int(price_strong.get_text(strip=True).replace(" ", "").replace("Kč", "").replace(" ", ""))
        except ValueError:
            pass

    lat, lon, okres, kraj = geocode_address(location)
    vzd_km, cesta_min = haversine_distance(NERATOVICE_LAT, NERATOVICE_LON, lat, lon)

    return {
        "lokalita": location,
        "vymera": None,
        "cena": cena,
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
        "fotky": None,
        "odkaz": odkaz,
        "zdroj": "reality.idnes.cz",
        "datum_zverejneni": datetime.today().strftime("%Y-%m-%d")
    }

def scrape_idnes():
    url = BASE_URL + "/s/prodej/pozemky/stavebni-pozemek/cena-do-1000000/"
    listings = []

    for page in range(1, 3):
        if page > 1:
            page_url = f"{url}?page={page}"
        else:
            page_url = url

        print(f"🔍 Procházím stránku {page}: {page_url}")
        res = requests.get(page_url)
        soup = BeautifulSoup(res.text, "html.parser")

        articles = soup.find_all("article")
        for article in articles:
            result = parse_listing(article)
            if result:
                print(f"✅ idnes: zpracován inzerát {result['odkaz']}")
                listings.append(result)

    print(f"✅ idnes: nalezeno {len(listings)} inzerátů")
    return listings
