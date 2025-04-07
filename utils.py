
def geocode_address(city):
    # TODO: Tady by mělo být reálné geokódování
    lat = 50.0
    lon = 14.0
    okres = ""
    kraj = ""
    return lat, lon, okres, kraj

def haversine_distance(lat1, lon1, lat2, lon2):
    from math import radians, cos, sin, asin, sqrt
    R = 6371  # poloměr Země v km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    distance_km = R * c
    time_by_car_min = int(distance_km / 50 * 60)  # odhad průměrné rychlosti
    return round(distance_km), time_by_car_min
