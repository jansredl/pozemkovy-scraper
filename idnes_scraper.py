import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from utils import geocode_address, haversine_distance

def scrape_idnes():
    results = []
    base_url = "https://reality.idnes.cz/s/prodej/pozemky/stavebni-pozemek/cena-do-1000000/"
    headers = {"User-Agent": "Mozilla/5.0"}

    for page in range(1, 3):
        url = base_url if page == 1 else f"{base_url}?page={page}"
        print(f"🔍 Procházím stránku {page}: {url}")
        try:
            r = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            cards = soup.select("a[data-type='estate']")

            for card in cards:
                link = card.get("href")
                full_url = "https://reality.idnes.cz" + link if link.startswith("/") else link
                text = card.get_text(separator=" ", strip=True)

                lokalita_match = re.search(r"pozemek.*?(\d+\s*m²)?\s+(.*?)\s+\d", text)
                vymera_match = re.search(r"(\d+)\s*m²", text)
                cena_match = re.search(r"(\d[\d\s]*)\s*Kč", text)

                lokalita = lokalita_match.group(2).strip() if lokalita_match else "Neznámá lokalita"
                vymera = int(vymera_match.group(1)) if vymera_match else None
                cena = int(cena_match.group(1).replace(" ", "")) if cena_match else None

                lat, lon = geocode_address(f"{lokalita}, Česká republika")
                vzdalenost = haversine_distance(50.2597, 14.5162, lat, lon) if lat and lon else None
                cesta_autem_min = round(vzdalenost / 0.75) if vzdalenost else None

                results.append({
                    "lokalita": lokalita,
                    "vymera": vymera,
                    "cena": cena,
                    "okres": None,
                    "kraj": None,
                    "lat": lat,
                    "lon": lon,
                    "vzdalenost_od": "Neratovice",
                    "vzdalenost_km": vzdalenost,
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
                    "odkaz": full_url,
                    "zdroj": "reality.idnes.cz",
                    "datum_zverejneni": datetime.today().strftime("%Y-%m-%d")
                })
        except Exception as e:
            print(f"⚠️ Chyba při načítání stránky {url}: {e}")

    return results