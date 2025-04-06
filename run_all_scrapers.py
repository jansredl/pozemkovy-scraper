import json
from idnes_scraper import scrape_idnes

def run():
    data = []
    data.extend(scrape_idnes())

    print(f"✅ Celkem inzerátů: {len(data)}")
    with open("pozemky.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    run()