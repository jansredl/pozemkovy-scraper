import json
from datetime import datetime
from sreality_scraper import scrape_sreality
from bezrealitky_scraper import scrape_bezrealitky
from idnes_scraper import scrape_idnes

def main():
    data = []
    data += scrape_sreality()
    data += scrape_bezrealitky()
    data += scrape_idnes()

    for item in data:
        item.setdefault("datum_zverejneni", datetime.today().strftime("%Y-%m-%d"))

    with open("pozemky.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ Uloženo {len(data)} inzerátů do pozemky.json")

if __name__ == "__main__":
    main()