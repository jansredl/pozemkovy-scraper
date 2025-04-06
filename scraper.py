
import json
from datetime import datetime
import re

def mock_scrape():
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
            "sit_voda": True,
            "sit_cov": False,
            "sit_kanalizace": True,
            "sit_elektrina": True,
            "cislo_parcely": "345/2",
            "katastr": "Bernartice u Trutnova",
            "uzemni_plan_url": "https://www.bernartice.eu/assets/File.ashx?id_org=12345&id_dokumenty=6789",
            "odkaz": "https://www.sreality.cz/detail/prodej/pozemek/bydleni/bernartice-bernartice-/3371065932",
            "zdroj": "sreality.cz",
            "datum_zverejneni": datetime.today().strftime('%Y-%m-%d'),
            "fotky": 9,
            "mobilni_dum_vhodne": True
        },
        {
            "lokalita": "Řeka",
            "vymera": 1069,
            "cena": 1835000,
            "okres": "Frýdek-Místek",
            "lat": 49.631,
            "lon": 18.541,
            "vzdalenost_od": "Neratovice",
            "vzdalenost_km": 298,
            "sit_voda": True,
            "sit_cov": True,
            "sit_kanalizace": False,
            "sit_elektrina": True,
            "cislo_parcely": "123/1",
            "katastr": "Řeka",
            "uzemni_plan_url": "https://www.obecreka.cz/uzemni-plan",
            "odkaz": "https://www.sreality.cz/detail/prodej/pozemek/bydleni/reka/1234567890",
            "zdroj": "sreality.cz",
            "datum_zverejneni": datetime.today().strftime('%Y-%m-%d'),
            "fotky": 6,
            "mobilni_dum_vhodne": False
        }
    ]

if __name__ == "__main__":
    data = mock_scrape()
    with open("pozemky.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
