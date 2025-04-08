from idnes_scraper import scrape_idnes
import json

def run():
    print("🔍 Procházím stránku 1: https://reality.idnes.cz/s/prodej/pozemky/stavebni-pozemek/cena-do-1000000/")
    data = scrape_idnes()
    print(f"✅ Celkem inzerátů: {len(data)}")
    with open("pozemky.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    run()
