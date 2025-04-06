import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import time

def scrape_idnes(max_pages=10):
    results = []
    seen_links = set()

    for page in range(1, max_pages + 1):
        url = f"https://reality.idnes.cz/s/prodej/pozemky/stavebni-parcely/?price_to=1000000&page={page}"
        print(f"🔎 Procházím stránku {page}: {url}")
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        offers = soup.select("a[href*='/detail/prodej/pozemek/']")
        for a in offers:
            href = a["href"]
            full_url = href if href.startswith("http") else "https://reality.idnes.cz" + href
            if full_url in seen_links:
                continue
            seen_links.add(full_url)

            text = a.get_text(" ", strip=True)

            vymera_match = re.search(r"(\d+)\s*m²", text)
            cena_match = re.search(r"(\d[\d\s\xa0]*)\s*Kč", text)
            lokalita_match = re.search(r"pozemku\s+([\w\s\-]+)", text, re.IGNORECASE)

            vymera = int(vymera_match.group(1)) if vymera_match else None
            cena = int(re.sub(r"\s+", "", cena_match.group(1))) if cena_match else None
            lokalita = lokalita_match.group(1).strip() if lokalita_match else "Neznámá lokalita"

            if not (vymera and cena):
                continue

            results.append({
                "lokalita": lokalita,
                "vymera": vymera,
                "cena": cena,
                "fotky": None,
                "okres": None,
                "lat": None,
                "lon": None,
                "vzdalenost_od": "Neratovice",
                "vzdalenost_km": None,
                "cesta_autem_min": None,
                "sit_voda": None,
                "sit_cov": None,
                "sit_kanalizace": None,
                "sit_elektrina": None,
                "mobilni_dum_vhodne": None,
                "cislo_parcely": None,
                "katastr": None,
                "uzemni_plan_url": None,
                "odkaz": full_url,
                "zdroj": "reality.idnes.cz",
                "datum_zverejneni": datetime.today().strftime("%Y-%m-%d")
            })

            time.sleep(0.5)

    print(f"✅ Hotovo – iDNES: nalezeno {len(results)} inzerátů")
    return results