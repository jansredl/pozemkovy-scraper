
import requests
from bs4 import BeautifulSoup
from utils import geocode_address, haversine_distance
import time
from datetime import datetime

NERATOVICE_LAT = 50.2597
NERATOVICE_LON = 14.5195

def scrape_idnes():
    listings = []
    base_url = "https://reality.idnes.cz/s/prodej/pozemky/stavebni-pozemek/cena-do-1000000/"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    for page in range(1, 3):  # Pro testování projdeme první 2 stránky
        if page == 1:
            url = base_url
        else:
            url = f"{base_url}?page={page}"

        print(f"🔍 Procházím stránku {page}: {url}")
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.find_all('article')

        for article in articles:
            try:
                title_tag = article.find("h2", class_="c-products__title")
                if not title_tag:
                    continue

                title_text = title_tag.get_text(strip=True).lower()
                if any(podil in title_text for podil in ["polovina", "spoluvlastnictví", "ideální", "část", "podíl"]):
                    continue  # Ignorujeme podíly

                location_tag = article.find("p", class_="c-products__info")
                price_tag = article.find("p", class_="c-products__price")
                link_tag = article.find("a", class_="c-products__link")

                if not (location_tag and price_tag and link_tag):
                    continue

                lokalita = location_tag.get_text(strip=True)
                cena_raw = price_tag.find("strong").get_text(strip=True).replace(" ", "").replace("Kč", "")
                cena = int(cena_raw) if cena_raw.isdigit() else None
                odkaz = link_tag["href"]
                if not odkaz.startswith("http"):
                    odkaz = "https://reality.idnes.cz" + odkaz

                vymera = None
                if "m²" in title_text:
                    try:
                        vymera = int(title_text.split("m²")[0].split()[-1])
                    except:
                        pass

                lat, lon = geocode_address(lokalita)
                vzd_km, cesta_min = haversine_distance(lat, lon, NERATOVICE_LAT, NERATOVICE_LON)

                listings.append({
                    "lokalita": lokalita,
                    "vymera": vymera,
                    "cena": cena,
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
                    "datum_zverejneni": datetime.now().strftime("%Y-%m-%d")
                })

                time.sleep(1)
            except Exception as e:
                print("Chyba při zpracování inzerátu:", e)

    print(f"✅ idnes: nalezeno {len(listings)} inzerátů")
    return listings
