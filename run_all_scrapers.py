
import json
import traceback

from sreality_scraper import scrape_sreality
from bezrealitky_scraper import scrape_bezrealitky
from idnes_scraper import scrape_idnes

all_data = []

for name, scraper in [
    ("sreality", scrape_sreality),
    ("bezrealitky", scrape_bezrealitky),
    ("idnes", scrape_idnes),
]:
    try:
        print(f"Spouštím scraper: {name}")
        data = scraper()
        all_data.extend(data)
        print(f"✅ {name}: nalezeno {len(data)} inzerátů")
    except Exception as e:
        print(f"❌ Chyba při spuštění scraperu {name}: {e}")
        traceback.print_exc()

with open("pozemky.json", "w", encoding="utf-8") as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)

print(f"🔄 Celkem inzerátů: {len(all_data)}")
