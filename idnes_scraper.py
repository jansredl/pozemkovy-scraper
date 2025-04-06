import requests
from bs4 import BeautifulSoup
from utils import geocode_address, haversine_distance
from datetime import datetime
import time

def is_partial_ownership(text):
    return any(podil in text.lower() for podil in ["1/2", "1/", "1\", "½", "polovina", "spoluvlastnictví", "ideální", "část"])

def scrape_idnes():
    results = []
    base_url = "https://reality.idnes.cz/s/prodej/pozemky/stavebni-pozemek/cena-do-1000000/"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    for page in range(1, 3):
        if page == 1:
            url = base_url
        else:
            url = f"{base_url}?page={page}"

        print(f"🔍 Procházím stránku {page}: {url}")
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        listings = soup.find_all("article")

        for listing in listings:
            link_tag = listing.find("a", class_="c-products__link")
            if not link_tag:
                continue

            url_detail = link_tag.get("href")
            if not url_detail.startswith("http"):
                url_detail = "https://reality.idnes.cz" + url_detail

            title = listing.find("h2")
            if title and is_partial_ownership(title.text):
                continue

            location_tag = listing.find("p", class_="c-products__info")
            location = location_tag.text.strip() if location_tag else ""

            price_tag = listing.find("p", class_="c-products__price")
            price_text = price_tag.find("strong").text.strip().replace(" ", "").replace("Kč", "") if price_tag else ""
            try:
                price = int(price_text)
            except:
                price = None

            area = None
            if title:
                for word in title.text.strip().split():
                    if word.endswith("m²") or word.endswith("m2"):
                        try:
                            area = int(word.replace("m²", "").replace("m2", "").strip())
                        except:
                            pass

            lat, lon, okres, kraj = geocode_address(location)
            vzdalenost_km, cesta_autem_min = haversine_distance(lat, lon)

            results.append({
                "lokalita": location,
                "vymera": area,
                "cena": price,
                "okres": okres,
                "kraj": kraj,
                "lat": lat,
                "lon": lon,
                "vzdalenost_od": "Neratovice",
                "vzdalenost_km": vzdalenost_km,
                "cesta_autem_min": cesta_autem_min,
                "sit_voda": None,
                "sit_cov": None,
                "sit_kanalizace": None,
                "sit_elektrina": None,
                "mobilni_dum_vhodne": None,
                "cislo_parcely": None,
                "katastr": None,
                "uzemni_plan_url": None,
                "fotky": None,
                "odkaz": url_detail,
                "zdroj": "reality.idnes.cz",
                "datum_zverejneni": datetime.today().strftime("%Y-%m-%d")
            })

            time.sleep(0.5)

    print(f"✅ idnes: nalezeno {len(results)} inzerátů")
    return results