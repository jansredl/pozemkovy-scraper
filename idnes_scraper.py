import asyncio
from playwright.async_api import async_playwright
from utils import geocode_address, haversine_distance
import re
import json
from datetime import datetime

BASE_URL = "https://reality.idnes.cz"
SEARCH_URL = "https://reality.idnes.cz/s/prodej/pozemky/stavebni-pozemek/cena-do-1000000/"
CITY_FROM = "Neratovice"

def is_share(text):
    keywords = ["polovina", "spoluvlastnictví", "ideální", "část", "podíl"]
    return any(k in text.lower() for k in keywords)

async def scrape_idnes():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(SEARCH_URL)

        results = []
        page_num = 1
        while True:
            print(f"🔍 Procházím stránku {page_num}: {page.url}")
            await page.wait_for_selector("article")

            listings = await page.locator("article").all()
            if not listings:
                break

            for article in listings:
                try:
                    title = await article.locator("h2").text_content()
                    if is_share(title):
                        continue

                    a_tag = article.locator("a.c-products__link")
                    detail_url = await a_tag.get_attribute("href")
                    if not detail_url:
                        continue

                    full_url = BASE_URL + detail_url
                    detail_page = await browser.new_page()
                    await detail_page.goto(full_url)
                    await detail_page.wait_for_selector("body")

                    content = await detail_page.content()

                    def extract(pattern, default="-"):
                        match = re.search(pattern, content)
                        return match.group(1).strip() if match else default

                    vymera = extract(r"([\d\s]+)\s*m²")
                    cena = extract(r"([\d\s]+)\s*Kč").replace(" ", "")
                    lokalita = extract(r'<h1[^>]*>(.*?)</h1>', "")
                    datum = datetime.today().strftime("%Y-%m-%d")

                    lat, lon, okres, kraj = geocode_address(lokalita)
                    vzd_km, cesta_min = haversine_distance(lat, lon)

                    voda = "❌" not in content
                    elektrina = "Elektřina" in content and "❌" not in content
                    kanalizace = "Kanalizace" in content and "❌" not in content
                    mobilni_dum = "Mobilní dům" in content and "❌" not in content
                    fotky = len(re.findall(r"compile/thumbs/", content))

                    results.append({
                        "lokalita": lokalita,
                        "vymera": int(vymera.replace(" ", "")) if vymera.isdigit() else None,
                        "cena": int(cena) if cena.isdigit() else None,
                        "okres": okres,
                        "kraj": kraj,
                        "lat": lat,
                        "lon": lon,
                        "vzdalenost_od": CITY_FROM,
                        "vzdalenost_km": vzd_km,
                        "cesta_autem_min": cesta_min,
                        "sit_voda": voda,
                        "sit_kanalizace": kanalizace,
                        "sit_elektrina": elektrina,
                        "mobilni_dum_vhodne": mobilni_dum,
                        "cislo_parcely": "-",
                        "katastr": "-",
                        "uzemni_plan_url": None,
                        "fotky": fotky,
                        "odkaz": full_url,
                        "zdroj": "reality.idnes.cz",
                        "datum_zverejneni": datum
                    })

                    await detail_page.close()
                except Exception as e:
                    print(f"⚠️ Chyba u inzerátu: {e}")
                    continue

            next_button = page.locator("a[aria-label='Další']")
            if await next_button.is_visible():
                await next_button.click()
                await page.wait_for_load_state("networkidle")
                page_num += 1
            else:
                break

        await browser.close()
        return results