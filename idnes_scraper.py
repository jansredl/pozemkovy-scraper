import requests
from bs4 import BeautifulSoup
from utils import geocode_address, haversine_distance
import time

BASE_URL = "https://reality.idnes.cz"
SEARCH_URL = f"{BASE_URL}/s/prodej/pozemky/stavebni-pozemek/cena-do-1000000/"
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

NERATOVICE_LAT, NERATOVICE_LON = 50.259, 14.517

IGNORED_KEYWORDS = ["polovina", "spoluvlastnictví", "ideální", "část", "podíl"]

def is_shared_ownership(text):
    if not text:
        return False
    text_lower = text.lower()
    return any(kw in text_lower for kw in IGNORED_KEYWORDS)

def get_total_pages():
    resp = requests.get(SEARCH_URL, headers=HEADERS)
    soup = BeautifulSoup(resp.text, "html.parser")
    last_page = soup.select_one(".paging .last a")
    if last_page and "?page=" in last_page.get("href", ""):
        return int(last_page["href"].split("?page=")[-1])
    return 1

def parse_listing(article):
    a = article.select_one("a.c-products__link")
    if not a:
        return None

    url = BASE_URL + a["href"]
    title = a.select_one("h2.c-products__title").get_text(strip=True)

    if is_shared_ownership(title):
        return None

    detail_resp = requests.get(url, headers=HEADERS)
    detail_soup = BeautifulSoup(detail_resp.text, "html.parser")

    def extract_text(label):
        span = detail_soup.find("span", string=label)
        if span and span.find_next_sibling("strong"):
            return span.find_next_sibling("strong").get_text(strip=True)
        return None

    def extract_bool(label):
        span = detail_soup.find("span", string=label)
        if span and span.find_next("svg"):
            return "icon-cross" not in span.find_next("svg").get("class", [])
        return None

    cena = extract_text("Cena:")
    vymera = extract_text("Plocha pozemku:")
    lokalita = title.split(",")[0] if "," in title else title

    geo = geocode_address(lokalita)
    if len(geo) == 4:
        lat, lon, okres, kraj = geo
    else:
        lat, lon, okres, kraj = None, None, None, None

    if lat and lon:
        vzd_km, cesta_min = haversine_distance(lat, lon, NERATOVICE_LAT, NERATOVICE_LON)
    else:
        vzd_km, cesta_min = None, None

    return {
        "lokalita": lokalita,
        "vymera": parse_number(vymera),
        "cena": parse_number(cena),
        "okres": okres,
        "kraj": kraj,
        "lat": lat,
        "lon": lon,
        "vzdalenost_od": "Neratovice",
        "vzdalenost_km": vzd_km,
        "cesta_autem_min": cesta_min,
        "sit_voda": extract_bool("Voda:"),
        "sit_cov": extract_bool("ČOV:"),
        "sit_kanalizace": extract_bool("Kanalizace:"),
        "sit_elektrina": extract_bool("Elektřina:"),
        "mobilni_dum_vhodne": extract_bool("Mobilní dům:"),
        "cislo_parcely": extract_text("Parcelní číslo:"),
        "katastr": extract_text("Katastr:"),
        "uzemni_plan_url": None,
        "fotky": len(detail_soup.select(".c-gallery__item")),
        "odkaz": url,
        "zdroj": "reality.idnes.cz",
        "datum_zverejneni": extract_text("Datum zveřejnění:")
    }

def parse_number(text):
    if not text:
        return None
    digits = "".join(c for c in text if c.isdigit())
    return int(digits) if digits else None

def scrape_idnes():
    results = []
    total_pages = get_total_pages()

    for page in range(1, total_pages + 1):
        url = SEARCH_URL if page == 1 else f"{SEARCH_URL}?page={page}"
        print(f"🔎 Procházím stránku {page}: {url}")
        resp = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(resp.text, "html.parser")
        articles = soup.select("article.c-products__item")

        for article in articles:
            result = parse_listing(article)
            if result:
                print("✅ idnes: zpracován inzerát", result["odkaz"])
                results.append(result)
            time.sleep(0.8)

    print(f"✅ idnes: nalezeno {len(results)} inzerátů")
    return results
