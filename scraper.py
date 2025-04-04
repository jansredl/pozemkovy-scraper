import json
from datetime import datetime
import math

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(d_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 1)

def run():
    pozemky = [
  {
    "nazev": "Stavební pozemek u lesa",
    "lokalita": "Praha - západ, Jílové",
    "cena": 980000,
    "vymera": 612,
    "odkaz": "https://www.sreality.cz/detail/test1",
    "zdroj": "sreality.cz",
    "datum_zverejneni": "2025-04-04",
    "mobilni_domy_vhodne": True,
    "vzdalenost_od": "Praha",
    "vzdalenost_km": 20.3
  },
  {
    "nazev": "Rovinatý pozemek 500 m²",
    "lokalita": "Plzeň - sever, Kaznějov",
    "cena": 899000,
    "vymera": 500,
    "odkaz": "https://www.sreality.cz/detail/test2",
    "zdroj": "sreality.cz",
    "datum_zverejneni": "2025-04-04",
    "mobilni_domy_vhodne": false,
    "vzdalenost_od": "Praha",
    "vzdalenost_km": 78.1
  },
  {
    "nazev": "Klidný pozemek pro tiny house",
    "lokalita": "Vysočina, Žďár nad Sázavou",
    "cena": 750000,
    "vymera": 450,
    "odkaz": "https://www.sreality.cz/detail/test3",
    "zdroj": "sreality.cz",
    "datum_zverejneni": "2025-04-04",
    "mobilni_domy_vhodne": True,
    "vzdalenost_od": "Praha",
    "vzdalenost_km": 122.0
  }
]
    with open("pozemky.json", "w", encoding="utf-8") as f:
        json.dump(pozemky, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    run()
