import time

def scrape_idnes():
    print("🟦 Spouštím scraper: idnes")
    results = []

    # Simulace 2 záznamů
    for i in range(1, 3):
        print(f"🧭 Procházím stránku {i}: https://reality.idnes.cz/s/prodej/pozemky/stavebni-parcely/?price_to=1000000&page={i}")
        time.sleep(0.5)  # simulace čekání
        results.append({
            "lokalita": f"Ukázková lokalita {i}",
            "vymera": 1000 + i,
            "cena": 990000 - i * 10000,
            "okres": "Ukázkový okres",
            "kraj": "Ukázkový kraj",
            "lat": 50.0 + i * 0.01,
            "lon": 14.0 + i * 0.01,
            "vzdalenost_od": "Neratovice",
            "vzdalenost_km": 50 + i,
            "cesta_autem_min": 60 + i * 2,
            "sit_voda": True,
            "sit_cov": False,
            "sit_kanalizace": i % 2 == 0,
            "sit_elektrina": True,
            "mobilni_dum_vhodne": i % 2 == 1,
            "cislo_parcely": f"123{i}/1",
            "katastr": f"Katastr {i}",
            "uzemni_plan_url": None,
            "fotky": i + 2,
            "odkaz": f"https://reality.idnes.cz/detail/{i}",
            "zdroj": "reality.idnes.cz",
            "datum_zverejneni": "2025-04-06"
        })

    print(f"✅ idnes: nalezeno {len(results)} inzerátů")
    return results