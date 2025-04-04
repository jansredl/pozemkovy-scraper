import requests
import json
import math
from datetime import datetime
from urllib.parse import urlencode

START_CITY = "Neratovice"

def get_coordinates(address):
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": address, "format": "json", "limit": 1}
        response = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        data = response.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except:
        return None, None
    return None, None

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(d_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 1)

def get_sreality_data():
    results = []
    base_url = "https://www.sreality.cz/api/cs/v2/estates"
    query = {
        "category_main_cb": 3,
        "category_sub_cb": 6,
        # Odebráno – hledání po celé ČR "region_entity_type": "municipality",
        # Odebráno – hledání po celé ČR "region_entity_id": 0,
        "per_page": 20,
        "tms": int(datetime.now().timestamp()),
        "price_to": 2000000,
        "offer_type": "sale",
        "page": 1
    }

    for page in range(1, 4):
        query["page"] = page
        url = f"{base_url}?{urlencode(query)}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            break
        data = response.json()["_embedded"]["estates"]
        for item in data:
            lokalita = item.get("locality", "").strip()
            nazev = item.get("name", "").strip()
            cena = item.get("price", 0)
            vymera = item.get("land_area", 0)
            odkaz = f'https://www.sreality.cz/detail/prodej/pozemek/{item.get("seo", {}).get("locality", "")}/{item.get("hash_id")}'
            okres = item.get("region_tip", {}).get("name", "")
            kraj = item.get("region", "")

            lat, lon = get_coordinates(lokalita)
            if lat and lon:
                start_lat, start_lon = get_coordinates(START_CITY)
                vzdalenost = haversine_distance(start_lat, start_lon, lat, lon)
            else:
                vzdalenost = None

            results.append({
                "nazev": nazev,
                "lokalita": lokalita,
                "cena": cena,
                "vymera": vymera,
                "odkaz": odkaz,
                "zdroj": "sreality.cz",
                "datum_zverejneni": datetime.today().strftime("%Y-%m-%d"),
                "okres": okres,
                "kraj": kraj,
                "lat": lat,
                "lon": lon,
                "vzdalenost_od": START_CITY,
                "vzdalenost_km": vzdalenost
            })
    return results

def run():
    pozemky = get_sreality_data()
    print(f"Nalezeno {len(pozemky)} pozemků")
    with open("pozemky.json", "w", encoding="utf-8") as f:
        json.dump(pozemky, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    run()
