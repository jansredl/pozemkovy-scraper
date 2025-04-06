
import datetime

def scrape():
    today = datetime.date.today().isoformat()
    return [
        {
            "lokalita": "Bernartice",
            "vymera": 1530,
            "cena": 1950000,
            "okres": "Trutnov",
            "lat": 50.583,
            "lon": 16.028,
            "vzdalenost_od": "Neratovice",
            "vzdalenost_km": 78.3,
            "cesta_autem_min": 82,
            "sit_voda": True,
            "sit_cov": False,
            "sit_kanalizace": True,
            "sit_elektrina": True,
            "mobilni_dum_vhodne": True,
            "cislo_parcely": "345/2",
            "katastr": "Bernartice u Trutnova",
            "uzemni_plan_url": "https://www.bernartice.eu/assets/File.ashx?id_org=12345&id_dokumenty=6789",
            "fotky": 9,
            "odkaz": "https://www.sreality.cz/detail/prodej/pozemek/bydleni/bernartice-bernartice-/3371065932",
            "zdroj": "sreality.cz",
            "datum_zverejneni": today
        }
    ]

if __name__ == "__main__":
    import json
    with open("pozemky.json", "w", encoding="utf-8") as f:
        json.dump(scrape(), f, ensure_ascii=False, indent=2)
