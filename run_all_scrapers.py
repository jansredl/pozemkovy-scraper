from sreality_scraper import scrape_sreality
from bezrealitky_scraper import scrape_bezrealitky
from idnes_scraper import scrape_idnes
import json

def run():
    data = []
    try:
        data += scrape_sreality()
    except Exception as e:
        print(f"❌ Chyba při spuštění scraperu sreality: {e}")
    try:
        data += scrape_bezrealitky()
    except Exception as e:
        print(f"❌ Chyba při spuštění scraperu bezrealitky: {e}")
    try:
        data += scrape_idnes()
    except Exception as e:
        print(f"❌ Chyba při spuštění scraperu idnes: {e}")

    with open("pozemky.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ Celkem inzerátů: {len(data)}")

if __name__ == "__main__":
    run()