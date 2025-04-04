import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import re

def extract_number(text):
    match = re.search(r'\d+(\s?\d+)*', text)
    if match:
        return int(match.group(0).replace(" ", ""))
    return None

def scrape_sreality(max_pages=10):
    base_url = "https://www.sreality.cz/hledani/prodej/pozemky/stavebni-parcely?cena-do=1000000&stranka="
    headers = {"User-Agent": "Mozilla/5.0"}

    results = []
    for page in range(1, max_pages + 1):
        url = base_url + str(page)
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        ads = soup.find_all("div", class_="property")

        if not ads:
            break

        for ad in ads:
            try:
                title = ad.find("span", class_="name").get_text(strip=True)
                locality = ad.find("span", class_="locality").get_text(strip=True)
                price_text = ad.find("span", class_="norm-price").get_text(strip=True)
                link = "https://www.sreality.cz" + ad.find("a")["href"]
                desc = ad.get_text()

                price = extract_number(price_text)
                area = extract_number(desc)
                mobilni_domy = any(kw in desc.lower() for kw in ["mobilheim", "mobilní", "tiny", "rekreační"])

                results.append({
                    "nazev": title,
                    "lokalita": locality,
                    "cena": price,
                    "vymera": area,
                    "odkaz": link,
                    "zdroj": "sreality.cz",
                    "datum_zverejneni": datetime.today().strftime("%Y-%m-%d"),
                    "mobilni_domy_vhodne": mobilni_domy
                })
            except Exception as e:
                print("Chyba při zpracování inzerátu:", e)

    with open("pozemky.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    scrape_sreality()
